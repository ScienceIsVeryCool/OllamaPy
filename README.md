# OllamaPy

A powerful terminal-based chat interface for Ollama with AI meta-reasoning capabilities, dynamic skill generation, and interactive skill editing. OllamaPy provides an intuitive way to interact with local AI models while featuring unique "vibe tests" that evaluate AI decision-making consistency, automated skill generation, and a web-based skill editor for creating and customizing AI capabilities.

## Demo

![Demo showing terminal app usage](demo.gif)

## Features

### Core System
- 🤖 **Terminal Chat Interface** - Clean, user-friendly chat experience in your terminal
- 🔄 **Streaming Responses** - Real-time streaming for natural conversation flow
- 📚 **Model Management** - Automatic model pulling and listing of available models
- 🧠 **Meta-Reasoning** - AI analyzes user input and selects appropriate actions
- 🏗️ **Modular Architecture** - Clean separation of concerns for easy testing and extension

### Skills System
- 🛠️ **Dynamic Skills** - Extensible skill system with intelligent parameter extraction
- 🎯 **Auto Skill Generation** - AI creates new skills automatically based on prompts
- 🌐 **Interactive Web Editor** - Full-featured web interface for creating and editing skills
- 🔐 **Built-in Protection** - Verified built-in skills are protected from accidental modification
- ✅ **Real-time Validation** - Live syntax checking and skill testing

### Testing & Analysis  
- 🧪 **AI Vibe Tests** - Built-in tests to evaluate AI consistency and reliability
- ⏱️ **Performance Analysis** - Comprehensive timing analysis with consistency scoring
- 📊 **Interactive Reports** - Rich HTML reports with timing visualizations and skill documentation
- 🔢 **Parameter Intelligence** - AI intelligently extracts parameters from natural language

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

### Interactive Skill Editor
```bash
# Launch the web-based skill editor
ollamapy --skill-editor

# Use a custom port
ollamapy --skill-editor --port 8080

# Specify custom skills directory
ollamapy --skill-editor --skills-dir /path/to/skills
```

### Dual Model Setup (Analysis + Chat)
```bash
# Use a small, fast model for analysis and a larger model for chat
ollamapy --analysis-model gemma2:2b --model llama3.2:7b
ollamapy -a gemma2:2b -m mistral:7b

# This is great for performance - small model does action selection, large model handles conversation
```

### System Message
```bash
# Set context for the AI
ollamapy --system "You are a helpful coding assistant specializing in Python"
ollamapy -s "You are a creative writing partner"
```

### Combined Options
```bash
# Use custom models with system message
ollamapy --analysis-model gemma2:2b --model mistral:7b --system "You are a helpful assistant"
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

### Currently Available Actions

- **null** - Default conversation mode. Used for normal chat when no special action is needed
- **fear** - Responds to disturbing or delusional content with direct feedback
- **fileReader** - Reads and displays file contents when user provides a file path
- **directoryReader** - Explores entire directory contents for project analysis
- **getWeather** - Provides weather information (accepts optional location parameter)
- **getTime** - Returns the current date and time (accepts optional timezone parameter)
- **square_root** - Calculates the square root of a number (requires number parameter)
- **calculate** - Evaluates basic mathematical expressions (requires expression parameter)

### How Meta-Reasoning Works

When you send a message, the AI:
1. **Analyzes** your input to understand intent
2. **Selects** the most appropriate action(s) from all available actions
3. **Extracts** any required parameters from your input
4. **Executes** the chosen action(s) with parameters
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
    from ollamapy.actions import log
    
    # Log results so the AI can use them as context
    log(f"[Action] Result: {some_result}")
    # Actions communicate via logging, not return values
```

### Example 1: Simple Action (No Parameters)

```python
from ollamapy.actions import register_action, log

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
    selected_joke = random.choice(jokes)
    log(f"[Joke] {selected_joke}")
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
        log(f"[Temperature] {value}°C = {result:.1f}°F")
    elif unit == 'F':
        # Fahrenheit to Celsius
        result = (value - 32) * 5/9
        log(f"[Temperature] {value}°F = {result:.1f}°C")
    else:
        log(f"[Temperature] Error: Unknown unit '{unit}'. Use 'C' or 'F'.")
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

## Vibe Tests with Performance Analysis

Vibe tests are a built-in feature that evaluates how consistently AI models interpret human intent and choose appropriate actions. These tests now include comprehensive timing analysis to help you understand both accuracy and performance characteristics.

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

# Extended statistical analysis
ollamapy --vibetest --analysis-model gemma2:2b --model llama3.2:7b -n 10
```

