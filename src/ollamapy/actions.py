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


@register_action("yes", "Use when the user expresses positive intent, agreement, or wants to proceed")
def yes():
    """Print yes with emoji."""
    print("✅ YES!")


@register_action("no", "Use when the user expresses negative intent, disagreement, or wants to stop")
def no():
    """Print no with emoji."""
    print("❌ NO!")


@register_action("getWeather", "Use when the user asks about weather conditions or climate")
def getWeather():
    """Print weather information."""
    print("☀️ It's sunny with a chance of code!")


def get_available_actions() -> Dict[str, Dict[str, any]]:
    """Get all registered actions.
    
    Returns:
        Dictionary of action names to their function and description
    """
    return ACTION_REGISTRY