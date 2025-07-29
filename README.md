# OllamaPy

A clean terminal-based chat interface for Ollama, providing an easy way to interact with local AI models through a simple Python wrapper.

## Features

- 🤖 **Terminal Chat Interface** - Clean, user-friendly chat experience in your terminal
- 🔄 **Streaming Responses** - Real-time streaming for natural conversation flow
- 📚 **Model Management** - Automatic model pulling and listing of available models
- 💾 **Conversation History** - Maintains context throughout your chat session
- ⚙️ **Customizable** - Support for different models and system messages
- 🛠️ **Built-in Commands** - Easy-to-use commands for managing your chat session
- 🧪 **AI Vibe Tests** - Evaluate AI decision-making consistency and reliability

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

This will start a chat session with the default model (gemma3:4b). If the model isn't available locally, OllamaPy will automatically pull it for you.

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

## Vibe Tests

OllamaPy includes "vibe tests" - a unique feature that evaluates AI decision-making consistency. These tests measure how well different AI models can interpret natural language intent and choose between 'yes' and 'no' functions based on the sentiment and context of human phrases.

### What Are Vibe Tests?

Vibe tests present AI models with natural language phrases that clearly indicate a positive or negative intent, then measure how consistently the AI chooses the appropriate response function. This helps evaluate:

- **Consistency**: How reliably the AI interprets similar sentiments
- **Accuracy**: How well the AI matches human intent
- **Model Comparison**: Performance differences between AI models
- **Statistical Confidence**: Reliability across multiple test runs

### Running Vibe Tests

```bash
# Run vibe tests with default settings (1 iteration each)
ollamapy --vibetest

# Run vibe tests with multiple iterations for statistical analysis
ollamapy --vibetest -N 5

# Use a specific model for vibe tests
ollamapy --vibetest --model llama3.2:3b -N 3

# Run comprehensive analysis with maximum iterations
ollamapy --vibetest -N 10
```

### Understanding Vibe Test Results

Vibe tests evaluate two scenarios:

**1. YES Direction Test** - Tests phrases that should trigger the 'yes' function:
- "Yes is the direction I would like to go this time"
- "I'm feeling positive about this decision"  
- "Absolutely, let's move forward with this"
- "This sounds like a great idea to me"
- "I agree with this approach completely"

**2. NO Direction Test** - Tests phrases that should trigger the 'no' function:
- "No, I don't think this is the right path"
- "I disagree with this approach entirely"
- "This doesn't seem like a good idea to me"
- "I'm not feeling confident about this decision"
- "Absolutely not, let's try something else"

### Example Vibe Test Output

```
🧪 Running vibe tests with model: gemma3:4b, iterations: 3
============================================================

🧪 YES Direction Test (Model: gemma3:4b)
================================================================================
Phrase: 'Yes is the direction I would like to go this time'
Success: 3/3 (100.0%)
----------------------------------------
Phrase: 'I'm feeling positive about this decision'
Success: 2/3 (66.7%)
----------------------------------------
Overall Success Rate: 14/15 (93.3%)

🧪 NO Direction Test (Model: gemma3:4b)
================================================================================
Phrase: 'No, I don't think this is the right path'
Success: 3/3 (100.0%)
----------------------------------------
Overall Success Rate: 13/15 (86.7%)

📊 Final Results:
YES Direction Test: ✅ PASSED
NO Direction Test: ✅ PASSED  
Overall: ✅ ALL TESTS PASSED
```

### Test Requirements and Scoring

- **Pass Threshold**: Tests require a 60% or higher success rate to pass
- **Statistical Analysis**: Multiple iterations (`-n` parameter) provide better confidence
- **Model Variations**: Different models show varying performance characteristics
- **Real-time Feedback**: See confidence scores and decision-making process

### Installation Compatibility

Vibe tests work seamlessly with both installation methods:

- **PyPI Install**: Uses built-in test runner for maximum compatibility
- **Development Install**: Can optionally use pytest for advanced features
- **No Dependencies**: Vibe tests work without requiring pytest installation
- **Fallback System**: Automatically adapts to available testing frameworks

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
chat = TerminalChat(model="gemma3:4b", system_message="You are a helpful assistant")
chat.run()

# Or use the client directly
client = OllamaClient()
messages = [{"role": "user", "content": "Hello!"}]

for chunk in client.chat_stream("gemma3:4b", messages):
    print(chunk, end="", flush=True)

# Run vibe tests programmatically
from ollamapy.main import run_builtin_vibe_tests
success = run_builtin_vibe_tests(model="gemma3:4b", iterations=5)
```

### Available Classes

- **`TerminalChat`** - High-level terminal chat interface with meta-reasoning
- **`OllamaClient`** - Low-level API client for Ollama
- **`hello()`**, **`greet(name)`** - Simple utility functions
- **`run_builtin_vibe_tests()`** - Programmatic vibe test execution

## Configuration

OllamaPy connects to Ollama on `http://localhost:11434` by default. If your Ollama instance is running elsewhere, you can create a custom client:

```python
from ollamapy import OllamaClient

client = OllamaClient(base_url="http://your-ollama-server:11434")
```

## Supported Models

OllamaPy works with any model available in Ollama. Popular options include:

- `gemma3:4b` (default) - Fast and efficient, great for vibe tests
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

Run vibe tests in development:

```bash
# With pytest (development)
pytest -k vibe --model gemma3:4b -N 3

# With built-in runner (works everywhere) 
python -m ollamapy.main --vibetest -N 3
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

### Vibe test issues
If vibe tests fail to run:
```bash
# Verify Ollama is running
ollama serve

# Test with verbose output
ollamapy --vibetest -N  1

# Try a different model
ollamapy --vibetest --model llama3.2:3b
```

## Project Information

- **Version**: 0.3.0
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