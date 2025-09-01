"""Enhanced Ollama API client with model context size support"""

import json
import logging
import re
import requests
from typing import Dict, List, Optional, Generator, Any

logger = logging.getLogger(__name__)


class OllamaClient:
    """Enhanced Ollama API client with model context size support"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize the Ollama client.

        Args:
            base_url: The base URL for the Ollama API server
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self._model_cache: Dict[str, int] = {}

    def is_available(self) -> bool:
        """Check if Ollama server is running and accessible."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except requests.exceptions.RequestException:
            return []

    def get_model_context_size(self, model: str) -> int:
        """Get the context window size for a model"""
        if model in self._model_cache:
            return self._model_cache[model]

        try:
            response = self.session.post(
                f"{self.base_url}/api/show", json={"name": model}
            )
            response.raise_for_status()
            data = response.json()

            # Try to extract context size from model info
            context_size = self._get_default_context_size(model)
            if "modelfile" in data:
                # Look for context size in modelfile
                match = re.search(r'num_ctx["\s]+(\d+)', data["modelfile"])
                if match:
                    context_size = int(match.group(1))

            self._model_cache[model] = context_size
            return context_size
        except:
            return 4096  # Default context size

    def _get_default_context_size(self, model: str) -> int:
        """Get default context size based on model name."""
        model_lower = model.lower()

        # Known context sizes for popular models
        if "gemma3:4b" in model_lower or "gemma2-2b" in model_lower:
            return 128000
        elif "llama3.2:3b" in model_lower or "llama3.2:1b" in model_lower:
            return 128000
        elif "llama3.1" in model_lower:
            return 128000
        elif "llama3:8b" in model_lower or "llama3:7b" in model_lower:
            return 8192
        elif "mistral" in model_lower:
            return 32768
        elif "codellama" in model_lower:
            return 16384
        else:
            return 4096  # Conservative default

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation).

        This uses a simple heuristic: ~4 characters per token on average.
        For more accurate counting, we could use tiktoken or similar, but
        this approximation is sufficient for context monitoring.
        """
        if not text:
            return 0

        # Simple estimation: 1 token ≈ 4 characters (varies by model/language)
        char_count = len(text)
        estimated_tokens = char_count // 3.5  # Slightly more conservative

        # Add some tokens for special tokens and formatting
        return int(estimated_tokens) + 10

    def count_prompt_tokens(
        self, prompt: str, system: Optional[str] = None, context: Optional[str] = None
    ) -> int:
        """Count approximate tokens for a complete prompt.

        Args:
            prompt: The main prompt text
            system: Optional system message
            context: Optional additional context

        Returns:
            Estimated total token count
        """
        total_tokens = 0

        if system:
            total_tokens += self.estimate_tokens(system)

        if context:
            total_tokens += self.estimate_tokens(context)

        total_tokens += self.estimate_tokens(prompt)

        # Add some buffer for formatting and special tokens
        return total_tokens + 20

    def get_context_usage(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get context window usage information.

        Args:
            model: The model name
            prompt: The prompt text
            system: Optional system message
            context: Optional additional context

        Returns:
            Dict with usage information
        """
        max_context = self.get_model_context_size(model)
        used_tokens = self.count_prompt_tokens(prompt, system, context)

        # Reserve some tokens for the response (typically 20-30% of context)
        response_reserve = int(max_context * 0.25)  # Reserve 25% for response
        available_for_prompt = max_context - response_reserve

        usage_percent = (used_tokens / available_for_prompt) * 100

        return {
            "model": model,
            "max_context": max_context,
            "used_tokens": used_tokens,
            "available_tokens": available_for_prompt,
            "reserved_for_response": response_reserve,
            "usage_percent": usage_percent,
            "is_over_limit": used_tokens > available_for_prompt,
        }

    def print_context_usage(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        context: Optional[str] = None,
    ) -> None:
        """Print context usage information."""
        usage = self.get_context_usage(model, prompt, system, context)

        # Color coding for usage levels
        if usage["usage_percent"] < 50:
            color = "\033[92m"  # Green
            status = "🟢"
        elif usage["usage_percent"] < 80:
            color = "\033[93m"  # Yellow
            status = "🟡"
        elif usage["usage_percent"] < 100:
            color = "\033[91m"  # Red
            status = "🟠"
        else:
            color = "\033[91m"  # Red
            status = "🔴"

        reset = "\033[0m"  # Reset color

        print(
            f"{status} Context: {color}{usage['usage_percent']:.1f}%{reset} ({usage['used_tokens']}/{usage['available_tokens']} tokens, {usage['model']})"
        )

        if usage["is_over_limit"]:
            print(f"⚠️  Warning: Prompt exceeds recommended context limit!")

    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        show_context: bool = True,
    ) -> str:
        """Generate a response from the model with context monitoring."""
        try:
            # Show context usage if requested
            if show_context:
                self.print_context_usage(model, prompt, system)

            payload = {"model": model, "prompt": prompt, "stream": False}
            if system:
                payload["system"] = system

            response = self.session.post(
                f"{self.base_url}/api/generate", json=payload, timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Generation failed: {e}")
            return ""

    def pull_model(self, model: str) -> bool:
        """Pull a model if it's not available locally."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/pull", json={"name": model}, stream=True
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "status" in data:
                        print(f"\r{data['status']}", end="", flush=True)
                    if data.get("status") == "success":
                        print()  # New line after completion
                        return True
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error pulling model: {e}")
            return False

    def chat_stream(
        self, model: str, messages: List[Dict[str, str]], system: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Stream chat responses from Ollama.

        Args:
            model: The model to use for chat
            messages: List of message dicts with 'role' and 'content'
            system: Optional system message

        Yields:
            Response chunks as strings
        """
        payload = {"model": model, "messages": messages, "stream": True}

        if system:
            payload["system"] = system

        try:
            response = self.session.post(
                f"{self.base_url}/api/chat", json=payload, stream=True
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
                    if data.get("done", False):
                        break

        except requests.exceptions.RequestException as e:
            yield f"Error: {e}"
