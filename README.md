# OllamaPy

A powerful terminal-based chat interface for Ollama with AI meta-reasoning capabilities. OllamaPy provides an intuitive way to interact with local AI models while featuring unique "vibe tests" that evaluate AI decision-making consistency.

## Features

- 🤖 **Terminal Chat Interface** - Clean, user-friendly chat experience in your terminal
- 🔄 **Streaming Responses** - Real-time streaming for natural conversation flow
- 📚 **Model Management** - Automatic model pulling and listing of available models
- 🧠 **Meta-Reasoning** - AI analyzes user input and selects appropriate actions
- 🛠️ **Extensible Actions** - Easy-to-extend action system for AI decision-making
- 🧪 **AI Vibe Tests** - Built-in tests to evaluate AI consistency and reliability

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

This will start a chat session with the default model (llama3.2:3b). If the model isn't available locally, OllamaPy will automatically pull it for you.

## Usage Examples

### Basic Chat
```bash
# Start chat with default model
ollamapy
```

### Custom Model
```bash
# Use a specific model
ollamapy --model gemma2:2b
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
ollamapy --model mistral:7b --system "You are a helpful coding assistant"
```

## Meta-Reasoning System

OllamaPy features a unique meta-reasoning system where the AI analyzes user input and dynamically selects from available actions. The AI examines the intent behind your message and chooses the most appropriate response action.

Currently available actions:
- **yes** - For positive intent or agreement
- **no** - For negative intent or disagreement  
- **getWeather** - For weather-related queries

The system is designed to be easily extensible - new actions can be added by registering functions with names and descriptions.

## Vibe Tests

Vibe tests are a built-in feature that evaluates how consistently AI models interpret human intent. These tests help you understand model behavior and compare performance across different models.

### Running Vibe Tests

```bash
# Run vibe tests with default settings
ollamapy --vibetest

# Run with multiple iterations for statistical confidence
ollamapy --vibetest -n 5

# Test a specific model
ollamapy --vibetest --model gemma2:2b -n 3
```

### Understanding Results

Vibe tests evaluate the AI's ability to consistently choose appropriate actions based on clearly-intentioned phrases. The tests measure:

- **Consistency**: How reliably the AI interprets similar sentiments
- **Accuracy**: How well the AI matches expected human intent
- **Statistical Confidence**: Reliability across multiple test runs

Tests pass with a 60% or higher success rate, ensuring the AI demonstrates reasonable consistency in decision-making.

## Chat Commands

While chatting, you can use these built-in commands:

- `quit`, `exit`, `bye` - End the conversation
- `clear` - Clear conversation history
- `help` - Show available commands
- `model` - Display current model
- `models` - List all available models
- `actions` - Show available actions the AI can choose from

## Python API

You can also use OllamaPy programmatically:

```python
from ollamapy import TerminalChat, OllamaClient

# Start a chat session programmatically
chat = TerminalChat(model="llama3.2:3b", system_message="You are a helpful assistant")
chat.run()

# Or use the client directly
client = OllamaClient()
messages = [{"role": "user", "content": "Hello!"}]

for chunk in client.chat_stream("llama3.2:3b", messages):
    print(chunk, end="", flush=True)

# Run vibe tests programmatically
from ollamapy import run_vibe_tests
success = run_vibe_tests(model="gemma2:2b", iterations=5)
```

### Available Classes and Functions

- **`TerminalChat`** - High-level terminal chat interface with meta-reasoning
- **`OllamaClient`** - Low-level API client for Ollama
- **`run_vibe_tests()`** - Execute vibe tests programmatically
- **`get_available_actions()`** - Get registered actions from the action system

## Configuration

OllamaPy connects to Ollama on `http://localhost:11434` by default. If your Ollama instance is running elsewhere:

```python
from ollamapy import OllamaClient

client = OllamaClient(base_url="http://your-ollama-server:11434")
```

## Supported Models

OllamaPy works with any model available in Ollama. Popular options include:

- `llama3.2:3b` (default) - Fast and capable general-purpose model
- `gemma2:2b` - Efficient model great for quick responses
- `gemma2:9b` - Larger Gemma model for complex tasks
- `codellama:7b` - Specialized for coding tasks
- `mistral:7b` - Strong general-purpose model

To see available models on your system: `ollama list`

## Extending Actions

The action system is designed to be extensible. Actions are registered with decorators in the `actions.py` file:

```python
from ollamapy.actions import register_action

@register_action("greet", "Use when the user wants a greeting or says hello")
def greet():
    print("👋 Hello there!")
```

Each action needs:
- A unique name (what the AI will say when choosing it)
- A description (helps the AI understand when to use it)
- A function that executes the action

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

## Troubleshooting

### "Ollama server is not running!"
Make sure Ollama is installed and running:
```bash
ollama serve
```

### Model not found
OllamaPy will automatically pull models, but you can also pull manually:
```bash
ollama pull llama3.2:3b
```

### Connection issues
Verify Ollama is accessible:
```bash
curl http://localhost:11434/api/tags
```

### Vibe test issues
- Ensure Ollama is running: `ollama serve`
- Try a different model: `ollamapy --vibetest --model gemma2:2b`
- Run with single iteration for quick feedback: `ollamapy --vibetest -n 1`

## Project Information

- **Version**: 0.5.0
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