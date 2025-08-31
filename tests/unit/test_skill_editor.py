"""Unit tests for the skill editor API."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

try:
    from src.ollamapy.skill_editor.api import SkillEditorAPI
    from src.ollamapy.skill_editor.validator import SkillValidator, ValidationResult

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not FLASK_AVAILABLE, reason="Flask dependencies not available"
)


class TestSkillValidator:
    """Test the skill validator."""

    def test_validator_initialization(self):
        """Test validator creates successfully."""
        validator = SkillValidator()
        assert validator is not None
        assert len(validator.required_fields) > 0

    def test_valid_skill_validation(self):
        """Test validation of a valid skill."""
        validator = SkillValidator()

        skill_data = {
            "name": "valid_skill",
            "description": "A valid test skill for validation",
            "function_code": "def execute(param1=None):\n    log('[ValidSkill] Working!')",
            "vibe_test_phrases": ["test phrase", "another phrase"],
            "parameters": {
                "param1": {
                    "type": "string",
                    "required": True,
                    "description": "A test parameter",
                }
            },
            "role": "general",
        }

        result = validator.validate_skill_data(skill_data)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_invalid_skill_name(self):
        """Test validation of invalid skill names."""
        validator = SkillValidator()

        skill_data = {
            "name": "invalid-name-with-hyphens",
            "description": "Test skill",
            "function_code": "def execute(): pass",
        }

        result = validator.validate_skill_data(skill_data)
        assert result.is_valid is False
        assert any("identifier" in error.lower() for error in result.errors)

    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        validator = SkillValidator()

        skill_data = {
            "name": "test_skill"
            # Missing description and function_code
        }

        result = validator.validate_skill_data(skill_data)
        assert result.is_valid is False
        assert any("description" in error for error in result.errors)
        assert any("function_code" in error for error in result.errors)

    def test_invalid_python_syntax(self):
        """Test validation of invalid Python syntax."""
        validator = SkillValidator()

        skill_data = {
            "name": "syntax_error_skill",
            "description": "Test skill with syntax error",
            "function_code": "def execute(\n    print('broken')",  # Missing closing parenthesis
        }

        result = validator.validate_skill_data(skill_data)
        assert result.is_valid is False
        assert any("syntax" in error.lower() for error in result.errors)

    def test_missing_execute_function(self):
        """Test validation when execute function is missing."""
        validator = SkillValidator()

        skill_data = {
            "name": "no_execute_skill",
            "description": "Test skill without execute function",
            "function_code": "def other_function(): pass",  # Wrong function name
        }

        result = validator.validate_skill_data(skill_data)
        assert result.is_valid is False
        assert any("execute" in error.lower() for error in result.errors)

    def test_invalid_parameter_types(self):
        """Test validation of invalid parameter types."""
        validator = SkillValidator()

        skill_data = {
            "name": "invalid_params_skill",
            "description": "Test skill with invalid parameters",
            "function_code": "def execute(): pass",
            "parameters": {
                "bad_param": {
                    "type": "invalid_type",  # Not in valid types
                    "required": True,
                }
            },
        }

        result = validator.validate_skill_data(skill_data)
        assert result.is_valid is False
        assert any("invalid type" in error.lower() for error in result.errors)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestSkillEditorAPI:
    """Test the Skill Editor API."""

    @pytest.fixture
    def temp_skills_dir(self):
        """Create temporary skills directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def app(self, temp_skills_dir):
        """Create test Flask app."""
        api = SkillEditorAPI(skills_directory=temp_skills_dir, port=5555)
        api.app.config["TESTING"] = True
        return api.app.test_client()

    def test_api_initialization(self, temp_skills_dir):
        """Test API initializes correctly."""
        api = SkillEditorAPI(skills_directory=temp_skills_dir, port=5555)
        assert api.registry is not None
        assert api.validator is not None

    def test_get_all_skills_endpoint(self, app):
        """Test the GET /api/skills endpoint."""
        response = app.get("/api/skills")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "skills" in data
        assert len(data["skills"]) > 0  # Should have built-in skills

    def test_get_specific_skill_endpoint(self, app):
        """Test the GET /api/skills/<name> endpoint."""
        # Test getting a built-in skill
        response = app.get("/api/skills/fear")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["skill"]["name"] == "fear"
        assert data["skill"]["verified"] is True

    def test_get_nonexistent_skill(self, app):
        """Test getting a skill that doesn't exist."""
        response = app.get("/api/skills/nonexistent_skill")
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data["success"] is False

    def test_create_new_skill_endpoint(self, app):
        """Test the POST /api/skills endpoint."""
        skill_data = {
            "name": "test_api_skill",
            "description": "A skill created via API test",
            "function_code": "def execute():\n    log('[TestAPISkill] Working!')",
            "vibe_test_phrases": ["test api"],
            "parameters": {},
            "role": "general",
        }

        response = app.post(
            "/api/skills", json=skill_data, content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

        # Verify skill was created
        response = app.get("/api/skills/test_api_skill")
        assert response.status_code == 200

    def test_create_duplicate_skill(self, app):
        """Test creating a skill with a name that already exists."""
        # Try to create skill with built-in name
        skill_data = {
            "name": "fear",  # Built-in skill name
            "description": "Duplicate skill",
            "function_code": "def execute(): pass",
        }

        response = app.post(
            "/api/skills", json=skill_data, content_type="application/json"
        )

        assert response.status_code == 409  # Conflict
        data = json.loads(response.data)
        assert data["success"] is False

    def test_update_custom_skill_endpoint(self, app):
        """Test the PUT /api/skills/<name> endpoint."""
        # First create a skill
        skill_data = {
            "name": "update_test_skill",
            "description": "Original description",
            "function_code": "def execute():\n    log('[UpdateTest] Original')",
            "vibe_test_phrases": ["update test"],
            "parameters": {},
            "role": "general",
        }

        app.post("/api/skills", json=skill_data, content_type="application/json")

        # Now update it
        updated_data = skill_data.copy()
        updated_data["description"] = "Updated description"
        updated_data["function_code"] = (
            "def execute():\n    log('[UpdateTest] Updated')"
        )

        response = app.put(
            "/api/skills/update_test_skill",
            json=updated_data,
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

        # Verify update
        response = app.get("/api/skills/update_test_skill")
        skill = json.loads(response.data)["skill"]
        assert skill["description"] == "Updated description"

    def test_cannot_update_builtin_skill(self, app):
        """Test that built-in skills cannot be updated."""
        skill_data = {
            "name": "fear",
            "description": "Modified built-in",
            "function_code": "def execute(): pass",
            "verified": True,
        }

        response = app.put(
            "/api/skills/fear", json=skill_data, content_type="application/json"
        )

        assert response.status_code == 403  # Forbidden
        data = json.loads(response.data)
        assert data["success"] is False
        assert "built-in" in data["error"].lower()

    def test_delete_custom_skill_endpoint(self, app):
        """Test the DELETE /api/skills/<name> endpoint."""
        # Create a skill to delete
        skill_data = {
            "name": "delete_test_skill",
            "description": "A skill to be deleted",
            "function_code": "def execute(): pass",
            "parameters": {},
            "role": "general",
        }

        app.post("/api/skills", json=skill_data, content_type="application/json")

        # Delete it
        response = app.delete("/api/skills/delete_test_skill")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True

        # Verify deletion
        response = app.get("/api/skills/delete_test_skill")
        assert response.status_code == 404

    def test_cannot_delete_builtin_skill(self, app):
        """Test that built-in skills cannot be deleted."""
        response = app.delete("/api/skills/fear")

        assert response.status_code == 403  # Forbidden
        data = json.loads(response.data)
        assert data["success"] is False
        assert "built-in" in data["error"].lower()

    def test_validate_skill_endpoint(self, app):
        """Test the POST /api/skills/validate endpoint."""
        valid_skill = {
            "name": "valid_test",
            "description": "A valid skill for testing validation",
            "function_code": "def execute():\n    log('[ValidTest] OK')",
        }

        response = app.post(
            "/api/skills/validate", json=valid_skill, content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["is_valid"] is True

        # Test invalid skill
        invalid_skill = {
            "name": "invalid-name",  # Invalid identifier
            "description": "Invalid",
            "function_code": "def execute(\n    pass",  # Syntax error
        }

        response = app.post(
            "/api/skills/validate", json=invalid_skill, content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["is_valid"] is False
        assert len(data["errors"]) > 0

    def test_test_skill_endpoint(self, app):
        """Test the POST /api/skills/test endpoint."""
        skill_data = {
            "name": "test_execution",
            "description": "A skill for testing execution",
            "function_code": "def execute():\n    log('[TestExecution] Success!')",
            "vibe_test_phrases": ["test execution"],
            "parameters": {},
        }

        request_data = {"skill_data": skill_data, "test_input": {}}

        response = app.post(
            "/api/skills/test", json=request_data, content_type="application/json"
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["execution_successful"] is True
        assert len(data["output"]) > 0

    def test_main_interface_endpoints(self, app):
        """Test the main web interface endpoints."""
        # Test index page
        response = app.get("/")
        assert response.status_code == 200
        assert b"Skill Editor" in response.data

        # Test new skill page
        response = app.get("/new-skill")
        assert response.status_code == 200
        assert b"Create New Skill" in response.data

        # Test skill editor page (for existing skill)
        response = app.get("/skill/fear")
        assert response.status_code == 200
        assert b"Edit Skill: fear" in response.data
