"""Unit tests for the skills system."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.ollamapy.skills import Skill, SkillRegistry


class TestSkill:
    """Test the Skill data class."""

    def test_skill_creation(self):
        """Test basic skill creation."""
        skill = Skill(
            name="test_skill",
            description="A test skill",
            vibe_test_phrases=["test phrase"],
            parameters={"param": {"type": "string", "required": True}},
            function_code="def execute(): pass",
        )

        assert skill.name == "test_skill"
        assert skill.description == "A test skill"
        assert skill.verified is False
        assert skill.scope == "local"
        assert skill.role == "general"

    def test_skill_to_dict(self):
        """Test skill serialization."""
        skill = Skill(
            name="test_skill",
            description="A test skill",
            vibe_test_phrases=["test phrase"],
            parameters={},
            function_code="def execute(): pass",
        )

        skill_dict = skill.to_dict()
        assert isinstance(skill_dict, dict)
        assert skill_dict["name"] == "test_skill"
        assert "created_at" in skill_dict
        assert "last_modified" in skill_dict

    def test_skill_from_dict(self):
        """Test skill deserialization."""
        skill_data = {
            "name": "test_skill",
            "description": "A test skill",
            "vibe_test_phrases": ["test phrase"],
            "parameters": {},
            "function_code": "def execute(): pass",
            "verified": False,
            "scope": "local",
            "role": "general",
            "created_at": "2023-01-01T00:00:00",
            "last_modified": "2023-01-01T00:00:00",
            "execution_count": 0,
            "success_rate": 100.0,
            "average_execution_time": 0.0,
            "tags": [],
        }

        skill = Skill.from_dict(skill_data)
        assert skill.name == "test_skill"
        assert skill.verified is False


class TestSkillRegistry:
    """Test the SkillRegistry class."""

    def test_registry_initialization(self):
        """Test registry creates with built-in skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(skills_directory=tmpdir)

            # Should have built-in skills
            assert len(registry.skills) > 0

            # Should have fear skill
            assert "fear" in registry.skills
            assert registry.skills["fear"].verified is True

    def test_register_custom_skill(self):
        """Test registering a custom skill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(skills_directory=tmpdir)

            skill = Skill(
                name="custom_test",
                description="A custom test skill",
                vibe_test_phrases=["test custom"],
                parameters={},
                function_code="""
def execute():
    log("[CustomTest] Hello from custom skill!")
""",
                verified=False,
            )

            success = registry.register_skill(skill)
            assert success is True
            assert "custom_test" in registry.skills
            assert "custom_test" in registry.compiled_functions

    def test_execute_skill(self):
        """Test skill execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(skills_directory=tmpdir)

            # Test built-in skill execution
            registry.clear_logs()
            registry.execute_skill("fear")

            logs = registry.get_logs()
            assert len(logs) > 0
            assert any("fear" in log.lower() for log in logs)

    def test_skill_compilation_error(self):
        """Test handling of skill compilation errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(skills_directory=tmpdir)

            # Create skill with invalid Python code
            bad_skill = Skill(
                name="bad_skill",
                description="A skill with bad code",
                vibe_test_phrases=["bad"],
                parameters={},
                function_code="def execute(\n    print('broken syntax')",
                verified=False,
            )

            success = registry.register_skill(bad_skill)
            assert success is False
            assert "bad_skill" not in registry.skills

    def test_get_skills_by_role(self):
        """Test filtering skills by role."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(skills_directory=tmpdir)

            math_skills = registry.get_skills_by_role("mathematics")
            assert len(math_skills) > 0

            # All returned skills should have mathematics role
            for skill in math_skills.values():
                assert skill.role == "mathematics"

    def test_get_verified_skills(self):
        """Test filtering verified skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = SkillRegistry(skills_directory=tmpdir)

            verified_skills = registry.get_verified_skills()
            assert len(verified_skills) > 0

            # All returned skills should be verified
            for skill in verified_skills.values():
                assert skill.verified is True

    def test_skill_persistence(self):
        """Test that skills are saved to and loaded from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first registry and add custom skill
            registry1 = SkillRegistry(skills_directory=tmpdir)

            custom_skill = Skill(
                name="persistent_test",
                description="A persistent test skill",
                vibe_test_phrases=["persistent"],
                parameters={},
                function_code="def execute(): log('[PersistentTest] Working!')",
                verified=False,
            )

            registry1.register_skill(custom_skill)

            # Create second registry from same directory
            registry2 = SkillRegistry(skills_directory=tmpdir)

            # Should have the custom skill
            assert "persistent_test" in registry2.skills
            assert (
                registry2.skills["persistent_test"].description
                == "A persistent test skill"
            )

    @patch("builtins.print")
    def test_skill_loading_error_handling(self, mock_print):
        """Test handling of corrupted skill files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create corrupted skill file
            corrupted_file = Path(tmpdir) / "corrupted.json"
            with open(corrupted_file, "w") as f:
                f.write("{ invalid json")

            # Should handle the error gracefully
            registry = SkillRegistry(skills_directory=tmpdir)

            # Should still have built-in skills
            assert len(registry.skills) > 0

            # Should have printed error
            mock_print.assert_called()
            error_calls = [
                call
                for call in mock_print.call_args_list
                if "Error loading skill" in str(call)
            ]
            assert len(error_calls) > 0
