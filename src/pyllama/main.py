"""Main module with hello world functionality."""


def hello():
    """Return a hello message."""
    return "Hello, World!"


def greet(name):
    """Greet someone by name."""
    return f"Hello, {name}!"


def main():
    """CLI entry point."""
    print(hello())
    print(greet("Python"))


if __name__ == "__main__":
    main()