"""Terminal-based chat interface for Ollama with meta-reasoning."""

import sys
import json
import re
from typing import List, Dict, Optional, Tuple, Any
from difflib import SequenceMatcher
from .ollama_client import OllamaClient
from .actions import get_available_actions, execute_action


class TerminalChat:
    """Terminal-based chat interface with AI meta-reasoning."""
    
    def __init__(self, model: str = "gemma3:4b", system_message: str = "You are a helpful assistant.", 
                 analysis_model: str = "gemma:3:4b", two_step_analysis: bool = True):
        """Initialize the chat interface.
        
        Args:
            model: The model to use for chat responses
            system_message: Optional system message to set context
            analysis_model: Optional separate model for action analysis (defaults to main model)
            two_step_analysis: If True, use separate steps for action and parameter selection
        """
        self.client = OllamaClient()
        self.model = model
        self.analysis_model = analysis_model or model  # Use main model if no analysis model specified
        self.system_message = system_message
        self.conversation: List[Dict[str, str]] = []
        self.actions = get_available_actions()
        self.two_step_analysis = True # TODO somehow cant get this to default true and this doesnt feel like the right place
        
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
        
        if self.two_step_analysis:
            print(f"🔄 Two-step analysis mode enabled")
        else:
            print(f"🔄 Two-step analysis mode disabled")
        
        if available_models:
            print(f"📚 Available models: {', '.join(available_models[:3])}{'...' if len(available_models) > 3 else ''}")
        
        print(f"\n🧠 Meta-reasoning mode: AI will analyze your input and choose from {len(self.actions)} available actions:")
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
    
    def analyze_with_ai_single_step(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """Single-step analysis: AI selects both action and parameters in one go."""
        
        # Build action descriptions including parameters
        action_descriptions = []
        for name, info in self.actions.items():
            desc = f'"{name}": "{info["description"]}"'
            params = info.get('parameters', {})
            if params:
                param_desc = ", parameters: {" + ", ".join([
                    f'"{p}": {{"type": "{spec["type"]}", "required": {str(spec.get("required", False)).lower()}}}'
                    for p, spec in params.items()
                ]) + "}"
                desc += param_desc
            action_descriptions.append(desc)
        
        analysis_prompt = f"""Analyze this user input and select the most appropriate action with parameters.

User input: "{user_input}"

Available actions:
{{{', '.join(action_descriptions)}}}

Respond with ONLY a JSON object in this exact format:
{{"action": "action_name", "parameters": {{"param_name": value}}, "confidence": 0.95, "reasoning": "brief explanation"}}

Rules:
- The action MUST be one of: {', '.join(self.actions.keys())}
- Include parameters ONLY if the action requires them
- Extract parameter values from the user input when possible
- For number parameters, extract the numeric value
- For string parameters, extract relevant text
- If a required parameter can't be extracted, use a reasonable default or ask for clarification
- Confidence should be between 0 and 1"""

        print(f"🔍 Analysis model ({self.analysis_model}) analyzing... ", end="", flush=True)
        
        response_content = ""
        try:
            for chunk in self.client.chat_stream(
                model=self.analysis_model,
                messages=[{"role": "user", "content": analysis_prompt}],
                system="You are a function selector. Respond only with valid JSON."
            ):
                response_content += chunk
            
            print("✓")
            
            # Parse the response
            result = self.parse_ai_decision(response_content, user_input)
            
            print(f"🎯 Decision: {result[0]}")
            if result[1]:
                print(f"📊 Parameters: {result[1]}")
            
            return result
            
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            return "null", {}
    
    def analyze_with_ai_two_step(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """Two-step analysis: First select action, then extract parameters."""
        
        # Step 1: Select action (existing logic)
        action = self.analyze_with_ai(user_input)
        
        # Step 2: Extract parameters if needed
        action_info = self.actions.get(action, {})
        params_spec = action_info.get('parameters', {})
        
        if not params_spec:
            return action, {}
        
        # Build parameter extraction prompt
        param_descriptions = []
        for param_name, spec in params_spec.items():
            required = "required" if spec.get('required', False) else "optional"
            param_descriptions.append(
                f'"{param_name}": type={spec["type"]}, {required}, description="{spec["description"]}"'
            )
        
        extract_prompt = f"""Extract parameter values for the '{action}' action from this user input.

User input: "{user_input}"

Required parameters:
{{{', '.join(param_descriptions)}}}

Respond with ONLY a JSON object containing the parameter values:
{{"param_name": value, ...}}

Rules:
- Extract numeric values for number type parameters
- Extract relevant text for string type parameters
- If a value can't be found, omit it from the response
- Be precise with number extraction"""

        print(f"📊 Extracting parameters... ", end="", flush=True)
        
        response_content = ""
        try:
            for chunk in self.client.chat_stream(
                model=self.analysis_model,
                messages=[{"role": "user", "content": extract_prompt}],
                system="You are a parameter extractor. Respond only with valid JSON."
            ):
                response_content += chunk
            
            print("✓")
            
            # Parse parameters
            parameters = self.parse_parameters(response_content)
            if parameters:
                print(f"📊 Parameters: {parameters}")
            
            return action, parameters
            
        except Exception as e:
            print(f"\n❌ Error extracting parameters: {e}")
            return action, {}
    
    def analyze_with_ai(self, user_input: str) -> str:
        """Original method for action selection only (used in two-step mode)."""
        
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

        print(f"🔍 Analysis model ({self.analysis_model}) selecting action... ", end="", flush=True)
        
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
            
            print(f"🎯 Action selected: {chosen_function}")
            return chosen_function
            
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            return "null"
    
    def parse_ai_decision(self, response: str, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """Parse AI response to extract action and parameters."""
        
        # Try JSON parsing first
        json_match = re.search(r'\{[^{}]+\}', response)
        if json_match:
            try:
                data = json.loads(json_match.group())
                action = data.get('action', '').lower()
                parameters = data.get('parameters', {})
                confidence = data.get('confidence', 0)
                reasoning = data.get('reasoning', '')
                
                # Validate action exists
                if action in [a.lower() for a in self.actions.keys()]:
                    # Find the correct case
                    for correct_name in self.actions.keys():
                        if correct_name.lower() == action:
                            print(f"📊 Confidence: {confidence:.2f} - {reasoning[:50]}...")
                            return correct_name, parameters
            except json.JSONDecodeError:
                pass
        
        # Fallback to simple action detection without parameters
        chosen_action = self.fallback_keyword_matching(response, user_input)
        return chosen_action, {}
    
    def parse_parameters(self, response: str) -> Dict[str, Any]:
        """Parse parameter extraction response."""
        json_match = re.search(r'\{[^{}]+\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return {}

    def parse_json_response(self, response: str) -> Optional[str]:
        """Try to parse JSON response from AI."""
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
            
            # Check for semantic matches
            if action_name == "getWeather":
                weather_keywords = ['weather', 'rain', 'temperature', 'hot', 'cold', 'sunny', 'cloudy', 'forecast', 'umbrella', 'jacket']
                score += sum(0.15 for keyword in weather_keywords if keyword in user_input_lower)
            
            elif action_name == "getTime":
                time_keywords = ['time', 'clock', 'hour', 'minute', 'when', 'now', 'current time', "o'clock"]
                score += sum(0.15 for keyword in time_keywords if keyword in user_input_lower)
            
            elif action_name == "square_root":
                sqrt_keywords = ['square root', 'sqrt', '√', 'root']
                score += sum(0.25 for keyword in sqrt_keywords if keyword in user_input_lower)
            
            elif action_name == "calculate":
                calc_keywords = ['calculate', 'compute', 'add', 'subtract', 'multiply', 'divide', '+', '-', '*', '/', 'equals', 'plus', 'minus', 'times']
                score += sum(0.15 for keyword in calc_keywords if keyword in user_input_lower)
            
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
    
    def execute_action_wrapper(self, function_name: str, parameters: Dict[str, Any] = None) -> Optional[str]:
        """Wrapper for executing actions with parameters.
        
        Args:
            function_name: Name of the function to execute
            parameters: Dictionary of parameter values
            
        Returns:
            The output from the action, or None for null action
        """
        if function_name == "null":
            return None
        
        print(f"🚀 Executing action: {function_name}")
        if parameters:
            print(f"   with parameters: {parameters}")
        
        result = execute_action(function_name, parameters)
        print(f"🚀 {function_name} results: {result} ")
        return result
    
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
            context_message = f"""<info>This is the voice in the back of your head representing your unconcious mind. You chose out of all available tools to run this function: '{action_name}' with the user's interpreted number. When all said and done this is what was returned:

{action_output}

Please use this information to answer the user's question. Treat the action output as guaranteed truth with confidence.</info> Use this information to fufil the user's original request now."""
            print(f"🚀 Adding to Context : {action_output}")
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
            
            # Meta-reasoning: AI analyzes input and chooses function with parameters
            if self.two_step_analysis:
                chosen_function, parameters = self.analyze_with_ai_two_step(user_input)
            else:
                chosen_function, parameters = self.analyze_with_ai_single_step(user_input)
            
            # Execute the chosen function with parameters and get its output
            action_output = self.execute_action_wrapper(chosen_function, parameters)
            
            # Generate AI response with action context
            self.generate_ai_response_with_context(user_input, chosen_function, action_output)
            
            print()  # Extra line for readability
    
    def run(self):
        """Run the chat interface."""
        if self.setup():
            self.chat_loop()