"""Terminal-based chat interface for Ollama."""

import sys
from typing import List, Dict
from .ollama_client import OllamaClient


class TerminalChat:
    """Terminal-based chat interface."""
    
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
        
    def setup(self) -> bool:
        """Setup the chat environment and ensure model is available."""
        print("🤖 OllamaPy Chat Interface")
        print("=" * 40)
        
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
        print("  model           - Show current model")
        print("  models          - List available models")
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
    
    def chat_loop(self):
        """Main chat loop."""
        while True:
            user_input = self.get_user_input()
            
            if not user_input:
                continue
            
            # Handle commands
            if self.handle_command(user_input):
                break
            
            # Add user message to conversation
            self.conversation.append({"role": "user", "content": user_input})
            
            # Get AI response
            print("🤖 Assistant: ", end="", flush=True)
            
            response_content = ""
            try:
                for chunk in self.client.chat_stream(
                    model=self.model,
                    messages=self.conversation,
                    system=self.system_message
                ):
                    print(chunk, end="", flush=True)
                    response_content += chunk
                
                print()  # New line after response
                
                # Add assistant response to conversation
                if response_content:
                    self.conversation.append({"role": "assistant", "content": response_content})
                
            except Exception as e:
                print(f"\n❌ Error getting response: {e}")
                # Remove the user message if we couldn't get a response
                if self.conversation and self.conversation[-1]["role"] == "user":
                    self.conversation.pop()
            
            print()  # Extra line for readability
    
    def run(self):
        """Run the chat interface."""
        if self.setup():
            self.chat_loop()