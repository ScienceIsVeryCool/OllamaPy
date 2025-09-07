# 🤖 OllamaPy

A terminal-based chat interface for Ollama that adds a skills system, automated testing, and interactive skill management. Connect to your local Ollama models with features for meta-reasoning, skill generation, and comprehensive testing.

## 🌐 Project Resources

**[View Live Documentation](https://scienceisverycool.github.io/OllamaPy/)** (when available)

Explore the project capabilities:
- **Skills Browser** - View available AI skills and their implementations
- **Test Reports** - Coverage and test results
- **API Documentation** - Technical reference

## ✨ What It Does

### Core Features
- 🤖 **Terminal Chat** - Command-line interface for chatting with Ollama models
- 🔄 **Streaming Responses** - Real-time response streaming from AI models  
- 📚 **Model Management** - Automatic model detection and pulling
- 🧠 **Meta-Reasoning** - AI analyzes input and selects appropriate skills to execute
- 🎯 **Dual Model Support** - Use different models for analysis and chat responses

### Skills System
- 🎯 **Dynamic Skills** - Extensible system for adding AI capabilities
- ⚡ **Skill Generation** - AI can attempt to generate new skills
- 🌐 **Web Editor** - Browser-based interface for skill management (requires Flask)
- ✅ **Skill Testing** - Validation system to test skill functionality
- 📋 **15+ Built-in Skills** - Pre-configured skills for common tasks

#### Included Skill Categories:
- **Mathematics**: Basic calculator, square root
- **File Operations**: Read files and directories
- **Information**: Weather mock-ups, time display  
- **Utilities**: Password generation, anagram checking, haiku creation
- **Advanced**: Contract summarization examples

### Testing & Documentation
- 🔬 **Vibe Tests** - Consistency testing for AI responses
- ⏱️ **Performance Analysis** - Timing and reliability metrics
- 📊 **Test Coverage** - Automated testing with coverage reports
- 📈 **CI/CD** - GitHub Actions for automated testing and deployment

## 📦 Installation

### From PyPI:
```bash
pip install ollamapy
```

### From Source:
```bash
git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
cd OllamaPy
pip install -e .
```

### Prerequisites
Requires [Ollama](https://ollama.ai/) installed and running:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama server
ollama serve
```

## 🚀 Getting Started

### Basic Usage:
```bash
# Start with default settings
ollamapy

# Specify a model
ollamapy --model gemma2:2b

# Use separate models for analysis and chat
ollamapy --analysis-model gemma2:2b --model llama3.2:7b
```

### Additional Features:
```bash
# Open web-based skill editor (requires Flask)
ollamapy --skill-editor

# Run consistency tests
ollamapy --vibetest

# Try to generate new skills
ollamapy --skillgen --count 3

# Set custom system message
ollamapy --system "You are a helpful coding assistant"
```

## 🎯 How the Skills System Works

The meta-reasoning system allows the AI to:
1. **Analyze** your input to understand what you're asking
2. **Select** relevant skills from those available
3. **Extract** parameters needed for the skills
4. **Execute** the selected skills
5. **Respond** with results integrated into the conversation

### Example Interactions:
- "What's the weather?" → Executes weather skill (returns mock data)
- "Calculate 25 * 4" → Runs calculator skill
- "Read file.txt" → Uses file reading skill
- "Generate a haiku about coding" → Creates a haiku

## 🛠️ Development

### Setup Development Environment:
```bash
git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
cd OllamaPy
pip install -e ".[dev]"
```

### Running Tests:
```bash
# Run all tests
pytest

# Generate coverage report
pytest --cov=src/ollamapy --cov-report=html

# Run specific test types
pytest tests/unit/
pytest tests/integration/
```

### Building Documentation:
```bash
# Generate documentation site
python -m ollamapy.docs_generator

# Serve locally
python -m http.server 8000 -d docs/
```

## 🔧 Configuration

### Model Selection:
The choice of model affects performance and quality:
- **Small models** (gemma2:2b): Fast responses, lower resource usage
- **Medium models** (gemma3:4b): Balance of speed and quality
- **Large models** (llama3.2:7b+): Best quality, slower responses

### Environment Setup:
```python
from ollamapy import OllamaClient

# Connect to custom Ollama server
client = OllamaClient(base_url="http://your-server:11434")

# Adjust timeout
client = OllamaClient(timeout=60)
```

## 🆘 Common Issues

### "Ollama server is not running"
Make sure Ollama is started:
```bash
ollama serve
```

### "Model not found"
The specified model will be automatically pulled if available:
```bash
# Or manually pull:
ollama pull gemma2:2b
```

### Skill editor not working
Install Flask dependencies:
```bash
pip install ollamapy[editor]
# or
pip install flask flask-cors
```

## 📊 Project Status

- **Version**: 0.8.0
- **Status**: Beta - Core features working, some features experimental
- **Testing**: 117+ tests with automated CI/CD
- **Coverage**: ~35% code coverage
- **Python**: Supports 3.8+

## 🤝 Contributing

Contributions are welcome! Areas that could use improvement:
- Additional skills
- Test coverage
- Documentation
- UI enhancements
- Performance optimizations

Please check the issues page for specific needs.

## 📜 License

This project is licensed under GPL-3.0-or-later. See LICENSE file for details.

## 🙏 Acknowledgments

Built on top of [Ollama](https://ollama.ai/) for local AI model hosting.

---

*Note: This is an experimental project. Features like skill generation and web editing may not always work as expected. The weather skill returns mock data and doesn't fetch real weather information.*