"""Terminal-based chat interface for Ollama with meta-reasoning."""

import sys
from typing import List, Dict, Optional
from difflib import SequenceMatcher
from .ollama_client import OllamaClient
from .actions import get_available_actions


class TerminalChat:
    """Terminal-based chat interface with AI meta-reasoning."""
    
    def __init__(self, model: str = "gemma3:4b", system_message: str = "You are a helpful assistant.", analysis_model: str = None):
        """Initialize the chat interface.
        
        Args:
            model: The model to use for chat responses
            system_message: Optional system message to set context
            analysis_model: Optional separate model for action analysis (defaults to main model)
        """
        self.client = OllamaClient()
        self.model = model
        self.analysis_model = analysis_model or model  # Use main model if no analysis model specified
        self.system_message = system_message
        self.conversation: List[Dict[str, str]] = []
        self.actions = get_available_actions()
        
    def setup(self) -> bool:
        """Setup the chat environment and ensure models are available."""
        print("🤖 OllamaPy Meta-Reasoning Chat Interface")
        print("=" * 50)
        
        # Check if Ollama is running
        if not self.client.is_available():
            print("❌ Error: Ollama server is not running!")
            print("Please start Ollama with: ollama serve")
            return False
        
        print("✅ Connected to Ollama server")
        
        # Check if models are available
        available_models = self.client.list_models()
        
        # Check main model
        main_model_available = any(self.model in model for model in available_models)
        if not main_model_available:
            print(f"📥 Chat model '{self.model}' not found locally. Pulling...")
            if not self.client.pull_model(self.model):
                print(f"❌ Failed to pull model '{self.model}'")
                return False
        
        # Check analysis model (if different from main model)
        if self.analysis_model != self.model:
            analysis_model_available = any(self.analysis_model in model for model in available_models)
            if not analysis_model_available:
                print(f"📥 Analysis model '{self.analysis_model}' not found locally. Pulling...")
                if not self.client.pull_model(self.analysis_model):
                    print(f"❌ Failed to pull analysis model '{self.analysis_model}'")
                    return False
        
        print(f"🎯 Using chat model: {self.model}")
        if self.analysis_model != self.model:
            print(f"🔍 Using analysis model: {self.analysis_model}")
        else:
            print(f"🔍 Using same model for analysis and chat")
        
        if available_models:
            print(f"📚 Available models: {', '.join(available_models[:3])}{'...' if len(available_models) > 3 else ''}")
        
        print(f"\n🧠 Meta-reasoning mode: AI will analyze your input and choose from {len(self.actions)} available actions:")
        for action_name in self.actions:
            print(f"   • {action_name}")
        print("\n💬 Chat started! Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("   Type 'clear' to clear conversation history.")
        print("   Type 'help' for more commands.\n")
        
        return True
    
    def print_help(self):
        """Print help information."""
        print("\n📖 Available commands:")
        print("  quit, exit, bye  - End the conversation")
        print("  clear           - Clear conversation history")
        print("  help            - Show this help message")
        print("  model           - Show current models")
        print("  models          - List available models")
        print("  actions         - Show available actions the AI can choose")
        print(f"\n🧠 Meta-reasoning: The AI analyzes your input and chooses from {len(self.actions)} available functions.")
        print()
    
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        command = user_input.lower().strip()
        
        if command in ['quit', 'exit', 'bye']:
            print("\n👋 Goodbye! Thanks for chatting!")
            return True
        
        elif command == 'clear':
            self.conversation.clear()
            print("🧹 Conversation history cleared!")
            return False
        
        elif command == 'help':
            self.print_help()
            return False
        
        elif command == 'model':
            print(f"🎯 Chat model: {self.model}")
            if self.analysis_model != self.model:
                print(f"🔍 Analysis model: {self.analysis_model}")
            else:
                print("🔍 Using same model for analysis and chat")
            return False
        
        elif command == 'models':
            models = self.client.list_models()
            if models:
                print(f"📚 Available models: {', '.join(models)}")
            else:
                print("❌ No models found")
            return False
        
        elif command == 'actions':
            print(f"🔧 Available actions ({len(self.actions)}):")
            for name, info in self.actions.items():
                print(f"   • {name}: {info['description']}")
            return False
        
        return False
    
    def get_user_input(self) -> str:
        """Get user input with a nice prompt."""
        try:
            return input("👤 You: ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for chatting!")
            sys.exit(0)
        except EOFError:
            print("\n\n👋 Goodbye! Thanks for chatting!")
            sys.exit(0)
    
    def analyze_with_ai(self, user_input: str) -> str:
        """Use AI to analyze user input and decide which function to call."""
        
        # Build a structured prompt that encourages clear, parseable output
        action_descriptions = []
        for name, info in self.actions.items():
            action_descriptions.append(f'"{name}": "{info["description"]}"')
        
        analysis_prompt = f"""Analyze this user input and select the most appropriate action.

    User input: "{user_input}"

    Available actions:
    {{{', '.join(action_descriptions)}}}

    Respond with ONLY a JSON object in this exact format:
    {{"action": "action_name", "confidence": 0.95, "reasoning": "brief explanation"}}

    The action MUST be one of: {', '.join(self.actions.keys())}
    Confidence should be between 0 and 1.
    If no action clearly matches, use "null" with lower confidence."""

        print(f"🔍 Analysis model ({self.analysis_model}) analyzing... ", end="", flush=True)
        
        response_content = ""
        try:
            for chunk in self.client.chat_stream(
                model=self.analysis_model,
                messages=[{"role": "user", "content": analysis_prompt}],
                system="You are a function selector. Respond only with valid JSON."
            ):
                response_content += chunk
            
            print(f"✓")
            
            # Try to parse as JSON first (most reliable)
            chosen_function = self.parse_json_response(response_content)
            
            # If JSON parsing fails, fall back to keyword matching
            if not chosen_function:
                chosen_function = self.fallback_keyword_matching(response_content, user_input)
            
            print(f"🎯 Decision: {chosen_function}")
            return chosen_function
            
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            return "null"

    def parse_json_response(self, response: str) -> Optional[str]:
        """Try to parse JSON response from AI."""
        import json
        import re
        
        # Extract JSON from response (in case there's extra text)
        json_match = re.search(r'\{[^{}]+\}', response)
        if not json_match:
            return None
        
        try:
            data = json.loads(json_match.group())
            action = data.get('action', '').lower()
            confidence = data.get('confidence', 0)
            reasoning = data.get('reasoning', '')
            
            # Validate action exists
            if action in [a.lower() for a in self.actions.keys()]:
                # Find the correct case
                for correct_name in self.actions.keys():
                    if correct_name.lower() == action:
                        print(f"📊 Confidence: {confidence:.2f} - {reasoning[:50]}...")
                        return correct_name
        except json.JSONDecodeError:
            pass
        
        return None

    def fallback_keyword_matching(self, response: str, user_input: str) -> str:
        """Fallback method using keyword and intent matching."""
        response_lower = response.lower()
        user_input_lower = user_input.lower()
        
        scores = {}
        
        for action_name, action_info in self.actions.items():
            score = 0.0
            action_lower = action_name.lower()
            
            # Direct mention in response
            if action_lower in response_lower:
                score += 0.5
            
            # Check description keywords against user input
            description_words = action_info['description'].lower().split()
            important_words = [w for w in description_words if len(w) > 3]
            
            for word in important_words:
                if word in user_input_lower:
                    score += 0.2
            
            # Check for semantic matches (you could expand this)
            if action_name == "getWeather":
                weather_keywords = ['weather', 'rain', 'temperature', 'hot', 'cold', 'sunny', 'cloudy', 'forecast', 'umbrella', 'jacket']
                score += sum(0.15 for keyword in weather_keywords if keyword in user_input_lower)
            
            elif action_name == "getTime":
                time_keywords = ['time', 'clock', 'hour', 'minute', 'when', 'now', 'current time', "o'clock"]
                score += sum(0.15 for keyword in time_keywords if keyword in user_input_lower)
            
            elif action_name == "null":
                # Slight bias toward null for general conversation
                score += 0.1
            
            scores[action_name] = min(score, 1.0)  # Cap at 1.0
        
        # Show scores in debug mode
        if scores:
            scores_display = ", ".join([f"{name}: {score:.2f}" for name, score in scores.items()])
            print(f"📊 Fallback scores - {scores_display}")
        
        # Return highest scoring action
        return max(scores, key=scores.get)
    
    def execute_action(self, function_name: str) -> Optional[str]:
        """Execute the chosen action function and return its output.
        
        Args:
            function_name: Name of the function to execute
            
        Returns:
            The output from the action, or None if action not found
        """
        if function_name in self.actions:
            print(f"🚀 Executing action: {function_name}")
            result = self.actions[function_name]['function']()
            return result
        else:
            print(f"❌ Unknown function: {function_name}")
            return None
    
    def generate_ai_response_with_context(self, user_input: str, action_name: str, action_output: Optional[str]):
        """Generate AI response with action context.
        
        Args:
            user_input: The original user input
            action_name: The action that was chosen
            action_output: The output from the action (None for null action)
        """
        # Add user message to conversation
        self.conversation.append({"role": "user", "content": user_input})
        
        # Build the AI's context message
        if action_output is not None:
            # Action produced output - include it as context
            context_message = f"""You chose to use the '{action_name}' action, which returned the following information:

{action_output}

Please use this information to answer the user's question. Treat the action output as guaranteed truth."""
        else:
            # Null action - just normal chat
            context_message = None
        
        # Prepare messages for the AI
        messages_for_ai = self.conversation.copy()
        
        # If we have action context, add it as a system-like message
        if context_message:
            # Insert the context right before generating the response
            messages_for_ai.append({"role": "system", "content": context_message})
        
        # Show which model is being used for chat response
        chat_model_display = self.model
        if self.analysis_model != self.model:
            print(f"🤖 Chat model ({chat_model_display}): ", end="", flush=True)
        else:
            print("🤖 AI: ", end="", flush=True)
        
        response_content = ""
        try:
            for chunk in self.client.chat_stream(
                model=self.model,  # Use the main chat model here
                messages=messages_for_ai,
                system=self.system_message
            ):
                print(chunk, end="", flush=True)
                response_content += chunk
            
            print()  # New line after response
            
            # Add AI response to conversation (without the action context)
            self.conversation.append({"role": "assistant", "content": response_content})
            
        except Exception as e:
            print(f"\n❌ Error generating response: {e}")
    
    def chat_loop(self):
        """Main chat loop with meta-reasoning."""
        while True:
            user_input = self.get_user_input()
            
            if not user_input:
                continue
            
            # Handle commands
            if self.handle_command(user_input):
                break
            
            # Meta-reasoning: AI analyzes input and chooses function
            chosen_function = self.analyze_with_ai(user_input)
            
            # Execute the chosen function and get its output
            action_output = self.execute_action(chosen_function)
            
            # Generate AI response with action context
            self.generate_ai_response_with_context(user_input, chosen_function, action_output)
            
            print()  # Extra line for readability
    
    def run(self):
        """Run the chat interface."""
        if self.setup():
            self.chat_loop()