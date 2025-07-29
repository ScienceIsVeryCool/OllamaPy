"""Terminal-based chat interface for Ollama with meta-reasoning."""

import sys
from typing import List, Dict
from difflib import SequenceMatcher
from .ollama_client import OllamaClient
from .actions import yes, no


class TerminalChat:
    """Terminal-based chat interface with AI meta-reasoning."""
    
    def __init__(self, model: str = "gemma3:4b", system_message: str = "You are a helpful assistant."):
        """Initialize the chat interface.
        
        Args:
            model: The model to use for chat
            system_message: Optional system message to set context
        """
        self.client = OllamaClient()
        self.model = model
        self.system_message = system_message
        self.conversation: List[Dict[str, str]] = []
        self.actions = {
            "yes": yes,
            "no": no
        }
        
    def setup(self) -> bool:
        """Setup the chat environment and ensure model is available."""
        print("🤖 OllamaPy Meta-Reasoning Chat Interface")
        print("=" * 50)
        
        # Check if Ollama is running
        if not self.client.is_available():
            print("❌ Error: Ollama server is not running!")
            print("Please start Ollama with: ollama serve")
            return False
        
        print("✅ Connected to Ollama server")
        
        # Check if model is available
        available_models = self.client.list_models()
        model_available = any(self.model in model for model in available_models)
        
        if not model_available:
            print(f"📥 Model '{self.model}' not found locally. Pulling...")
            if not self.client.pull_model(self.model):
                print(f"❌ Failed to pull model '{self.model}'")
                return False
        
        print(f"🎯 Using model: {self.model}")
        
        if available_models:
            print(f"📚 Available models: {', '.join(available_models[:3])}{'...' if len(available_models) > 3 else ''}")
        
        print("\n🧠 Meta-reasoning mode: AI will analyze your input and choose between 'yes' or 'no' actions.")
        print("💬 Chat started! Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("   Type 'clear' to clear conversation history.")
        print("   Type 'help' for more commands.\n")
        
        return True
    
    def print_help(self):
        """Print help information."""
        print("\n📖 Available commands:")
        print("  quit, exit, bye  - End the conversation")
        print("  clear           - Clear conversation history")
        print("  help            - Show this help message")
        print("  model           - Show current model")
        print("  models          - List available models")
        print("\n🧠 Meta-reasoning: The AI analyzes your input and chooses to run either 'yes' or 'no' function.")
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
            print(f"🎯 Current model: {self.model}")
            return False
        
        elif command == 'models':
            models = self.client.list_models()
            if models:
                print(f"📚 Available models: {', '.join(models)}")
            else:
                print("❌ No models found")
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
        """Use AI to analyze user input and decide between yes/no functions.
        
        Args:
            user_input: The user's input to analyze
            
        Returns:
            The chosen function name ('yes' or 'no')
        """
        analysis_prompt = f"""Given this user input: "{user_input}"

You must choose between calling a 'yes' function or a 'no' function. 

Respond with exactly 5 repeated words. Each word must be either 'yes' or 'no'. This will help determine which function to call.

Example responses:
- yes yes yes yes yes
- no no no no no

Your 5 words:"""

        # Create a temporary conversation for analysis
        analysis_messages = [{"role": "user", "content": analysis_prompt}]
        
        print("🧠 AI analyzing... ", end="", flush=True)
        
        response_content = ""
        try:
            for chunk in self.client.chat_stream(
                model=self.model,
                messages=analysis_messages,
                system="You are an assistant that must respond with exactly 5 words, each being either 'yes' or 'no'."
            ):
                response_content += chunk
            
            print(f"'{response_content.strip()}'")
            
            # Parse the response and determine function
            chosen_function = self.determine_function_from_response(response_content)
            print(f"🎯 Decision: {chosen_function}")
            
            return chosen_function
            
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            print("🎲 Defaulting to 'no'")
            return "no"
    
    def determine_function_from_response(self, response: str) -> str:
        """Use confidence-based fuzzy matching to determine which function to call.
        
        Args:
            response: The AI's response containing the 5 words
            
        Returns:
            The function name to call ('yes' or 'no')
        """
        # Split response into words and take first 5
        words = response.strip().lower().split()[:5]
        
        yes_confidence = 0.0
        no_confidence = 0.0
        
        for word in words:
            # Calculate similarity to 'yes' and 'no'
            yes_similarity = SequenceMatcher(None, word, "yes").ratio()
            no_similarity = SequenceMatcher(None, word, "no").ratio()
            
            yes_confidence += yes_similarity
            no_confidence += no_similarity
        
        print(f"📊 Confidence scores - Yes: {yes_confidence:.2f}, No: {no_confidence:.2f}")
        
        return "yes" if yes_confidence > no_confidence else "no"
    
    def execute_action(self, function_name: str):
        """Execute the chosen action function.
        
        Args:
            function_name: Name of the function to execute
        """
        if function_name in self.actions:
            print("🚀 Executing action:")
            self.actions[function_name]()
        else:
            print(f"❌ Unknown function: {function_name}")
            print("🎲 Defaulting to 'no'")
            self.actions["no"]()
    
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
            
            # Execute the chosen function
            self.execute_action(chosen_function)
            
            print()  # Extra line for readability
    
    def run(self):
        """Run the chat interface."""
        if self.setup():
            self.chat_loop()