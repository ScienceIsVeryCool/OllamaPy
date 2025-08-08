"""Terminal-based chat interface for Ollama with simplified meta-reasoning."""

import sys
import re
from typing import List, Dict, Optional, Tuple, Any
from .ollama_client import OllamaClient
from .actions import get_available_actions, execute_action, get_action_logs, clear_action_logs


class TerminalChat:
    """Terminal-based chat interface with simplified AI meta-reasoning.
    
    This class implements a straightforward action selection process:
    1. For EVERY available action, ask the AI a simple yes/no question
    2. For each selected action, extract parameters individually
    3. Execute ALL selected actions, collecting their log outputs
    4. Use the combined logs as context for the response
    """
    
    def __init__(self, model: str = "gemma3:4b", 
                 system_message: str = "You are a helpful assistant.", 
                 analysis_model: str = "gemma3:4b"):
        """Initialize the chat interface.
        
        Args:
            model: The model to use for chat responses
            system_message: Optional system message to set context
            analysis_model: Optional separate model for action analysis (defaults to main model)
        """
        self.client = OllamaClient()
        self.model = model
        self.analysis_model = analysis_model or model
        self.system_message = system_message
        self.conversation: List[Dict[str, str]] = []
        self.actions = get_available_actions()
        
    def setup(self) -> bool:
        """Setup the chat environment and ensure models are available."""
        print("🤖 OllamaPy Multi-Action Chat Interface")
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
        
        print(f"\n🧠 Multi-action system: AI evaluates ALL {len(self.actions)} actions for every query")
        for action_name, action_info in self.actions.items():
            params = action_info.get('parameters', {})
            if params:
                param_list = ', '.join([f"{p}: {info['type']}" for p, info in params.items()])
                print(f"   • {action_name} ({param_list})")
            else:
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
        print(f"\n🧠 Multi-action: The AI evaluates ALL actions and can run multiple per query.")
        print()
    
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled and should exit."""
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
                params = info.get('parameters', {})
                if params:
                    param_list = ', '.join([f"{p}: {spec['type']}" for p, spec in params.items()])
                    print(f"   • {name}({param_list}): {info['description']}")
                else:
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
    
    def remove_thinking_blocks(self, text: str) -> str:
        """Remove <think></think> blocks from AI output.
        
        This allows models with thinking steps to be used without interference.
        
        Args:
            text: The text to clean
            
        Returns:
            The text with thinking blocks removed
        """
        # Remove <think>...</think> blocks (including nested content)
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        return cleaned.strip()
    
    def ask_yes_no_question(self, prompt: str) -> bool:
        """Ask the analysis model a yes/no question and parse the response.
        
        This is the core of our simplified analysis. We ask a clear yes/no question
        and parse the response to determine if the answer is yes.
        
        Args:
            prompt: The yes/no question to ask
            
        Returns:
            True if the model answered yes, False otherwise
        """
        response_content = ""
        try:
            # Stream the response from the analysis model
            for chunk in self.client.chat_stream(
                model=self.analysis_model,
                messages=[{"role": "user", "content": prompt}],
                system="You are a decision assistant. Answer only 'yes' or 'no' to questions."
            ):
                response_content += chunk
            
            # Remove thinking blocks if present
            cleaned_response = self.remove_thinking_blocks(response_content)
            
            # Convert to lowercase for easier parsing
            response_lower = cleaned_response.lower().strip()
            
            # Check for yes indicators at the beginning of the response
            # This handles "yes", "yes.", "yes,", "yes!", etc.
            if response_lower.startswith('yes'):
                return True
            
            # Also check if just "yes" appears alone in the first few characters
            if response_lower[:10].strip() == 'yes':
                return True
                
            # If we see "no" at the start, definitely return False
            if response_lower.startswith('no'):
                return False
                
            # Default to False if unclear
            return False
            
        except Exception as e:
            print(f"\n❌ Error during yes/no question: {e}")
            return False
    
    def extract_single_parameter(self, user_input: str, action_name: str, 
                                param_name: str, param_spec: Dict[str, Any]) -> Any:
        """Extract a single parameter value from user input.
        
        This asks the AI to extract just one parameter value, making it simple and reliable.
        
        Args:
            user_input: The original user input
            action_name: The name of the action being executed
            param_name: The name of the parameter to extract
            param_spec: The specification for this parameter (type, description, required)
            
        Returns:
            The extracted parameter value, or None if not found
        """
        param_type = param_spec.get('type', 'string')
        param_desc = param_spec.get('description', '')
        is_required = param_spec.get('required', False)
        
        # Build a simple, focused prompt for parameter extraction
        prompt = f"""From this user input: "{user_input}"

Extract the value for the parameter '{param_name}' which is described as: {param_desc}

The parameter type is: {param_type}

Respond with ONLY the parameter value, nothing else.
If the parameter value cannot be found in the user input, respond with only: NOT_FOUND

