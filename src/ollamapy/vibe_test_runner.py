"""Standalone vibe test runner that can be used programmatically."""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .vibe_tests import VibeTestRunner as BaseVibeTestRunner, TimingStats
from .ollama_client import OllamaClient


class VribeTestRunner:
    """Programmatic interface for running vibe tests with configurable options."""
    
    def __init__(self, 
                 models: Optional[List[str]] = None,
                 config_path: Optional[str] = None,
                 output_dir: Optional[str] = None):
        """Initialize the vibe test runner.
        
        Args:
            models: List of model names to test. If None, uses config file.
            config_path: Path to model configuration file
            output_dir: Directory to save test results
        """
        self.models = models
        self.output_dir = Path(output_dir) if output_dir else Path("./docs")
        self.client = OllamaClient()
        
        # Load configuration
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "vibe_test_models.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Results storage
        self.all_results = {}
        self.test_timestamp = datetime.now().isoformat()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load the model configuration."""
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                
            # If specific models were provided, filter the config
            if self.models:
                config["models"] = [
                    m for m in config.get("models", [])
                    if m["name"] in self.models
                ]
                
                # Add any models not in config as simple entries
                configured_models = {m["name"] for m in config["models"]}
                for model in self.models:
                    if model not in configured_models:
                        config["models"].append({
                            "name": model,
                            "display_name": model,
                            "description": f"Model: {model}",
                            "enabled": True
                        })
                        
            return config
            
        except FileNotFoundError:
            # Create default config for specified models
            if self.models:
                return {
                    "models": [
                        {
                            "name": model,
                            "display_name": model,
                            "description": f"Model: {model}",
                            "enabled": True
                        }
                        for model in self.models
                    ],
                    "test_config": {
                        "iterations": 5,
                        "timeout": 120,
                        "collect_runtime_stats": True
                    }
                }
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "models": [
                {
                    "name": "gemma3:4b",
                    "display_name": "Gemma 3 4B",
                    "description": "Compact 4B parameter model",
                    "enabled": True
                }
            ],
            "test_config": {
                "iterations": 5,
                "timeout": 120,
                "collect_runtime_stats": True
            }
        }
        
    def check_model_availability(self, model_name: str, timeout: int = 60) -> bool:
        """Check if a model is available in Ollama."""
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Model check timed out after {timeout}s")
                
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            try:
                response = self.client.generate(model=model_name, prompt="Hello")
                signal.alarm(0)
                return response is not None
            finally:
                signal.alarm(0)
                
        except TimeoutError:
            print(f"⏱️ Model {model_name} check timed out")
            return False
        except Exception as e:
            print(f"❌ Model {model_name} not available: {e}")
            return False
            
    def run_tests_for_model(self, 
                           model_name: str,
                           display_name: Optional[str] = None,
                           description: Optional[str] = None,
                           iterations: int = 5) -> Dict[str, Any]:
        """Run vibe tests for a single model.
        
        Args:
            model_name: Name of the model to test
            display_name: Display name for the model
            description: Description of the model
            iterations: Number of iterations per test
            
        Returns:
            Dictionary containing test results
        """
        display_name = display_name or model_name
        description = description or f"Model: {model_name}"
        
        print(f"\n🧪 Testing Model: {display_name} ({model_name})")
        print(f"📄 Description: {description}")
        print("=" * 80)
        
        start_time = time.perf_counter()
        
        # Create a vibe test runner for this model
        runner = BaseVibeTestRunner(model=model_name, analysis_model=model_name)
        
        # Run the tests
        success = runner.run_all_tests(iterations=iterations)
        
        end_time = time.perf_counter()
        total_runtime = end_time - start_time
        
        # Get detailed results
        detailed_results = runner.all_test_results
        
        # Aggregate statistics
        total_tests = sum(
            result["results"]["total_tests"] 
            for result in detailed_results.values()
        )
        total_correct = sum(
            result["results"]["total_correct"]
            for result in detailed_results.values()
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
            "model_name": model_name,
            "display_name": display_name,
            "description": description,
            "success": success,
            "total_runtime": total_runtime,
            "overall_success_rate": overall_success_rate,
            "total_tests": total_tests,
            "total_correct": total_correct,
            "timing_stats": {
                "mean": overall_timing.mean,
                "median": overall_timing.median,
                "min": overall_timing.min,
                "max": overall_timing.max,
                "std": overall_timing.std_dev,
            },
            "detailed_results": detailed_results,
            "timestamp": datetime.now().isoformat()
        }
        
    def run_all_models(self, iterations: int = 5, progress_callback=None) -> Dict[str, Any]:
        """Run tests for all configured models.
        
        Args:
            iterations: Number of iterations per test
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing all test results
        """
        enabled_models = [
            m for m in self.config.get("models", [])
            if m.get("enabled", True)
        ]
        
        if not enabled_models:
            print("❌ No models enabled for testing!")
            return {}
            
        print(f"\n🚀 Running vibe tests for {len(enabled_models)} models")
        print(f"🔁 Iterations per test: {iterations}")
        
        results = {}
        
        for i, model_config in enumerate(enabled_models, 1):
            model_name = model_config["name"]
            
            if progress_callback:
                progress_callback(i, len(enabled_models), model_name)
                
            print(f"\n[{i}/{len(enabled_models)}] Processing {model_name}...")
            
            # Check availability
            if not self.check_model_availability(model_name):
                print(f"⚠️ Skipping {model_name} - not available")
                results[model_name] = {
                    "model_name": model_name,
                    "display_name": model_config.get("display_name", model_name),
                    "description": model_config.get("description", ""),
                    "success": False,
                    "error": "Model not available",
                    "skipped": True
                }
                continue
                
            # Run tests
            try:
                result = self.run_tests_for_model(
                    model_name=model_name,
                    display_name=model_config.get("display_name"),
                    description=model_config.get("description"),
                    iterations=iterations
                )
                results[model_name] = result
                
            except Exception as e:
                print(f"❌ Error testing {model_name}: {e}")
                results[model_name] = {
                    "model_name": model_name,
                    "display_name": model_config.get("display_name", model_name),
                    "description": model_config.get("description", ""),
                    "success": False,
                    "error": str(e)
                }
                
        self.all_results = results
        return results
        
    def save_results(self, output_path: Optional[str] = None) -> str:
        """Save test results to a JSON file.
        
        Args:
            output_path: Optional path to save results
            
        Returns:
            Path where results were saved
        """
        if not output_path:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = self.output_dir / "vibe_test_results.json"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
        # Prepare output data
        output_data = {
            "timestamp": self.test_timestamp,
            "config": self.config,
            "results": self.all_results,
            "summary": self._generate_summary()
        }
        
        # Save to file
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2, default=str)
            
        print(f"✅ Results saved to: {output_path}")
        return str(output_path)
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of all test results."""
        if not self.all_results:
            return {}
            
        successful_models = [
            name for name, result in self.all_results.items()
            if result.get("success", False) and not result.get("skipped", False)
        ]
        
        failed_models = [
            name for name, result in self.all_results.items()
            if not result.get("success", False) and not result.get("skipped", False)
        ]
        
        skipped_models = [
            name for name, result in self.all_results.items()
            if result.get("skipped", False)
        ]
        
        # Calculate average success rates
        success_rates = [
            result.get("overall_success_rate", 0)
            for result in self.all_results.values()
            if result.get("success", False) and not result.get("skipped", False)
        ]
        
        avg_success_rate = (
            sum(success_rates) / len(success_rates)
            if success_rates else 0
        )
        
        return {
            "total_models_tested": len(self.all_results),
            "successful_models": len(successful_models),
            "failed_models": len(failed_models),
            "skipped_models": len(skipped_models),
            "average_success_rate": avg_success_rate,
            "model_names": {
                "successful": successful_models,
                "failed": failed_models,
                "skipped": skipped_models
            }
        }
        
    def get_results_for_docs(self) -> Dict[str, Any]:
        """Get results formatted for documentation generation.
        
        Returns:
            Dictionary with results formatted for documentation
        """
        return {
            "timestamp": self.test_timestamp,
            "models": self.all_results,
            "summary": self._generate_summary(),
            "config": self.config
        }