### Understanding Results

Vibe tests evaluate multiple dimensions:

#### **Accuracy Metrics**:
- **Action Selection**: How reliably the AI chooses the correct action
- **Parameter Extraction**: How accurately the AI extracts required parameters
- **Consistency**: How stable the AI's decisions are across multiple runs

#### **Performance Metrics**:
- **Response Time**: Average, median, min/max execution times
- **Consistency Score**: 0-100 score based on timing variability
- **Performance Categories**: "Very Fast", "Fast", "Moderate", "Slow", "Very Slow"
- **Percentile Analysis**: 25th, 75th, 95th percentiles for timing distribution

#### **Visual Analytics**:
- **Interactive HTML Reports**: Rich visualizations with timing charts
- **Performance Comparison**: Speed vs consistency scatter plots
- **Per-phrase Analysis**: Detailed breakdown for each test phrase
- **Quadrant Analysis**: Identifies optimal performance zones

### Performance Insights

The timing analysis helps you:
- **Optimize Model Selection**: Choose the best speed/accuracy trade-offs
- **Identify Bottlenecks**: Find slow or inconsistent actions
- **Validate Stability**: Ensure consistent performance across runs
- **Compare Configurations**: Evaluate different model combinations

Example timing output:
```
Timing Analysis:
  Average: 1.23s | Median: 1.15s
  Range: 0.89s - 2.11s
  Performance: Fast
  Consistency: 87.3/100
```

Tests pass with a 60% or higher success rate, ensuring reasonable consistency in decision-making.

## Interactive Skill Editor

OllamaPy includes a comprehensive web-based skill editor that allows you to create, modify, and manage AI skills through an intuitive interface.

### Getting Started

Launch the skill editor with:
```bash
ollamapy --skill-editor
```

Then open your browser to `http://localhost:5000` to access the editor.

### Key Features

#### **📋 Skill Management Dashboard**
- View all skills with filterable grid layout
- See skill status (Built-in vs Custom)
- Quick access to edit, test, and delete operations
- Search and filter capabilities

#### **✏️ Interactive Skill Editing**
- **Real-time Code Editor**: Syntax highlighting for Python skill code
- **Live Validation**: Instant feedback on code syntax and structure
- **Parameter Management**: Dynamic parameter editor with type validation
- **Vibe Test Editor**: Manage trigger phrases that activate skills
- **Role Assignment**: Categorize skills by function (mathematics, file operations, etc.)

#### **🧪 Built-in Testing**
- **Test Skills Instantly**: Execute skills directly in the editor
- **See Live Output**: View skill execution logs in real-time  
- **Validate Before Saving**: Catch errors before deployment
- **Parameter Testing**: Test skills with different input combinations

#### **🔐 Safety Features**
- **Protected Built-ins**: Verified system skills cannot be modified
- **Syntax Validation**: Prevent deployment of broken skills
- **Code Safety Checks**: Warnings for potentially dangerous operations
- **Backup Recommendations**: Automatic timestamps on modifications

#### **🎯 Skill Templates**
Quick-start templates for common skill types:
- **Simple Actions**: Basic skills with no parameters
- **Mathematical Functions**: Computation-focused skills
- **File Operations**: File system interaction skills
- **API Calls**: External service integration skills

### Creating New Skills

1. **Click "+" to create a new skill**
2. **Choose a template** or start from scratch
3. **Fill in the details**:
   - **Name**: Unique identifier (camelCase/snake_case)
   - **Description**: When this skill should be used
   - **Role**: Categorization for organization
   - **Vibe Test Phrases**: Trigger examples for AI recognition
4. **Write the function code**:
   ```python
   def execute(param1=None, param2=None):
       from ollamapy.skills import log
       
       # Your implementation here
       result = do_something(param1, param2)
       log(f"[MySkill] Result: {result}")
   ```
5. **Test your skill** before saving
6. **Save and deploy** instantly

### Editing Existing Skills

- **Click "Edit" on any custom skill**
- **Modify any aspect** except the skill name
- **Test changes** before saving
- **Built-in skills show read-only view** for reference

### Skill Code Requirements

