# Contributing to OllamaPy

Thank you for your interest in contributing to OllamaPy! This guide will help you get started.

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/OllamaPy.git
cd OllamaPy
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e .[dev]
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

## Running Tests

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### All Tests with Coverage
```bash
pytest tests/ --cov=src/ollamapy --cov-report=html
```

## Code Quality

### Linting
```bash
flake8 src/
black --check src/ tests/
isort --check-only src/ tests/
```

### Type Checking
```bash
mypy src/
```

### Security Scanning
```bash
bandit -r src/
safety check
```

## Testing the Skill Editor

### Start Development Server
```bash
python -m src.ollamapy.main --skill-editor --port 8765
```

### Run Editor Tests
```bash
pytest tests/unit/test_skill_editor.py -v
```

## Docker Development

### Build Image
```bash
docker build -t ollamapy-dev .
```

### Run Container
```bash
docker run -p 8765:8765 ollamapy-dev
```

## Submitting Changes

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Follow existing code style
- Add tests for new functionality
- Update documentation if needed

### 3. Test Your Changes
```bash
# Run all tests
pytest tests/

# Check code quality
flake8 src/
black src/ tests/
```

### 4. Commit and Push
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### 5. Create Pull Request
Open a pull request from your fork to the main repository.

## Guidelines

### Code Style
- Follow PEP 8
- Use type hints where appropriate
- Write clear docstrings
- Keep functions focused and small

### Commit Messages
Follow conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for code refactoring

### Testing
- Write tests for new functionality
- Maintain test coverage above 80%
- Include both unit and integration tests

## Getting Help

- Open an issue for bugs or feature requests
- Join discussions in GitHub Discussions
- Check existing issues before creating new ones

## Release Process

Releases are automated via GitHub Actions when tags are pushed:

1. Update version in `pyproject.toml` and `setup.py`
2. Create and push a git tag: `git tag v0.8.1 && git push origin v0.8.1`
3. GitHub Actions will build and publish to PyPI automatically