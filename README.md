# OllamaPy

A simple Python package for Ollama utilities.

## Installation

Install from PyPI:

```bash
pip install ollamapy
```

Or install from source:

```bash
git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
cd OllamaPy
pip install .
```

## Usage

```python
from ollamapy import hello, greet

print(hello())        # Output: Hello, World!
print(greet("World")) # Output: Hello, World!
```

## CLI

After installation, you can use the command line interface:

```bash
ollamapy
```

This will run the main function and display:
```
Hello, World!
Hello, Python!
```

## Development

Clone the repository and install in development mode:

```bash
git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
cd OllamaPy
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format code:

```bash
black src/ tests/
isort src/ tests/
```

Type checking:

```bash
mypy src/
```

## Project Information

- **Version**: 0.1.0
- **License**: GPL-3.0-or-later
- **Author**: The Lazy Artist
- **Python**: >=3.8

## Links

- [PyPI Package](https://pypi.org/project/ollamapy/)
- [GitHub Repository](https://github.com/ScienceIsVeryCool/OllamaPy)
- [Issues](https://github.com/ScienceIsVeryCool/OllamaPy/issues)