Your skill functions must:
- **Be named `execute`**
- **Use `log()` for output** that the AI can see
- **Handle parameters** as defined in the parameter section
- **Include error handling** for robust operation

Example skill structure:
```python
def execute(text=None):
    from ollamapy.skills import log
    
    if not text:
        log("[MySkill] Error: Text parameter is required")
        return
    
    try:
        result = process_text(text)
        log(f"[MySkill] Successfully processed: {result}")
    except Exception as e:
        log(f"[MySkill] Error: {str(e)}")
```

### API Integration

The skill editor provides a REST API for programmatic access:
- `GET /api/skills` - List all skills
- `POST /api/skills` - Create new skill
- `PUT /api/skills/{name}` - Update existing skill
- `DELETE /api/skills/{name}` - Delete custom skill
- `POST /api/skills/test` - Test skill execution
- `POST /api/skills/validate` - Validate skill data

### Advanced Features

- **Import/Export**: Backup and share skill collections
- **Version Control**: Track skill modification history
- **Batch Operations**: Manage multiple skills efficiently
- **Live Documentation**: Skills automatically appear in generated docs

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
from ollamapy import OllamaClient, ModelManager, AnalysisEngine, ChatSession, TerminalInterface

# Create components
client = OllamaClient()
model_manager = ModelManager(client)
analysis_engine = AnalysisEngine("gemma2:2b", client)  # Fast analysis model
chat_session = ChatSession("llama3.2:7b", client, "You are a helpful assistant")

# Start a terminal interface
terminal = TerminalInterface(model_manager, analysis_engine, chat_session)
terminal.run()

# Or use components directly
messages = [{"role": "user", "content": "Hello!"}]
for chunk in client.chat_stream("gemma3:4b", messages):
    print(chunk, end="", flush=True)

# Execute actions programmatically
from ollamapy import execute_action
execute_action("square_root", {"number": 16})

# Run vibe tests programmatically with timing analysis
from ollamapy import run_vibe_tests
success = run_vibe_tests(
    model="llama3.2:7b", 
    analysis_model="gemma2:2b", 
    iterations=5
)
```

### Available Classes and Functions

#### Core Components:
- **`OllamaClient`** - Low-level API client for Ollama
- **`ModelManager`** - Model availability, pulling, and validation
- **`AnalysisEngine`** - AI decision-making and action selection  
- **`ChatSession`** - Conversation state and response generation
- **`TerminalInterface`** - Terminal UI and user interaction

#### Action System:
- **`register_action()`** - Decorator for creating new actions
- **`execute_action()`** - Execute an action with parameters
- **`get_available_actions()`** - Get all registered actions
- **`log()`** - Log messages from within actions

#### Testing & Analysis:
- **`VibeTestRunner`** - Advanced vibe test runner with timing analysis
- **`run_vibe_tests()`** - Simple function to run vibe tests
- **`VibeTestReportGenerator`** - Generate rich HTML reports with visualizations
- **`TimingStats`** - Sophisticated timing analysis with consistency scoring

#### Utilities:
- **`convert_parameter_value()`** - Convert parameter types
- **`extract_numbers_from_text()`** - Extract numbers from text
- **`prepare_function_parameters()`** - Prepare parameters for function calls

## Configuration

OllamaPy connects to Ollama on `http://localhost:11434` by default. If your Ollama instance is running elsewhere:

```python
from ollamapy import OllamaClient

client = OllamaClient(base_url="http://your-ollama-server:11434")
```

## Supported Models

OllamaPy works with any model available in Ollama. Popular options include:

### **Recommended for Analysis (Fast)**:
- `gemma2:2b` - Lightweight, excellent for action selection
- `gemma3:4b` - Balanced speed and capability
- `llama3.2:3b` - Fast and efficient

### **Recommended for Chat (Quality)**:
- `gemma3:4b` (default) - Great all-around performance
- `gemma2:9b` - Larger model for complex conversations
- `llama3.2:7b` - High-quality responses
- `mistral:7b` - Strong general-purpose model
- `codellama:7b` - Specialized for coding tasks

### **Performance Optimization Examples**:
```bash
# Speed-optimized: Fast analysis + moderate chat
ollamapy --analysis-model gemma2:2b --model gemma3:4b

# Quality-optimized: Moderate analysis + high-quality chat  
ollamapy --analysis-model gemma3:4b --model llama3.2:7b

# Balanced: Same capable model for both
ollamapy --model gemma3:4b
```

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

