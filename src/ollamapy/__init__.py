__version__ = "0.1.0"

from .main import hello, greet, chat
from .ollama_client import OllamaClient
from .terminal_chat import TerminalChat

__all__ = ["hello", "greet", "chat", "OllamaClient", "TerminalChat"]