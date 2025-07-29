"""Main module with Ollama chat functionality."""

import argparse
from .terminal_chat import TerminalChat


def hello():
    """Return a hello message."""
    return "Hello, World!"


def greet(name):
    """Greet someone by name."""
    return f"Hello, {name}!"


def chat(model: str = "gemma3:4b", system: str = "You are a helpful assistant."):
    """Start a chat session with Ollama.
    
    Args:
        model: The model to use for chat (default: gemma3:4b)
        system: Optional system message to set context
    """
    chat_interface = TerminalChat(model=model, system_message=system)
    chat_interface.run()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OllamaPy - Terminal chat interface for Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ollamapy                          # Start chat with default model (gemma2:2b)
  ollamapy --model llama3.2:3b      # Use a specific model
  ollamapy --system "You are a helpful coding assistant"  # Set system message
        """
    )
    
    parser.add_argument(
        "--model", "-m",
        default="gemma3:4b",
        help="Model to use for chat (default: gemma3:4b)"
    )
    
    parser.add_argument(
        "--system", "-s",
        help="System message to set context for the AI"
    )
    
    parser.add_argument(
        "--hello",
        action="store_true",
        help="Just print hello and exit (for testing)"
    )
    
    args = parser.parse_args()
    
    if args.hello:
        print(hello())
        print(greet("Python"))
    else:
        chat(model=args.model, system=args.system)


if __name__ == "__main__":
    main()