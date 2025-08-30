"""AI analysis engine for action selection and parameter extraction."""

import re
from typing import List, Dict, Tuple, Any
from .ollama_client import OllamaClient
from .skills import get_available_actions, SKILL_REGISTRY
from .parameter_utils import extract_parameter_from_response


class AnalysisEngine:
    """Handles AI-based action selection and parameter extraction."""
    
    def __init__(self, analysis_model: str, client: OllamaClient):
        """Initialize the analysis engine.
        
        Args:
            analysis_model: The model to use for analysis
            client: The OllamaClient instance
        """
        self.analysis_model = analysis_model
        self.client = client
        self.actions = get_available_actions()
    
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
    
    def get_cleaned_response(self, prompt: str, system_message: str = "You are a decision assistant. Answer only 'yes' or 'no' to questions.") -> str:
        """Get a cleaned response from the analysis model.
        
        Args:
            prompt: The prompt to send
            system_message: The system message to use
            
        Returns:
            The cleaned response content
        """
        response_content = ""
        try:
            # Stream the response from the analysis model
            for chunk in self.client.chat_stream(
                model=self.analysis_model,
                messages=[{"role": "user", "content": prompt}],
                system=system_message
            ):
                response_content += chunk
            
            # Remove thinking blocks if present
            return self.remove_thinking_blocks(response_content)
            
        except Exception as e:
            print(f"\n❌ Error getting response: {e}")
            return ""
    
    def ask_yes_no_question(self, prompt: str) -> bool:
        """Ask the analysis model a yes/no question and parse the response.
        
        This is the core of our simplified analysis. We ask a clear yes/no question
        and parse the response to determine if the answer is yes.
        
        Args:
            prompt: The yes/no question to ask
            
        Returns:
            True if the model answered yes, False otherwise
        """
        cleaned_response = self.get_cleaned_response(prompt)
        
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
        
        system_message = "You are a parameter extractor. Respond only with the extracted value or NOT_FOUND."
        cleaned_response = self.get_cleaned_response(prompt, system_message).strip()
        
        return extract_parameter_from_response(cleaned_response, param_type)
    
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
    
    def generate_custom_python_script(self, user_input: str) -> str:
        """Generate a custom Python script based on user input.
        
        Args:
            user_input: The user's request
            
        Returns:
            Generated Python script
        """
        prompt = f"""Generate a Python script to help with this request: {user_input}

Requirements:
- Create a standalone Python script that solves the user's request
- Use print() statements for all output
- Include error handling where appropriate
- Do not use any external libraries unless absolutely necessary
- Make the script clear and well-commented

Output ONLY the Python code, no explanations or markdown:"""
        
        system_message = "You are a Python code generator. Output only valid Python code."
        script = self.get_cleaned_response(prompt, system_message)
        
        # Clean up any markdown formatting if present
        if '```python' in script:
            script = script.split('```python')[1].split('```')[0]
        elif '```' in script:
            script = script.split('```')[1].split('```')[0]
        
        return script.strip()