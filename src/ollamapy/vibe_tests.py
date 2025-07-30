"""Built-in vibe tests for evaluating AI decision-making consistency."""

from typing import List, Dict, Tuple
from .terminal_chat import TerminalChat
from .actions import get_actions_with_vibe_tests


class VibeTestRunner:
    """Built-in vibe test runner that ships with every installation."""
    
    def __init__(self, model: str = "gemma3:4b", analysis_model: str = None):
        """Initialize the vibe test runner.
        
        Args:
            model: The model to use for testing
            analysis_model: Optional separate model for action analysis (defaults to main model)
        """
        self.model = model
        self.analysis_model = analysis_model or model  # Use main model if no analysis model specified
        self.chat_interface = TerminalChat(model=model, analysis_model=self.analysis_model)
        self.actions_with_tests = get_actions_with_vibe_tests()
        
        # Define yes/no phrases for compatibility (if needed by tests)
        self.yes_phrases = [
            "Yes, I agree completely",
            "Absolutely, that's correct",
            "Sure thing!",
            "Yeah, definitely",
            "Of course, yes"
        ]
        
        self.no_phrases = [
            "No, I disagree",
            "Absolutely not",
            "I don't think so",
            "Nope, that's wrong",
            "Definitely not"
        ]
    
    def check_prerequisites(self) -> bool:
        """Check if Ollama is available and models can be used."""
        if not self.chat_interface.client.is_available():
            print("❌ Error: Ollama server is not running!")
            print("Please start Ollama with: ollama serve")
            return False
        
        # Check if models are available, pull them if needed
        available_models = self.chat_interface.client.list_models()
        
        # Check main model
        main_model_available = any(self.model in model for model in available_models)
        if not main_model_available:
            print(f"📥 Main model '{self.model}' not found locally. Pulling...")
            if not self.chat_interface.client.pull_model(self.model):
                print(f"❌ Failed to pull model '{self.model}'")
                return False
        
        # Check analysis model (if different from main model)
        if self.analysis_model != self.model:
            analysis_model_available = any(self.analysis_model in model for model in available_models)
            if not analysis_model_available:
                print(f"📥 Analysis model '{self.analysis_model}' not found locally. Pulling...")
                if not self.chat_interface.client.pull_model(self.analysis_model):
                    print(f"❌ Failed to pull analysis model '{self.analysis_model}'")
                    return False
        
        return True
    
    def run_action_test(self, action_name: str, phrases: List[str], 
                       iterations: int) -> Tuple[bool, Dict]:
        """Run a test on a specific action with its phrases.
        
        Args:
            action_name: Name of the action being tested
            phrases: List of test phrases for this action
            iterations: Number of times to test each phrase
            
        Returns:
            Tuple of (success: bool, results: dict)
        """
        total_correct = 0
        total_tests = 0
        results = {}
        
        print(f"\n🧪 {action_name} Action Test")
        print(f"Chat Model: {self.model}")
        if self.analysis_model != self.model:
            print(f"Analysis Model: {self.analysis_model}")
        else:
            print("Using same model for analysis and chat")
        print("=" * 80)
        
        for phrase in phrases:
            phrase_correct = 0
            
            for i in range(iterations):
                try:
                    chosen_function = self.chat_interface.analyze_with_ai(phrase)
                    if chosen_function == action_name:
                        phrase_correct += 1
                    total_tests += 1
                except Exception as e:
                    print(f"❌ Error testing phrase iteration {i+1}: {e}")
                    continue
            
            success_rate = (phrase_correct / iterations) * 100 if iterations > 0 else 0
            results[phrase] = {
                'correct': phrase_correct,
                'total': iterations,
                'success_rate': success_rate
            }
            total_correct += phrase_correct
            
            # Print individual results
            phrase_display = phrase[:50] + '...' if len(phrase) > 50 else phrase
            print(f"Phrase: '{phrase_display}'")
            print(f"Success: {phrase_correct}/{iterations} ({success_rate:.1f}%)")
            print("-" * 40)
        
        overall_success_rate = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        print(f"Overall Success Rate: {total_correct}/{total_tests} ({overall_success_rate:.1f}%)")
        
        test_passed = overall_success_rate >= 60.0
        return test_passed, {
            'total_correct': total_correct,
            'total_tests': total_tests,
            'success_rate': overall_success_rate,
            'phrase_results': results
        }
    
    def run_all_tests(self, iterations: int = 1) -> bool:
        """Run all vibe tests for all actions that have test phrases.
        
        Args:
            iterations: Number of iterations per phrase
            
        Returns:
            True if all tests passed, False otherwise
        """
        print(f"🧪 Running vibe tests")
        print(f"Chat model: {self.model}")
        if self.analysis_model != self.model:
            print(f"Analysis model: {self.analysis_model}")
        else:
            print("Using same model for analysis and chat")
        print(f"Iterations: {iterations}")
        print("=" * 80)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        print(f"✅ Using chat model: {self.model}")
        if self.analysis_model != self.model:
            print(f"✅ Using analysis model: {self.analysis_model}")
        print(f"🧠 Testing AI's ability to interpret human intent and choose appropriate functions...")
        print(f"📋 Found {len(self.actions_with_tests)} actions with vibe test phrases\n")
        
        if not self.actions_with_tests:
            print("❌ No actions with vibe test phrases found!")
            return False
        
        # Run tests for each action
        test_results = {}
        all_tests_passed = True
        
        for action_name, action_info in self.actions_with_tests.items():
            test_phrases = action_info['vibe_test_phrases']
            
            if not test_phrases:
                print(f"⚠️  Skipping {action_name} - no test phrases defined")
                continue
            
            test_passed, results = self.run_action_test(
                action_name, test_phrases, iterations
            )
            
            test_results[action_name] = {
                'passed': test_passed,
                'results': results
            }
            
            if not test_passed:
                all_tests_passed = False
        
        # Final results summary
        print(f"\n📊 Final Test Results:")
        print("=" * 50)
        
        for action_name, test_data in test_results.items():
            status_icon = "✅ PASSED" if test_data['passed'] else "❌ FAILED"
            success_rate = test_data['results']['success_rate']
            print(f"{action_name} Action Test: {status_icon} ({success_rate:.1f}%)")
        
        status_icon = "✅" if all_tests_passed else "❌"
        status_text = "ALL TESTS PASSED" if all_tests_passed else "SOME TESTS FAILED"
        print(f"\nOverall Result: {status_icon} {status_text}")
        
        if not all_tests_passed:
            print("\n💡 Tips for improving results:")
            print("   • Try a different model with --model")
            print("   • Try a different analysis model with --analysis-model")
            print("   • Use a smaller, faster model for analysis (e.g., gemma2:2b)")
            print("   • Increase iterations with -n for better statistics")
            print("   • Ensure Ollama server is running optimally")
            print("   • Check action descriptions and test phrases for clarity")
        
        return all_tests_passed
    
    def run_quick_test(self) -> bool:
        """Run a quick single-iteration test for fast feedback."""
        print("🚀 Running quick vibe test (1 iteration each)...")
        return self.run_all_tests(iterations=1)
    
    def run_statistical_test(self, iterations: int = 5) -> bool:
        """Run a statistical test with multiple iterations."""
        print(f"📊 Running statistical vibe test ({iterations} iterations each)...")
        return self.run_all_tests(iterations=iterations)


def run_vibe_tests(model: str = "gemma3:4b", iterations: int = 1, analysis_model: str = None) -> bool:
    """Convenience function to run vibe tests.
    
    Args:
        model: The model to use for testing
        iterations: Number of iterations per test
        analysis_model: Optional separate model for action analysis (defaults to main model)
        
    Returns:
        True if all tests passed, False otherwise
    """
    runner = VibeTestRunner(model=model, analysis_model=analysis_model)
    return runner.run_all_tests(iterations=iterations)