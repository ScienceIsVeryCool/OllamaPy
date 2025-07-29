# My Package

A simple Python package.

## Installation

```bash
pipx install .
```

## Usage

```python
from my_package import hello, greet

print(hello())
print(greet("World"))
```

## CLI

```bash
my-cli
```

## Development

```bash
pip install -e ".[dev]"
pytest