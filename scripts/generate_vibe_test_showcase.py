#!/usr/bin/env python3
"""Generate vibe test showcase page for GitHub Pages with multi-model comparison."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def load_vibe_test_results(results_path: str) -> Dict[str, Any]:
    """Load vibe test results from JSON file."""
    try:
        with open(results_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Vibe test results not found: {results_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in results file: {e}")
        return {}


def format_timing_stats(stats: Dict[str, float]) -> str:
    """Format timing statistics for display."""
    if not stats or stats.get("mean", 0) == 0:
        return "No data"
    
    mean = stats.get("mean", 0)
    consistency = stats.get("consistency_score", 0)
    category = stats.get("performance_category", "Unknown")
    
    return f"{mean:.2f}s avg, {category}, {consistency:.0f}/100 consistency"


def generate_model_comparison_section(results: Dict[str, Any]) -> str:
    """Generate HTML for model comparison section."""
    if not results.get("models"):
        return "<p>No model results available.</p>"
    
    models = results["models"]
    
    # Sort models by success rate
    sorted_models = sorted(models, key=lambda x: x["summary"]["overall_success_rate"], reverse=True)
    
    html = f"""
    <div class="model-comparison">
        <h2>🏆 Model Performance Comparison</h2>
        <p class="subtitle">Tested {len(models)} models with {results['metadata']['test_config']['iterations']} iterations each</p>
        
        <div class="comparison-grid">
"""

    for i, model in enumerate(sorted_models, 1):
        success_rate = model["summary"]["overall_success_rate"]
        timing_stats = model["summary"]["overall_timing_stats"]
        
        badge_class = "success" if success_rate >= 80 else "warning" if success_rate >= 60 else "danger"
        
        html += f"""
            <div class="model-card">
                <div class="model-rank">#{i}</div>
                <h3 class="model-name">{model['display_name']}</h3>
                <p class="model-description">{model['description']}</p>
                
                <div class="model-stats">
                    <div class="stat">
                        <span class="stat-label">Success Rate</span>
                        <span class="stat-value badge {badge_class}">{success_rate:.1f}%</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Average Response Time</span>
                        <span class="stat-value">{timing_stats['mean']:.2f}s</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Consistency Score</span>
                        <span class="stat-value">{timing_stats['consistency_score']:.0f}/100</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Performance Category</span>
                        <span class="stat-value">{timing_stats['performance_category']}</span>
                    </div>
                </div>
                
                <div class="model-actions">
                    <button class="btn btn-primary" onclick="showModelDetails('{model['model_name']}')">
                        View Detailed Results
                    </button>
                </div>
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html


