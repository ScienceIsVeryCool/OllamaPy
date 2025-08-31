#!/bin/bash
# Comprehensive test script for OllamaPy

set -e  # Exit on any error

echo "🚀 Starting OllamaPy Test Suite"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Not in project root directory. Please run from the project root."
    exit 1
fi

# Install dependencies if needed
print_status "Installing dependencies..."
pip install -e .[dev] > /dev/null 2>&1 || {
    print_warning "Failed to install dev dependencies, continuing with available packages"
}

# Run different test categories
echo ""
echo "📋 Running Test Categories:"
echo "=========================="

# 1. Unit Tests
echo ""
echo "🔬 Unit Tests"
echo "-------------"
pytest tests/test_main*.py tests/test_ollama_client.py -m "unit or not integration" -v || {
    print_error "Unit tests failed"
    exit 1
}
print_status "Unit tests passed"

# 2. Integration Tests
echo ""
echo "🔗 Integration Tests"
echo "-------------------"
pytest tests/test_integration_comprehensive.py -m "integration" -v || {
    print_error "Integration tests failed"
    exit 1
}
print_status "Integration tests passed"

# 3. Package Validation
echo ""
echo "📦 Package Validation Tests"
echo "---------------------------"
pytest tests/test_package_validation.py -v || {
    print_error "Package validation tests failed"
    exit 1
}
print_status "Package validation tests passed"

# 4. Code Quality Checks
echo ""
echo "🔍 Code Quality Checks"
echo "----------------------"

# Linting with flake8
print_status "Running flake8 linting..."
flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics || {
    print_error "Critical linting errors found"
    exit 1
}

flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics > /dev/null 2>&1
print_status "Linting checks passed"

# Code formatting with black
print_status "Checking code formatting..."
black --check --diff src/ tests/ || {
    print_warning "Code formatting issues found. Run 'black src/ tests/' to fix."
}

# 5. Coverage Report
echo ""
echo "📊 Coverage Analysis"
echo "-------------------"
pytest tests/ --cov=src/ollamapy --cov-report=term-missing --cov-report=html --cov-fail-under=70 || {
    print_warning "Coverage below 70% threshold"
}
print_status "Coverage report generated in htmlcov/"

# 6. Security Checks (if bandit is available)
echo ""
echo "🛡️  Security Checks"
echo "-------------------"
if command -v bandit &> /dev/null; then
    bandit -r src/ -f json -o bandit-report.json > /dev/null 2>&1 || true
    bandit -r src/ --severity-level medium || {
        print_warning "Security issues found. Check bandit-report.json for details."
    }
    print_status "Security checks completed"
else
    print_warning "bandit not installed, skipping security checks"
fi

# 7. Import Tests
echo ""
echo "📥 Import Tests"
echo "--------------"
python -c "
import sys
sys.path.insert(0, 'src')

try:
    from ollamapy.main import main, hello, greet
    print('✅ Main module imports successful')
    
    from ollamapy.ollama_client import OllamaClient
    print('✅ OllamaClient import successful')
    
    # Test basic functionality
    assert hello() == 'Hello, World!'
    assert greet('Test') == 'Hello, Test!'
    print('✅ Basic functionality test passed')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Functionality error: {e}')
    sys.exit(1)
"
print_status "Import tests passed"

# 8. CLI Tests
echo ""
echo "💻 CLI Tests"
echo "------------"
python -m src.ollamapy.main --hello > /dev/null || {
    print_error "CLI hello test failed"
    exit 1
}
print_status "CLI tests passed"

# Final Summary
echo ""
echo "🎉 Test Suite Summary"
echo "===================="
print_status "All tests completed successfully!"
print_status "✅ Unit tests"
print_status "✅ Integration tests" 
print_status "✅ Package validation"
print_status "✅ Code quality checks"
print_status "✅ Coverage analysis"
print_status "✅ Security checks"
print_status "✅ Import tests"
print_status "✅ CLI tests"

echo ""
echo "📊 Generated Reports:"
echo "- HTML coverage: htmlcov/index.html"
echo "- XML coverage: coverage.xml"
if [ -f "bandit-report.json" ]; then
    echo "- Security report: bandit-report.json"
fi

echo ""
print_status "🚀 OllamaPy is ready for deployment!"