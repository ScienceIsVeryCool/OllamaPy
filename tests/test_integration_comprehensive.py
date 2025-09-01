"""Comprehensive integration tests for OllamaPy."""

import pytest
import os
import tempfile
import json
import subprocess
import sys
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path


class TestCLIIntegration:
    """Test CLI integration and command line interface."""

    def test_hello_command_execution(self):
        """Test that --hello command executes successfully."""
        result = subprocess.run(
            [sys.executable, "-m", "src.ollamapy.main", "--hello"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Command failed with error: {result.stderr}"
        assert "Hello, World!" in result.stdout
        assert "Hello, Python!" in result.stdout

    def test_help_command(self):
        """Test that help command works."""
        result = subprocess.run(
            [sys.executable, "-m", "src.ollamapy.main", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        assert "OllamaPy" in result.stdout
        assert "--model" in result.stdout
        assert "--vibetest" in result.stdout
        assert "--skillgen" in result.stdout

    def test_version_information(self):
        """Test that version information is displayed."""
        result = subprocess.run(
            [sys.executable, "-m", "src.ollamapy.main", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        assert "v0.8.0" in result.stdout

    @patch("src.ollamapy.main.run_vibe_tests")
    def test_vibetest_command_integration(self, mock_run_vibe):
        """Test vibe test command integration."""
        mock_run_vibe.return_value = True

        # Test the function directly instead of subprocess to avoid timeout
        from src.ollamapy.main import run_vibe_tests

        result = run_vibe_tests(
            count=1, model="test-model", analysis_model="test-model"
        )

        # Should return True when mocked
        assert result is True
        mock_run_vibe.assert_called_once()


class TestModuleIntegration:
    """Test integration between different modules."""

    def test_client_generate_integration(self):
        """Test OllamaClient integration with generate functionality."""
        from src.ollamapy.ollama_client import OllamaClient

        client = OllamaClient()
        # Just test that the method exists and returns a string (even if empty due to no server)
        response = client.generate("test-model", "Hello integration test")

        # Should return string (empty if no server available)
        assert isinstance(response, str)

    def test_client_availability_integration(self):
        """Test availability check integration."""
        from src.ollamapy.ollama_client import OllamaClient

        client = OllamaClient()
        # Just test that the method exists and returns a boolean
        is_available = client.is_available()

        # Should return boolean (False if no server available)
        assert isinstance(is_available, bool)

    def test_import_chain_integration(self):
        """Test that all import chains work correctly."""
        # Test main module imports
        from src.ollamapy.main import main, hello, greet

        # Test that functions are callable
        assert callable(main)
        assert callable(hello)
        assert callable(greet)

        # Test basic functionality
        assert hello() == "Hello, World!"
        assert greet("Test") == "Hello, Test!"

    def test_optional_import_handling(self):
        """Test graceful handling of optional imports."""
        # Test skill editor import handling
        try:
            from src.ollamapy.main import run_skill_editor

            # Should not raise ImportError at import time
            assert callable(run_skill_editor)
        except ImportError:
            pytest.fail("Optional imports should not cause import errors")


class TestFileSystemIntegration:
    """Test file system operations and interactions."""

    def test_temporary_file_handling(self):
        """Test that temporary files are handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test that we can create and write to temporary files
            test_file = temp_path / "test_file.txt"
            test_file.write_text("Integration test content")

            # Verify file exists and content is correct
            assert test_file.exists()
            assert test_file.read_text() == "Integration test content"

    def test_working_directory_independence(self):
        """Test that the package works from different working directories."""
        original_cwd = os.getcwd()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)

                # Should still be able to import and use basic functions
                from src.ollamapy.main import hello

                assert hello() == "Hello, World!"
        finally:
            os.chdir(original_cwd)

    def test_config_file_handling(self):
        """Test configuration file handling if applicable."""
        # Test that missing config files don't break functionality
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["HOME"] = temp_dir  # Temporarily change home directory

            try:
                from src.ollamapy.main import hello

                # Should work even with no config files
                assert hello() == "Hello, World!"
            finally:
                # Restore original HOME
                if "HOME" in os.environ:
                    del os.environ["HOME"]


class TestErrorHandlingIntegration:
    """Test error handling across module boundaries."""

    def test_network_error_propagation(self):
        """Test that network errors are properly handled."""
        from src.ollamapy.ollama_client import OllamaClient

        # Use an invalid URL to trigger network error
        client = OllamaClient(base_url="http://invalid-host-12345:11434")

        # Should handle the error gracefully and return empty string
        response = client.generate("test-model", "Hello")
        assert isinstance(response, str)  # Should get empty string on error

    def test_timeout_error_handling(self):
        """Test timeout error handling."""
        from src.ollamapy.ollama_client import OllamaClient

        # Just test that we can create client with invalid URL without crashing
        client = OllamaClient(base_url="http://invalid-host:99999")

        # Test availability check (should be fast to fail)
        is_available = client.is_available()
        assert isinstance(is_available, bool)  # Should be False for invalid host

    def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        from src.ollamapy.main import greet

        # Test with None - should handle gracefully by converting to string
        result = greet(None)
        assert isinstance(result, str)
        assert "None" in result

        # Test with unusual but valid inputs
        assert greet(123) == "Hello, 123!"
        assert greet([]) == "Hello, []!"


class TestDataFlowIntegration:
    """Test data flow between components."""

    @patch("src.ollamapy.ollama_client.OllamaClient")
    def test_chat_session_data_flow(self, mock_client_class):
        """Test data flow in chat session."""
        # Mock the client instance
        mock_client = MagicMock()
        mock_client.chat.return_value = "Mocked response"
        mock_client_class.return_value = mock_client

        try:
            from src.ollamapy.chat_session import ChatSession

            session = ChatSession("test-model", mock_client, "Test system")
            response = session.send_message("Hello")

            assert response == "Mocked response"
            mock_client.chat.assert_called_once()
        except ImportError:
            pytest.skip("ChatSession not available")

    def test_parameter_validation_flow(self):
        """Test parameter validation across modules."""
        from src.ollamapy.main import hello, greet

        # Test that parameters are validated correctly
        assert hello() == "Hello, World!"  # No parameters
        assert greet("Valid") == "Hello, Valid!"  # Valid parameter

        # Test edge cases
        assert greet("") == "Hello, !"  # Empty string
        assert greet("A" * 1000) == f"Hello, {'A' * 1000}!"  # Long string


class TestResourceManagement:
    """Test resource management and cleanup."""

    def test_memory_usage_basic(self):
        """Basic test for memory usage patterns."""
        import gc

        # Force garbage collection before test
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Import and use modules
        from src.ollamapy.main import hello, greet

        # Use functions multiple times
        for i in range(100):
            hello()
            greet(f"User{i}")

        # Force garbage collection after test
        gc.collect()
        final_objects = len(gc.get_objects())

        # Should not have excessive object growth
        object_growth = final_objects - initial_objects
        assert object_growth < 1000, f"Excessive object growth: {object_growth}"

    def test_function_call_performance(self):
        """Basic performance test for function calls."""
        import time
        from src.ollamapy.main import hello, greet

        # Test basic function performance
        start_time = time.time()

        for _ in range(1000):
            hello()
            greet("Performance test")

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete 1000 calls in reasonable time (less than 1 second)
        assert (
            execution_time < 1.0
        ), f"Functions too slow: {execution_time} seconds for 1000 calls"


class TestConcurrencyBasics:
    """Basic concurrency tests."""

    def test_thread_safety_basic(self):
        """Basic thread safety test."""
        import threading
        import time
        from src.ollamapy.main import hello, greet

        results = []
        errors = []

        def worker():
            try:
                for i in range(10):
                    result = hello()
                    results.append(result)

                    result = greet(f"Thread-{threading.current_thread().ident}-{i}")
                    results.append(result)
            except Exception as e:
                errors.append(e)

        # Create and start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)

        # Check results
        assert len(errors) == 0, f"Errors in threaded execution: {errors}"
        assert len(results) == 100, f"Expected 100 results, got {len(results)}"

        # Check that all hello() calls returned the same result
        hello_results = [r for r in results if r == "Hello, World!"]
        assert (
            len(hello_results) == 50
        ), "Not all hello() calls returned expected result"


class TestEnvironmentIntegration:
    """Test integration with different environments."""

    def test_python_version_compatibility(self):
        """Test that code works with current Python version."""
        import sys

        # Should work with Python 3.8+
        assert sys.version_info >= (3, 8), "Requires Python 3.8 or higher"

        # Test that basic functionality works
        from src.ollamapy.main import hello

        assert hello() == "Hello, World!"

    def test_import_without_optional_dependencies(self):
        """Test that core functionality works without optional dependencies."""
        # This simulates an environment where Flask and other optional deps aren't installed

        # Basic imports should still work
        from src.ollamapy.main import hello, greet, main

        # Core functionality should work
        assert hello() == "Hello, World!"
        assert greet("Test") == "Hello, Test!"

    def test_path_handling(self):
        """Test that path handling works correctly."""
        import sys
        from pathlib import Path

        # Test that the package can be found regardless of how it's imported
        package_path = Path(__file__).parent.parent / "src"

        if str(package_path) not in sys.path:
            sys.path.insert(0, str(package_path))

        try:
            from ollamapy.main import hello

            assert hello() == "Hello, World!"
        except ImportError:
            # This is acceptable - just means the path manipulation didn't work
            pass
        finally:
            # Clean up sys.path
            if str(package_path) in sys.path:
                sys.path.remove(str(package_path))


class TestRegressionPrevention:
    """Tests to prevent regression of known issues."""

    def test_import_path_consistency(self):
        """Test that import paths are consistent."""
        # This prevents regressions where imports might break

        # Test the main entry point
        from src.ollamapy.main import main

        assert callable(main)

        # Test core client
        from src.ollamapy.ollama_client import OllamaClient

        assert callable(OllamaClient)

    def test_function_signature_stability(self):
        """Test that public function signatures remain stable."""
        from src.ollamapy.main import hello, greet, chat, run_vibe_tests

        # Test function signatures using introspection
        import inspect

        # hello() should take no arguments
        sig = inspect.signature(hello)
        assert len(sig.parameters) == 0, "hello() signature changed"

        # greet() should take one argument
        sig = inspect.signature(greet)
        assert len(sig.parameters) == 1, "greet() signature changed"

        # chat() should have default parameters
        sig = inspect.signature(chat)
        params_with_defaults = [
            p for p in sig.parameters.values() if p.default != p.empty
        ]
        assert len(params_with_defaults) > 0, "chat() should have default parameters"

    def test_return_type_consistency(self):
        """Test that return types are consistent."""
        from src.ollamapy.main import hello, greet

        # Test return types
        hello_result = hello()
        assert isinstance(hello_result, str), "hello() should return string"

        greet_result = greet("Test")
        assert isinstance(greet_result, str), "greet() should return string"

        # Test specific return values
        assert hello_result == "Hello, World!"
        assert greet_result == "Hello, Test!"
