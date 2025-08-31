# Getting Started

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama installed and running

### Basic Installation

```bash
pip install ollamapy
```

### Installation with Skill Editor

```bash
pip install ollamapy[editor]
```

### Development Installation

```bash
git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
cd OllamaPy
pip install -e .[dev]
```

## First Run

### Start Chat Interface

```bash
ollamapy
```

### Launch Skill Editor

```bash
ollamapy --skill-editor
```

The skill editor will be available at `http://localhost:8765`.

### Configuration

OllamaPy stores configuration and custom skills in `~/.ollamapy/`.

## Docker Usage

### Run Container

```bash
docker run -p 8765:8765 -v ~/.ollamapy:/home/ollamapy/.ollamapy scienceisverycoool/ollamapy
```

### Build from Source

```bash
git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
cd OllamaPy
docker build -t ollamapy .
docker run -p 8765:8765 ollamapy
```

## Next Steps

- Explore the [Skills System](skills/index.md)
- Try the [Skill Editor](skill-editor/index.md)
- Read about [Contributing](development/contributing.md)