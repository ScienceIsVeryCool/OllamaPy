"""Main module with Ollama chat functionality."""

import argparse
import subprocess
import sys
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


def run_vibe_tests(model: str = "gemma3:4b", iterations: int = 1):
    """Run vibe tests using pytest.
    
    Args:
        model: The model to use for testing (default: gemma3:4b)
        iterations: Number of iterations per test (default: 1)
    """
    print(f"🧪 Running vibe tests with model: {model}, iterations: {iterations}")
    print("=" * 60)
    
    # Build pytest command
    pytest_args = [
        "pytest", 
        "-v", 
        "-s",  # Don't capture output so we can see real-time results
        "--tb=short",  # Shorter traceback format
        f"--model={model}",
        f"--iterations={iterations}",
        "-k", "vibe"  # Only run tests with 'vibe' in the name
    ]
    
    try:
        # Run pytest as subprocess
        result = subprocess.run(pytest_args, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Error: pytest not found. Please install pytest:")
        print("   pip install pytest")
        return False
    except Exception as e:
        print(f"❌ Error running vibe tests: {e}")
        return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OllamaPy - Terminal chat interface for Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ollamapy                          # Start chat with default model (gemma3:4b)
  ollamapy --model llama3.2:3b      # Use a specific model
  ollamapy --system "You are a helpful coding assistant"  # Set system message
  ollamapy --vibetest               # Run vibe tests with default settings
  ollamapy --vibetest -N 5          # Run vibe tests with 5 iterations each
  ollamapy --vibetest --model llama3.2:3b -N 3  # Custom model and iterations
        """
    )
    
    parser.add_argument(
        "--model", "-m",
        default="gemma3:4b",
        help="Model to use for chat or testing (default: gemma3:4b)"
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
    
    parser.add_argument(
        "--vibetest",
        action="store_true",
        help="Run vibe tests to evaluate AI decision-making consistency"
    )
    
    parser.add_argument(
        "-N", "--iterations",
        type=int,
        default=1,
        help="Number of iterations for vibe tests (default: 1)"
    )
    
    args = parser.parse_args()
    
    if args.hello:
        print(hello())
        print(greet("Python"))
    elif args.vibetest:
        success = run_vibe_tests(model=args.model, iterations=args.iterations)
        sys.exit(0 if success else 1)
    else:
        chat(model=args.model, system=args.system)


if __name__ == "__main__":
    main()