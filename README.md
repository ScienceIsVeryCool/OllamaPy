# 🤖 OllamaPy

A powerful terminal-based chat interface for Ollama with AI meta-reasoning capabilities, dynamic skill generation, interactive skill editing, and comprehensive testing infrastructure. OllamaPy provides an intuitive way to interact with local AI models while featuring unique "vibe tests" for AI consistency evaluation, automated skill generation, a web-based skill editor, and a unified capabilities dashboard.

## 🌐 Live Demo & Showcase

**🎯 [View Live Capabilities Dashboard](https://scienceisverycool.github.io/OllamaPy/)**

Explore all OllamaPy capabilities in our interactive showcase:
- **📊 [Skills Showcase](https://scienceisverycool.github.io/OllamaPy/skills.html)** - Browse 15+ AI skills with implementations
- **📈 [Test Coverage Reports](https://scienceisverycool.github.io/OllamaPy/coverage.html)** - View comprehensive test coverage
- **⚡ Dynamic Reports** - Auto-generated from codebase capabilities

![Demo showing terminal app usage](demo.gif)

## ✨ Features Overview

### 🏗️ Core System
- 🤖 **Terminal Chat Interface** - Clean, user-friendly chat experience in your terminal
- 🔄 **Streaming Responses** - Real-time streaming for natural conversation flow
- 📚 **Model Management** - Automatic model pulling and listing of available models
- 🧠 **Meta-Reasoning** - AI analyzes user input and selects appropriate actions
- 🎯 **Dual Model Architecture** - Fast analysis + powerful chat models
- 📊 **Comprehensive Testing** - 117 tests with 35%+ coverage

### 🛠️ Skills System (15+ Skills Available)
- 🎯 **Dynamic Skills** - Extensible skill system with intelligent parameter extraction
- ⚡ **Auto Skill Generation** - AI creates new skills automatically based on prompts
- 🌐 **Interactive Web Editor** - Full-featured web interface for creating and editing skills
- 🔐 **Built-in Protection** - Verified built-in skills are protected from accidental modification
- ✅ **Real-time Validation** - Live syntax checking and skill testing
- 📋 **Skills Showcase** - Browse all capabilities with live examples

#### Available Skills Categories:
- **🧮 Mathematics** (2): Calculator, square root functions
- **📁 File Operations** (2): File/directory reading capabilities
- **ℹ️ Information** (2): Weather queries, time functions
- **🎨 General** (7): Haiku generation, anagram checking, password generation, etc.
- **🧠 Advanced** (1): Legal contract summarization
- **💭 Emotional** (1): Fear response simulation

### 🧪 Testing & Analysis Infrastructure
- 🔬 **AI Vibe Tests** - Built-in tests to evaluate AI consistency and reliability
- ⏱️ **Performance Analysis** - Comprehensive timing analysis with consistency scoring
- 📊 **Interactive Reports** - Rich HTML reports with timing visualizations and skill documentation
- 📈 **Coverage Dashboard** - Real-time test coverage with 117 passing tests
- 🎯 **Skills Documentation** - Auto-generated skill showcase from JSON definitions
- 🚀 **CI/CD Pipeline** - Automated testing and deployment via GitHub Actions

### 🌐 Unified Capabilities Dashboard
- 🏠 **Main Dashboard** - Centralized view of all OllamaPy capabilities
- 📊 **Live Statistics** - Real-time stats on skills, tests, and coverage
- 🔍 **Interactive Exploration** - Browse skills with code implementations
- 📈 **Performance Metrics** - Test results and coverage reports
- 🎨 **Modern UI** - Responsive design with smooth animations
- 🔗 **Deep Linking** - Direct access to specific capabilities and reports

## 📦 Installation

### Quick Install from PyPI:
```bash
pip install ollamapy
```

### Development Install:
```bash
git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
cd OllamaPy
pip install -e ".[dev]"
```

### Prerequisites
You need [Ollama](https://ollama.ai/) installed and running:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Start the Ollama server
ollama serve
```

## 🚀 Quick Start

### Basic Usage:
```bash
# Start chat with default model
ollamapy

# Use a specific model
ollamapy --model gemma2:2b

# Dual model setup (recommended for performance)
ollamapy --analysis-model gemma2:2b --model llama3.2:7b
```

### Interactive Features:
```bash
# Launch the web-based skill editor
ollamapy --skill-editor

# Run AI consistency tests
ollamapy --vibetest

# Generate new skills automatically
ollamapy --skillgen --count 3

# Custom system prompt
ollamapy --system "You are a helpful coding assistant"
```

## 🎯 Meta-Reasoning System

OllamaPy features a sophisticated meta-reasoning system where the AI analyzes user input and dynamically selects from 15+ available skills. The AI examines the intent behind your message and chooses the most appropriate response action.

### How It Works:
1. **🔍 Analyzes** your input to understand intent
2. **🎯 Selects** the most appropriate skill(s) from all available skills
3. **⚙️ Extracts** any required parameters from your input
4. **⚡ Executes** the chosen skill(s) with parameters
5. **💬 Responds** using the skill's output as context

### Available Skills:

#### 🧮 **Mathematics Skills**:
- **`calculate`** - Evaluates mathematical expressions
- **`square_root`** - Calculates square roots of numbers

#### 📁 **File Operations**:
- **`fileReader`** - Reads and displays file contents
- **`directoryReader`** - Explores entire directory contents

#### ℹ️ **Information Services**:
- **`getWeather`** - Provides weather information with location support
- **`getTime`** - Returns current date/time with timezone support

#### 🎨 **General Purpose** (7 skills):
- **`GenerateaSimpleHaiku`** - Creates 5-7-5 syllable haikus
- **`CheckIfTwoStringsAreAnagrams`** - Validates anagram pairs
- **`GenerateARandomPasswordOfASpecifiedLength`** - Creates secure passwords
- **`ExtractFirstSentence`** - Isolates first sentence from text
- **`TranslateSingleWordIntoRandomSynonym`** - Word substitution
- **`Generatesimple`** - General-purpose text generation
- **`customPythonShell`** - Interactive Python execution

#### 🧠 **Advanced Capabilities**:
- **`SummarizeLegalContractsIntoPlainLanguage`** - Legal document analysis

#### 💭 **Emotional Intelligence**:
- **`fear`** - Responds to disturbing content with direct feedback

### Performance Optimization:
```bash
# Speed-optimized: Fast analysis + moderate chat
ollamapy --analysis-model gemma2:2b --model gemma3:4b

# Quality-optimized: Moderate analysis + high-quality chat  
ollamapy --analysis-model gemma3:4b --model llama3.2:7b

# Balanced: Same capable model for both
ollamapy --model gemma3:4b
```

## 🌐 Interactive Skill Editor

Launch a comprehensive web-based interface for managing AI skills:

```bash
ollamapy --skill-editor
# Opens http://localhost:5000
```

### ✨ Editor Features:
- **📋 Dashboard** - View all skills with filterable grid
- **✏️ Live Editing** - Real-time code editor with syntax highlighting
- **🧪 Instant Testing** - Execute skills directly in the browser
- **🔐 Safety Features** - Protected built-ins and validation
- **📊 Skill Analytics** - Performance metrics and usage stats
- **🎯 Templates** - Quick-start templates for common skill types

### Creating New Skills:
```python
def execute(param1=None, param2=None):
    from ollamapy.skills import log
    
    # Your implementation here
    result = do_something(param1, param2)
    log(f"[MySkill] Result: {result}")
```

## 🔬 Vibe Testing with Analytics

Evaluate AI consistency and performance with comprehensive analytics:

```bash
# Run vibe tests with timing analysis
ollamapy --vibetest -n 5

# Test specific model performance
ollamapy --vibetest --model gemma2:2b -n 10

# Dual model performance testing
ollamapy --vibetest --analysis-model gemma2:2b --model llama3.2:7b -n 5
```

### 📊 Analytics Include:
- **🎯 Accuracy Metrics**: Action selection and parameter extraction success rates
- **⏱️ Performance Metrics**: Response times, consistency scores, percentile analysis
- **📈 Visual Reports**: Interactive HTML reports with timing charts and scatter plots
- **🎯 Consistency Scoring**: 0-100 score based on timing variability and reliability

## 🧬 Dynamic Skill Generation

Generate new AI skills automatically:

```bash
# Generate skills from ideas
ollamapy --skillgen --count 3

# Generate with custom model
ollamapy --skillgen --model llama3.2:7b --analysis-model gemma2:2b

# Generate from specific ideas
ollamapy --skillgen --ideas "weather forecasting,code optimization"
```

## 💻 Python API

Use OllamaPy programmatically with comprehensive class structure:

```python
from ollamapy import (
    OllamaClient, ModelManager, AnalysisEngine, 
    ChatSession, TerminalInterface, run_vibe_tests
)

# Create and configure components
client = OllamaClient()
model_manager = ModelManager(client)
analysis_engine = AnalysisEngine("gemma2:2b", client)
chat_session = ChatSession("llama3.2:7b", client, "You are helpful")

# Start terminal interface
terminal = TerminalInterface(model_manager, analysis_engine, chat_session)
terminal.run()

# Run comprehensive vibe tests
success = run_vibe_tests(
    model="llama3.2:7b", 
    analysis_model="gemma2:2b", 
    iterations=5
)

# Execute skills programmatically
from ollamapy import execute_skill
execute_skill("calculate", {"expression": "2 + 2"})
```

### 🏗️ Architecture Overview:
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ TerminalInterface   │    │  AnalysisEngine     │    │   ChatSession       │
│ • User interaction  │ ←→ │ • Skill selection   │ ←→ │ • Conversation      │
│ • Command handling  │    │ • Parameter extract │    │ • Response gen      │
│ • Performance UI    │    │ • ⏱️ Timing analysis │    │ • History tracking  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
         │                           │                           │
         └─────────────────────────────────┼───────────────────────────────┘
                                     │
        ┌─────────────────────────────────────────────────┐
        │              Skills & Testing System            │
        │ • 15+ Skills   • VibeTestRunner • ReportGen    │
        │ • Skill Editor • TimingStats    • WebUI        │
        │ • Auto-gen     • Analytics      • Dashboard    │
        └─────────────────────────────────────────────────┘
                                     │
                    ┌─────────────────────────────────┐
                    │   Infrastructure & Deployment   │
                    │ • OllamaClient  • GitHub Pages  │
                    │ • ModelManager  • CI/CD         │
                    │ • Test Suite    • Live Reports  │
                    └─────────────────────────────────┘
```

## 📊 Live Reporting & Documentation

### 🌐 GitHub Pages Dashboard
- **[Main Dashboard](https://scienceisverycool.github.io/OllamaPy/)** - Unified capabilities overview
- **[Skills Showcase](https://scienceisverycool.github.io/OllamaPy/skills.html)** - Interactive skill browser
- **[Coverage Reports](https://scienceisverycool.github.io/OllamaPy/coverage.html)** - Test coverage analysis
- **Auto-updating** - Refreshed on every commit to main branch

### 📈 Comprehensive Testing
- **117 Tests** passing consistently
- **35%+ Coverage** across all modules  
- **Integration Tests** for cross-module functionality
- **Performance Tests** with timing analysis
- **Vibe Tests** for AI consistency validation

### 🔄 CI/CD Pipeline
- **Automated Testing** on every commit
- **Coverage Reporting** with visual dashboards
- **Skills Documentation** auto-generated from JSON
- **GitHub Pages Deployment** for live showcase
- **Multi-environment Testing** across Python versions

## 🎛️ Advanced Configuration

### Model Recommendations:
```bash
# 🚀 Speed-optimized setup
ollamapy --analysis-model gemma2:2b --model gemma3:4b

# 🎯 Quality-optimized setup
ollamapy --analysis-model gemma3:4b --model llama3.2:7b

# 💼 Production-ready setup
ollamapy --analysis-model gemma2:2b --model mistral:7b --system "Professional assistant"

# 🧪 Testing setup
ollamapy --analysis-model gemma2:2b --model codellama:7b --skill-editor --port 8080
```

### Environment Configuration:
```python
from ollamapy import OllamaClient

# Custom Ollama server
client = OllamaClient(base_url="http://your-server:11434")

# Custom timeout settings
client = OllamaClient(timeout=60)
```

## 🛠️ Development & Testing

### Development Setup:
```bash
git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
cd OllamaPy
pip install -e ".[dev]"
```

### Running Tests:
```bash
# All tests
pytest

# Coverage report
pytest --cov=src/ollamapy --cov-report=html

# Vibe tests only
pytest -m vibetest

# Performance tests
pytest -m slow

# Specific test categories
pytest tests/integration/
pytest tests/unit/
```

### Building Documentation:
```bash
# Generate skills showcase
python scripts/generate_skills_showcase.py

# View local documentation
python -m http.server 8000 -d docs/
# Open http://localhost:8000
```

## 🆘 Troubleshooting

### Common Issues:

**🔌 "Ollama server is not running!"**
```bash
ollama serve
# Ensure Ollama is running on localhost:11434
```

**📦 Model not found**
```bash
ollama pull gemma3:4b
# OllamaPy auto-pulls models, but manual pull also works
```

**🧪 Vibe test failures**
```bash
# Try different models
ollamapy --vibetest --model gemma2:9b -n 5

# Use separate analysis model
ollamapy --vibetest --analysis-model gemma2:2b --model llama3.2:7b
```

**🌐 Skill Editor Issues**
```bash
# Install web dependencies
pip install flask flask-cors

# Try different port
ollamapy --skill-editor --port 8080

# Check port availability
lsof -i :5000
```

**⚡ Performance Issues**
```bash
# Use lighter analysis model
ollamapy --analysis-model gemma2:2b

# Check system resources
ollama ps

# Monitor performance
ollamapy --vibetest -n 10  # Check timing reports
```

## 📋 Project Information

- **Version**: 0.8.0
- **License**: GPL-3.0-or-later
- **Author**: The Lazy Artist
- **Python**: >=3.8
- **Skills Available**: 15+ across 6 categories
- **Test Coverage**: 35%+ with 117 passing tests
- **Live Demo**: [GitHub Pages Dashboard](https://scienceisverycool.github.io/OllamaPy/)

### Dependencies:
- **Core**: `requests>=2.25.0` (Ollama API client)
- **Analytics**: `plotly>=5.0.0` (Interactive reports and visualizations)
- **Web Editor**: `flask>=2.0.0`, `flask-cors>=3.0.0` (Optional web interface)
- **Testing**: `pytest`, `pytest-cov` (Development testing framework)

## 🔗 Links & Resources

- 📦 **[PyPI Package](https://pypi.org/project/ollamapy/)** - Install via pip
- 🌐 **[Live Demo](https://scienceisverycool.github.io/OllamaPy/)** - Interactive capabilities dashboard
- 📂 **[GitHub Repository](https://github.com/ScienceIsVeryCool/OllamaPy)** - Source code and issues
- 🎯 **[Skills Showcase](https://scienceisverycool.github.io/OllamaPy/skills.html)** - Browse all 15+ skills
- 📊 **[Coverage Reports](https://scienceisverycool.github.io/OllamaPy/coverage.html)** - Test coverage analysis
- 📖 **[Ollama Documentation](https://ollama.ai/)** - Local AI model platform

## 🎯 Future Roadmap

- 🔄 **Enhanced Skill Generation** - More sophisticated auto-generation with templates
- 📊 **Advanced Analytics** - Deeper performance insights and skill optimization
- 🌐 **Skill Marketplace** - Share and discover community skills
- 🤖 **Multi-Model Support** - Enhanced support for different model providers
- 📱 **Mobile Interface** - Responsive mobile-optimized skill editor
- 🔌 **Plugin System** - Extensible architecture for third-party integrations

## 📄 License

This project is licensed under the GPL-3.0-or-later license. See the [LICENSE](LICENSE) file for details.

---

**🚀 Ready to explore AI capabilities?** 
[**Try the Live Demo →**](https://scienceisverycool.github.io/OllamaPy/)