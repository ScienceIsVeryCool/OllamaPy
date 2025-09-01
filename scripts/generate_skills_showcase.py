#!/usr/bin/env python3
"""
Generate a skills showcase HTML page from skill JSON files.
This script reads all skill JSON files and creates a navigatable HTML showcase.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def load_skills(skills_dir: Path) -> List[Dict[str, Any]]:
    """Load all skill JSON files from the skills directory."""
    skills = []
    
    if not skills_dir.exists():
        print(f"Warning: Skills directory {skills_dir} does not exist")
        return skills
    
    for json_file in skills_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                skill_data = json.load(f)
                skill_data['filename'] = json_file.name
                skills.append(skill_data)
        except Exception as e:
            print(f"Warning: Could not load {json_file}: {e}")
    
    return sorted(skills, key=lambda x: x.get('name', '').lower())

def format_function_code(code: str) -> str:
    """Format function code for HTML display with syntax highlighting."""
    if not code:
        return "<em>No implementation available</em>"
    
    # Basic HTML escaping
    code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Add line numbers and basic syntax highlighting
    lines = code.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('def '):
            line = f'<span class="def-keyword">{line}</span>'
        elif line.strip().startswith('import ') or line.strip().startswith('from '):
            line = f'<span class="import-keyword">{line}</span>'
        elif line.strip().startswith('#'):
            line = f'<span class="comment">{line}</span>'
        
        formatted_lines.append(f'<span class="line-number">{i:3}</span> {line}')
    
    return '<br>'.join(formatted_lines)

def generate_skills_showcase_html(skills: List[Dict[str, Any]]) -> str:
    """Generate the complete HTML for the skills showcase."""
    
    # Calculate stats
    total_skills = len(skills)
    verified_skills = len([s for s in skills if s.get('verified', False)])
    roles = list(set(s.get('role', 'unknown') for s in skills))
    scopes = list(set(s.get('scope', 'unknown') for s in skills))
    
    # Group skills by role
    skills_by_role = {}
    for skill in skills:
        role = skill.get('role', 'unknown')
        if role not in skills_by_role:
            skills_by_role[role] = []
        skills_by_role[role].append(skill)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OllamaPy Skills Showcase</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f8f9fa;
        }}
        
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            margin-bottom: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.2em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .navigation {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .nav-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
        }}
        
        .nav-link {{
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s;
            font-weight: 500;
        }}
        
        .nav-link:hover {{
            background: #5a6fd8;
            transform: translateY(-1px);
        }}
        
        .role-section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .role-header {{
            background: #667eea;
            color: white;
            padding: 20px;
            font-size: 1.3em;
            font-weight: 600;
            text-transform: capitalize;
        }}
        
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 0;
        }}
        
        .skill-card {{
            padding: 25px;
            border-bottom: 1px solid #eee;
            border-right: 1px solid #eee;
            transition: background-color 0.2s;
        }}
        
        .skill-card:hover {{
            background-color: #f8f9ff;
        }}
        
        .skill-name {{
            font-size: 1.3em;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }}
        
        .skill-description {{
            color: #666;
            margin-bottom: 15px;
            font-style: italic;
        }}
        
        .skill-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 15px;
        }}
        
        .meta-badge {{
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        
        .verified {{
            background: #d4edda;
            color: #155724;
        }}
        
        .unverified {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .scope-global {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .scope-local {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .vibe-tests {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
        }}
        
        .vibe-tests h4 {{
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 0.9em;
        }}
        
        .vibe-test {{
            background: white;
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 4px;
            border-left: 3px solid #667eea;
            font-size: 0.85em;
            color: #495057;
        }}
        
        .parameters {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
        }}
        
        .parameters h4 {{
            margin: 0 0 10px 0;
            color: #495057;
            font-size: 0.9em;
        }}
        
        .parameter {{
            margin-bottom: 8px;
            font-size: 0.85em;
        }}
        
        .param-name {{
            font-weight: 600;
            color: #333;
        }}
        
        .param-type {{
            color: #667eea;
            font-family: monospace;
        }}
        
        .param-desc {{
            color: #666;
            font-style: italic;
        }}
        
        .function-code {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85em;
            line-height: 1.4;
        }}
        
        .line-number {{
            color: #718096;
            margin-right: 15px;
        }}
        
        .def-keyword {{
            color: #68d391;
        }}
        
        .import-keyword {{
            color: #90cdf4;
        }}
        
        .comment {{
            color: #a0aec0;
            font-style: italic;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .footer-links {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }}
        
        .footer-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .footer-link:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            .skills-grid {{
                grid-template-columns: 1fr;
            }}
            
            .skill-card {{
                border-right: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 OllamaPy Skills Showcase</h1>
        <p>Dynamic AI capabilities and skill implementations</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{total_skills}</div>
            <div class="stat-label">Total Skills</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{verified_skills}</div>
            <div class="stat-label">Verified Skills</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(roles)}</div>
            <div class="stat-label">Skill Roles</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(scopes)}</div>
            <div class="stat-label">Scope Types</div>
        </div>
    </div>
    
    <div class="navigation">
        <div class="nav-links">"""
    
    # Add navigation links for each role
    for role in sorted(skills_by_role.keys()):
        count = len(skills_by_role[role])
        html += f'<a href="#{role}" class="nav-link">{role.title()} ({count})</a>'
    
    html += """
            <a href="coverage.html" class="nav-link">📊 Test Coverage</a>
            <a href="https://github.com/ScienceIsVeryCool/OllamaPy" class="nav-link">📦 GitHub Repo</a>
        </div>
    </div>
"""
    
    # Generate skill sections by role
    for role in sorted(skills_by_role.keys()):
        role_skills = skills_by_role[role]
        html += f"""
    <div id="{role}" class="role-section">
        <div class="role-header">
            {role.title()} Skills ({len(role_skills)})
        </div>
        <div class="skills-grid">"""
        
        for skill in role_skills:
            # Generate skill card
            name = skill.get('name', 'Unknown')
            desc = skill.get('description', 'No description available')
            verified = skill.get('verified', False)
            scope = skill.get('scope', 'unknown')
            vibe_tests = skill.get('vibe_test_phrases', [])
            parameters = skill.get('parameters', {})
            function_code = skill.get('function_code', '')
            
            html += f"""
            <div class="skill-card">
                <div class="skill-name">{name}</div>
                <div class="skill-description">{desc}</div>
                
                <div class="skill-meta">
                    <span class="meta-badge {'verified' if verified else 'unverified'}">
                        {'✅ Verified' if verified else '⚠️ Unverified'}
                    </span>
                    <span class="meta-badge scope-{scope}">
                        🌍 {scope.title()}
                    </span>
                </div>"""
            
            # Add vibe tests if available
            if vibe_tests:
                html += """
                <div class="vibe-tests">
                    <h4>📝 Example Use Cases</h4>"""
                for test in vibe_tests[:3]:  # Show max 3 examples
                    html += f'<div class="vibe-test">{test}</div>'
                if len(vibe_tests) > 3:
                    html += f'<div class="vibe-test"><em>... and {len(vibe_tests) - 3} more examples</em></div>'
                html += "</div>"
            
            # Add parameters if available
            if parameters:
                html += """
                <div class="parameters">
                    <h4>⚙️ Parameters</h4>"""
                for param_name, param_info in parameters.items():
                    param_type = param_info.get('type', 'unknown')
                    param_desc = param_info.get('description', 'No description')
                    required = param_info.get('required', False)
                    req_badge = ' (required)' if required else ' (optional)'
                    html += f"""
                    <div class="parameter">
                        <span class="param-name">{param_name}</span>
                        <span class="param-type">{param_type}{req_badge}</span>
                        <br><span class="param-desc">{param_desc}</span>
                    </div>"""
                html += "</div>"
            
            # Add function code (collapsed by default, expandable)
            if function_code:
                formatted_code = format_function_code(function_code)
                html += f"""
                <details>
                    <summary style="cursor: pointer; font-weight: 600; color: #495057; margin-bottom: 10px;">
                        🔍 View Implementation
                    </summary>
                    <div class="function-code">{formatted_code}</div>
                </details>"""
            
            html += "</div>"
        
        html += "</div></div>"
    
    # Add footer
    html += f"""
    <div class="footer">
        <p><strong>OllamaPy Skills Showcase</strong></p>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p>This page showcases the current AI skill capabilities available in OllamaPy.</p>
        
        <div class="footer-links">
            <a href="coverage.html" class="footer-link">📊 Test Coverage</a>
            <a href="https://github.com/ScienceIsVeryCool/OllamaPy" class="footer-link">📦 GitHub Repository</a>
            <a href="https://pypi.org/project/ollamapy/" class="footer-link">🐍 PyPI Package</a>
        </div>
    </div>
    
    <script>
        // Add smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});
    </script>
</body>
</html>"""
    
    return html

def main():
    """Main function to generate the skills showcase."""
    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    skills_dir = project_root / "src" / "ollamapy" / "skills_data"
    output_file = project_root / "docs" / "skills.html"
    
    print(f"Looking for skills in: {skills_dir}")
    print(f"Output file: {output_file}")
    
    # Load skills
    skills = load_skills(skills_dir)
    print(f"Found {len(skills)} skills")
    
    if not skills:
        print("No skills found. Exiting.")
        return
    
    # Generate HTML
    html_content = generate_skills_showcase_html(skills)
    
    # Ensure output directory exists
    output_file.parent.mkdir(exist_ok=True)
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Skills showcase generated: {output_file}")
    # Print skills by role summary
    role_counts = {}
    for skill in skills:
        role = skill.get('role', 'unknown')
        role_counts[role] = role_counts.get(role, 0) + 1
    
    role_summary = ', '.join([f'{role}({count})' for role, count in sorted(role_counts.items())])
    print(f"Skills by role: {role_summary}")

if __name__ == "__main__":
    main()