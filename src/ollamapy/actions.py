"""Action functions that the AI can choose to execute."""

from typing import Dict, Callable, List, Any, Optional, Union
from datetime import datetime
import math

# Function registry to store available actions
ACTION_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_action(
    name: str, 
    description: str, 
    vibe_test_phrases: List[str] = None,
    parameters: Dict[str, Dict[str, Any]] = None
):
    """Decorator to register functions as available actions.
    
    Args:
        name: The name of the action (what the AI will say)
        description: Description of when to use this action
        vibe_test_phrases: List of phrases to test this action with
        parameters: Dictionary defining expected parameters with their types and descriptions
                   Format: {"param_name": {"type": "number|string", "description": "...", "required": bool}}
    """
    def decorator(func: Callable):
        ACTION_REGISTRY[name] = {
            'function': func,
            'description': description,
            'vibe_test_phrases': vibe_test_phrases or [],
            'parameters': parameters or {}
        }
        return func
    return decorator


@register_action(
    name="null", 
    description="null. This is your null/default option. Use when the user wants normal conversation, and compared to other actions seems more efficient and/or helpful. This is a safe option if not obvious. This is just normal chat mode. the keyword here is null",
    vibe_test_phrases=[
        "Just talk to me without using any tools",
        "null option",
        "chat only with no functions please",
        "chat only please",
        "null null null null null"
    ]
)
def null() -> Optional[str]:
    """Signal that normal chat response is needed."""
    return None  # Return None to indicate normal chat


@register_action(
    name="getWeather", 
    description="Use when the user asks about weather conditions or climate. Like probably anything close to weather conditions. UV, Humidity, temperature, etc. The keyword is getWeather",
    vibe_test_phrases=[
        "Is it raining right now?",
        "Do I need a Jacket when I go outside due to weather?",
        "Is it going to be hot today?",
        "Do I need an umbrella due to rain today?",
        "Do I need sunscreen today due to UV?"
    ],
    parameters={
        "location": {
            "type": "string",
            "description": "The location to get weather for (city name or coordinates)",
            "required": False
        }
    }
)
def getWeather(location: str = "current location") -> str:
    """Get weather information.
    
    Args:
        location: The location to get weather for
    """
    # In a real implementation, this would fetch actual weather data
    return f"Current weather in {location}: Sunny, 72°F (22°C), Humidity: 45%, UV Index: 6 (High), Wind: 5 mph NW"


@register_action(
    name="getTime", 
    description="Use when the user asks about the current time. If they ask about what time it is stuff like that.",
    vibe_test_phrases=[
        "what is the current time?",
        "is it noon yet?",
        "what time is it?",
        "Is it 4 o'clock?"
    ],
    parameters={
        "timezone": {
            "type": "string",
            "description": "The timezone to get time for (e.g., 'EST', 'PST', 'UTC')",
            "required": False
        }
    }
)
def getTime(timezone: str = None) -> str:
    """Get current time.
    
    Args:
        timezone: Optional timezone specification
    """
    current_time = datetime.now()
    tz_info = f" ({timezone})" if timezone else ""
    return f"Current time{tz_info}: {current_time.strftime('%I:%M %p on %A, %B %d, %Y')}"


@register_action(
    name="square_root",
    description="Use when the user wants to calculate the square root of a number. Keywords include: square root, sqrt, √",
    vibe_test_phrases=[
        "what's the square root of 16?",
        "calculate sqrt(25)",
        "find the square root of 144",
        "√81 = ?",
        "I need the square root of 2"
    ],
    parameters={
        "number": {
            "type": "number",
            "description": "The number to calculate the square root of",
            "required": True
        }
    }
)
def square_root(number: Union[float, int]) -> str:
    """Calculate the square root of a number.
    
    Args:
        number: The number to calculate the square root of
        
    Returns:
        A string describing the result
    """
    try:
        if number < 0:
            # Handle complex numbers elegantly
            result = math.sqrt(abs(number))
            return f"The square root of {number} is {result:.6f}i (imaginary number)"
        
        result = math.sqrt(number)
        
        # Format nicely - show exact values for perfect squares
        if result.is_integer():
            return f"The square root of {number} is {int(result)}"
        else:
            # Show more precision for irrational numbers
            return f"The square root of {number} is approximately {result:.6f}"
            
    except (ValueError, TypeError) as e:
        return f"Error calculating square root: {str(e)}"


