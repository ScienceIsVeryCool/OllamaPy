"""Action functions that the AI can choose to execute."""

from typing import Dict, Callable


# Function registry to store available actions
ACTION_REGISTRY: Dict[str, Dict[str, any]] = {}


def register_action(name: str, description: str):
    """Decorator to register functions as available actions.
    
    Args:
        name: The name of the action (what the AI will say)
        description: Description of when to use this action
    """
    def decorator(func: Callable):
        ACTION_REGISTRY[name] = {
            'function': func,
            'description': description
        }
        return func
    return decorator


@register_action("null", "null. This is your null/default option. Use when the user wants normal conversation, and compared to other actions seems more efficient and/or helpful. This is a safe option if not obvious. This is just normal chat mode. the keyword here is null")
def null():
    """Signal that normal chat response is needed."""
    return "NORMAL_CHAT_RESPONSE"

@register_action("getWeather", "Use when the user asks about weather conditions or climate. Like probably anything close to weather conditions. UV, Humidity, temperature, etc. The keyword is getWeather")
def getWeather():
    """Print weather information."""
    print("☀️ It's sunny with a chance of code!")


def get_available_actions() -> Dict[str, Dict[str, any]]:
    """Get all registered actions.
    
    Returns:
        Dictionary of action names to their function and description
    """
    return ACTION_REGISTRY