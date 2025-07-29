"""Action functions that the AI can choose to execute."""

from typing import Dict, Callable, List
from datetime import datetime

# Function registry to store available actions
ACTION_REGISTRY: Dict[str, Dict[str, any]] = {}


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
def null():
    """Signal that normal chat response is needed."""
    return "NORMAL_CHAT_RESPONSE"


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
def getWeather():
    """Print weather information."""
    print("☀️ It's sunny with a chance of code!")

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
def getTime():
    """Print time."""
    current_time = datetime.now()
    print(current_time)

def get_available_actions() -> Dict[str, Dict[str, any]]:
    """Get all registered actions.
    
    Returns:
        Dictionary of action names to their function, description, and vibe test phrases
    """
    return ACTION_REGISTRY


def get_actions_with_vibe_tests() -> Dict[str, Dict[str, any]]:
    """Get all actions that have vibe test phrases defined.
    
    Returns:
        Dictionary of action names to their info, filtered to only include actions with vibe test phrases
    """
    return {
        name: action_info 
        for name, action_info in ACTION_REGISTRY.items() 
        if action_info['vibe_test_phrases']
    }