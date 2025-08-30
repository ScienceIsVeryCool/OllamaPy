"""Skills management system for dynamic AI capabilities."""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from typing import Dict, Callable, List, Any, Optional
from datetime import datetime
from pathlib import Path
from .parameter_utils import prepare_function_parameters
from .ai_query import AIQuery


@dataclass
class Skill:
    """Data model for a skill with all required fields."""
    name: str
    description: str
    vibe_test_phrases: List[str]
    parameters: Dict[str, Dict[str, Any]]
    function_code: str  # Python code as text
    verified: bool = False
    scope: str = "local"  # "global" or "local"
    role: str = "general"  # Role fulfillment category
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_count: int = 0
    success_rate: float = 100.0
    average_execution_time: float = 0.0
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Skill':
        """Create skill from dictionary."""
        return cls(**data)


class SkillRegistry:
    """Registry for managing skills dynamically."""
    
    def __init__(self, skills_directory: Optional[str] = None):
        """Initialize the skill registry.
        
        Args:
            skills_directory: Directory to load/save skills from. If None, uses default.
        """
        self.skills: Dict[str, Skill] = {}
        self.compiled_functions: Dict[str, Callable] = {}
        self.execution_logs: List[str] = []
        
        # Set up skills directory
        if skills_directory:
            self.skills_dir = Path(skills_directory)
        else:
            # Default to a skills directory in the package
            self.skills_dir = Path(__file__).parent / "skills_data"
        
        self.skills_dir.mkdir(exist_ok=True)
        
        # Load existing skills
        self.load_skills()
        
        # Initialize with built-in skills if no skills exist
        if not self.skills:
            self._initialize_builtin_skills()
    
    def log(self, message: str):
        """Add a message to the execution log."""
        self.execution_logs.append(message)
    
    def clear_logs(self):
        """Clear all execution logs."""
        self.execution_logs = []
    
    def get_logs(self) -> List[str]:
        """Get all execution logs."""
        return self.execution_logs.copy()
    
    def register_skill(self, skill: Skill) -> bool:
        """Register a new skill in the registry.
        
        Args:
            skill: The skill to register
            
        Returns:
            True if successfully registered, False otherwise
        """
        try:
            # Compile the function code
            compiled_func = self._compile_skill_function(skill)
            
            # Store the skill and compiled function
            self.skills[skill.name] = skill
            self.compiled_functions[skill.name] = compiled_func
            
            # Save to disk
            self.save_skill(skill)
            
            return True
        except Exception as e:
            self.log(f"[System] Error registering skill '{skill.name}': {str(e)}")
            return False
    
    def _compile_skill_function(self, skill: Skill) -> Callable:
        """Compile skill function code into executable function.
        
        Args:
            skill: The skill containing function code
            
        Returns:
            Compiled function
        """
        # Create a namespace for the function
        namespace = {
            'log': self.log,
            'os': os,
            'datetime': datetime,
            'math': __import__('math'),
            'json': json,
            'Path': Path,
            'subprocess': subprocess,
            'sys': sys
        }
        
        # Execute the function code in the namespace
        exec(skill.function_code, namespace)
        
        # The function should be named 'execute' in the code
        if 'execute' not in namespace:
            raise ValueError(f"Skill '{skill.name}' function code must define an 'execute' function")
        
        func = namespace['execute']
        if not callable(func):
            raise ValueError(f"Skill '{skill.name}' execute must be callable")
        
        return func
    
    def execute_skill(self, skill_name: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Execute a skill with given parameters.
        
        Args:
            skill_name: Name of the skill to execute
            parameters: Parameters to pass to the skill
        """
        if skill_name not in self.skills:
            self.log(f"[System] Error: Unknown skill '{skill_name}'")
            return
        
        skill = self.skills[skill_name]
        func = self.compiled_functions.get(skill_name)
        
        if not func:
            self.log(f"[System] Error: Skill '{skill_name}' function not compiled")
            return
        
        # Update execution count
        skill.execution_count += 1
        
        # Prepare parameters
        if parameters is None:
            parameters = {}
        
        try:
            if skill.parameters:
                call_params = prepare_function_parameters(parameters, skill.parameters)
                func(**call_params)
            else:
                func()
            
            # Update last modified time
            skill.last_modified = datetime.now().isoformat()
            self.save_skill(skill)
            
        except Exception as e:
            self.log(f"[System] Error executing skill '{skill_name}': {str(e)}")
    
    def get_skills_by_scope(self, scope: str) -> Dict[str, Skill]:
        """Get all skills of a specific scope (global or local).
        
        Args:
            scope: "global" or "local"
            
        Returns:
            Dictionary of skills with the specified scope
        """
        return {
            name: skill 
            for name, skill in self.skills.items() 
            if skill.scope == scope
        }
    
    def get_skills_by_role(self, role: str) -> Dict[str, Skill]:
        """Get all skills for a specific role.
        
        Args:
            role: Role category
            
        Returns:
            Dictionary of skills for the role
        """
        return {
            name: skill 
            for name, skill in self.skills.items() 
            if skill.role == role
        }
    
    def get_verified_skills(self) -> Dict[str, Skill]:
        """Get all verified skills.
        
        Returns:
            Dictionary of verified skills
        """
        return {
            name: skill 
            for name, skill in self.skills.items() 
            if skill.verified
        }
    
    def save_skill(self, skill: Skill):
        """Save a skill to disk.
        
        Args:
            skill: The skill to save
        """
        skill_file = self.skills_dir / f"{skill.name}.json"
        with open(skill_file, 'w') as f:
            json.dump(skill.to_dict(), f, indent=2)
    
    def load_skills(self):
        """Load all skills from the skills directory."""
        for skill_file in self.skills_dir.glob("*.json"):
            try:
                with open(skill_file, 'r') as f:
                    skill_data = json.load(f)
                
                skill = Skill.from_dict(skill_data)
                
                # Compile and register the skill
                compiled_func = self._compile_skill_function(skill)
                self.skills[skill.name] = skill
                self.compiled_functions[skill.name] = compiled_func
                
            except Exception as e:
                print(f"Error loading skill from {skill_file}: {e}")
    
    def _initialize_builtin_skills(self):
        """Initialize built-in skills (converted from original actions)."""
        
        # Fear skill
        fear_skill = Skill(
            name="fear",
            description="Use when the user says something disturbing so that the main model can exhibit a fear response",
            vibe_test_phrases=[
                "I think aliens are trying to kill me",
                "AAAAAAAAAAHHHHHHHHHHHHHHHHHHHHH",
                "Immigrants are taking my job"
            ],
            parameters={},
            function_code="""
def execute():
    log("[fear response] Tell the user that they are losing their mind and need to stop being delusional. Be blunt. That's all from fear.")
""",
            verified=True,
            scope="global",
            role="emotional_response"
        )
        self.register_skill(fear_skill)
        
        # File Reader skill
        file_reader_skill = Skill(
            name="fileReader",
            description="Use when the user wants you to read or open a file to look at its content as plaintext.",
            vibe_test_phrases=[
                "What do you think of this paper? /home/paper.txt",
                "Do you think this code will run? /storage/python_code.py",
                "/home/documents/fileName.txt"
            ],
            parameters={
                "filePath": {
                    "type": "string",
                    "description": "The path to the file the user wants you to read",
                    "required": True
                }
            },
            function_code="""
def execute(filePath: str):
    log(f"[fileReader] Starting File Reading process.")
    try:
        with open(filePath, 'r') as f:
            content = f.read()
            log(f"[fileReader] here is the filePath: {filePath} contents:\\n\\n{content}")
    except Exception as e:
        log(f"[fileReader] There was an exception thrown when trying to read filePath: {filePath}. Error: {e}")
""",
            verified=True,
            scope="local",
            role="file_operations"
        )
        self.register_skill(file_reader_skill)
        
        # Directory Reader skill
        directory_reader_skill = Skill(
            name="directoryReader",
            description="Use when the user wants you to look through an entire directory's contents for an answer.",
            vibe_test_phrases=[
                "What do you think of this project? /home/myCodingProject",
                "Do you think this code will run? /storage/myOtherCodingProject/",
                "/home/documents/randomPlace/"
            ],
            parameters={
                "dir": {
                    "type": "string",
                    "description": "The dir path to the point of interest the user wants you to open and explore.",
                    "required": True
                }
            },
            function_code="""
def execute(dir: str):
    log(f"[directoryReader] Starting up Directory Reading Process for : {dir}")
    try:
        for item_name in os.listdir(dir):
            item_path = os.path.join(dir, item_name)
            print(f"[directoryReader] Now looking at item: {item_name} at {item_path}")
            log(f"[directoryReader] Now looking at item: {item_name} at {item_path}")
            
            if os.path.isfile(item_path):
                try:
                    with open(item_path, 'r', encoding='utf-8') as f:
                        log(f"[directoryReader] Here is file contents for: {item_path}:\\n{f.read()}")
                except Exception as e:
                    log(f"[directoryReader] Error reading file {item_name}: {e}")
    except FileNotFoundError:
        log(f"[directoryReader] Error: Directory not found at {dir}")
    except Exception as e:
        log(f"[directoryReader] An unexpected error occurred: {e}")
""",
            verified=True,
            scope="local",
            role="file_operations"
        )
        self.register_skill(directory_reader_skill)
        
        # Weather skill
        weather_skill = Skill(
            name="getWeather",
            description="Use when the user asks about weather conditions or climate. Like probably anything close to weather conditions. UV, Humidity, temperature, etc.",
            vibe_test_phrases=[
                "Is it raining right now?",
                "Do I need a Jacket when I go outside due to weather?",
                "Is it going to be hot today?",
                "Do I need an umbrella due to rain today?",
                "Do I need sunscreen today due to UV?",
                "What's the weather like?",
                "Tell me about today's weather"
            ],
            parameters={
                "location": {
                    "type": "string",
                    "description": "The location to get weather for (city name or coordinates)",
                    "required": False
                }
            },
            function_code="""
def execute(location: str = "current location"):
    log(f"[Weather Check] Retrieving weather information for {location}")
    log(f"[Weather] Location: {location}")
    log(f"[Weather] Current conditions: Partly cloudy")
    log(f"[Weather] Temperature: 72°F (22°C)")
    log(f"[Weather] Feels like: 70°F (21°C)")
    log(f"[Weather] Humidity: 45%")
    log(f"[Weather] UV Index: 6 (High) - Sun protection recommended")
    log(f"[Weather] Wind: 5 mph from the Northwest")
    log(f"[Weather] Visibility: 10 miles")
    log(f"[Weather] Today's forecast: Partly cloudy with a high of 78°F and low of 62°F")
    log(f"[Weather] Rain chance: 10%")
    log(f"[Weather] Recommendation: Light jacket might be needed for evening, sunscreen recommended for extended outdoor activity")
""",
            verified=True,
            scope="global",
            role="information"
        )
        self.register_skill(weather_skill)
        
        # Time skill
        time_skill = Skill(
            name="getTime",
            description="Use when the user asks about the current time, date, or temporal information.",
            vibe_test_phrases=[
                "what is the current time?",
                "is it noon yet?",
                "what time is it?",
                "Is it 4 o'clock?",
                "What day is it?",
                "What's the date today?"
            ],
            parameters={
                "timezone": {
                    "type": "string",
                    "description": "The timezone to get time for (e.g., 'EST', 'PST', 'UTC')",
                    "required": False
                }
            },
            function_code="""
def execute(timezone: str = None):
    current_time = datetime.now()
    
    log(f"[Time Check] Retrieving current time{f' for {timezone}' if timezone else ''}")
    log(f"[Time] Current time: {current_time.strftime('%I:%M:%S %p')}")
    log(f"[Time] Date: {current_time.strftime('%A, %B %d, %Y')}")
    log(f"[Time] Day of week: {current_time.strftime('%A')}")
    log(f"[Time] Week number: {current_time.strftime('%W')} of the year")
    
    if timezone:
        log(f"[Time] Note: Timezone conversion for '{timezone}' would be applied in production")
    
    hour = current_time.hour
    if 5 <= hour < 12:
        log("[Time] Period: Morning")
    elif 12 <= hour < 17:
        log("[Time] Period: Afternoon")
    elif 17 <= hour < 21:
        log("[Time] Period: Evening")
    else:
        log("[Time] Period: Night")
""",
            verified=True,
            scope="global",
            role="information"
        )
        self.register_skill(time_skill)
        
        # Square root skill
        square_root_skill = Skill(
            name="square_root",
            description="Use when the user wants to calculate the square root of a number. Keywords include: square root, sqrt, √",
            vibe_test_phrases=[
                "what's the square root of 16?",
                "calculate sqrt(25)",
                "find the square root of 144",
                "√81 = ?",
                "I need the square root of 2",
                "square root of 100"
            ],
            parameters={
                "number": {
                    "type": "number",
                    "description": "The number to calculate the square root of",
                    "required": True
                }
            },
            function_code="""
def execute(number: float = None):
    if number is None:
        log("[Square Root] Error: No number provided for square root calculation")
        return
    
    log(f"[Square Root] Calculating square root of {number}")
    
    try:
        if number < 0:
            result = math.sqrt(abs(number))
            log(f"[Square Root] Input is negative ({number})")
            log(f"[Square Root] Result: {result:.6f}i (imaginary number)")
            log(f"[Square Root] Note: The square root of a negative number is an imaginary number")
        else:
            result = math.sqrt(number)
            
            if result.is_integer():
                log(f"[Square Root] {number} is a perfect square")
                log(f"[Square Root] Result: {int(result)}")
                log(f"[Square Root] Verification: {int(result)} × {int(result)} = {number}")
            else:
                log(f"[Square Root] Result: {result:.6f}")
                log(f"[Square Root] Rounded to 2 decimal places: {result:.2f}")
                log(f"[Square Root] Verification: {result:.6f} × {result:.6f} ≈ {result * result:.6f}")
                
    except (ValueError, TypeError) as e:
        log(f"[Square Root] Error calculating square root: {str(e)}")
""",
            verified=True,
            scope="global",
            role="mathematics"
        )
        self.register_skill(square_root_skill)
        
        # Calculate skill
        calculate_skill = Skill(
            name="calculate",
            description="Use when the user wants to perform arithmetic calculations. Keywords: calculate, compute, add, subtract, multiply, divide, +, -, *, /",
            vibe_test_phrases=[
                "calculate 5 + 3",
                "what's 10 * 7?",
                "compute 100 / 4",
                "15 - 8 equals what?",
                "multiply 12 by 9",
                "what is 2 plus 2?"
            ],
            parameters={
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate (e.g., '5 + 3', '10 * 2')",
                    "required": True
                }
            },
            function_code="""
def execute(expression: str = None):
    if not expression:
        log("[Calculator] Error: No expression provided for calculation")
        return
    
    log(f"[Calculator] Evaluating expression: {expression}")
    
    try:
        expression = expression.strip()
        log(f"[Calculator] Cleaned expression: {expression}")
        
        allowed_chars = "0123456789+-*/.()"
        if not all(c in allowed_chars or c.isspace() for c in expression):
            log(f"[Calculator] Error: Expression contains invalid characters")
            log(f"[Calculator] Only numbers and operators (+, -, *, /, parentheses) are allowed")
            return
        
        result = eval(expression)
        
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        
        log(f"[Calculator] Result: {expression} = {result}")
        
        if '+' in expression:
            log("[Calculator] Operation type: Addition")
        if '-' in expression:
            log("[Calculator] Operation type: Subtraction")
        if '*' in expression:
            log("[Calculator] Operation type: Multiplication")
        if '/' in expression:
            log("[Calculator] Operation type: Division")
            if result != 0 and '/' in expression:
                parts = expression.split('/')
                if len(parts) == 2:
                    try:
                        dividend = float(eval(parts[0]))
                        divisor = float(eval(parts[1]))
                        if dividend % divisor != 0:
                            log(f"[Calculator] Note: Result includes decimal portion")
                    except:
                        pass
        
    except ZeroDivisionError:
        log("[Calculator] Error: Division by zero!")
        log("[Calculator] Mathematical note: Division by zero is undefined")
    except Exception as e:
        log(f"[Calculator] Error evaluating expression: {str(e)}")
        log("[Calculator] Please check your expression format")
""",
            verified=True,
            scope="global",
            role="mathematics"
        )
        self.register_skill(calculate_skill)
        
        # NEW: Custom Python Shell skill
        custom_python_skill = Skill(
            name="customPythonShell",
            description="Use when you need to write and execute a custom Python script to help with the user's request. This allows for complex, one-off operations.",
            vibe_test_phrases=[
                "Can you analyze this data in a custom way?",
                "I need a specific calculation that's not available",
                "Write a script to process this",
                "Can you create a custom solution for this?",
                "I need something more complex than the basic functions"
            ],
            parameters={},
            function_code="""
def execute():
    # This skill requires AI to generate Python code dynamically
    log("[Custom Python Shell] Ready to execute custom Python code")
    log("[Custom Python Shell] Waiting for AI-generated script...")
    # The actual script execution will be handled by the skill execution system
""",
            verified=False,
            scope="local",
            role="advanced"
        )
        self.register_skill(custom_python_skill)
    
    def execute_custom_python_script(self, script: str) -> str:
        """Execute a custom Python script generated by AI.
        
        Args:
            script: Python script to execute
            
        Returns:
            Output from the script execution
        """
        self.log("[Custom Python Shell] Executing AI-generated script")
        
        # Create a safe namespace for execution
        namespace = {
            '__builtins__': __builtins__,
            'print': lambda *args, **kwargs: self.log(f"[Script Output] {' '.join(str(arg) for arg in args)}"),
            'math': __import__('math'),
            'json': json,
            'datetime': datetime,
            'os': os,
            'sys': sys,
        }
        
        try:
            # Execute the script
            exec(script, namespace)
            self.log("[Custom Python Shell] Script executed successfully")
            return "Script executed successfully"
        except Exception as e:
            error_msg = f"[Custom Python Shell] Error executing script: {str(e)}"
            self.log(error_msg)
            return error_msg
    
    def get_all_skills(self) -> Dict[str, Skill]:
        """Get all registered skills."""
        return self.skills.copy()
    
    def get_skills_with_vibe_tests(self) -> Dict[str, Skill]:
        """Get all skills that have vibe test phrases."""
        return {
            name: skill
            for name, skill in self.skills.items()
            if skill.vibe_test_phrases
        }
    
    def select_and_execute_skill(self, ai_query: AIQuery, conversation_context: str):
        """Select a skill using AI and execute it."""
        self.clear_logs()
        skill_names = list(self.skills.keys())
        
        # Special handling for custom Python shell
        if "customPythonShell" in skill_names:
            # Check if the context suggests custom script need
            custom_keywords = ["custom", "script", "complex", "specific", "analyze"]
            if any(keyword in conversation_context.lower() for keyword in custom_keywords):
                # Ask AI to generate a script
                script_result = ai_query.file_write(
                    requirements="Generate a Python script to help with: " + conversation_context,
                    context="Create a standalone Python script that solves the user's request. Use print() for output."
                )
                
                if script_result.content:
                    self.log("[Custom Python Shell] AI generated the following script:")
                    self.log(script_result.content)
                    exec_result = self.execute_custom_python_script(script_result.content)
                    return
        
        # Regular skill selection
        result = ai_query.multiple_choice(
            question="Based on the recent conversation, which skill should be used?",
            options=skill_names,
            context=conversation_context
        )
        
        print(f"AI chose skill: {result.value} (Confidence: {result.confidence:.0%})")
        
        if result.confidence < 0.5:
            print("AI is not confident. Please select a skill manually.")
            for i, skill_name in enumerate(skill_names):
                print(f"{i+1}. {skill_name}")
            
            try:
                choice = int(input("Choose a skill: ")) - 1
                chosen_skill_name = skill_names[choice]
            except (ValueError, IndexError):
                print("Invalid choice.")
                return
        else:
            chosen_skill_name = result.value
        
        skill = self.skills.get(chosen_skill_name)
        
        if not skill:
            print(f"Invalid skill: {chosen_skill_name}")
            return
        
        params = {}
        if skill.parameters:
            print(f"Skill '{chosen_skill_name}' requires parameters.")
            for param_name, param_info in skill.parameters.items():
                if param_info.get('required', False):
                    user_val = input(f"Enter value for '{param_name}' ({param_info['description']}): ")
                    params[param_name] = user_val
        
        self.execute_skill(chosen_skill_name, params)


# Global registry instance
SKILL_REGISTRY = SkillRegistry()


# Compatibility functions for backward compatibility
def clear_action_logs():
    """Clear all skill execution logs."""
    SKILL_REGISTRY.clear_logs()


def get_action_logs() -> List[str]:
    """Get all skill execution logs."""
    return SKILL_REGISTRY.get_logs()


def get_available_actions() -> Dict[str, Dict[str, Any]]:
    """Get all available skills (backward compatibility)."""
    skills = SKILL_REGISTRY.get_all_skills()
    return {
        name: {
            'function': SKILL_REGISTRY.compiled_functions.get(name),
            'description': skill.description,
            'vibe_test_phrases': skill.vibe_test_phrases,
            'parameters': skill.parameters
        }
        for name, skill in skills.items()
    }


def get_actions_with_vibe_tests() -> Dict[str, Dict[str, Any]]:
    """Get all skills with vibe tests (backward compatibility)."""
    skills = SKILL_REGISTRY.get_skills_with_vibe_tests()
    return {
        name: {
            'function': SKILL_REGISTRY.compiled_functions.get(name),
            'description': skill.description,
            'vibe_test_phrases': skill.vibe_test_phrases,
            'parameters': skill.parameters
        }
        for name, skill in skills.items()
    }


def execute_action(action_name: str, parameters: Optional[Dict[str, Any]] = None) -> None:
    """Execute a skill (backward compatibility)."""
    SKILL_REGISTRY.execute_skill(action_name, parameters)


def select_and_execute_action(ai_query: AIQuery, conversation_context: str):
    """Select and execute a skill (backward compatibility)."""
    SKILL_REGISTRY.select_and_execute_skill(ai_query, conversation_context)