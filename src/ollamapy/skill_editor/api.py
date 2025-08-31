"""Flask API for interactive skill editing."""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from ..skills import SkillRegistry, Skill
from .validator import SkillValidator


class SkillEditorAPI:
    """Flask-based API for skill editing operations."""

    def __init__(self, skills_directory: Optional[str] = None, port: int = 5000):
        """Initialize the skill editor API.

        Args:
            skills_directory: Directory containing skill JSON files
            port: Port to run the Flask server on
        """
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend requests

        # Initialize skill registry
        self.registry = SkillRegistry(skills_directory)
        self.validator = SkillValidator()
        self.port = port

        # Set up routes
        self._setup_routes()

    def _setup_routes(self):
        """Set up all API routes."""

        @self.app.route("/api/skills", methods=["GET"])
        def get_all_skills():
            """Get all skills."""
            try:
                skills = self.registry.get_all_skills()
                skill_data = {}
                for name, skill in skills.items():
                    skill_data[name] = skill.to_dict()
                return jsonify({"success": True, "skills": skill_data})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/skills/<skill_name>", methods=["GET"])
        def get_skill(skill_name):
            """Get a specific skill."""
            try:
                if skill_name not in self.registry.skills:
                    return jsonify({"success": False, "error": "Skill not found"}), 404

                skill = self.registry.skills[skill_name]
                return jsonify({"success": True, "skill": skill.to_dict()})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/skills/<skill_name>", methods=["PUT"])
        def update_skill(skill_name):
            """Update an existing skill."""
            try:
                skill_data = request.json
                if not skill_data:
                    return jsonify({"success": False, "error": "No data provided"}), 400

                # Check if skill exists
                if skill_name not in self.registry.skills:
                    return jsonify({"success": False, "error": "Skill not found"}), 404

                existing_skill = self.registry.skills[skill_name]

                # Protect built-in skills
                if existing_skill.verified:
                    return (
                        jsonify(
                            {"success": False, "error": "Cannot modify built-in skill"}
                        ),
                        403,
                    )

                # Validate the skill data
                validation_result = self.validator.validate_skill_data(skill_data)
                if not validation_result.is_valid:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Validation failed",
                                "validation_errors": validation_result.errors,
                            }
                        ),
                        400,
                    )

                # Update timestamps
                skill_data["last_modified"] = datetime.now().isoformat()
                skill_data["name"] = skill_name  # Ensure name consistency

                # Create updated skill
                updated_skill = Skill.from_dict(skill_data)

                # Register the updated skill
                success = self.registry.register_skill(updated_skill)
                if not success:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Failed to register updated skill",
                            }
                        ),
                        500,
                    )

                return jsonify(
                    {"success": True, "message": "Skill updated successfully"}
                )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/skills/<skill_name>", methods=["DELETE"])
        def delete_skill(skill_name):
            """Delete a skill."""
            try:
                if skill_name not in self.registry.skills:
                    return jsonify({"success": False, "error": "Skill not found"}), 404

                skill = self.registry.skills[skill_name]

                # Protect built-in skills
                if skill.verified:
                    return (
                        jsonify(
                            {"success": False, "error": "Cannot delete built-in skill"}
                        ),
                        403,
                    )

                # Remove from registry
                del self.registry.skills[skill_name]
                if skill_name in self.registry.compiled_functions:
                    del self.registry.compiled_functions[skill_name]

                # Remove file
                skill_file = self.registry.skills_dir / f"{skill_name}.json"
                if skill_file.exists():
                    skill_file.unlink()

                return jsonify(
                    {"success": True, "message": "Skill deleted successfully"}
                )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/skills", methods=["POST"])
        def create_skill():
            """Create a new skill."""
            try:
                skill_data = request.json
                if not skill_data:
                    return jsonify({"success": False, "error": "No data provided"}), 400

                # Validate required fields
                required_fields = ["name", "description", "function_code"]
                for field in required_fields:
                    if field not in skill_data:
                        return (
                            jsonify(
                                {
                                    "success": False,
                                    "error": f"Missing required field: {field}",
                                }
                            ),
                            400,
                        )

                skill_name = skill_data["name"]

                # Check if skill already exists
                if skill_name in self.registry.skills:
                    return (
                        jsonify({"success": False, "error": "Skill already exists"}),
                        409,
                    )

                # Set defaults for optional fields
                skill_data.setdefault("vibe_test_phrases", [])
                skill_data.setdefault("parameters", {})
                skill_data.setdefault("verified", False)
                skill_data.setdefault("scope", "local")
                skill_data.setdefault("role", "general")
                skill_data.setdefault("tags", [])
                skill_data.setdefault("execution_count", 0)
                skill_data.setdefault("success_rate", 100.0)
                skill_data.setdefault("average_execution_time", 0.0)
                skill_data["created_at"] = datetime.now().isoformat()
                skill_data["last_modified"] = datetime.now().isoformat()

                # Validate the skill data
                validation_result = self.validator.validate_skill_data(skill_data)
                if not validation_result.is_valid:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Validation failed",
                                "validation_errors": validation_result.errors,
                            }
                        ),
                        400,
                    )

                # Create skill
                new_skill = Skill.from_dict(skill_data)

                # Register the skill
                success = self.registry.register_skill(new_skill)
                if not success:
                    return (
                        jsonify(
                            {"success": False, "error": "Failed to register skill"}
                        ),
                        500,
                    )

                return jsonify(
                    {
                        "success": True,
                        "message": "Skill created successfully",
                        "skill_name": skill_name,
                    }
                )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/skills/validate", methods=["POST"])
        def validate_skill():
            """Validate skill data without saving."""
            try:
                skill_data = request.json
                if not skill_data:
                    return jsonify({"success": False, "error": "No data provided"}), 400

                validation_result = self.validator.validate_skill_data(skill_data)

                return jsonify(
                    {
                        "success": True,
                        "is_valid": validation_result.is_valid,
                        "errors": validation_result.errors,
                        "warnings": validation_result.warnings,
                    }
                )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/skills/test", methods=["POST"])
        def test_skill():
            """Test a skill without saving it."""
            try:
                request_data = request.json
                skill_data = request_data.get("skill_data")
                test_input = request_data.get("test_input", {})

                if not skill_data:
                    return (
                        jsonify({"success": False, "error": "No skill data provided"}),
                        400,
                    )

                # Validate first
                validation_result = self.validator.validate_skill_data(skill_data)
                if not validation_result.is_valid:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Skill validation failed",
                                "validation_errors": validation_result.errors,
                            }
                        ),
                        400,
                    )

                # Create temporary skill instance
                temp_skill = Skill.from_dict(skill_data)

                # Clear logs before testing
                self.registry.clear_logs()

                # Try to compile and execute
                try:
                    func = self.registry._compile_skill_function(temp_skill)

                    # Execute with test input
                    if temp_skill.parameters and test_input:
                        func(**test_input)
                    else:
                        func()

                    # Get execution logs
                    logs = self.registry.get_logs()

                    return jsonify(
                        {
                            "success": True,
                            "execution_successful": True,
                            "output": logs,
                            "message": "Skill executed successfully",
                        }
                    )

                except Exception as exec_error:
                    return jsonify(
                        {
                            "success": True,
                            "execution_successful": False,
                            "error": str(exec_error),
                            "message": "Skill compilation or execution failed",
                        }
                    )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/skills/roles", methods=["GET"])
        def get_skill_roles():
            """Get all available skill roles."""
            roles = [
                "general",
                "text_processing",
                "mathematics",
                "data_analysis",
                "file_operations",
                "web_utilities",
                "time_date",
                "formatting",
                "validation",
                "emotional_response",
                "information",
                "advanced",
            ]
            return jsonify({"success": True, "roles": roles})

        @self.app.route("/api/skills/export", methods=["GET"])
        def export_skills():
            """Export all skills as JSON."""
            try:
                skills = self.registry.get_all_skills()
                skill_data = {}
                for name, skill in skills.items():
                    skill_data[name] = skill.to_dict()

                return jsonify(
                    {
                        "success": True,
                        "export_date": datetime.now().isoformat(),
                        "skills_count": len(skill_data),
                        "skills": skill_data,
                    }
                )
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/skills/import", methods=["POST"])
        def import_skills():
            """Import skills from JSON data."""
            try:
                import_data = request.json
                if not import_data or "skills" not in import_data:
                    return (
                        jsonify({"success": False, "error": "Invalid import data"}),
                        400,
                    )

                imported_count = 0
                errors = []

                for skill_name, skill_data in import_data["skills"].items():
                    try:
                        # Skip if skill already exists
                        if skill_name in self.registry.skills:
                            errors.append(
                                f"Skill '{skill_name}' already exists, skipped"
                            )
                            continue

                        # Validate skill data
                        validation_result = self.validator.validate_skill_data(
                            skill_data
                        )
                        if not validation_result.is_valid:
                            errors.append(
                                f"Skill '{skill_name}' validation failed: {validation_result.errors}"
                            )
                            continue

                        # Create and register skill
                        skill = Skill.from_dict(skill_data)
                        success = self.registry.register_skill(skill)
                        if success:
                            imported_count += 1
                        else:
                            errors.append(f"Failed to register skill '{skill_name}'")

                    except Exception as skill_error:
                        errors.append(
                            f"Error importing skill '{skill_name}': {str(skill_error)}"
                        )

                return jsonify(
                    {
                        "success": True,
                        "imported_count": imported_count,
                        "errors": errors,
                    }
                )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/")
        def serve_index():
            """Serve the main editor interface."""
            return self._get_editor_html()

        @self.app.route("/skill/<skill_name>")
        def serve_skill_editor(skill_name):
            """Serve the skill editor interface."""
            return self._get_skill_editor_html(skill_name)

        @self.app.route("/new-skill")
        def serve_new_skill():
            """Serve the new skill creation interface."""
            return self._get_new_skill_html()

    def _get_editor_html(self) -> str:
        """Generate the main editor interface HTML."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skill Editor - OllamaPy</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .skill-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .skill-card:hover {
            transform: translateY(-2px);
        }
        .skill-title {
            margin: 0 0 10px 0;
            color: #333;
        }
        .skill-description {
            color: #666;
            margin: 10px 0;
            font-size: 14px;
        }
        .skill-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
        }
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge.verified {
            background: #28a745;
            color: white;
        }
        .badge.unverified {
            background: #ffc107;
            color: #000;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
        }
        .btn:hover {
            background: #5a67d8;
        }
        .btn-danger {
            background: #dc3545;
        }
        .btn-danger:hover {
            background: #c82333;
        }
        .new-skill-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #28a745;
            color: white;
            border: none;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .loading {
            text-align: center;
            padding: 40px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔧 Skill Editor</h1>
        <p>Manage and edit your OllamaPy skills</p>
    </div>
    
    <div id="loading" class="loading">Loading skills...</div>
    <div id="skills-container" class="skills-grid" style="display: none;"></div>
    
    <button class="new-skill-btn" onclick="location.href='/new-skill'" title="Create New Skill">+</button>
    
    <script>
        async function loadSkills() {
            try {
                const response = await fetch('/api/skills');
                const data = await response.json();
                
                document.getElementById('loading').style.display = 'none';
                
                if (data.success) {
                    displaySkills(data.skills);
                } else {
                    alert('Failed to load skills: ' + data.error);
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                alert('Error loading skills: ' + error.message);
            }
        }
        
        function displaySkills(skills) {
            const container = document.getElementById('skills-container');
            container.innerHTML = '';
            
            Object.entries(skills).forEach(([name, skill]) => {
                const card = document.createElement('div');
                card.className = 'skill-card';
                
                const verifiedBadge = skill.verified ? 
                    '<span class="badge verified">VERIFIED</span>' : 
                    '<span class="badge unverified">CUSTOM</span>';
                
                card.innerHTML = `
                    <h3 class="skill-title">${name}</h3>
                    <p class="skill-description">${skill.description || 'No description'}</p>
                    <div class="skill-meta">
                        ${verifiedBadge}
                        <div>
                            <a href="/skill/${name}" class="btn">Edit</a>
                            ${!skill.verified ? `<button onclick="deleteSkill('${name}')" class="btn btn-danger">Delete</button>` : ''}
                        </div>
                    </div>
                `;
                
                container.appendChild(card);
            });
            
            container.style.display = 'grid';
        }
        
        async function deleteSkill(skillName) {
            if (!confirm(`Are you sure you want to delete the skill "${skillName}"?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/skills/${skillName}`, {
                    method: 'DELETE'
                });
                const data = await response.json();
                
                if (data.success) {
                    alert('Skill deleted successfully');
                    loadSkills(); // Reload the skills
                } else {
                    alert('Failed to delete skill: ' + data.error);
                }
            } catch (error) {
                alert('Error deleting skill: ' + error.message);
            }
        }
        
        // Load skills when page loads
        loadSkills();
    </script>
</body>
</html>"""

    def _get_skill_editor_html(self, skill_name: str) -> str:
        """Generate the skill editor interface HTML."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Skill: {skill_name} - OllamaPy</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
        }}
        .form-section {{
            padding: 30px;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }}
        .form-control {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
        }}
        .form-control:focus {{
            outline: none;
            border-color: #667eea;
        }}
        textarea.form-control {{
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            resize: vertical;
        }}
        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
            transition: background 0.2s;
        }}
        .btn:hover {{
            background: #5a67d8;
        }}
        .btn-secondary {{
            background: #6c757d;
        }}
        .btn-secondary:hover {{
            background: #5a6268;
        }}
        .btn-success {{
            background: #28a745;
        }}
        .btn-success:hover {{
            background: #218838;
        }}
        .parameter-editor {{
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            padding: 20px;
            margin-top: 10px;
        }}
        .parameter-item {{
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            align-items: end;
        }}
        .parameter-item input, .parameter-item select {{
            flex: 1;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .parameter-item button {{
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
        }}
        .test-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-top: 20px;
        }}
        .test-output {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            white-space: pre-wrap;
            margin-top: 10px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .loading {{
            text-align: center;
            padding: 40px;
        }}
        .error {{
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .success {{
            background: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✏️ Edit Skill: {skill_name}</h1>
            <p>Modify skill properties and test your changes</p>
        </div>
        
        <div id="loading" class="loading">Loading skill data...</div>
        
        <div id="editor-form" class="form-section" style="display: none;">
            <form id="skill-form">
                <div class="form-group">
                    <label>Skill Name</label>
                    <input type="text" id="skill-name" class="form-control" readonly>
                </div>
                
                <div class="form-group">
                    <label>Description</label>
                    <textarea id="skill-description" class="form-control" rows="3" placeholder="Describe when this skill should be used"></textarea>
                </div>
                
                <div class="form-group">
                    <label>Role</label>
                    <select id="skill-role" class="form-control">
                        <option value="general">General</option>
                        <option value="text_processing">Text Processing</option>
                        <option value="mathematics">Mathematics</option>
                        <option value="data_analysis">Data Analysis</option>
                        <option value="file_operations">File Operations</option>
                        <option value="web_utilities">Web Utilities</option>
                        <option value="time_date">Time & Date</option>
                        <option value="formatting">Formatting</option>
                        <option value="validation">Validation</option>
                        <option value="emotional_response">Emotional Response</option>
                        <option value="information">Information</option>
                        <option value="advanced">Advanced</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Vibe Test Phrases (one per line)</label>
                    <textarea id="vibe-phrases" class="form-control" rows="5" placeholder="Enter test phrases that should trigger this skill..."></textarea>
                </div>
                
                <div class="form-group">
                    <label>Parameters</label>
                    <div class="parameter-editor">
                        <div id="parameters-container">
                            <!-- Parameters will be added here dynamically -->
                        </div>
                        <button type="button" onclick="addParameter()" class="btn btn-secondary">Add Parameter</button>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Function Code</label>
                    <textarea id="function-code" class="form-control" rows="15" placeholder="def execute(param1=None):&#10;    from ollamapy.actions import log&#10;    log('[YourSkill] Your implementation here')"></textarea>
                </div>
                
                <div class="test-section">
                    <h3>Test Skill</h3>
                    <button type="button" onclick="testSkill()" class="btn btn-success">Test Execution</button>
                    <div id="test-output" class="test-output" style="display: none;"></div>
                </div>
                
                <div style="margin-top: 30px;">
                    <button type="submit" class="btn">Save Skill</button>
                    <button type="button" onclick="location.href='/'" class="btn btn-secondary">Cancel</button>
                </div>
            </form>
        </div>
        
        <div id="message-area"></div>
    </div>
    
    <script>
        let skillData = null;
        
        async function loadSkill() {{
            try {{
                const response = await fetch('/api/skills/{skill_name}');
                const data = await response.json();
                
                document.getElementById('loading').style.display = 'none';
                
                if (data.success) {{
                    skillData = data.skill;
                    populateForm(skillData);
                    document.getElementById('editor-form').style.display = 'block';
                }} else {{
                    showError('Failed to load skill: ' + data.error);
                }}
            }} catch (error) {{
                document.getElementById('loading').style.display = 'none';
                showError('Error loading skill: ' + error.message);
            }}
        }}
        
        function populateForm(skill) {{
            document.getElementById('skill-name').value = skill.name;
            document.getElementById('skill-description').value = skill.description || '';
            document.getElementById('skill-role').value = skill.role || 'general';
            document.getElementById('vibe-phrases').value = (skill.vibe_test_phrases || []).join('\\n');
            document.getElementById('function-code').value = skill.function_code || '';
            
            // Populate parameters
            const container = document.getElementById('parameters-container');
            container.innerHTML = '';
            if (skill.parameters) {{
                Object.entries(skill.parameters).forEach(([name, info]) => {{
                    addParameter(name, info.type, info.required, info.description);
                }});
            }}
        }}
        
        function addParameter(name = '', type = 'string', required = false, description = '') {{
            const container = document.getElementById('parameters-container');
            const div = document.createElement('div');
            div.className = 'parameter-item';
            div.innerHTML = `
                <input type="text" placeholder="Parameter name" value="${{name}}" onchange="updateParameterPreview()">
                <select onchange="updateParameterPreview()">
                    <option value="string" ${{type === 'string' ? 'selected' : ''}}>String</option>
                    <option value="number" ${{type === 'number' ? 'selected' : ''}}>Number</option>
                    <option value="boolean" ${{type === 'boolean' ? 'selected' : ''}}>Boolean</option>
                </select>
                <label><input type="checkbox" ${{required ? 'checked' : ''}} onchange="updateParameterPreview()"> Required</label>
                <input type="text" placeholder="Description" value="${{description}}" onchange="updateParameterPreview()">
                <button type="button" onclick="removeParameter(this)">Remove</button>
            `;
            container.appendChild(div);
        }}
        
        function removeParameter(button) {{
            button.parentElement.remove();
            updateParameterPreview();
        }}
        
        function updateParameterPreview() {{
            // This could be used to show a preview of the parameters
        }}
        
        function collectParameters() {{
            const parameters = {{}};
            const items = document.querySelectorAll('.parameter-item');
            
            items.forEach(item => {{
                const inputs = item.querySelectorAll('input');
                const select = item.querySelector('select');
                const name = inputs[0].value.trim();
                
                if (name) {{
                    parameters[name] = {{
                        type: select.value,
                        required: inputs[1].checked,
                        description: inputs[2].value.trim()
                    }};
                }}
            }});
            
            return parameters;
        }}
        
        async function testSkill() {{
            const skillData = {{
                name: document.getElementById('skill-name').value,
                description: document.getElementById('skill-description').value,
                role: document.getElementById('skill-role').value,
                vibe_test_phrases: document.getElementById('vibe-phrases').value.split('\\n').filter(p => p.trim()),
                parameters: collectParameters(),
                function_code: document.getElementById('function-code').value,
                verified: false,
                scope: 'local'
            }};
            
            try {{
                const response = await fetch('/api/skills/test', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{skill_data: skillData, test_input: {{}}}})
                }});
                
                const data = await response.json();
                const output = document.getElementById('test-output');
                
                if (data.success) {{
                    if (data.execution_successful) {{
                        output.textContent = 'Test passed!\\n\\nOutput:\\n' + data.output.join('\\n');
                        output.style.background = '#2d5a27';
                    }} else {{
                        output.textContent = 'Test failed:\\n' + data.error;
                        output.style.background = '#8b2635';
                    }}
                }} else {{
                    output.textContent = 'Error: ' + data.error;
                    output.style.background = '#8b2635';
                }}
                
                output.style.display = 'block';
            }} catch (error) {{
                const output = document.getElementById('test-output');
                output.textContent = 'Network error: ' + error.message;
                output.style.background = '#8b2635';
                output.style.display = 'block';
            }}
        }}
        
        document.getElementById('skill-form').addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            // Check if skill is verified (built-in)
            if (skillData && skillData.verified) {{
                showError('Cannot modify built-in skills');
                return;
            }}
            
            const formData = {{
                name: document.getElementById('skill-name').value,
                description: document.getElementById('skill-description').value,
                role: document.getElementById('skill-role').value,
                vibe_test_phrases: document.getElementById('vibe-phrases').value.split('\\n').filter(p => p.trim()),
                parameters: collectParameters(),
                function_code: document.getElementById('function-code').value,
                // Preserve existing fields
                ...skillData,
                last_modified: new Date().toISOString()
            }};
            
            try {{
                const response = await fetch('/api/skills/{skill_name}', {{
                    method: 'PUT',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(formData)
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    showSuccess('Skill updated successfully!');
                    // Reload skill data
                    loadSkill();
                }} else {{
                    showError('Failed to update skill: ' + data.error);
                    if (data.validation_errors) {{
                        showError('Validation errors: ' + data.validation_errors.join(', '));
                    }}
                }}
            }} catch (error) {{
                showError('Error updating skill: ' + error.message);
            }}
        }});
        
        function showError(message) {{
            const area = document.getElementById('message-area');
            area.innerHTML = `<div class="error">${{message}}</div>`;
            setTimeout(() => area.innerHTML = '', 5000);
        }}
        
        function showSuccess(message) {{
            const area = document.getElementById('message-area');
            area.innerHTML = `<div class="success">${{message}}</div>`;
            setTimeout(() => area.innerHTML = '', 5000);
        }}
        
        // Load skill when page loads
        loadSkill();
    </script>
</body>
</html>"""

    def _get_new_skill_html(self) -> str:
        """Generate the new skill creation interface HTML."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create New Skill - OllamaPy</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
        }
        .form-section {
            padding: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        .form-control {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        .form-control:focus {
            outline: none;
            border-color: #28a745;
        }
        textarea.form-control {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            resize: vertical;
        }
        .btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
            transition: background 0.2s;
        }
        .btn:hover {
            background: #218838;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-secondary:hover {
            background: #5a6268;
        }
        .btn-success {
            background: #17a2b8;
        }
        .btn-success:hover {
            background: #138496;
        }
        .parameter-editor {
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            padding: 20px;
            margin-top: 10px;
        }
        .parameter-item {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            align-items: end;
        }
        .parameter-item input, .parameter-item select {
            flex: 1;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .parameter-item button {
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
        }
        .template-section {
            background: #e7f5ff;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .template-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .test-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-top: 20px;
        }
        .test-output {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            white-space: pre-wrap;
            margin-top: 10px;
            max-height: 300px;
            overflow-y: auto;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .success {
            background: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>➕ Create New Skill</h1>
            <p>Build a custom skill for your OllamaPy system</p>
        </div>
        
        <div class="form-section">
            <div class="template-section">
                <h3>Quick Start Templates</h3>
                <p>Choose a template to get started faster:</p>
                <button class="template-btn" onclick="loadTemplate('simple')">Simple Action</button>
                <button class="template-btn" onclick="loadTemplate('calculation')">Mathematical Function</button>
                <button class="template-btn" onclick="loadTemplate('file_operation')">File Operation</button>
                <button class="template-btn" onclick="loadTemplate('api_call')">API Call</button>
            </div>
            
            <form id="skill-form">
                <div class="form-group">
                    <label>Skill Name *</label>
                    <input type="text" id="skill-name" class="form-control" required placeholder="e.g., myCustomSkill">
                    <small>Use camelCase or snake_case. No spaces or special characters.</small>
                </div>
                
                <div class="form-group">
                    <label>Description *</label>
                    <textarea id="skill-description" class="form-control" rows="3" required placeholder="Describe when this skill should be used. Be specific about the trigger conditions."></textarea>
                </div>
                
                <div class="form-group">
                    <label>Role</label>
                    <select id="skill-role" class="form-control">
                        <option value="general">General</option>
                        <option value="text_processing">Text Processing</option>
                        <option value="mathematics">Mathematics</option>
                        <option value="data_analysis">Data Analysis</option>
                        <option value="file_operations">File Operations</option>
                        <option value="web_utilities">Web Utilities</option>
                        <option value="time_date">Time & Date</option>
                        <option value="formatting">Formatting</option>
                        <option value="validation">Validation</option>
                        <option value="advanced">Advanced</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Vibe Test Phrases</label>
                    <textarea id="vibe-phrases" class="form-control" rows="5" placeholder="Enter test phrases that should trigger this skill (one per line)&#10;e.g., 'calculate the square of 5'&#10;     'what is 5 squared?'"></textarea>
                    <small>These help the AI know when to use your skill. Include various ways users might ask for this functionality.</small>
                </div>
                
                <div class="form-group">
                    <label>Parameters</label>
                    <div class="parameter-editor">
                        <div id="parameters-container">
                            <!-- Parameters will be added here dynamically -->
                        </div>
                        <button type="button" onclick="addParameter()" class="btn btn-secondary">Add Parameter</button>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Function Code *</label>
                    <textarea id="function-code" class="form-control" rows="15" required placeholder="def execute():&#10;    # Import the log function to output results&#10;    from ollamapy.skills import log&#10;    &#10;    # Your implementation here&#10;    result = 'Hello, World!'&#10;    log(f'[MySkill] Result: {result}')"></textarea>
                    <small>Your function must be named 'execute' and use log() to output results that the AI can see.</small>
                </div>
                
                <div class="test-section">
                    <h3>Test Skill</h3>
                    <button type="button" onclick="testSkill()" class="btn btn-success">Test Execution</button>
                    <div id="test-output" class="test-output" style="display: none;"></div>
                </div>
                
                <div style="margin-top: 30px;">
                    <button type="submit" class="btn">Create Skill</button>
                    <button type="button" onclick="location.href='/'" class="btn btn-secondary">Cancel</button>
                </div>
            </form>
        </div>
        
        <div id="message-area"></div>
    </div>
    
    <script>
        function loadTemplate(templateType) {
            const templates = {
                simple: {
                    name: 'sayHello',
                    description: 'Use when the user wants to be greeted or says hello',
                    role: 'general',
                    vibe_phrases: ['say hello\\nhello there\\ngreet me'],
                    parameters: {},
                    code: `def execute():\n    from ollamapy.skills import log\n    log('[SayHello] Hello! Nice to meet you!')`
                },
                calculation: {
                    name: 'powerOf',
                    description: 'Calculate a number raised to a power (exponentiation)',
                    role: 'mathematics',
                    vibe_phrases: ['2 to the power of 3\\nwhat is 5 raised to 2\\ncalculate 4^3'],
                    parameters: {
                        base: {type: 'number', required: true, description: 'The base number'},
                        exponent: {type: 'number', required: true, description: 'The exponent'}
                    },
                    code: `def execute(base=None, exponent=None):\n    from ollamapy.skills import log\n    \n    if base is None or exponent is None:\n        log('[PowerOf] Error: Both base and exponent are required')\n        return\n    \n    try:\n        result = base ** exponent\n        log(f'[PowerOf] {base} to the power of {exponent} = {result}')\n    except Exception as e:\n        log(f'[PowerOf] Error calculating power: {e}')`
                },
                file_operation: {
                    name: 'countLines',
                    description: 'Count the number of lines in a text file',
                    role: 'file_operations',
                    vibe_phrases: ['count lines in file\\nhow many lines are in this file\\nline count of file'],
                    parameters: {
                        file_path: {type: 'string', required: true, description: 'Path to the file to count lines in'}
                    },
                    code: `def execute(file_path=None):\n    from ollamapy.skills import log\n    \n    if not file_path:\n        log('[CountLines] Error: File path is required')\n        return\n    \n    try:\n        with open(file_path, 'r') as f:\n            line_count = sum(1 for line in f)\n        log(f'[CountLines] File {file_path} has {line_count} lines')\n    except FileNotFoundError:\n        log(f'[CountLines] Error: File not found: {file_path}')\n    except Exception as e:\n        log(f'[CountLines] Error reading file: {e}')`
                },
                api_call: {
                    name: 'getRandomFact',
                    description: 'Get a random interesting fact from an API',
                    role: 'web_utilities',
                    vibe_phrases: ['tell me a random fact\\nget me an interesting fact\\nshare a fun fact'],
                    parameters: {},
                    code: `def execute():\n    from ollamapy.skills import log\n    import json\n    \n    try:\n        # This is a placeholder - replace with actual API call\n        facts = [\n            "Honey never spoils. Archaeologists have found edible honey in ancient Egyptian tombs.",\n            "A group of flamingos is called a 'flamboyance'.",\n            "Octopuses have three hearts and blue blood."\n        ]\n        \n        import random\n        fact = random.choice(facts)\n        log(f'[RandomFact] Here\\'s a random fact: {fact}')\n        \n    except Exception as e:\n        log(f'[RandomFact] Error getting fact: {e}')`
                }
            };
            
            const template = templates[templateType];
            if (!template) return;
            
            document.getElementById('skill-name').value = template.name;
            document.getElementById('skill-description').value = template.description;
            document.getElementById('skill-role').value = template.role;
            document.getElementById('vibe-phrases').value = template.vibe_phrases;
            document.getElementById('function-code').value = template.code;
            
            // Clear existing parameters and add template parameters
            document.getElementById('parameters-container').innerHTML = '';
            if (template.parameters) {
                Object.entries(template.parameters).forEach(([name, info]) => {
                    addParameter(name, info.type, info.required, info.description);
                });
            }
        }
        
        function addParameter(name = '', type = 'string', required = false, description = '') {
            const container = document.getElementById('parameters-container');
            const div = document.createElement('div');
            div.className = 'parameter-item';
            div.innerHTML = `
                <input type="text" placeholder="Parameter name" value="${name}">
                <select>
                    <option value="string" ${type === 'string' ? 'selected' : ''}>String</option>
                    <option value="number" ${type === 'number' ? 'selected' : ''}>Number</option>
                    <option value="boolean" ${type === 'boolean' ? 'selected' : ''}>Boolean</option>
                </select>
                <label><input type="checkbox" ${required ? 'checked' : ''}> Required</label>
                <input type="text" placeholder="Description" value="${description}">
                <button type="button" onclick="removeParameter(this)">Remove</button>
            `;
            container.appendChild(div);
        }
        
        function removeParameter(button) {
            button.parentElement.remove();
        }
        
        function collectParameters() {
            const parameters = {};
            const items = document.querySelectorAll('.parameter-item');
            
            items.forEach(item => {
                const inputs = item.querySelectorAll('input');
                const select = item.querySelector('select');
                const name = inputs[0].value.trim();
                
                if (name) {
                    parameters[name] = {
                        type: select.value,
                        required: inputs[1].checked,
                        description: inputs[2].value.trim()
                    };
                }
            });
            
            return parameters;
        }
        
        async function testSkill() {
            const skillData = {
                name: document.getElementById('skill-name').value,
                description: document.getElementById('skill-description').value,
                role: document.getElementById('skill-role').value,
                vibe_test_phrases: document.getElementById('vibe-phrases').value.split('\\n').filter(p => p.trim()),
                parameters: collectParameters(),
                function_code: document.getElementById('function-code').value,
                verified: false,
                scope: 'local'
            };
            
            try {
                const response = await fetch('/api/skills/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({skill_data: skillData, test_input: {}})
                });
                
                const data = await response.json();
                const output = document.getElementById('test-output');
                
                if (data.success) {
                    if (data.execution_successful) {
                        output.textContent = 'Test passed!\\n\\nOutput:\\n' + data.output.join('\\n');
                        output.style.background = '#2d5a27';
                    } else {
                        output.textContent = 'Test failed:\\n' + data.error;
                        output.style.background = '#8b2635';
                    }
                } else {
                    output.textContent = 'Error: ' + data.error;
                    output.style.background = '#8b2635';
                }
                
                output.style.display = 'block';
            } catch (error) {
                const output = document.getElementById('test-output');
                output.textContent = 'Network error: ' + error.message;
                output.style.background = '#8b2635';
                output.style.display = 'block';
            }
        }
        
        document.getElementById('skill-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const skillName = document.getElementById('skill-name').value.trim();
            if (!skillName.match(/^[a-zA-Z_][a-zA-Z0-9_]*$/)) {
                showError('Skill name must be a valid identifier (no spaces or special characters except underscore)');
                return;
            }
            
            const formData = {
                name: skillName,
                description: document.getElementById('skill-description').value,
                role: document.getElementById('skill-role').value,
                vibe_test_phrases: document.getElementById('vibe-phrases').value.split('\\n').filter(p => p.trim()),
                parameters: collectParameters(),
                function_code: document.getElementById('function-code').value,
                verified: false,
                scope: 'local',
                tags: []
            };
            
            try {
                const response = await fetch('/api/skills', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showSuccess('Skill created successfully!');
                    setTimeout(() => {
                        location.href = '/skill/' + skillName;
                    }, 2000);
                } else {
                    showError('Failed to create skill: ' + data.error);
                    if (data.validation_errors) {
                        showError('Validation errors: ' + data.validation_errors.join(', '));
                    }
                }
            } catch (error) {
                showError('Error creating skill: ' + error.message);
            }
        });
        
        function showError(message) {
            const area = document.getElementById('message-area');
            area.innerHTML = `<div class="error">${message}</div>`;
            setTimeout(() => area.innerHTML = '', 5000);
        }
        
        function showSuccess(message) {
            const area = document.getElementById('message-area');
            area.innerHTML = `<div class="success">${message}</div>`;
            setTimeout(() => area.innerHTML = '', 5000);
        }
    </script>
</body>
</html>"""

    def run(self):
        """Run the Flask development server."""
        print(f"🚀 Starting Skill Editor API on http://localhost:{self.port}")
        print(f"💾 Skills directory: {self.registry.skills_dir}")
        print(f"📊 Loaded {len(self.registry.skills)} skills")
        self.app.run(debug=True, port=self.port, host="0.0.0.0")