def generate_skill_results_section(results: Dict[str, Any]) -> str:
    """Generate HTML for skill-by-skill results with model dropdown."""
    if not results.get("models"):
        return "<p>No skill results available.</p>"
    
    # Get all unique skills across all models
    all_skills = set()
    for model in results["models"]:
        all_skills.update(model["skills"].keys())
    
    html = f"""
    <div class="skill-results">
        <h2>📊 Skill Performance by Model</h2>
        <p class="subtitle">Compare how different models perform on each skill</p>
        
        <div class="skill-grid">
"""

    for skill_name in sorted(all_skills):
        # Get skill data from first model that has it
        skill_data = None
        for model in results["models"]:
            if skill_name in model["skills"]:
                skill_data = model["skills"][skill_name]
                break
        
        if not skill_data:
            continue
            
        html += f"""
            <div class="skill-card" data-skill="{skill_name}">
                <div class="skill-header">
                    <h3 class="skill-name">{skill_name}</h3>
                    <p class="skill-description">{skill_data.get('action_description', 'No description')}</p>
                </div>
                
                <div class="model-selector">
                    <label for="model-select-{skill_name}">Select Model:</label>
                    <select id="model-select-{skill_name}" onchange="updateSkillDisplay('{skill_name}', this.value)">
"""

        # Add options for each model that has this skill
        for model in results["models"]:
            if skill_name in model["skills"]:
                html += f"""
                        <option value="{model['model_name']}">{model['display_name']}</option>
"""

        html += f"""
                    </select>
                </div>
                
                <div id="skill-content-{skill_name}" class="skill-content">
                    <!-- Content will be populated by JavaScript -->
                </div>
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html


def generate_vibe_test_page(results: Dict[str, Any]) -> str:
    """Generate complete HTML page for vibe test results."""
    
    metadata = results.get("metadata", {})
    generated_time = metadata.get("generated_at", datetime.now().isoformat())
    
    # Parse timestamp for display
    try:
        dt = datetime.fromisoformat(generated_time.replace('Z', '+00:00'))
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        formatted_time = generated_time
    
    model_comparison_html = generate_model_comparison_section(results)
    skill_results_html = generate_skill_results_section(results)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vibe Test Results - OllamaPy</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.1em;
            margin-bottom: 20px;
        }}
        
        .stats-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.7);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .model-comparison, .skill-results {{
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 40px;
        }}
        
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .model-card {{
            border: 2px solid #eee;
            border-radius: 15px;
            padding: 25px;
            transition: all 0.3s ease;
            position: relative;
            background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
        }}
        
        .model-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        
        .model-rank {{
            position: absolute;
            top: -10px;
            right: -10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2em;
        }}
        
        .model-name {{
            font-size: 1.5em;
            margin-bottom: 10px;
            color: #333;
        }}
        
        .model-description {{
            color: #666;
            margin-bottom: 20px;
            line-height: 1.5;
        }}
        
        .model-stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        
        .stat-label {{
            font-size: 0.85em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .stat-value {{
            font-weight: bold;
            color: #333;
        }}
        
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            text-align: center;
        }}
        
        .badge.success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge.warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge.danger {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .skill-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .skill-card {{
            border: 2px solid #eee;
            border-radius: 15px;
            padding: 25px;
            background: linear-gradient(135deg, #fff9f0 0%, #fff2e6 100%);
        }}
        
        .skill-header {{
            margin-bottom: 20px;
        }}
        
        .skill-name {{
            font-size: 1.3em;
            margin-bottom: 10px;
            color: #333;
        }}
        
        .skill-description {{
            color: #666;
            line-height: 1.5;
        }}
        
        .model-selector {{
            margin-bottom: 20px;
        }}
        
        .model-selector label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }}
        
        .model-selector select {{
            width: 100%;
            padding: 8px 12px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 1em;
            background: white;
        }}
        
        .skill-content {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #eee;
        }}
        
        .performance-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .metric {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
            display: block;
        }}
        
        .metric-label {{
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }}
        
        .phrase-results {{
            margin-top: 20px;
        }}
        
        .phrase-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }}
        
        .phrase-text {{
            font-style: italic;
            margin-bottom: 10px;
            color: #555;
        }}
        
        .phrase-stats {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .timestamp {{
            color: #888;
            font-size: 0.9em;
            margin-top: 20px;
        }}
        
        .nav-links {{
            text-align: center;
            margin: 40px 0;
        }}
        
        .nav-links a {{
            margin: 0 15px;
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 25px;
            transition: all 0.3s ease;
        }}
        
        .nav-links a:hover {{
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }}
        
        @media (max-width: 768px) {{
            .comparison-grid {{
                grid-template-columns: 1fr;
            }}
            
            .skill-grid {{
                grid-template-columns: 1fr;
            }}
            
            .model-stats {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Vibe Test Results</h1>
            <p class="subtitle">Multi-Model AI Performance Analysis for OllamaPy</p>
            
            <div class="stats-summary">
                <div class="stat-card">
                    <div class="stat-number">{len(results.get('models', []))}</div>
                    <div class="stat-label">Models Tested</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{metadata.get('test_config', {}).get('iterations', 0)}</div>
                    <div class="stat-label">Iterations Each</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(set(skill for model in results.get('models', []) for skill in model.get('skills', {})))}</div>
                    <div class="stat-label">Skills Tested</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(len(model.get('skills', {})) for model in results.get('models', []))}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
            </div>
            
            <div class="timestamp">Generated: {formatted_time}</div>
        </div>
        
        {model_comparison_html}
        
        {skill_results_html}
        
        <div class="nav-links">
            <a href="index.html">← Main Dashboard</a>
            <a href="skills.html">Skills Showcase</a>
            <a href="coverage.html">Test Coverage</a>
        </div>
    </div>
    
    <script>
        // Store the full results data for JavaScript access
        const vibeTestResults = {json.dumps(results, indent=2)};
        
        function updateSkillDisplay(skillName, modelName) {{
            const model = vibeTestResults.models.find(m => m.model_name === modelName);
            if (!model || !model.skills[skillName]) {{
                return;
            }}
            
            const skill = model.skills[skillName];
            const container = document.getElementById(`skill-content-${{skillName}}`);
            
            const successBadge = skill.success_rate >= 80 ? 'success' : 
                                skill.success_rate >= 60 ? 'warning' : 'danger';
            
            let html = `
                <div class="performance-metrics">
                    <div class="metric">
                        <span class="metric-value badge ${{successBadge}}">${{skill.success_rate.toFixed(1)}}%</span>
                        <div class="metric-label">Success Rate</div>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${{skill.timing_stats.mean.toFixed(2)}}s</span>
                        <div class="metric-label">Avg Time</div>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${{skill.timing_stats.consistency_score.toFixed(0)}}/100</span>
                        <div class="metric-label">Consistency</div>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${{skill.timing_stats.performance_category}}</span>
                        <div class="metric-label">Performance</div>
                    </div>
                </div>
                
                <div class="phrase-results">
                    <h4>Test Phrase Results:</h4>
            `;
            
            for (const [phrase, data] of Object.entries(skill.phrase_results)) {{
                const phraseBadge = data.success_rate >= 80 ? 'success' : 
                                   data.success_rate >= 60 ? 'warning' : 'danger';
                
                html += `
                    <div class="phrase-item">
                        <div class="phrase-text">"${{phrase}}"</div>
                        <div class="phrase-stats">
                            <span class="badge ${{phraseBadge}}">${{data.success_rate.toFixed(1)}}% Success</span>
                            <span>${{data.timing_stats.mean.toFixed(2)}}s avg</span>
                            <span>${{data.timing_stats.consistency_score.toFixed(0)}}/100 consistency</span>
                        </div>
                    </div>
                `;
            }}
            
            html += `</div>`;
            container.innerHTML = html;
        }}
        
        function showModelDetails(modelName) {{
            alert(`Detailed results for ${{modelName}} - Feature coming soon!`);
        }}
        
        // Initialize skill displays with first available model
        document.addEventListener('DOMContentLoaded', function() {{
            const skillCards = document.querySelectorAll('[data-skill]');
            skillCards.forEach(card => {{
                const skillName = card.getAttribute('data-skill');
                const select = card.querySelector('select');
                if (select && select.options.length > 0) {{
                    updateSkillDisplay(skillName, select.options[0].value);
                }}
            }});
        }});
    </script>
</body>
</html>"""
    
    return html


def main():
    """Generate vibe test showcase page."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    
    # Default results path
    results_path = docs_dir / "vibe_test_results.json"
    
    # Check if results file exists
    if not results_path.exists():
        print(f"❌ Vibe test results not found at {results_path}")
        print("Run multi-model vibe tests first to generate results.")
        return False
    
    print(f"📊 Generating vibe test showcase from {results_path}")
    
    # Load results
    results = load_vibe_test_results(results_path)
    if not results:
        return False
    
    # Generate HTML
    html_content = generate_vibe_test_page(results)
    
    # Write to docs directory
    output_path = docs_dir / "vibe_tests.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Vibe test showcase generated: {output_path}")
    print(f"🌐 View at: https://scienceisverycool.github.io/OllamaPy/vibe_tests.html")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)