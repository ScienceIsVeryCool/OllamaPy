"""Integration tests for complete skill lifecycle."""

import pytest
import tempfile
import json
from pathlib import Path

from src.ollamapy.skills import SkillRegistry, Skill

try:
    from src.ollamapy.skill_editor.api import SkillEditorAPI
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class TestSkillLifecycle:
    """Test complete skill lifecycle from creation to execution."""
    
    def test_skill_creation_registration_execution(self):
        """Test creating, registering, and executing a custom skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize registry
            registry = SkillRegistry(skills_directory=tmpdir)
            initial_count = len(registry.skills)
            
            # Create a custom skill
            custom_skill = Skill(
                name="lifecycle_test",
                description="A skill for testing the complete lifecycle",
                vibe_test_phrases=[
                    "test lifecycle",
                    "run lifecycle test",
                    "lifecycle check"
                ],
                parameters={
                    "message": {
                        "type": "string",
                        "required": False,
                        "description": "Optional message to display"
                    }
                },
                function_code="""
def execute(message=None):
    if message:
        log(f'[LifecycleTest] Custom message: {message}')
    else:
        log('[LifecycleTest] Default lifecycle test executed successfully!')
    
    # Simulate some work
    result = "Lifecycle test completed"
    log(f'[LifecycleTest] Result: {result}')
""",
                verified=False,
                role="general"
            )
            
            # Register the skill
            success = registry.register_skill(custom_skill)
            assert success is True
            assert len(registry.skills) == initial_count + 1
            assert "lifecycle_test" in registry.skills
            assert "lifecycle_test" in registry.compiled_functions
            
            # Verify skill file was created
            skill_file = Path(tmpdir) / "lifecycle_test.json"
            assert skill_file.exists()
            
            # Verify file contents
            with open(skill_file, 'r') as f:
                saved_skill = json.load(f)
            assert saved_skill["name"] == "lifecycle_test"
            assert saved_skill["verified"] is False
            
            # Execute the skill without parameters
            registry.clear_logs()
            registry.execute_skill("lifecycle_test")
            
            logs = registry.get_logs()
            assert len(logs) >= 2  # Should have at least 2 log messages
            assert any("Default lifecycle test" in log for log in logs)
            assert any("Result:" in log for log in logs)
            
            # Execute the skill with parameters
            registry.clear_logs()
            registry.execute_skill("lifecycle_test", {"message": "Custom test message"})
            
            logs = registry.get_logs()
            assert any("Custom test message" in log for log in logs)
            
            # Verify execution count was updated
            updated_skill = registry.skills["lifecycle_test"]
            assert updated_skill.execution_count == 2
    
    def test_skill_persistence_across_registry_instances(self):
        """Test that skills persist across different registry instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create skill in first registry
            registry1 = SkillRegistry(skills_directory=tmpdir)
            
            persistent_skill = Skill(
                name="persistent_skill",
                description="A skill that should persist",
                vibe_test_phrases=["persistent test"],
                parameters={},
                function_code="def execute():\n    log('[PersistentSkill] I persist!')",
                verified=False
            )
            
            registry1.register_skill(persistent_skill)
            initial_skills = list(registry1.skills.keys())
            
            # Create new registry from same directory
            registry2 = SkillRegistry(skills_directory=tmpdir)
            
            # Should have same skills
            assert len(registry2.skills) == len(registry1.skills)
            assert "persistent_skill" in registry2.skills
            assert set(registry2.skills.keys()) == set(initial_skills)
            
            # Should be able to execute the persisted skill
            registry2.clear_logs()
            registry2.execute_skill("persistent_skill")
            
            logs = registry2.get_logs()
            assert any("I persist!" in log for log in logs)
    
    def test_skill_modification_workflow(self):
        """Test modifying an existing skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(skills_directory=tmpdir)
            
            # Create initial skill
            original_skill = Skill(
                name="modifiable_skill",
                description="Original description",
                vibe_test_phrases=["original test"],
                parameters={},
                function_code="def execute():\n    log('[ModifiableSkill] Original version')",
                verified=False
            )
            
            registry.register_skill(original_skill)
            
            # Execute original version
            registry.clear_logs()
            registry.execute_skill("modifiable_skill")
            logs = registry.get_logs()
            assert any("Original version" in log for log in logs)
            
            # Modify the skill
            modified_skill = Skill(
                name="modifiable_skill",
                description="Modified description",
                vibe_test_phrases=["modified test", "updated test"],
                parameters={
                    "version": {
                        "type": "string",
                        "required": False,
                        "description": "Version identifier"
                    }
                },
                function_code="""
def execute(version=None):
    if version:
        log(f'[ModifiableSkill] Modified version {version}')
    else:
        log('[ModifiableSkill] Modified version (no version specified)')