@register_action(
    name="calculate",
    description="Use when the user wants to perform basic arithmetic calculations. Keywords: calculate, compute, add, subtract, multiply, divide, +, -, *, /",
    vibe_test_phrases=[
        "calculate 5 + 3",
        "what's 10 * 7?",
        "compute 100 / 4",
        "15 - 8 equals what?",
        "multiply 12 by 9"
    ],
    parameters={
        "expression": {
            "type": "string",
            "description": "The mathematical expression to evaluate (e.g., '5 + 3', '10 * 2')",
            "required": True
        }
    }
)
def calculate(expression: str) -> str:
    """Evaluate a basic mathematical expression.
    
    Args:
        expression: The mathematical expression to evaluate
        
    Returns:
        A string with the result
    """
    try:
        # Clean up the expression
        expression = expression.strip()
        
        # Basic safety check - only allow numbers and basic operators
        allowed_chars = "0123456789+-*/.()"
        if not all(c in allowed_chars or c.isspace() for c in expression):
            return f"Error: Expression contains invalid characters. Only numbers and +, -, *, /, (), . are allowed."
        
        # Evaluate the expression
        result = eval(expression)
        
        # Format the result nicely
        if isinstance(result, float) and result.is_integer():
            result = int(result)
            
        return f"{expression} = {result}"
        
    except ZeroDivisionError:
        return "Error: Division by zero! That's undefined in mathematics."
    except Exception as e:
        return f"Error evaluating expression '{expression}': {str(e)}"


def get_available_actions() -> Dict[str, Dict[str, Any]]:
    """Get all registered actions.
    
    Returns:
        Dictionary of action names to their function, description, parameters, and vibe test phrases
    """
    return ACTION_REGISTRY


def get_actions_with_vibe_tests() -> Dict[str, Dict[str, Any]]:
    """Get all actions that have vibe test phrases defined.
    
    Returns:
        Dictionary of action names to their info, filtered to only include actions with vibe test phrases
    """
    return {
        name: action_info 
        for name, action_info in ACTION_REGISTRY.items() 
        if action_info['vibe_test_phrases']
    }


def execute_action(action_name: str, parameters: Dict[str, Any] = None) -> Optional[str]:
    """Execute an action with the given parameters.
    
    Args:
        action_name: Name of the action to execute
        parameters: Dictionary of parameter values
        
    Returns:
        The result of the action execution, or None if action not found
    """
    if action_name not in ACTION_REGISTRY:
        return f"Error: Unknown action '{action_name}'"
    
    action_info = ACTION_REGISTRY[action_name]
    func = action_info['function']
    expected_params = action_info.get('parameters', {})
    
    # If no parameters expected, just call the function
    if not expected_params:
        return func()
    
    # Prepare parameters for function call
    if parameters is None:
        parameters = {}
    
    # Validate and convert parameters
    call_params = {}
    for param_name, param_spec in expected_params.items():
        if param_name in parameters:
            value = parameters[param_name]
            
            # Type conversion
            if param_spec['type'] == 'number' and value is not None:
                try:
                    # Try to convert to number
                    if isinstance(value, str):
                        # Remove any whitespace
                        value = value.strip()
                        # Handle both int and float
                        value = float(value)
                        # Convert to int if it's a whole number
                        if value.is_integer():
                            value = int(value)
                except (ValueError, AttributeError):
                    return f"Error: Parameter '{param_name}' must be a number, got '{value}'"
            
            call_params[param_name] = value
        elif param_spec.get('required', False):
            return f"Error: Required parameter '{param_name}' not provided for action '{action_name}'"
    
    # Call the function with parameters
    try:
        return func(**call_params)
    except Exception as e:
        return f"Error executing action '{action_name}': {str(e)}"