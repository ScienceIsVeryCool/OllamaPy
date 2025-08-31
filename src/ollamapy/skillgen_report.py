"""Navigatable documentation generation for skills with individual pages and comprehensive reporting."""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import os
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class SkillDocumentationGenerator:
    """Generates navigatable HTML documentation for all skills with individual pages."""
    
    def __init__(self, model: str = None, analysis_model: str = None, output_dir: str = "skill_docs"):
        """Initialize the documentation generator.
        
        Args:
            model: The generation model used (optional)
            analysis_model: The analysis model used for vibe tests (optional)
            output_dir: Directory to save documentation files
        """
        self.model = model or "N/A"
        self.analysis_model = analysis_model or "N/A"
        self.output_dir = Path(output_dir)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.skills_data_dir = Path("src/ollamapy/skills_data")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_all_skills(self) -> Dict[str, Dict]:
        """Load all skills from the skills_data directory.
        
        Returns:
            Dictionary of skill name to skill data
        """
        skills = {}
        if self.skills_data_dir.exists():
            for skill_file in self.skills_data_dir.glob("*.json"):
                try:
                    with open(skill_file, 'r') as f:
                        skill_data = json.load(f)
                        skills[skill_data['name']] = skill_data
                except Exception as e:
                    print(f"Error loading skill {skill_file}: {e}")
        return skills
    
    def generate_skill_page(self, skill_data: Dict, is_new: bool = False) -> str:
        """Generate an individual HTML page for a skill.
        
        Args:
            skill_data: The skill's data dictionary
            is_new: Whether this is a newly generated skill
            
        Returns:
            HTML content for the skill page
        """
        skill_name = skill_data.get('name', 'Unknown')
        description = skill_data.get('description', 'No description')
        role = skill_data.get('role', 'general')
        created_at = skill_data.get('created_at', 'Unknown')
        verified = skill_data.get('verified', False)
        
        # Format vibe test phrases
        vibe_phrases_html = ""
        if skill_data.get('vibe_test_phrases'):
            vibe_phrases_html = "<ul>"
            for phrase in skill_data['vibe_test_phrases']:
                vibe_phrases_html += f"<li>{phrase}</li>"
            vibe_phrases_html += "</ul>"
        else:
            vibe_phrases_html = "<p>No vibe test phrases defined</p>"
        
        # Format parameters
        params_html = ""
        if skill_data.get('parameters'):
            params_html = "<table class='params-table'>"
            params_html += "<tr><th>Parameter</th><th>Type</th><th>Required</th><th>Description</th></tr>"
            for param_name, param_info in skill_data['parameters'].items():
                required = "✓" if param_info.get('required', False) else ""
                params_html += f"""
                <tr>
                    <td><code>{param_name}</code></td>
                    <td>{param_info.get('type', 'unknown')}</td>
                    <td>{required}</td>
                    <td>{param_info.get('description', '')}</td>
                </tr>
                """
            params_html += "</table>"
        else:
            params_html = "<p>No parameters required</p>"
        
        # Format code with syntax highlighting
        code = skill_data.get('function_code', 'No code available')
        code_html = f"<pre><code class='language-python'>{self.escape_html(code)}</code></pre>"
        
        # Badge for new skills
        new_badge = '<span class="badge-new">NEW</span>' if is_new else ''
        verified_badge = '<span class="badge-verified">VERIFIED</span>' if verified else '<span class="badge-unverified">UNVERIFIED</span>'
        
        # Edit button (only for non-verified skills)
        edit_button = f'<button class="edit-btn" onclick="editSkill()" {"disabled" if verified else ""}>{"🔒 Protected" if verified else "✏️ Edit Skill"}</button>' if not verified else '<span class="protected-note">🔒 Built-in skills cannot be edited</span>'
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{skill_name} - Skill Documentation</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
    <style>
        {self.get_common_styles()}
        .skill-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px 15px 0 0;
            margin: -40px -40px 30px -40px;
        }}
        .skill-title {{
            font-size: 2.5em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .badge-new {{
            background: #ffc107;
            color: #000;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.4em;
            font-weight: bold;
        }}
        .badge-verified {{
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.4em;
        }}
        .badge-unverified {{
            background: #dc3545;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.4em;
        }}
        .skill-meta {{
            display: flex;
            gap: 30px;
            opacity: 0.9;
            flex-wrap: wrap;
        }}
        .meta-item {{
            display: flex;
            flex-direction: column;
        }}
        .meta-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        .meta-value {{
            font-size: 1.1em;
            font-weight: bold;
        }}
        .section {{
            margin: 30px 0;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .section h2 {{
            margin-top: 0;
            color: #333;
        }}
        .params-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .params-table th {{
            background: #667eea;
            color: white;
            padding: 10px;
            text-align: left;
        }}
        .params-table td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        .params-table code {{
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #2d2d2d;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
        }}
        pre code {{
            color: #f8f8f2;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }}
        .nav-buttons {{
            display: flex;
            justify-content: space-between;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
        }}
        .nav-button {{
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            transition: background 0.3s;
        }}
        .nav-button:hover {{
            background: #764ba2;
        }}
        .edit-btn {{
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
            transition: background 0.2s;
        }}
        .edit-btn:hover:not(:disabled) {{
            background: #218838;
        }}
        .edit-btn:disabled {{
            background: #6c757d;
            cursor: not-allowed;
        }}
        .protected-note {{
            color: #6c757d;
            font-style: italic;
            padding: 12px 0;
        }}
        .edit-panel {{
            display: none;
            background: #fff;
            border: 2px solid #667eea;
            border-radius: 10px;
            padding: 30px;
            margin: 30px 0;
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
            box-sizing: border-box;
        }}
        .form-control:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .form-control.code {{
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            resize: vertical;
        }}
        .btn-save {{
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            margin-right: 10px;
        }}
        .btn-cancel {{
            background: #6c757d;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
        }}
        .btn-test {{
            background: #17a2b8;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            margin-right: 10px;
        }}
        .message {{
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }}
        .message.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .message.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
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
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="skill-header">
            <h1 class="skill-title">
                {skill_name}
                {new_badge}
                {verified_badge}
            </h1>
            <p style="font-size: 1.2em; margin: 10px 0;">{description}</p>
            <div class="skill-meta">
                <div class="meta-item">
                    <span class="meta-label">Role</span>
                    <span class="meta-value">{role}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Created</span>
                    <span class="meta-value">{created_at[:10] if len(created_at) > 10 else created_at}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Execution Count</span>
                    <span class="meta-value">{skill_data.get('execution_count', 0)}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Success Rate</span>
                    <span class="meta-value">{skill_data.get('success_rate', 0):.1f}%</span>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            {edit_button}
        </div>
        
        <div id="edit-panel" class="edit-panel">
            <h2>✏️ Edit Skill</h2>
            <div id="message-area"></div>
            <form id="edit-form">
                <div class="form-group">
                    <label>Description</label>
                    <textarea id="edit-description" class="form-control" rows="3">{description}</textarea>
                </div>
                
                <div class="form-group">
                    <label>Role</label>
                    <select id="edit-role" class="form-control">
                        <option value="general" {"selected" if role == "general" else ""}>General</option>
                        <option value="text_processing" {"selected" if role == "text_processing" else ""}>Text Processing</option>
                        <option value="mathematics" {"selected" if role == "mathematics" else ""}>Mathematics</option>
                        <option value="data_analysis" {"selected" if role == "data_analysis" else ""}>Data Analysis</option>
                        <option value="file_operations" {"selected" if role == "file_operations" else ""}>File Operations</option>
                        <option value="web_utilities" {"selected" if role == "web_utilities" else ""}>Web Utilities</option>
                        <option value="time_date" {"selected" if role == "time_date" else ""}>Time & Date</option>
                        <option value="formatting" {"selected" if role == "formatting" else ""}>Formatting</option>
                        <option value="validation" {"selected" if role == "validation" else ""}>Validation</option>
                        <option value="emotional_response" {"selected" if role == "emotional_response" else ""}>Emotional Response</option>
                        <option value="information" {"selected" if role == "information" else ""}>Information</option>
                        <option value="advanced" {"selected" if role == "advanced" else ""}>Advanced</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Vibe Test Phrases (one per line)</label>
                    <textarea id="edit-vibe-phrases" class="form-control" rows="5">{"\\n".join(skill_data.get('vibe_test_phrases', []))}</textarea>
                </div>
                
                <div class="form-group">
                    <label>Function Code</label>
                    <textarea id="edit-function-code" class="form-control code" rows="15">{self.escape_html(skill_data.get('function_code', ''))}</textarea>
                </div>
                
                <div style="margin: 20px 0;">
                    <button type="button" class="btn-test" onclick="testSkill()">🧪 Test Skill</button>
                    <div id="test-output" class="test-output"></div>
                </div>
                
                <div>
                    <button type="submit" class="btn-save">💾 Save Changes</button>
                    <button type="button" class="btn-cancel" onclick="cancelEdit()">❌ Cancel</button>
                </div>
            </form>
        </div>
        
        <div id="view-panel">
            <div class="section">
                <h2>📝 Description</h2>
                <p>{description}</p>
            </div>
        
        <div class="section">
            <h2>🧪 Vibe Test Phrases</h2>
            <p>These phrases should trigger this skill:</p>
            {vibe_phrases_html}
        </div>
        
        <div class="section">
            <h2>⚙️ Parameters</h2>
            {params_html}
        </div>
        
            <div class="section">
                <h2>💻 Implementation</h2>
                {code_html}
            </div>
        </div>
        
        <div class="nav-buttons">
            <a href="index.html" class="nav-button">← Back to Index</a>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
    
    <script>
        const skillData = {json.dumps(skill_data, indent=2)};
        const isBuiltIn = {str(verified).lower()};
        
        function editSkill() {{
            if (isBuiltIn) {{
                showMessage('Built-in skills cannot be edited', 'error');
                return;
            }}
            document.getElementById('view-panel').style.display = 'none';
            document.getElementById('edit-panel').style.display = 'block';
        }}
        
        function cancelEdit() {{
            document.getElementById('edit-panel').style.display = 'none';
            document.getElementById('view-panel').style.display = 'block';
            clearMessage();
        }}
        
        async function testSkill() {{
            const formData = collectFormData();
            
            try {{
                const response = await fetch('http://localhost:5000/api/skills/test', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        skill_data: formData,
                        test_input: {{}}
                    }})
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
        
        function collectFormData() {{
            const vibePhrasesText = document.getElementById('edit-vibe-phrases').value;
            return {{
                name: skillData.name,
                description: document.getElementById('edit-description').value,
                role: document.getElementById('edit-role').value,
                vibe_test_phrases: vibePhrasesText.split('\\n').filter(p => p.trim()),
                parameters: skillData.parameters || {{}},
                function_code: document.getElementById('edit-function-code').value,
                verified: skillData.verified,
                scope: skillData.scope || 'local',
                tags: skillData.tags || [],
                created_at: skillData.created_at,
                execution_count: skillData.execution_count || 0,
                success_rate: skillData.success_rate || 100.0,
                average_execution_time: skillData.average_execution_time || 0.0
            }};
        }}
        
        async function saveSkill() {{
            if (isBuiltIn) {{
                showMessage('Built-in skills cannot be edited', 'error');
                return;
            }}
            
            const formData = collectFormData();
            formData.last_modified = new Date().toISOString();
            
            try {{
                const response = await fetch(`http://localhost:5000/api/skills/${{skillData.name}}`, {{
                    method: 'PUT',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(formData)
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    showMessage('Skill updated successfully! Refresh the page to see changes.', 'success');
                    // Update local skill data
                    Object.assign(skillData, formData);
                }} else {{
                    showMessage('Failed to update skill: ' + data.error, 'error');
                    if (data.validation_errors) {{
                        showMessage('Validation errors: ' + data.validation_errors.join(', '), 'error');
                    }}
                }}
            }} catch (error) {{
                showMessage('Network error: ' + error.message, 'error');
            }}
        }}
        
        function showMessage(message, type) {{
            const area = document.getElementById('message-area');
            area.innerHTML = `<div class="message ${{type}}">${{message}}</div>`;
            setTimeout(() => area.innerHTML = '', 5000);
        }}
        
        function clearMessage() {{
            document.getElementById('message-area').innerHTML = '';
        }}
        
        // Form submission handler
        document.getElementById('edit-form').addEventListener('submit', function(e) {{
            e.preventDefault();
            saveSkill();
        }});
        
        // Check if skill editor API is available
        async function checkAPIAvailability() {{
            try {{
                await fetch('http://localhost:5000/api/skills', {{method: 'HEAD'}});
            }} catch (error) {{
                console.warn('Skill editor API not available. Interactive editing disabled.');
                const editBtn = document.querySelector('.edit-btn');
                if (editBtn && !isBuiltIn) {{
                    editBtn.disabled = true;
                    editBtn.textContent = '🔌 API Offline';
                    editBtn.title = 'Start the skill editor server to enable editing';
                }}
            }}
        }}
        
        // Check API availability on page load
        checkAPIAvailability();
    </script>
</body>
</html>"""
    
    def generate_index_page(self, all_skills: Dict[str, Dict], new_skills: List[str], 
                           generation_results: List[Dict] = None) -> str:
        """Generate the main index page with links to all skills.
        
        Args:
            all_skills: Dictionary of all skills
            new_skills: List of newly generated skill names
            generation_results: Optional list of generation results for reporting
            
        Returns:
            HTML content for the index page
        """
        # Group skills by role
        skills_by_role = {}
        for skill_name, skill_data in all_skills.items():
            role = skill_data.get('role', 'general')
            if role not in skills_by_role:
                skills_by_role[role] = []
            skills_by_role[role].append((skill_name, skill_data))
        
        # Sort skills within each role
        for role in skills_by_role:
            skills_by_role[role].sort(key=lambda x: x[0])
        
        # Generate skills listing HTML
        skills_html = ""
        for role in sorted(skills_by_role.keys()):
            role_emoji = self.get_role_emoji(role)
            skills_html += f"""
            <div class="role-section">
                <h2>{role_emoji} {role.replace('_', ' ').title()}</h2>
                <div class="skills-grid">
            """
            
            for skill_name, skill_data in skills_by_role[role]:
                is_new = skill_name in new_skills
                verified = skill_data.get('verified', False)
                description = skill_data.get('description', 'No description')[:100]
                if len(skill_data.get('description', '')) > 100:
                    description += '...'
                
                new_badge = '<span class="badge new">NEW</span>' if is_new else ''
                verified_badge = '<span class="badge verified">✓</span>' if verified else ''
                
                skills_html += f"""
                <a href="{skill_name}.html" class="skill-card {'new-skill' if is_new else ''}">
                    <div class="skill-card-header">
                        <h3>{skill_name}</h3>
                        <div class="badges">
                            {new_badge}
                            {verified_badge}
                        </div>
                    </div>
                    <p>{description}</p>
                </a>
                """
            
            skills_html += """
                </div>
            </div>
            """
        
        # Generate statistics
        total_skills = len(all_skills)
        new_count = len(new_skills)
        verified_count = sum(1 for s in all_skills.values() if s.get('verified', False))
        
        # Generate charts if we have generation results
        charts_html = ""
        if generation_results:
            charts_html = self.generate_report_charts(generation_results)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OllamaPy Skills Documentation</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        {self.get_common_styles()}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 15px;
            margin-bottom: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 3em;
            margin-bottom: 20px;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
            flex-wrap: wrap;
        }}
        .stat {{
            background: rgba(255, 255, 255, 0.2);
            padding: 20px 30px;
            border-radius: 10px;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .role-section {{
            margin: 40px 0;
        }}
        .role-section h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        .skill-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-decoration: none;
            color: #333;
            transition: all 0.3s;
            border: 2px solid transparent;
            display: block;
        }}
        .skill-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        .skill-card.new-skill {{
            background: linear-gradient(135deg, #fff9e6 0%, #fffbf0 100%);
            border-color: #ffc107;
        }}
        .skill-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .skill-card h3 {{
            margin: 0;
            color: #667eea;
        }}
        .skill-card p {{
            margin: 0;
            color: #666;
            font-size: 0.95em;
        }}
        .badges {{
            display: flex;
            gap: 5px;
        }}
        .badge {{
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: bold;
        }}
        .badge.new {{
            background: #ffc107;
            color: #000;
        }}
        .badge.verified {{
            background: #28a745;
            color: white;
        }}
        .search-box {{
            margin: 30px 0;
            text-align: center;
        }}
        .search-box input {{
            width: 100%;
            max-width: 500px;
            padding: 15px 20px;
            font-size: 1.1em;
            border: 2px solid #667eea;
            border-radius: 50px;
            outline: none;
        }}
        .search-box input:focus {{
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        .generation-report {{
            margin: 40px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .generation-report h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 OllamaPy Skills Documentation</h1>
            <p style="font-size: 1.2em;">Comprehensive documentation for all available AI skills</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_skills}</div>
                    <div class="stat-label">Total Skills</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{new_count}</div>
                    <div class="stat-label">New Skills</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{verified_count}</div>
                    <div class="stat-label">Verified</div>
                </div>
            </div>
        </div>
        
        <div class="search-box">
            <input type="text" id="skillSearch" placeholder="Search skills..." onkeyup="filterSkills()">
        </div>
        
        {charts_html}
        
        {skills_html}
        
        <div class="footer">
            <p>Generated: {self.timestamp}</p>
            <p>Models: {self.model} (generation) | {self.analysis_model} (analysis)</p>
        </div>
    </div>
    
    <script>
    function filterSkills() {{
        const input = document.getElementById('skillSearch');
        const filter = input.value.toLowerCase();
        const cards = document.getElementsByClassName('skill-card');
        
        for (let card of cards) {{
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(filter) ? '' : 'none';
        }}
    }}
    </script>
</body>
</html>"""
    
    def generate_error_report(self, failed_results: List[Dict]) -> str:
        """Generate a separate error report for failed generations.
        
        Args:
            failed_results: List of failed generation results
            
        Returns:
            HTML content for the error report
        """
        if not failed_results:
            return ""
        
        errors_html = ""
        for i, result in enumerate(failed_results, 1):
            errors = result.get('errors', ['Unknown error'])
            step_results = result.get('step_results', {})
            
            # Determine where it failed
            failure_point = "Unknown"
            if not step_results.get('plan_created'):
                failure_point = "Plan Creation"
            elif not step_results.get('validation_passed'):
                failure_point = "Validation"
            elif not step_results.get('skill_registered'):
                failure_point = "Registration"
            elif not step_results.get('vibe_test_passed'):
                failure_point = "Vibe Test"
            
            errors_html += f"""
            <div class="error-card">
                <h3>Failed Generation #{i}</h3>
                <div class="error-details">
                    <p><strong>Failure Point:</strong> {failure_point}</p>
                    <p><strong>Attempts:</strong> {result.get('attempts', 1)}</p>
                    <p><strong>Time:</strong> {result.get('generation_time', 0):.1f}s</p>
                    <p><strong>Errors:</strong></p>
                    <ul class="error-list">
            """
            
            for error in errors:
                errors_html += f"<li>{error}</li>"
            
            errors_html += """
                    </ul>
                </div>
            """
            
            # Add plan details if available
            if result.get('plan'):
                plan = result['plan']
                errors_html += f"""
                <div class="plan-details">
                    <h4>Attempted Skill Plan:</h4>
                    <p><strong>Idea:</strong> {plan.get('idea', 'N/A')}</p>
                    <p><strong>Name:</strong> {plan.get('name', 'N/A')}</p>
                    <p><strong>Description:</strong> {plan.get('description', 'N/A')}</p>
                    <p><strong>Role:</strong> {plan.get('role', 'N/A')}</p>
                </div>
                """
            
            errors_html += "</div>"
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skill Generation Error Report</title>
    <style>
        {self.get_common_styles()}
        .header {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .error-card {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .error-card h3 {{
            margin-top: 0;
            color: #856404;
        }}
        .error-details {{
            margin: 15px 0;
        }}
        .error-list {{
            background: white;
            padding: 10px 10px 10px 30px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .plan-details {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }}
        .plan-details h4 {{
            margin-top: 0;
            color: #495057;
        }}
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
        }}
        .nav-button {{
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
        }}
        .nav-button:hover {{
            background: #764ba2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>❌ Skill Generation Error Report</h1>
            <p>Analysis of failed skill generation attempts</p>
        </div>
        
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Failed Attempts:</strong> {len(failed_results)}</p>
            <p><strong>Generated:</strong> {self.timestamp}</p>
            <p>This report contains details about skill generation attempts that failed, 
            including the failure points and error messages to help improve future generations.</p>
        </div>
        
        {errors_html}
        
        <a href="index.html" class="nav-button">← Back to Skills Documentation</a>
    </div>
</body>
</html>"""
    
    def generate_report_charts(self, generation_results: List[Dict]) -> str:
        """Generate charts for the generation report.
        
        Args:
            generation_results: List of generation results
            
        Returns:
            HTML containing the charts
        """
        if not generation_results:
            return ""
        
        # Prepare data
        successful = sum(1 for r in generation_results if r.get('success', False))
        failed = len(generation_results) - successful
        
        # Success rate pie chart
        fig1 = go.Figure(data=[go.Pie(
            labels=['Successful', 'Failed'],
            values=[successful, failed],
            hole=0.3,
            marker=dict(colors=['#28a745', '#dc3545'])
        )])
        fig1.update_layout(
            title="Generation Success Rate",
            height=300,
            showlegend=True
        )
        
        chart1_html = fig1.to_html(full_html=False, include_plotlyjs=False, div_id="success-pie")
        
        return f"""
        <div class="generation-report">
            <h2>📊 Latest Generation Report</h2>
            <div class="chart-container">
                {chart1_html}
            </div>
            <p style="text-align: center; margin-top: 20px;">
                <a href="error_report.html" style="color: #dc3545;">View detailed error report →</a>
            </p>
        </div>
        """
    
    def get_role_emoji(self, role: str) -> str:
        """Get emoji for a skill role."""
        emojis = {
            'text_processing': '📝',
            'mathematics': '🔢',
            'data_analysis': '📊',
            'file_operations': '📁',
            'web_utilities': '🌐',
            'time_date': '⏰',
            'formatting': '✨',
            'validation': '✅',
            'general': '🔧'
        }
        return emojis.get(role, '🔧')
    
    def get_common_styles(self) -> str:
        """Get common CSS styles used across all pages."""
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: white;
            min-height: 100vh;
        }
        .footer {
            text-align: center;
            margin-top: 60px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
            color: #6c757d;
        }
        .chart-container {
            margin: 20px 0;
        }
        """
    
    def escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    
    def generate_documentation(self, generation_results: List[Dict] = None) -> str:
        """Generate complete documentation for all skills.
        
        Args:
            generation_results: Optional list of recent generation results
            
        Returns:
            Path to the generated documentation
        """
        # Load all skills
        all_skills = self.load_all_skills()
        
        # Identify new skills from generation results
        new_skills = []
        failed_results = []
        
        if generation_results:
            for result in generation_results:
                if result.get('success') and result.get('skill'):
                    skill = result['skill']
                    skill_name = skill.get('name') or (skill.name if hasattr(skill, 'name') else 'unknown')
                    new_skills.append(skill_name)
                elif not result.get('success'):
                    failed_results.append(result)
        
        # Generate individual skill pages
        for skill_name, skill_data in all_skills.items():
            is_new = skill_name in new_skills
            skill_html = self.generate_skill_page(skill_data, is_new)
            skill_file = self.output_dir / f"{skill_name}.html"
            with open(skill_file, 'w', encoding='utf-8') as f:
                f.write(skill_html)
        
        # Generate index page
        index_html = self.generate_index_page(all_skills, new_skills, generation_results)
        index_file = self.output_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        # Generate error report if there were failures
        if failed_results:
            error_html = self.generate_error_report(failed_results)
            error_file = self.output_dir / "error_report.html"
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(error_html)
        
        return str(self.output_dir / "index.html")


class SkillGenerationReporter:
    """Handles reporting for skill generation sessions."""
    
    def __init__(self, model: str = None, analysis_model: str = None):
        """Initialize the reporter.
        
        Args:
            model: The generation model used
            analysis_model: The analysis model used
        """
        self.model = model
        self.analysis_model = analysis_model
        self.results = []
        
    def add_result(self, result: Dict):
        """Add a generation result to the reporter.
        
        Args:
            result: Generation result dictionary
        """
        self.results.append(result)
    
    def generate_report(self, output_dir: str = "skill_docs") -> str:
        """Generate the complete report.
        
        Args:
            output_dir: Directory to save the documentation
            
        Returns:
            Path to the generated documentation
        """
        doc_generator = SkillDocumentationGenerator(
            model=self.model,
            analysis_model=self.analysis_model,
            output_dir=output_dir
        )
        
        # Convert results to the expected format
        formatted_results = []
        for result in self.results:
            formatted_result = {
                'success': result.get('success', False),
                'skill': result.get('skill'),
                'skill_name': None,
                'description': None,
                'plan': None,
                'errors': result.get('errors', []),
                'attempts': result.get('attempts', 1),
                'generation_time': result.get('generation_time', 0),
                'step_results': result.get('step_results', {}),
                'vibe_test_passed': result.get('vibe_test_passed', False),
                'vibe_test_results': result.get('vibe_test_results'),
                'function_code': None
            }
            
            # Extract skill details
            if result.get('skill'):
                skill = result['skill']
                if hasattr(skill, '__dict__'):
                    formatted_result['skill_name'] = skill.name
                    formatted_result['description'] = skill.description
                    formatted_result['function_code'] = skill.function_code
                elif isinstance(skill, dict):
                    formatted_result['skill_name'] = skill.get('name')
                    formatted_result['description'] = skill.get('description')
                    formatted_result['function_code'] = skill.get('function_code')
            
            # Extract plan details
            if result.get('plan'):
                plan = result['plan']
                if hasattr(plan, '__dict__'):
                    formatted_result['plan'] = {
                        'idea': plan.idea,
                        'name': plan.name,
                        'description': plan.description,
                        'role': plan.role
                    }
                elif isinstance(plan, dict):
                    formatted_result['plan'] = plan
            
            formatted_results.append(formatted_result)
        
        return doc_generator.generate_documentation(formatted_results)