# OllamaPy

A powerful terminal-based chat interface for Ollama with AI meta-reasoning capabilities. OllamaPy provides an intuitive way to interact with local AI models while featuring unique "vibe tests" that evaluate AI decision-making consistency.

## Features

- 🤖 **Terminal Chat Interface** - Clean, user-friendly chat experience in your terminal
- 🔄 **Streaming Responses** - Real-time streaming for natural conversation flow
- 📚 **Model Management** - Automatic model pulling and listing of available models
- 🧠 **Meta-Reasoning** - AI analyzes user input and selects appropriate actions
- 🛠️ **Extensible Actions** - Easy-to-extend action system with parameter support
- 🧪 **AI Vibe Tests** - Built-in tests to evaluate AI consistency and reliability
- 🔢 **Parameter Extraction** - AI intelligently extracts parameters from natural language

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
ollamapy --model gemma2:2b
ollamapy -m codellama:7b
```

### Dual Model Setup (Analysis + Chat)
```bash
# Use a small, fast model for analysis and a larger model for chat
ollamapy --analysis-model gemma2:2b --model llama3.2:7b
ollamapy -a gemma2:2b -m mistral:7b

# This is great for performance - small model does action selection, large model handles conversation
```

### Two-Step Analysis Mode
```bash
# Enable two-step analysis (better for smaller models)
ollamapy --two-step --analysis-model gemma2:2b

# Two-step mode separates action selection from parameter extraction
```

### System Message
```bash
# Set context for the AI
ollamapy --system "You are a helpful coding assistant specializing in Python"
ollamapy -s "You are a creative writing partner"
```

### Combined Options
```bash
# Use custom models with system message and two-step mode
ollamapy --two-step --analysis-model gemma2:2b --model mistral:7b --system "You are a helpful assistant"
```

## Meta-Reasoning System

OllamaPy features a unique meta-reasoning system where the AI analyzes user input and dynamically selects from available actions. The AI examines the intent behind your message and chooses the most appropriate response action.

### Dual Model Architecture

For optimal performance, you can use two different models:
- **Analysis Model**: A smaller, faster model (like `gemma2:2b`) for quick action selection
- **Chat Model**: A larger, more capable model (like `llama3.2:7b`) for generating responses

This architecture provides the best of both worlds - fast decision-making and high-quality responses.

```bash
# Example: Fast analysis with powerful chat
ollamapy --analysis-model gemma2:2b --model llama3.2:7b
```

### Analysis Modes

OllamaPy supports two analysis modes:

1. **Single-Step Mode** (default): The AI selects the action and extracts parameters in one analysis
2. **Two-Step Mode**: The AI first selects the action, then extracts parameters in a separate step

Two-step mode is particularly useful with smaller models that might struggle with complex multi-task analysis.

```bash
# Enable two-step mode
ollamapy --two-step
```

### Currently Available Actions

- **null** - Default conversation mode. Used for normal chat when no special action is needed
- **getWeather** - Provides weather information (accepts optional location parameter)
- **getTime** - Returns the current date and time (accepts optional timezone parameter)
- **square_root** - Calculates the square root of a number (requires number parameter)
- **calculate** - Evaluates basic mathematical expressions (requires expression parameter)

### How Meta-Reasoning Works

When you send a message, the AI:
1. **Analyzes** your input to understand intent
2. **Selects** the most appropriate action
3. **Extracts** any required parameters from your input
4. **Executes** the chosen action with parameters
5. **Responds** using the action's output as context

## Creating Custom Actions

The action system is designed to be easily extensible. Here's a comprehensive guide on creating your own actions:

### Basic Action Structure

```python
from ollamapy.actions import register_action

@register_action(
    name="action_name",
    description="When to use this action",
    vibe_test_phrases=["test phrase 1", "test phrase 2"],  # Optional
    parameters={  # Optional
        "param_name": {
            "type": "string|number",
            "description": "What this parameter is for",
            "required": True|False
        }
    }
)
def action_name(param_name=None):
    """Your action implementation."""
    # Do something useful
    return "Result string that will be given to the AI as context"
```

### Example 1: Simple Action (No Parameters)

```python
@register_action(
    name="joke",
    description="Use when the user wants to hear a joke or needs cheering up",
    vibe_test_phrases=[
        "tell me a joke",
        "I need a laugh",
        "cheer me up",
        "make me smile"
    ]
)
def joke():
    """Tell a random joke."""
    import random
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "Why don't eggs tell jokes? They'd crack each other up!"
    ]
    return random.choice(jokes)
