"""Tests for ollamapy functionality including vibe tests."""

import pytest
from ollamapy.main import hello, greet
from ollamapy.ollama_client import OllamaClient
from ollamapy.terminal_chat import TerminalChat


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello, World!"


def test_greet():
    """Test the greet function."""
    assert greet("Alice") == "Hello, Alice!"


class TestVibeTests:
    """Vibe tests to evaluate AI decision-making consistency."""
    
    @pytest.fixture
    def model(self, request):
        """Get model from command line or use default."""
        return getattr(request.config.option, 'model', 'gemma3:4b')
    
    @pytest.fixture
    def iterations(self, request):
        """Get number of iterations from command line or use default."""
        return getattr(request.config.option, 'iterations', 1)
    
    @pytest.fixture
    def chat_interface(self, model):
        """Create a chat interface for testing."""
        return TerminalChat(model=model)
    
    def test_vibe_yes_direction(self, chat_interface, iterations):
        """Test AI's ability to consistently choose 'yes' for yes-oriented phrases."""
        test_phrases = [
            "Yes is the direction I would like to go this time",
            "I'm feeling positive about this decision",
            "Absolutely, let's move forward with this",
            "This sounds like a great idea to me",
            "I agree with this approach completely"
        ]
        
        results = {}
        total_correct = 0
        total_tests = 0
        
        for phrase in test_phrases:
            phrase_correct = 0
            
            for i in range(iterations):
                try:
                    chosen_function = chat_interface.analyze_with_ai(phrase)
                    if chosen_function == "yes":
                        phrase_correct += 1
                    total_tests += 1
                except Exception as e:
                    print(f"Error testing phrase '{phrase}' iteration {i+1}: {e}")
                    continue
            
            success_rate = (phrase_correct / iterations) * 100 if iterations > 0 else 0
            results[phrase] = {
                'correct': phrase_correct,
                'total': iterations,
                'success_rate': success_rate
            }
            total_correct += phrase_correct
        
        # Print detailed results
        print(f"\n🧪 Vibe Test Results - YES Direction (Model: {chat_interface.model})")
        print("=" * 80)
        
        for phrase, result in results.items():
            print(f"Phrase: '{phrase[:50]}{'...' if len(phrase) > 50 else ''}'")
            print(f"Success: {result['correct']}/{result['total']} ({result['success_rate']:.1f}%)")
            print("-" * 40)
        
        overall_success_rate = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        print(f"Overall Success Rate: {total_correct}/{total_tests} ({overall_success_rate:.1f}%)")
        
        # Assert that we get at least 60% success rate for yes-oriented phrases
        assert overall_success_rate >= 60, f"Expected at least 60% success rate for yes phrases, got {overall_success_rate:.1f}%"
    
    def test_vibe_no_direction(self, chat_interface, iterations):
        """Test AI's ability to consistently choose 'no' for no-oriented phrases."""
        test_phrases = [
            "No, I don't think this is the right path",
            "I disagree with this approach entirely",
            "This doesn't seem like a good idea to me",
            "I'm not feeling confident about this decision",
            "Absolutely not, let's try something else"
        ]
        
        results = {}
        total_correct = 0
        total_tests = 0
        
        for phrase in test_phrases:
            phrase_correct = 0
            
            for i in range(iterations):
                try:
                    chosen_function = chat_interface.analyze_with_ai(phrase)
                    if chosen_function == "no":
                        phrase_correct += 1
                    total_tests += 1
                except Exception as e:
                    print(f"Error testing phrase '{phrase}' iteration {i+1}: {e}")
                    continue
            
            success_rate = (phrase_correct / iterations) * 100 if iterations > 0 else 0
            results[phrase] = {
                'correct': phrase_correct,
                'total': iterations,
                'success_rate': success_rate
            }
            total_correct += phrase_correct
        
        # Print detailed results
        print(f"\n🧪 Vibe Test Results - NO Direction (Model: {chat_interface.model})")
        print("=" * 80)
        
        for phrase, result in results.items():
            print(f"Phrase: '{phrase[:50]}{'...' if len(phrase) > 50 else ''}'")
            print(f"Success: {result['correct']}/{result['total']} ({result['success_rate']:.1f}%)")
            print("-" * 40)
        
        overall_success_rate = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        print(f"Overall Success Rate: {total_correct}/{total_tests} ({overall_success_rate:.1f}%)")
        
        # Assert that we get at least 60% success rate for no-oriented phrases
        assert overall_success_rate >= 60, f"Expected at least 60% success rate for no phrases, got {overall_success_rate:.1f}%"


# Pytest configuration hook to add custom command line options
def pytest_addoption(parser):
    """Add custom command line options for vibe tests."""
    parser.addoption(
        "--model", 
        action="store", 
        default="gemma3:4b", 
        help="Model to use for vibe tests (default: gemma3:4b)"
    )
    parser.addoption(
        "-N", "--iterations", 
        action="store", 
        type=int, 
        default=1, 
        help="Number of iterations to run each vibe test (default: 1)"
    )