# OllamaPy - AI Chat Interface with Interactive Skill Editor

Welcome to OllamaPy, a powerful terminal-based chat interface for Ollama with AI meta-reasoning capabilities, dynamic skill generation, and interactive skill editing.

## Features

- **Interactive Chat Interface**: Terminal-based chat with Ollama models
- **Dynamic Skill System**: AI-powered skill generation and management
- **Interactive Skill Editor**: Web-based interface for creating and editing skills
- **Vibe Testing**: Automatic skill matching based on conversation context
- **Meta-reasoning**: AI can reason about its own skills and capabilities

## Quick Start

### Installation

```bash
# Basic installation
pip install ollamapy

# With skill editor support
pip install ollamapy[editor]

# Development installation
pip install ollamapy[dev]
```

### Basic Usage

```bash
# Start chat interface
ollamapy

# Launch skill editor
ollamapy --skill-editor

# Get help
ollamapy --help
```

## Docker

```bash
# Run with Docker
docker run -p 8765:8765 scienceisverycoool/ollamapy

# Access skill editor at http://localhost:8765
```

## Navigation

- [Getting Started](getting-started.md) - Detailed installation and setup guide
- [Skills System](skills/index.md) - Learn about the skill system
- [Skill Editor](skill-editor/index.md) - Interactive skill creation and editing
- [Development](development/contributing.md) - Contributing to the project

## Links

- [GitHub Repository](https://github.com/ScienceIsVeryCool/OllamaPy)
- [PyPI Package](https://pypi.org/project/ollamapy/)
- [Docker Hub](https://hub.docker.com/r/scienceisverycoool/ollamapy)