```

### Example 2: Action with Required Parameter

```python
@register_action(
    name="convert_temp",
    description="Convert temperature between Celsius and Fahrenheit",
    vibe_test_phrases=[
        "convert 32 fahrenheit to celsius",
        "what's 100C in fahrenheit?",
        "20 degrees celsius in F"
    ],
    parameters={
        "value": {
            "type": "number",
            "description": "The temperature value to convert",
            "required": True
        },
        "unit": {
            "type": "string",
            "description": "The unit to convert from (C or F)",
            "required": True
        }
    }
)
def convert_temp(value, unit):
    """Convert temperature between units."""
    unit = unit.upper()
    if unit == 'C':
        # Celsius to Fahrenheit
        result = (value * 9/5) + 32
        return f"{value}°C is equal to {result:.1f}°F"
    elif unit == 'F':
        # Fahrenheit to Celsius
        result = (value - 32) * 5/9
        return f"{value}°F is equal to {result:.1f}°C"
    else:
        return f"Unknown unit '{unit}'. Please use 'C' for Celsius or 'F' for Fahrenheit."
```

### Example 3: Action with Optional Parameters

```python
@register_action(
    name="roll_dice",
    description="Roll dice for games or random number generation",
    vibe_test_phrases=[
        "roll a die",
        "roll 2d6",
        "roll three dice",
        "give me a random number between 1 and 6"
    ],
    parameters={
        "count": {
            "type": "number",
            "description": "Number of dice to roll",
            "required": False  # Defaults to 1 if not specified
        },
        "sides": {
            "type": "number",
            "description": "Number of sides on each die",
            "required": False  # Defaults to 6 if not specified
        }
    }
)
def roll_dice(count=1, sides=6):
    """Roll dice and return results."""
    import random
    
    # Ensure positive integers
    count = max(1, int(count))
    sides = max(2, int(sides))
    
    if count == 1:
        result = random.randint(1, sides)
        return f"Rolled a d{sides}: {result}"
    else:
        results = [random.randint(1, sides) for _ in range(count)]
        total = sum(results)
        return f"Rolled {count}d{sides}: {results} (Total: {total})"
```

### Best Practices for Creating Actions

1. **Clear Naming**: Use descriptive names that clearly indicate what the action does
   ```python
   # Good: specific and clear
   name="calculate_compound_interest"
   
   # Avoid: too generic
   name="calculate"
   ```

2. **Detailed Descriptions**: Help the AI understand when to use your action
   ```python
   # Good: specific keywords and use cases
   description="Calculate compound interest for investments. Keywords: compound interest, investment return, APY"
   
   # Avoid: too vague
   description="Do math stuff"
   ```

3. **Comprehensive Test Phrases**: Include varied ways users might request the action
   ```python
   vibe_test_phrases=[
       "calculate compound interest on $1000",
       "what's my investment worth after 5 years?",
       "compound interest calculator",
       "how much will I earn with 5% APY?"
   ]
   ```

4. **Parameter Validation**: Always validate and handle edge cases
   ```python
   def safe_divide(numerator, denominator):
       """Safely divide two numbers."""
       if denominator == 0:
           return "Error: Cannot divide by zero!"
       
       result = numerator / denominator
       return f"{numerator} ÷ {denominator} = {result}"
   ```

5. **Meaningful Return Values**: Return informative strings that help the AI respond
   ```python
   # Good: provides context and formatting
   return f"The calculation result is {result:.2f} ({increase:.1f}% increase)"
   
   # Avoid: just the raw number
   return str(result)
   ```

6. **Error Handling**: Always handle potential errors gracefully
   ```python
   try:
       result = complex_calculation(param)
       return f"Success: {result}"
   except ValueError as e:
       return f"Error: Invalid input - {str(e)}"
   except Exception as e:
       return f"Unexpected error: {str(e)}"
   ```

### Adding Your Actions to OllamaPy

1. Create a new Python file for your actions (e.g., `my_actions.py`)
2. Import and implement your actions using the patterns above
3. Import your actions module before starting OllamaPy

```python
# my_script.py
from ollamapy import chat
import my_actions  # This registers your actions