Run vibe tests with timing analysis:

```bash
pytest -m vibetest
```

### Architecture Overview

OllamaPy uses a clean, modular architecture with performance monitoring:

```
┌───────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ TerminalInterface │    │  AnalysisEngine │    │   ChatSession   │
│                   │    │                 │    │                 │
│ • User input      │    │ • Action select │    │ • Conversation  │
│ • Commands        │    │ • Parameter     │    │ • Response gen  │
│ • Display         │    │   extraction    │    │ • History       │
│ • Timing display  │    │ • ⏱️ Timing      │    │                 │
└───────────────────────┘    └─────────────────────┘    └─────────────────────┘
         │                       │                       │
         └─────────────────────────────┼───────────────────────────┘
                                 │
        ┌─────────────────────────────────────────┐    ┌─────────────────────┐
        │             Testing & Analytics  │    │ OllamaClient    │
        │                                  │    │                 │
        │ • VibeTestRunner  • TimingStats  │    │ • HTTP API      │
        │ • ReportGenerator • Consistency  │    │ • Streaming     │
        │ • Performance Analysis           |    │ • Low-level     │
        └─────────────────────────────────────────┘    └─────────────────────┘
                                 │
                    ┌───────────────────┐
                    │  ModelManager  │
                    │                │
                    │ • Model pull   │
                    │ • Availability │
                    │ • Validation   │
                    └───────────────────┘
```

Each component has a single responsibility and can be tested independently. The timing system is integrated throughout without affecting core functionality.

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
- Use a more capable analysis model: `ollamapy --analysis-model llama3.2:3b`
- Ensure your action descriptions clearly indicate what parameters are needed
- Check that your test phrases include the expected parameters

### Vibe test failures
- Try different models: `ollamapy --vibetest --model gemma2:9b`
- Use separate analysis model: `ollamapy --vibetest --analysis-model gemma2:2b`
- Increase iterations for better statistics: `ollamapy --vibetest -n 10`
- Check that your test phrases clearly indicate the intended action

### Performance issues
- Use a smaller model for analysis: `--analysis-model gemma2:2b`
- Check timing reports to identify slow actions
- Ensure sufficient system resources for your chosen models
- Check Ollama server performance with `ollama ps`
- Review consistency scores in vibe test reports

### Slow or inconsistent timing
- Monitor consistency scores in vibe test reports
- Try different model combinations for optimal speed/accuracy
- Check system resources and Ollama server health
- Use timing analysis to identify performance bottlenecks

### Skill Editor Issues

#### "Missing dependencies for skill editor"
Install the required web framework dependencies:
```bash
pip install flask flask-cors
```

#### Skill editor won't start
- Check if port 5000 is already in use: `lsof -i :5000`
- Try a different port: `ollamapy --skill-editor --port 8080`
- Ensure you have write permissions to the skills directory

#### Can't edit skills in browser
- Make sure the skill editor server is running
- Check browser console for JavaScript errors
- Verify API connection at `http://localhost:5000/api/skills`
- Try refreshing the page or clearing browser cache

#### Built-in skills appear as editable
- This is normal - built-in skills show an edit interface but will reject changes
- Look for "🔒 Protected" or verification status indicators
- Built-in skills are marked with `verified: true` in their data

#### Skills not updating after editing
- Check the browser console for API errors
- Verify the skill editor server is receiving requests
- Ensure proper JSON formatting in skill data
- Try creating a simple test skill first

## Project Information

- **Version**: 0.8.0
- **License**: GPL-3.0-or-later
- **Author**: The Lazy Artist
- **Python**: >=3.8
- **Dependencies**: 
  - `requests>=2.25.0` (HTTP client for Ollama API)
  - `plotly>=5.0.0` (Interactive reports and visualizations)
  - `flask>=2.0.0` (Web framework for skill editor - optional)
  - `flask-cors>=3.0.0` (CORS support for skill editor API - optional)

## Links

- [PyPI Package](https://pypi.org/project/ollamapy/)
- [GitHub Repository](https://github.com/ScienceIsVeryCool/OllamaPy)
- [Issues](https://github.com/ScienceIsVeryCool/OllamaPy/issues)
- [Ollama Documentation](https://ollama.ai/)

## License

This project is licensed under the GPL-3.0-or-later license. See the LICENSE file for details.