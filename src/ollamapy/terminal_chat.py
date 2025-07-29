"""Terminal-based chat interface for Ollama with meta-reasoning."""

import sys
from typing import List, Dict, Optional
from difflib import SequenceMatcher
from .ollama_client import OllamaClient
from .actions import get_available_actions


class TerminalChat:
    """Terminal-based chat interface with AI meta-reasoning."""
    
    def __init__(self, model: str = "llama3.2:3b", system_message: str = "You are a helpful assistant."):
        """Initialize the chat interface.
        
        Args:
            model: The model to use for chat
            system_message: Optional system message to set context
        """
        self.client = OllamaClient()
        self.model = model
        self.system_message = system_message
        self.conversation: List[Dict[str, str]] = []
        self.actions = get_available_actions()
        
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
        print("  model           - Show current model")
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
            print(f"🎯 Current model: {self.model}")
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
        """Use AI to analyze user input and decide which function to call.
        
        Args:
            user_input: The user's input to analyze
            
        Returns:
            The chosen function name
        """
        # Build the action descriptions for the prompt
        action_list = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.actions.items()
        ])
        action_list_name_repeated = "\n".join([
            f"- {name} {name} {name} {name} {name}"
            for name, info in self.actions.items()
        ])
        
        analysis_prompt = f"""Given this user input: "{user_input}"

You must choose which function to call from these available options with respect to the user input:
{action_list}

Make sure to memorize those, they are important and are the only options you have to choose from.

Respond with only the name of the function you think is most relevent exactly 5 times space separated so that an algorithm can pick up the title of the function correctly without any typos.

All possible responses (YOU MUST PICK 1 FUNCTION NAME ONLY AND REPEAT THAT 5 TIMES):
{action_list_name_repeated}

"""

        # Create a temporary conversation for analysis (not stored in main conversation)
        analysis_messages = [{"role": "user", "content": analysis_prompt}]
        
        print("🧠 AI analyzing... ", end="", flush=True)
        
        response_content = ""
        try:
            for chunk in self.client.chat_stream(
                model=self.model,
                messages=analysis_messages,
                system=f"You are an assistant that must respond with exactly 5 words, each being one of these function names: {', '.join(self.actions.keys())}"
            ):
                response_content += chunk
            
            print(f"'{response_content.strip()}'")
            
            # Parse the response and determine function
            chosen_function = self.determine_function_from_response(response_content)
            print(f"🎯 Decision: {chosen_function}")
            
            return chosen_function
            
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            # Default to null action
            print(f"🎲 Defaulting to 'null'")
            return "null"
    
    def determine_function_from_response(self, response: str) -> str:
        """Use confidence-based fuzzy matching to determine which function to call.
        
        Args:
            response: The AI's response containing the 5 words
            
        Returns:
            The function name to call
        """
        # Split response into words and take first 5
        words = response.strip().lower().split()[:5]
        
        # Count occurrences and calculate confidence for each action
        action_scores = {}
        for action_name in self.actions:
            action_scores[action_name] = 0.0
            
            for word in words:
                # Calculate similarity between word and action name
                similarity = SequenceMatcher(None, word.lower(), action_name.lower()).ratio()
                action_scores[action_name] += similarity
        
        # Show confidence scores for available actions
        scores_display = ", ".join([f"{name}: {score:.2f}" for name, score in action_scores.items()])
        print(f"📊 Confidence scores - {scores_display}")
        
        # Return the action with highest score
        return max(action_scores, key=action_scores.get)
    
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
        
        print("🤖 AI: ", end="", flush=True)
        
        response_content = ""
        try:
            for chunk in self.client.chat_stream(
                model=self.model,
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