# Now start chat with your custom actions available
chat()
```

### Testing Your Actions

Always test your actions with vibe tests to ensure the AI can reliably select them:

```bash
# Run vibe tests including your custom actions
ollamapy --vibetest

# Test with different models
ollamapy --vibetest --model llama3.2:3b -n 5
```

## Vibe Tests

Vibe tests are a built-in feature that evaluates how consistently AI models interpret human intent and choose appropriate actions. These tests help you understand model behavior and compare performance across different models.

### Running Vibe Tests

```bash
# Run vibe tests with default settings
ollamapy --vibetest

# Run with multiple iterations for statistical confidence
ollamapy --vibetest -n 5

# Test a specific model
ollamapy --vibetest --model gemma2:2b -n 3

# Use dual models for testing (analysis + chat)
ollamapy --vibetest --analysis-model gemma2:2b --model llama3.2:7b -n 5

# Test with two-step analysis
ollamapy --vibetest --two-step --model gemma2:2b
```

### Understanding Results

Vibe tests evaluate:
- **Action Selection**: How reliably the AI chooses the correct action
- **Parameter Extraction**: How accurately the AI extracts required parameters
- **Consistency**: How stable the AI's decisions are across multiple runs

Tests pass with a 60% or higher success rate, ensuring reasonable consistency in decision-making.

## Chat Commands

While chatting, you can use these built-in commands:

- `quit`, `exit`, `bye` - End the conversation
- `clear` - Clear conversation history
- `help` - Show available commands
- `model` - Display current models (both chat and analysis)
- `models` - List all available models
- `actions` - Show available actions the AI can choose from

## Python API

You can also use OllamaPy programmatically:

```python
from ollamapy import TerminalChat, OllamaClient, execute_action

# Start a chat session programmatically with dual models
chat = TerminalChat(
    model="llama3.2:7b", 
    analysis_model="gemma2:2b",
    system_message="You are a helpful assistant",
    two_step_analysis=True
)
chat.run()

# Or use the client directly
client = OllamaClient()
messages = [{"role": "user", "content": "Hello!"}]

for chunk in client.chat_stream("gemma3:4b", messages):
    print(chunk, end="", flush=True)

# Execute actions programmatically
result = execute_action("square_root", {"number": 16})
print(result)  # "The square root of 16 is 4"

# Run vibe tests programmatically with dual models
from ollamapy import run_vibe_tests
success = run_vibe_tests(
    model="llama3.2:7b", 
    analysis_model="gemma2:2b", 
    iterations=5
)
```

### Available Classes and Functions

- **`TerminalChat`** - High-level terminal chat interface with meta-reasoning
- **`OllamaClient`** - Low-level API client for Ollama
- **`run_vibe_tests()`** - Execute vibe tests programmatically
- **`get_available_actions()`** - Get all registered actions
- **`execute_action()`** - Execute an action with parameters programmatically
- **`register_action()`** - Decorator for creating new actions

## Configuration

OllamaPy connects to Ollama on `http://localhost:11434` by default. If your Ollama instance is running elsewhere:

```python
from ollamapy import OllamaClient

client = OllamaClient(base_url="http://your-ollama-server:11434")
```

## Supported Models

OllamaPy works with any model available in Ollama. Popular options include:

- `gemma3:4b` (default) - Fast and capable general-purpose model
- `llama3.2:3b` - Efficient and responsive for most tasks
- `gemma2:2b` - Lightweight model, great for analysis tasks
- `gemma2:9b` - Larger Gemma model for complex tasks
- `codellama:7b` - Specialized for coding tasks
- `mistral:7b` - Strong general-purpose model

To see available models on your system: `ollama list`

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

Run vibe tests:

```bash
pytest -m vibetest
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
ollama pull gemma3:4b
```

### Parameter extraction issues
- Try two-step mode: `ollamapy --two-step`
- Use a more capable analysis model: `ollamapy --analysis-model llama3.2:3b`
- Ensure your action descriptions clearly indicate what parameters are needed

### Vibe test failures
- Try different models: `ollamapy --vibetest --model gemma2:9b`
- Use two-step analysis: `ollamapy --vibetest --two-step`
- Increase iterations for better statistics: `ollamapy --vibetest -n 10`
- Check that your test phrases clearly indicate the intended action

## Project Information

- **Version**: 0.6.2
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