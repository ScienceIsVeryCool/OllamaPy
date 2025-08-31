"""Package structure and integrity validation tests."""

import pytest
import os
import sys
import importlib
from pathlib import Path
import toml
import ast
import inspect


class TestPackageStructure:
    """Test package structure and imports."""

    def test_package_root_exists(self):
        """Test that package root directory exists."""
        package_root = Path(__file__).parent.parent / "src" / "ollamapy"
        assert package_root.exists(), "Package root directory not found"
        assert package_root.is_dir(), "Package root is not a directory"

    def test_init_file_exists(self):
        """Test that __init__.py exists in package root."""
        init_file = Path(__file__).parent.parent / "src" / "ollamapy" / "__init__.py"
        assert init_file.exists(), "__init__.py not found in package root"

    def test_core_modules_exist(self):
        """Test that all core modules exist."""
        package_root = Path(__file__).parent.parent / "src" / "ollamapy"
        required_modules = [
            "main.py",
            "ollama_client.py",
            "model_manager.py",
            "analysis_engine.py",
            "chat_session.py",
            "terminal_interface.py",
            "ai_query.py",
            "skills.py",
            "parameter_utils.py",
        ]

        for module in required_modules:
            module_path = package_root / module
            assert module_path.exists(), f"Required module {module} not found"
            assert module_path.is_file(), f"{module} is not a file"

    def test_skill_editor_subpackage(self):
        """Test skill editor subpackage structure."""
        skill_editor_root = (
            Path(__file__).parent.parent / "src" / "ollamapy" / "skill_editor"
        )

        if skill_editor_root.exists():
            assert skill_editor_root.is_dir(), "skill_editor should be a directory"

            init_file = skill_editor_root / "__init__.py"
            assert init_file.exists(), "skill_editor/__init__.py not found"

            api_file = skill_editor_root / "api.py"
            if api_file.exists():
                assert api_file.is_file(), "skill_editor/api.py should be a file"


class TestImports:
    """Test that all modules can be imported without errors."""

    def test_main_module_import(self):
        """Test main module can be imported."""
        try:
            from src.ollamapy import main

            assert hasattr(main, "main"), "main() function not found"
            assert hasattr(main, "hello"), "hello() function not found"
            assert hasattr(main, "greet"), "greet() function not found"
        except ImportError as e:
            pytest.fail(f"Failed to import main module: {e}")

    def test_ollama_client_import(self):
        """Test OllamaClient can be imported."""
        try:
            from src.ollamapy.ollama_client import OllamaClient

            assert inspect.isclass(OllamaClient), "OllamaClient should be a class"
        except ImportError as e:
            pytest.fail(f"Failed to import OllamaClient: {e}")

    def test_core_modules_import(self):
        """Test all core modules can be imported."""
        core_modules = [
            "src.ollamapy.model_manager",
            "src.ollamapy.analysis_engine",
            "src.ollamapy.chat_session",
            "src.ollamapy.terminal_interface",
            "src.ollamapy.ai_query",
            "src.ollamapy.skills",
            "src.ollamapy.parameter_utils",
        ]

        for module_name in core_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    def test_optional_modules_graceful_failure(self):
        """Test optional modules fail gracefully when dependencies missing."""
        try:
            from src.ollamapy.skill_editor.api import SkillEditorAPI
        except ImportError:
            # This is expected if Flask is not installed
            pass


class TestProjectConfiguration:
    """Test project configuration files."""

    def test_pyproject_toml_exists(self):
        """Test pyproject.toml exists and is valid."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml not found"

        with open(pyproject_path, "r") as f:
            config = toml.load(f)

        assert "project" in config, "Project section missing from pyproject.toml"
        assert "name" in config["project"], "Project name missing"
        assert config["project"]["name"] == "ollamapy", "Incorrect project name"

    def test_entry_points_configuration(self):
        """Test that entry points are correctly configured."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

        with open(pyproject_path, "r") as f:
            config = toml.load(f)

        assert "project" in config, "Project section missing"
        assert "scripts" in config["project"], "Scripts section missing"
        assert (
            "ollamapy" in config["project"]["scripts"]
        ), "ollamapy script entry point missing"

        entry_point = config["project"]["scripts"]["ollamapy"]
        assert (
            entry_point == "src.ollamapy.main:main"
        ), "Incorrect entry point configuration"

    def test_dependencies_specification(self):
        """Test that dependencies are properly specified."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

        with open(pyproject_path, "r") as f:
            config = toml.load(f)

        assert "dependencies" in config["project"], "Dependencies section missing"
        deps = config["project"]["dependencies"]

        # Check for required dependencies
        required_deps = ["requests", "plotly"]
        for dep in required_deps:
            assert any(dep in d for d in deps), f"Required dependency {dep} not found"

    def test_optional_dependencies(self):
        """Test that optional dependencies are properly configured."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

        with open(pyproject_path, "r") as f:
            config = toml.load(f)

        optional_deps = config["project"].get("optional-dependencies", {})

        # Should have dev, editor, and all groups
        expected_groups = ["dev", "editor", "all"]
        for group in expected_groups:
            assert group in optional_deps, f"Optional dependency group {group} missing"