Examples for {param_type} type:
- If type is number and user says "square root of 16", respond: 16
- If type is string and user says "weather in Paris", respond: Paris
- If type is string and user says "calculate 5+3", respond: 5+3
"""
        
        response_content = ""
        try:
            # Stream the response
            for chunk in self.client.chat_stream(
                model=self.analysis_model,
                messages=[{"role": "user", "content": prompt}],
                system="You are a parameter extractor. Respond only with the extracted value or NOT_FOUND."
            ):
                response_content += chunk
            
            # Remove thinking blocks
            cleaned_response = self.remove_thinking_blocks(response_content).strip()
            
            # Check if not found
            if 'NOT_FOUND' in cleaned_response.upper() or not cleaned_response:
                return None
            
            # Process based on type
            if param_type == 'number':
                # Try to extract a number from the response
                # First try to convert the whole response
                try:
                    value = float(cleaned_response)
                    return int(value) if value.is_integer() else value
                except:
                    # Try to find a number in the response
                    import re
                    numbers = re.findall(r'-?\d+\.?\d*', cleaned_response)
                    if numbers:
                        value = float(numbers[0])
                        return int(value) if value.is_integer() else value
                    return None
            else:
                # For string type, return the cleaned response
                return cleaned_response
                
        except Exception as e:
            print(f"\n❌ Error extracting parameter '{param_name}': {e}")
            return None
    
    def select_all_applicable_actions(self, user_input: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Select ALL applicable actions and extract their parameters.
        
        This evaluates EVERY action and returns a list of all that apply.
        
        Args:
            user_input: The user's input to analyze
            
        Returns:
            List of tuples containing (action_name, parameters_dict)
        """
        print(f"🔍 Analyzing user input with {self.analysis_model}...")
        
        selected_actions = []
        
        # Iterate through EVERY action and check if it's applicable
        for action_name, action_info in self.actions.items():
            # Build a comprehensive prompt for this specific action
            description = action_info['description']
            vibe_phrases = action_info.get('vibe_test_phrases', [])
            parameters = action_info.get('parameters', {})
            
            # Create the yes/no prompt for this action
            prompt = f"""Consider this user input: "{user_input}"

Should the '{action_name}' action be used?

Action description: {description}

Example phrases that would trigger this action:
{chr(10).join(f'- "{phrase}"' for phrase in vibe_phrases[:5]) if vibe_phrases else '- No examples available'}

{f"This action requires parameters: {', '.join(parameters.keys())}" if parameters else "This action requires no parameters"}

Answer only 'yes' if this action should be used for the user's input, or 'no' if it should not.
"""
            
            # Ask if this action is applicable
            print(f"  Checking {action_name}... ", end="", flush=True)
            
            if self.ask_yes_no_question(prompt):
                print("✓ Selected!", end="")
                
                # Extract parameters if needed
                extracted_params = {}
                if parameters:
                    print(" Extracting parameters:", end="")
                    
                    for param_name, param_spec in parameters.items():
                        value = self.extract_single_parameter(
                            user_input, action_name, param_name, param_spec
                        )
                        
                        if value is not None:
                            extracted_params[param_name] = value
                            print(f" {param_name}✓", end="")
                        else:
                            if param_spec.get('required', False):
                                print(f" {param_name}✗(required)", end="")
                                # Still add the action, but note the missing parameter
                            else:
                                print(f" {param_name}✗", end="")
                
                selected_actions.append((action_name, extracted_params))
                print()  # New line after this action
            else:
                print("✗")
        
        if selected_actions:
            print(f"🎯 Selected {len(selected_actions)} action(s): {', '.join([a[0] for a in selected_actions])}")
        else:
            print("🎯 No specific actions needed for this query")
        
        return selected_actions
    
    def execute_multiple_actions(self, actions_with_params: List[Tuple[str, Dict[str, Any]]]) -> str:
        """Execute multiple actions and collect their log outputs.
        
        Args:
            actions_with_params: List of (action_name, parameters) tuples
            
        Returns:
            Combined log output from all actions
        """
        if not actions_with_params:
            return ""
        
        # Clear any previous logs
        clear_action_logs()
        
        print(f"🚀 Executing {len(actions_with_params)} action(s)...")
        
        for action_name, parameters in actions_with_params:
            print(f"   Running {action_name}", end="")
            if parameters:
                print(f" with {parameters}", end="")
            print("...")
            
            # Execute the action (it will log internally)
            execute_action(action_name, parameters)
        
        # Get all the logs that were generated
        combined_logs = get_action_logs()
        
        if combined_logs:
            print(f"📝 Actions generated {len(combined_logs)} log entries")
        
        return "\n".join(combined_logs)
    
    def generate_ai_response_with_context(self, user_input: str, action_logs: str):
        """Generate AI response with action context from logs.
        
        Args:
            user_input: The original user input
            action_logs: The combined log output from all executed actions
        """
        # Add user message to conversation
        self.conversation.append({"role": "user", "content": user_input})
        
        # Build the AI's context message
        if action_logs:
            # Actions produced logs - include them as context
            context_message = f"""<context>
The following information was gathered from various tools and actions:

{action_logs}

Use this information to provide a comprehensive and accurate response to the user.
</context>"""
        else:
            # No actions executed - just normal chat
            context_message = None
        
        # Prepare messages for the AI
        messages_for_ai = self.conversation.copy()
        
        # If we have action context, add it as a system-like message
        if context_message:
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
        """Main chat loop with multi-action execution."""
        while True:
            user_input = self.get_user_input()
            
            if not user_input:
                continue
            
            # Handle commands
            if self.handle_command(user_input):
                break
            
            # Select ALL applicable actions and extract their parameters
            selected_actions = self.select_all_applicable_actions(user_input)
            
            # Execute all selected actions and collect logs
            action_logs = self.execute_multiple_actions(selected_actions)
            
            # Generate AI response with action context from logs
            self.generate_ai_response_with_context(user_input, action_logs)
            
            print()  # Extra line for readability
    
    def run(self):
        """Run the chat interface."""
        if self.setup():
            self.chat_loop()