# Contributing to OllamaPy

We welcome contributions to OllamaPy! This guide will help you get started.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ScienceIsVeryCool/OllamaPy.git
   cd OllamaPy
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   ```

## Running Tests

Run vibe tests:
```bash
ollamapy --vibetest
```

Run comprehensive tests:
```bash
ollamapy --multi-model-vibetest
```

## Contributing Code

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Write clear commit messages