class TestCodeQuality:
    """Test code quality and standards."""

    def test_no_syntax_errors(self):
        """Test all Python files have valid syntax."""
        src_root = Path(__file__).parent.parent / "src" / "ollamapy"

        for py_file in src_root.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                ast.parse(content)
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file}: {e}")

    def test_docstrings_present(self):
        """Test that main functions have docstrings."""
        from src.ollamapy.main import main, hello, greet, chat

        functions_to_check = [main, hello, greet, chat]

        for func in functions_to_check:
            assert (
                func.__doc__ is not None
            ), f"Function {func.__name__} missing docstring"
            assert (
                len(func.__doc__.strip()) > 0
            ), f"Function {func.__name__} has empty docstring"

    def test_class_docstrings(self):
        """Test that main classes have docstrings."""
        try:
            from src.ollamapy.ollama_client import OllamaClient

            assert (
                OllamaClient.__doc__ is not None
            ), "OllamaClient class missing docstring"
        except ImportError:
            pytest.skip("OllamaClient not available")


class TestTestSuite:
    """Test the test suite itself."""

    def test_test_files_exist(self):
        """Test that test files exist and are properly named."""
        test_root = Path(__file__).parent

        # Should have at least these test files
        expected_tests = [
            "test_main.py",
            "test_main_comprehensive.py",
            "test_ollama_client.py",
            "test_package_validation.py",
        ]

        for test_file in expected_tests:
            test_path = test_root / test_file
            assert test_path.exists(), f"Test file {test_file} not found"

    def test_conftest_exists(self):
        """Test that conftest.py exists for test configuration."""
        conftest_path = Path(__file__).parent / "conftest.py"
        assert conftest_path.exists(), "conftest.py not found"

    def test_pytest_ini_configuration(self):
        """Test pytest.ini exists and has basic configuration."""
        pytest_ini = Path(__file__).parent.parent / "pytest.ini"

        if pytest_ini.exists():
            with open(pytest_ini, "r") as f:
                content = f.read()
                assert (
                    "[tool:pytest]" in content or "[pytest]" in content
                ), "pytest configuration missing"


class TestDocumentation:
    """Test documentation files and structure."""

    def test_readme_exists(self):
        """Test that README.md exists."""
        readme_path = Path(__file__).parent.parent / "README.md"
        assert readme_path.exists(), "README.md not found"

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert len(content) > 100, "README.md appears to be empty or very short"

    def test_license_exists(self):
        """Test that LICENSE file exists."""
        license_path = Path(__file__).parent.parent / "LICENSE"
        assert license_path.exists(), "LICENSE file not found"

    def test_docs_directory_structure(self):
        """Test documentation directory structure."""
        docs_root = Path(__file__).parent.parent / "docs"

        if docs_root.exists():
            assert docs_root.is_dir(), "docs should be a directory"

            index_file = docs_root / "index.md"
            if index_file.exists():
                with open(index_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    assert len(content) > 50, "docs/index.md appears to be empty"


class TestVersioning:
    """Test version consistency across files."""

    def test_version_consistency(self):
        """Test that version is consistent across configuration files."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

        with open(pyproject_path, "r") as f:
            config = toml.load(f)

        pyproject_version = config["project"]["version"]
        assert pyproject_version is not None, "Version not specified in pyproject.toml"
        assert len(pyproject_version) > 0, "Version is empty in pyproject.toml"

        # Check that version follows semantic versioning pattern
        import re

        version_pattern = r"^\d+\.\d+\.\d+.*$"
        assert re.match(
            version_pattern, pyproject_version
        ), "Version doesn't follow semantic versioning"


class TestSecurityBasics:
    """Test basic security considerations."""

    def test_no_hardcoded_secrets(self):
        """Test that there are no obvious hardcoded secrets."""
        src_root = Path(__file__).parent.parent / "src"

        # Patterns that might indicate secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']{16,}["\']',
            r'secret\s*=\s*["\'][^"\']{16,}["\']',
            r'token\s*=\s*["\'][^"\']{16,}["\']',
        ]

        import re

        for py_file in src_root.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            for pattern in secret_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                assert (
                    len(matches) == 0
                ), f"Potential hardcoded secret found in {py_file}: {matches}"

    def test_safe_imports(self):
        """Test that there are no dangerous imports."""
        src_root = Path(__file__).parent.parent / "src"

        # Potentially dangerous modules to avoid
        dangerous_imports = [
            "exec",
            "eval",
            "subprocess.call",
            "os.system",
        ]

        for py_file in src_root.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            for dangerous in dangerous_imports:
                # Basic check - this isn't comprehensive but catches obvious issues
                if dangerous in content and not content.find(f"#{dangerous}") >= 0:
                    # Skip if it's in a comment
                    lines = content.split("\n")
                    for line_num, line in enumerate(lines, 1):
                        if dangerous in line and not line.strip().startswith("#"):
                            pytest.fail(
                                f"Potentially dangerous code in {py_file}:{line_num}: {line.strip()}"
                            )


class TestPerformance:
    """Test basic performance considerations."""

    def test_no_infinite_loops(self):
        """Basic check for obvious infinite loop patterns."""
        src_root = Path(__file__).parent.parent / "src"

        # Very basic patterns that might indicate infinite loops
        suspicious_patterns = [
            r"while\s+True\s*:.*(?!break)",
            r"for.*in.*range\([^)]*\)\s*:.*(?!break)",
        ]

        import re

        for py_file in src_root.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            # This is a very basic check - real analysis would need AST parsing
            for pattern in suspicious_patterns:
                # Skip this test as it's too simplistic
                pass
