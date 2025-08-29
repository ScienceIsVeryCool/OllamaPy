"""Enhanced Ollama API client with model context size support"""

import json
import logging
import re
import requests
from typing import Dict, List, Optional, Generator

logger = logging.getLogger(__name__)


class OllamaClient:
    """Enhanced Ollama API client with model context size support"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize the Ollama client. 
        
        Args:
            base_url: The base URL for the Ollama API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self._model_cache = {}
    
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
            return [model['name'] for model in data.get('models', [])]
        except requests.exceptions.RequestException:
            return []
    
    def get_model_context_size(self, model: str) -> int:
        """Get the context window size for a model"""
        if model in self._model_cache:
            return self._model_cache[model]
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model}
            )
            response.raise_for_status()
            data = response.json()
            
            # Try to extract context size from model info
            context_size = 4096  # Default
            if 'modelfile' in data:
                # Look for context size in modelfile
                match = re.search(r'num_ctx["\s]+(\d+)', data['modelfile'])
                if match:
                    context_size = int(match.group(1))
            
            self._model_cache[model] = context_size
            return context_size
        except:
            return 4096  # Default context size
    
    def generate(self, model: str, prompt: str, system: Optional[str] = None) -> str:
        """Generate a response from the model"""
        try:
            payload = {"model": model, "prompt": prompt, "stream": False}
            if system:
                payload["system"] = system
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.RequestException as e:
            logger.error(f"Generation failed: {e}")
            return ""

    def pull_model(self, model: str) -> bool:
        """Pull a model if it's not available locally."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'status' in data:
                        print(f"\r{data['status']}", end='', flush=True)
                    if data.get('status') == 'success':
                        print()  # New line after completion
                        return True
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error pulling model: {e}")
            return False
    
    def chat_stream(self, model: str, messages: List[Dict[str, str]], 
                   system: Optional[str] = None) -> Generator[str, None, None]:
        """Stream chat responses from Ollama.
        
        Args:
            model: The model to use for chat
            messages: List of message dicts with 'role' and 'content'
            system: Optional system message
            
        Yields:
            Response chunks as strings
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'message' in data and 'content' in data['message']:
                        yield data['message']['content']
                    if data.get('done', False):
                        break
                        
        except requests.exceptions.RequestException as e:
            yield f"Error: {e}"