__version__ = "0.6.2"

from .main import hello, greet, chat
from .ollama_client import OllamaClient
from .terminal_chat import TerminalChat
from .actions import get_available_actions, get_actions_with_vibe_tests, execute_action
from .vibe_tests import VibeTestRunner, run_vibe_tests

__all__ = [
    "hello", 
    "greet", 
    "chat", 
    "OllamaClient", 
    "TerminalChat", 
    "get_available_actions",
    "get_actions_with_vibe_tests",
    "execute_action",
    "VibeTestRunner", 
    "run_vibe_tests"
]