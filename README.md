# OllamaPy

A clean terminal-based chat interface for Ollama, providing an easy way to interact with local AI models through a simple Python wrapper.

## Features

- 🤖 **Terminal Chat Interface** - Clean, user-friendly chat experience in your terminal
- 🔄 **Streaming Responses** - Real-time streaming for natural conversation flow
- 📚 **Model Management** - Automatic model pulling and listing of available models
- 💾 **Conversation History** - Maintains context throughout your chat session
- ⚙️ **Customizable** - Support for different models and system messages
- 🛠️ **Built-in Commands** - Easy-to-use commands for managing your chat session

## Prerequisites

You need to have [Ollama](https://ollama.ai/) installed and running on your system.

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Start the Ollama server
ollama serve
```

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

## Quick Start

Simply run the chat interface:

```bash
ollamapy
```

This will start a chat session with the default model (gemma2:2b). If the model isn't available locally, OllamaPy will automatically pull it for you.

## Usage Examples

### Basic Chat
```bash
# Start chat with default model
ollamapy
```

### Custom Model
```bash
# Use a specific model
ollamapy --model llama3.2:3b
ollamapy -m codellama:7b
```

### System Message
```bash
# Set context for the AI
ollamapy --system "You are a helpful coding assistant specializing in Python"
ollamapy -s "You are a creative writing partner"
```

### Combined Options
```bash
# Use custom model with system message
ollamapy --model llama3.2:3b --system "You are a helpful coding assistant"
```

## Chat Commands

While chatting, you can use these built-in commands:

- `quit`, `exit`, `bye` - End the conversation
- `clear` - Clear conversation history and start fresh
- `help` - Show available commands
- `model` - Display current model being used
- `models` - List all available models

## Python API

You can also use OllamaPy programmatically:

```python
from ollamapy import TerminalChat, OllamaClient

# Start a chat session programmatically
chat = TerminalChat(model="gemma2:2b", system_message="You are a helpful assistant")
chat.run()

# Or use the client directly
client = OllamaClient()
messages = [{"role": "user", "content": "Hello!"}]

for chunk in client.chat_stream("gemma2:2b", messages):
    print(chunk, end="", flush=True)
```

### Available Classes

- **`TerminalChat`** - High-level terminal chat interface
- **`OllamaClient`** - Low-level API client for Ollama
- **`hello()`**, **`greet(name)`** - Simple utility functions

## Configuration

OllamaPy connects to Ollama on `http://localhost:11434` by default. If your Ollama instance is running elsewhere, you can create a custom client:

```python
from ollamapy import OllamaClient

client = OllamaClient(base_url="http://your-ollama-server:11434")
```

## Supported Models

OllamaPy works with any model available in Ollama. Popular options include:

- `gemma3:4b` (default) - Fast and efficient
- `llama3.2:3b` - Good balance of speed and capability
- `codellama:7b` - Specialized for coding tasks
- `mistral:7b` - General purpose conversations

To see available models: `ollama list` or use the `models` command in chat.

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

## Troubleshooting

### "Ollama server is not running!"
Make sure Ollama is installed and running:
```bash
ollama serve
```

### Model not found
OllamaPy will automatically pull models, but you can also pull them manually:
```bash
ollama pull gemma3:4b
```

### Connection issues
Verify Ollama is accessible:
```bash
curl http://localhost:11434/api/tags
```

## Project Information

- **Version**: 0.1.0
- **License**: GPL-3.0-or-later
- **Author**: The Lazy Artist
- **Python**: >=3.8
- **Dependencies**: requests>=2.25.0

## Links

- [PyPI Package](https://pypi.org/project/ollamapy/)
- [GitHub Repository](https://github.com/ScienceIsVeryCool/OllamaPy)
- [Issues](https://github.com/ScienceIsVeryCool/OllamaPy/issues)
- [Ollama Documentation](https://ollama.ai/)

## License

This project is licensed under the GPL-3.0-or-later license. See the LICENSE file for details.