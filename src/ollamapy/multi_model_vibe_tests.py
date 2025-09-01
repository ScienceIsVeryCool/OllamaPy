"""Multi-model vibe test runner for comprehensive model comparison and GitHub Pages integration."""

import json
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

from .vibe_tests import VibeTestRunner, TimingStats
from .ollama_client import OllamaClient


class MultiModelVibeTestRunner:
    """Runs vibe tests across multiple models and generates comprehensive reports for GitHub Pages."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the multi-model vibe test runner.

        Args:
            config_path: Path to the model configuration file
        """
        if config_path is None:
            # Default to config/vibe_test_models.json
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "vibe_test_models.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.client = OllamaClient()
        self.all_results = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load the model configuration."""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if config file is missing."""
        return {
            "models": [
                {
                    "name": "gemma3:4b",
                    "display_name": "Gemma 3 4B",
                    "description": "Compact 4B parameter model optimized for speed",
                }
            ],
            "test_config": {
                "iterations": 5,
                "timeout": 120,
                "collect_runtime_stats": True,
                "include_performance_metrics": True,
            },
        }

    def check_model_availability(self, model_name: str, timeout: int = 60) -> bool:
        """Check if a model is available in Ollama.

        Args:
            model_name: Name of the model to check
            timeout: Timeout in seconds for the availability check
        """
        try:
            # Try to generate a simple response to test availability with timeout
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(
                    f"Model availability check timed out after {timeout}s"
                )

            # Set timeout for the check
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

            try:
                response = self.client.generate(model=model_name, prompt="Hello")
                signal.alarm(0)  # Cancel timeout
                return response is not None
            finally:
                signal.alarm(0)  # Ensure timeout is cancelled

        except TimeoutError as e:
            print(f"❌ Model {model_name} availability check timed out: {e}")
            return False
        except Exception as e:
            print(f"❌ Model {model_name} not available: {e}")
            return False

    def run_tests_for_model(
        self, model_config: Dict[str, str], iterations: int
    ) -> Dict[str, Any]:
        """Run vibe tests for a single model.

        Args:
            model_config: Model configuration dictionary
            iterations: Number of iterations per test

        Returns:
            Dictionary containing test results and metadata
        """
        model_name = model_config["name"]
        print(f"\n🧪 Testing Model: {model_config['display_name']} ({model_name})")
        print(f"📄 Description: {model_config['description']}")
        print("=" * 80)

        start_time = time.perf_counter()

        # Create a vibe test runner for this model
        # Use the same model for both chat and analysis to get pure model performance
        runner = VibeTestRunner(model=model_name, analysis_model=model_name)

        # Run the tests
        success = runner.run_all_tests(iterations=iterations)

        end_time = time.perf_counter()
        total_runtime = end_time - start_time

        # Get the detailed results from the runner
        detailed_results = runner.all_test_results

        # Aggregate statistics
        total_tests = sum(
            result["results"]["total_tests"] for result in detailed_results.values()
        )
        total_correct = sum(
            result["results"]["total_correct"] for result in detailed_results.values()
        )
        overall_success_rate = (
            (total_correct / total_tests * 100) if total_tests > 0 else 0
        )

        # Calculate overall timing statistics
        all_times = []
        for result in detailed_results.values():
            all_times.extend(result["results"]["overall_timing_stats"]["raw_times"])

        overall_timing = TimingStats(all_times) if all_times else TimingStats([])

        return {
            "model_config": model_config,
            "success": success,
            "total_runtime": total_runtime,
            "summary": {
                "total_tests": total_tests,
                "total_correct": total_correct,
                "overall_success_rate": overall_success_rate,
                "overall_timing_stats": overall_timing.to_dict(),
            },
            "detailed_results": detailed_results,
            "timestamp": datetime.now().isoformat(),
            "iterations": iterations,
        }

    def run_all_model_tests(self, iterations: Optional[int] = None) -> bool:
        """Run vibe tests for all configured models.

        Args:
            iterations: Override for number of iterations (uses config default if None)

        Returns:
            True if all models passed their tests, False otherwise
        """
        if iterations is None:
            iterations = self.config["test_config"]["iterations"]

        # Filter only enabled models
        enabled_models = [m for m in self.config["models"] if m.get("enabled", True)]
        total_models = len(enabled_models)
        disabled_count = len(self.config["models"]) - total_models
        
        print("🌟 Multi-Model Vibe Test Suite")
        print(
            f"📋 Testing {total_models} enabled models with {iterations} iterations each"
        )
        if disabled_count > 0:
            print(f"⚠️  Skipping {disabled_count} disabled models")
        print(f"📊 Collecting runtime statistics and performance metrics")
        print("=" * 80)

        # Check Ollama availability
        if not self.client.is_available():
            print(
                "❌ Ollama server is not available. Please start it with: ollama serve"
            )
            return False

        all_success = True
        self.all_results = {}

        for i, model_config in enumerate(enabled_models, 1):
            model_name = model_config["name"]
            model_timeout = model_config.get("timeout", 60)

            print(
                f"\n[{i}/{total_models}] Preparing to test {model_name}..."
            )
            print(f"⏱️  Model timeout: {model_timeout}s")

            # Check if model is available with model-specific timeout
            if not self.check_model_availability(model_name, model_timeout):
                print(f"❌ Skipping {model_name} - not available")
                continue

            # Run tests for this model
            try:
                results = self.run_tests_for_model(model_config, iterations)
                self.all_results[model_name] = results

                if not results["success"]:
                    all_success = False

            except Exception as e:
                print(f"❌ Error testing {model_name}: {e}")
                all_success = False
                continue

        # Generate comparison report
        self._print_comparison_summary()

        return all_success

    def _print_comparison_summary(self):
        """Print a comparison summary of all tested models."""
        if not self.all_results:
            return

        print("\n" + "=" * 80)
        print("📊 Multi-Model Comparison Summary")
        print("=" * 80)

        # Sort models by overall success rate
        sorted_models = sorted(
            self.all_results.items(),
            key=lambda x: x[1]["summary"]["overall_success_rate"],
            reverse=True,
        )

        print(
            f"{'Model':<20} {'Success Rate':<12} {'Avg Time':<10} {'Consistency':<12} {'Status':<10}"
        )
        print("-" * 70)

        for model_name, results in sorted_models:
            display_name = results["model_config"]["display_name"]
            success_rate = results["summary"]["overall_success_rate"]
            avg_time = results["summary"]["overall_timing_stats"]["mean"]
            consistency = results["summary"]["overall_timing_stats"][
                "consistency_score"
            ]
            status = "✅ PASS" if results["success"] else "❌ FAIL"

            print(
                f"{display_name:<20} {success_rate:>6.1f}%     {avg_time:>6.2f}s    {consistency:>6.1f}/100     {status}"
            )

        # Performance insights
        fastest_model = min(
            sorted_models, key=lambda x: x[1]["summary"]["overall_timing_stats"]["mean"]
        )
        most_consistent = max(
            sorted_models,
            key=lambda x: x[1]["summary"]["overall_timing_stats"]["consistency_score"],
        )

        print(f"\n🏆 Performance Insights:")
        print(
            f"   Fastest: {fastest_model[1]['model_config']['display_name']} ({fastest_model[1]['summary']['overall_timing_stats']['mean']:.2f}s avg)"
        )
        print(
            f"   Most Consistent: {most_consistent[1]['model_config']['display_name']} ({most_consistent[1]['summary']['overall_timing_stats']['consistency_score']:.1f}/100)"
        )

        total_tests = sum(
            r["summary"]["total_tests"] for r in self.all_results.values()
        )
        total_time = sum(r["total_runtime"] for r in self.all_results.values())
        print(f"   Total Tests: {total_tests}")
        print(f"   Total Runtime: {total_time:.1f}s")

    def save_results_json(self, output_path: str) -> str:
        """Save detailed results to JSON file for GitHub Pages.

        Args:
            output_path: Path where to save the results

        Returns:
            Path to the saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create the complete results structure for GitHub Pages
        github_results = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "config_file": str(self.config_path),
                "total_models_tested": len(self.all_results),
                "test_config": self.config["test_config"],
            },
            "models": [],
        }

        for model_name, results in self.all_results.items():
            # Process detailed results for GitHub Pages format
            processed_skills = {}
            for skill_name, skill_data in results["detailed_results"].items():
                processed_skills[skill_name] = {
                    "action_name": skill_data["results"]["action_name"],
                    "action_description": skill_data["results"]["action_description"],
                    "passed": skill_data["passed"],
                    "success_rate": skill_data["results"]["success_rate"],
                    "total_tests": skill_data["results"]["total_tests"],
                    "total_correct": skill_data["results"]["total_correct"],
                    "timing_stats": skill_data["results"]["overall_timing_stats"],
                    "phrase_results": {},
                }

                # Process phrase-level results
                for phrase, phrase_data in skill_data["results"][
                    "phrase_results"
                ].items():
                    processed_skills[skill_name]["phrase_results"][phrase] = {
                        "success_rate": phrase_data["success_rate"],
                        "timing_stats": phrase_data["timing_stats"],
                        "expected_params": phrase_data["expected_params"],
                        "secondary_actions": phrase_data["secondary_action_counts"],
                    }

            model_result = {
                "model_name": model_name,
                "display_name": results["model_config"]["display_name"],
                "description": results["model_config"]["description"],
                "overall_success": results["success"],
                "summary": results["summary"],
                "skills": processed_skills,
                "timestamp": results["timestamp"],
                "iterations": results["iterations"],
            }
            github_results["models"].append(model_result)

        # Save to file
        with open(output_path, "w") as f:
            json.dump(github_results, f, indent=2)

        print(f"📁 Detailed results saved to: {output_path}")
        return str(output_path)

    def get_results_summary(self) -> Dict[str, Any]:
        """Get a summary of results for external use.

        Returns:
            Dictionary with summary statistics
        """
        if not self.all_results:
            return {}

        return {
            "total_models": len(self.all_results),
            "models_passed": sum(1 for r in self.all_results.values() if r["success"]),
            "models_failed": sum(
                1 for r in self.all_results.values() if not r["success"]
            ),
            "average_success_rate": sum(
                r["summary"]["overall_success_rate"] for r in self.all_results.values()
            )
            / len(self.all_results),
            "total_runtime": sum(r["total_runtime"] for r in self.all_results.values()),
            "fastest_model": (
                min(
                    self.all_results.items(),
                    key=lambda x: x[1]["summary"]["overall_timing_stats"]["mean"],
                )[0]
                if self.all_results
                else None
            ),
            "most_accurate_model": (
                max(
                    self.all_results.items(),
                    key=lambda x: x[1]["summary"]["overall_success_rate"],
                )[0]
                if self.all_results
                else None
            ),
        }


def run_multi_model_tests(
    config_path: Optional[str] = None,
    iterations: Optional[int] = None,
    output_path: Optional[str] = None,
) -> bool:
    """Convenience function to run multi-model vibe tests.

    Args:
        config_path: Path to model configuration file
        iterations: Number of iterations per test
        output_path: Path to save detailed JSON results

    Returns:
        True if all models passed tests, False otherwise
    """
    runner = MultiModelVibeTestRunner(config_path)
    success = runner.run_all_model_tests(iterations)

    if output_path:
        runner.save_results_json(output_path)

    return success
