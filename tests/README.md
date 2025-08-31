# OllamaPy Test Suite

This directory contains a comprehensive test suite for OllamaPy, designed to ensure code quality, reliability, and professional standards.

## Test Structure

### 📁 Test Files

- **`test_main_comprehensive.py`** - Comprehensive tests for main module functionality
- **`test_ollama_client.py`** - Complete test coverage for OllamaClient
- **`test_package_validation.py`** - Package structure and integrity validation
- **`test_integration_comprehensive.py`** - Integration tests across modules
- **`test_performance.py`** - Performance benchmarks and stress tests
- **`test_main.py`** - Basic legacy tests (maintained for compatibility)
- **`test_ai_query.py`** - AI query functionality tests
- **`unit/`** - Unit tests for specific components
- **`integration/`** - Integration test scenarios
- **`e2e/`** - End-to-end test scenarios

### 🏷️ Test Categories

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (cross-module)
- `@pytest.mark.slow` - Long-running tests (performance, stress)
- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.optional` - Tests for optional features

## Running Tests

### 🚀 Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ollamapy --cov-report=html

# Run comprehensive test suite
./scripts/test.sh
```

### 🎯 Targeted Testing

```bash
# Unit tests only
pytest -m "unit"

# Integration tests only  
pytest -m "integration"

# Fast tests (exclude slow tests)
pytest -m "not slow"

# Specific test file
pytest tests/test_main_comprehensive.py

# Specific test class
pytest tests/test_ollama_client.py::TestOllamaClientInitialization

# Specific test method
pytest tests/test_main_comprehensive.py::TestBasicFunctions::test_hello
```

### 📊 Coverage and Reporting

```bash
# Generate HTML coverage report
pytest --cov=src/ollamapy --cov-report=html
# Open htmlcov/index.html in browser

# Generate XML coverage (for CI)
pytest --cov=src/ollamapy --cov-report=xml

# Fail if coverage below threshold
pytest --cov=src/ollamapy --cov-fail-under=70

# Generate JUnit XML for CI integration
pytest --junit-xml=pytest-results.xml
```

## Test Standards

### ✅ Quality Requirements

- **Coverage**: Minimum 70% code coverage
- **Performance**: Core functions must handle >50K calls/sec
- **Memory**: No memory leaks in long-running tests  
- **Thread Safety**: All public APIs must be thread-safe
- **Error Handling**: All error paths must be tested

### 🏗️ Test Structure Standards

Each test file follows this structure:

```python
"""Module docstring describing test purpose."""

import pytest
from unittest.mock import patch, Mock
from src.ollamapy.module import Function

class TestFunctionality:
    """Test class for specific functionality."""
    
    def test_basic_case(self):
        """Test basic usage scenario."""
        # Arrange
        input_data = "test"
        
        # Act
        result = Function(input_data)
        
        # Assert
        assert result == "expected"
    
    def test_edge_case(self):
        """Test edge case handling."""
        pass
    
    def test_error_case(self):
        """Test error condition handling."""
        pass
```

### 🔧 Mocking Guidelines

- Mock external dependencies (network, file system)
- Use `@patch` decorator for cleaner test code
- Verify mock calls when testing integration
- Use `MagicMock` for complex mock objects

## Performance Testing

### 📈 Benchmarks

Performance tests validate:

- **Function Call Speed**: >50K calls/sec for basic functions
- **Memory Efficiency**: <10MB for 10K operations
- **Concurrency**: Handles multiple threads efficiently
- **Load Handling**: Maintains performance under load
- **Long-running Stability**: No performance degradation over time

### 🚨 Stress Tests

Stress tests validate behavior under extreme conditions:

- Very large input strings (1MB+)
- Rapid-fire function calls (100K+ operations)
- Extended runtime (10+ seconds)
- High concurrency (multiple threads)
- Resource constraints

## CI/CD Integration

### 🔄 GitHub Actions

Tests automatically run on:
- Push to main branch
- Pull request creation
- Release creation

Test results are:
- Uploaded as artifacts
- Sent to CodeCov for coverage tracking
- Used to generate test reports

### 📋 Test Reports

Generated reports include:
- HTML coverage report (`htmlcov/`)
- XML coverage report (`coverage.xml`) 
- JUnit test results (`pytest-results.xml`)
- Security scan results (`bandit-report.json`)

## Troubleshooting

### 🐛 Common Issues

**ImportError: No module named 'src.ollamapy'**
```bash
# Ensure you're in the project root
pip install -e .
```

**Coverage too low**
```bash
# Check which lines aren't covered
pytest --cov=src/ollamapy --cov-report=term-missing
```

**Tests timeout**
```bash
# Run with timeout
pytest --timeout=300
```

**Flaky tests**
```bash
# Run tests multiple times
pytest --count=10 tests/test_flaky.py
```

### 🔍 Debugging Tests

```bash
# Verbose output
pytest -v -s

# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb

# Run last failed tests only
pytest --lf
```

## Contributing

### ➕ Adding New Tests

1. Choose appropriate test file or create new one
2. Follow naming conventions (`test_*.py`)
3. Add appropriate markers (`@pytest.mark.unit`)
4. Include docstrings describing test purpose
5. Follow AAA pattern (Arrange, Act, Assert)
6. Mock external dependencies
7. Test both success and failure cases

### 📝 Test Checklist

Before submitting:

- [ ] All tests pass locally
- [ ] Coverage meets minimum threshold (70%)
- [ ] Performance tests pass
- [ ] Code follows style guidelines
- [ ] Tests are documented with docstrings
- [ ] Edge cases are covered
- [ ] Error conditions are tested

## Contact

For questions about the test suite, please:

1. Check existing test files for examples
2. Review this documentation
3. Open an issue for test-related bugs
4. Contribute improvements via pull request

---

*This test suite ensures OllamaPy maintains professional quality standards and reliability across all use cases.*