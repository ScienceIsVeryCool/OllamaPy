"""Action functions that the AI can choose to execute."""

from typing import Dict, Callable, List, Any, Optional
from datetime import datetime

# Function registry to store available actions
ACTION_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_action(name: str, description: str, vibe_test_phrases: List[str] = None):
    """Decorator to register functions as available actions.
    
    Args:
        name: The name of the action (what the AI will say)
        description: Description of when to use this action
        vibe_test_phrases: List of phrases to test this action with
    """
    def decorator(func: Callable):
        ACTION_REGISTRY[name] = {
            'function': func,
            'description': description,
            'vibe_test_phrases': vibe_test_phrases or []
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
    ]
)
def getWeather() -> str:
    """Get weather information."""
    # In a real implementation, this would fetch actual weather data
    return "Current weather: Sunny, 72°F (22°C), Humidity: 45%, UV Index: 6 (High), Wind: 5 mph NW"


@register_action(
    name="getTime", 
    description="Use when the user asks about the current time. If they ask about what time it is stuff like that.",
    vibe_test_phrases=[
        "what is the current time?",
        "is it noon yet?",
        "what time is it?",
        "Is it 4 o'clock?"
    ]
)
def getTime() -> str:
    """Get current time."""
    current_time = datetime.now()
    return f"Current time: {current_time.strftime('%I:%M %p on %A, %B %d, %Y')}"


def get_available_actions() -> Dict[str, Dict[str, Any]]:
    """Get all registered actions.
    
    Returns:
        Dictionary of action names to their function, description, and vibe test phrases
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