""",
                verified=False,
                execution_count=original_skill.execution_count,
                created_at=original_skill.created_at
            )
            
            # Re-register (update) the skill
            success = registry.register_skill(modified_skill)
            assert success is True
            
            # Verify modification
            updated_skill = registry.skills["modifiable_skill"]
            assert updated_skill.description == "Modified description"
            assert len(updated_skill.vibe_test_phrases) == 2
            assert "version" in updated_skill.parameters
            
            # Execute modified version
            registry.clear_logs()
            registry.execute_skill("modifiable_skill", {"version": "2.0"})
            logs = registry.get_logs()
            assert any("Modified version 2.0" in log for log in logs)
    
    def test_skill_error_handling(self):
        """Test error handling in skill execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(skills_directory=tmpdir)
            
            # Create skill with intentional error
            error_skill = Skill(
                name="error_skill",
                description="A skill that will cause an error",
                vibe_test_phrases=["error test"],
                parameters={
                    "should_error": {
                        "type": "boolean",
                        "required": False,
                        "description": "Whether to trigger an error"
                    }
                },
                function_code="""
def execute(should_error=False):
    log('[ErrorSkill] Starting execution')
    
    if should_error:
        raise ValueError("Intentional error for testing")
    
    log('[ErrorSkill] Execution completed successfully')
""",
                verified=False
            )
            
            registry.register_skill(error_skill)
            
            # Execute without error
            registry.clear_logs()
            registry.execute_skill("error_skill", {"should_error": False})
            logs = registry.get_logs()
            assert any("completed successfully" in log for log in logs)
            assert not any("Error executing" in log for log in logs)
            
            # Execute with error
            registry.clear_logs()
            registry.execute_skill("error_skill", {"should_error": True})
            logs = registry.get_logs()
            assert any("Error executing" in log for log in logs)
            assert any("Intentional error" in log for log in logs)


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestSkillEditorIntegration:
    """Integration tests for the skill editor with real skills."""
    
    def test_end_to_end_skill_creation_via_api(self):
        """Test creating a skill via API and using it in registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create API instance
            api = SkillEditorAPI(skills_directory=tmpdir, port=5555)
            client = api.app.test_client()
            
            # Create skill via API
            skill_data = {
                "name": "api_created_skill",
                "description": "A skill created through the API for integration testing",
                "vibe_test_phrases": [
                    "api test",
                    "integration test",
                    "test api creation"
                ],
                "parameters": {
                    "test_param": {
                        "type": "string",
                        "required": True,
                        "description": "A parameter for testing"
                    }
                },
                "function_code": """
def execute(test_param):
    log(f'[APICreatedSkill] Received parameter: {test_param}')
    
    # Process the parameter
    result = f"Processed: {test_param.upper()}"
    log(f'[APICreatedSkill] Result: {result}')
    
    return result
""",
                "role": "general"
            }
            
            # POST to create skill
            response = client.post('/api/skills',
                                 json=skill_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # Verify skill exists in registry
            registry = api.registry
            assert "api_created_skill" in registry.skills
            assert "api_created_skill" in registry.compiled_functions
            
            # Execute the skill
            registry.clear_logs()
            registry.execute_skill("api_created_skill", {"test_param": "integration"})
            
            logs = registry.get_logs()
            assert any("Received parameter: integration" in log for log in logs)
            assert any("Result: Processed: INTEGRATION" in log for log in logs)
            
            # Test skill via API
            test_data = {
                "skill_data": skill_data,
                "test_input": {"test_param": "api_test"}
            }
            
            response = client.post('/api/skills/test',
                                 json=test_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['execution_successful'] is True
            assert any("api_test" in output for output in data['output'])
    
    def test_skill_validation_integration(self):
        """Test skill validation with real validation scenarios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            api = SkillEditorAPI(skills_directory=tmpdir, port=5555)
            client = api.app.test_client()
            
            # Test valid skill
            valid_skill = {
                "name": "validation_test_good",
                "description": "A properly formatted skill that should pass validation",
                "function_code": """
def execute(name=None):
    if name:
        log(f'[ValidationTest] Hello, {name}!')
    else:
        log('[ValidationTest] Hello, World!')
""",
                "parameters": {
                    "name": {
                        "type": "string",
                        "required": False,
                        "description": "Name to greet"
                    }
                },
                "role": "general"
            }
            
            response = client.post('/api/skills/validate',
                                 json=valid_skill,
                                 content_type='application/json')
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['is_valid'] is True
            assert len(data['errors']) == 0
            
            # Test invalid skill (multiple issues)
            invalid_skill = {
                "name": "invalid-skill-name",  # Invalid identifier
                "description": "Bad",  # Too short
                "function_code": "def wrong_name():\n    pass",  # Wrong function name
                "parameters": {
                    "bad-param": {  # Invalid parameter name
                        "type": "invalid_type",  # Invalid type
                        "required": "not_boolean"  # Wrong type for required
                    }
                },
                "role": "invalid_role"  # Invalid role
            }
            
            response = client.post('/api/skills/validate',
                                 json=invalid_skill,
                                 content_type='application/json')
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['is_valid'] is False
            assert len(data['errors']) >= 4  # Should catch multiple errors
            
            # Verify specific error types
            errors = data['errors']
            assert any("identifier" in error.lower() for error in errors)  # Name
            assert any("execute" in error.lower() for error in errors)     # Function name
            assert any("invalid type" in error.lower() for error in errors)  # Parameter type
            assert any("invalid role" in error.lower() for error in errors)  # Role