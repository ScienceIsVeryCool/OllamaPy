"""Built-in vibe tests for evaluating AI decision-making consistency with visual reporting."""

import re
from typing import List, Dict, Tuple, Any
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .ollama_client import OllamaClient
from .model_manager import ModelManager
from .analysis_engine import AnalysisEngine
from .actions import get_actions_with_vibe_tests, clear_action_logs


class VibeTestRunner:
    """Built-in vibe test runner with multi-action support and visual reporting.
    
    Tests now check if the target action is selected, regardless of
    what other actions might also be selected, and generates comprehensive
    visual reports using Plotly.
    """
    
    def __init__(self, model: str = "gemma3:4b", analysis_model: str = "gemma3:4b"):
        """Initialize the vibe test runner.
        
        Args:
            model: The model to use for testing
            analysis_model: Optional separate model for action analysis (defaults to main model)
        """
        self.model = model
        self.analysis_model = analysis_model or model
        self.client = OllamaClient()
        self.model_manager = ModelManager(self.client)
        self.analysis_engine = AnalysisEngine(self.analysis_model, self.client)
        self.actions_with_tests = get_actions_with_vibe_tests()
        self.all_test_results = {}  # Store all results for report generation
    
    def check_prerequisites(self) -> bool:
        """Check if Ollama is available and models can be used."""
        success, main_status, analysis_status = self.model_manager.ensure_models_available(
            self.model, self.analysis_model
        )
        
        if not success:
            print("❌ Error: Ollama server is not running!")
            print("Please start Ollama with: ollama serve")
            return False
        
        return True
    
    def extract_expected_parameters(self, phrase: str, action_name: str) -> Dict[str, Any]:
        """Extract expected parameter values from test phrases.
        
        Args:
            phrase: The test phrase
            action_name: The action being tested
            
        Returns:
            Dictionary of expected parameter values
        """
        expected_params = {}
        
        # Extract numbers for square_root
        if action_name == "square_root":
            # Look for numbers in the phrase
            numbers = re.findall(r'\d+(?:\.\d+)?', phrase)
            if numbers:
                expected_params['number'] = float(numbers[0])
        
        # Extract expressions for calculate
        elif action_name == "calculate":
            # Look for mathematical expressions
            # Simple pattern for basic arithmetic
            expr_match = re.search(r'(\d+\s*[+\-*/]\s*\d+)', phrase)
            if expr_match:
                expected_params['expression'] = expr_match.group(1).replace(' ', '')
        
        # Extract location for weather (if mentioned)
        elif action_name == "getWeather":
            # Look for common city names or location indicators
            location_keywords = ['in', 'at', 'for']
            for keyword in location_keywords:
                if keyword in phrase.lower():
                    parts = phrase.lower().split(keyword)
                    if len(parts) > 1:
                        potential_location_parts = parts[1].strip().split()
                        if potential_location_parts:
                            potential_location = potential_location_parts[0]
                            if len(potential_location) > 2:
                                expected_params['location'] = potential_location
                            break
        
        return expected_params
    
    def run_action_test(self, action_name: str, action_info: Dict, phrases: List[str], 
                       iterations: int) -> Tuple[bool, Dict]:
        """Run a test on a specific action with its phrases.
        
        Tests if the target action is selected (other actions may also be selected).
        
        Args:
            action_name: Name of the action being tested
            action_info: Information about the action (description, etc.)
            phrases: List of test phrases for this action
            iterations: Number of times to test each phrase
            
        Returns:
            Tuple of (success: bool, results: dict)
        """
        total_correct = 0
        total_tests = 0
        results = {}
        
        print(f"\n🧪 {action_name} Action Test")
        print(f"Chat Model: {self.model}")
        if self.analysis_model != self.model:
            print(f"Analysis Model: {self.analysis_model}")
        else:
            print("Using same model for analysis and chat")
        print("Mode: Multi-action selection (target action must be selected)")
        print("=" * 80)
        
        for phrase in phrases:
            phrase_correct = 0
            parameter_correct = 0
            expected_params = self.extract_expected_parameters(phrase, action_name)
            
            # Track secondary actions per iteration for this phrase
            secondary_actions_per_iteration = []
            
            for i in range(iterations):
                try:
                    # Clear any previous logs
                    clear_action_logs()
                    
                    # Run the multi-action analysis
                    selected_actions = self.analysis_engine.select_all_applicable_actions(phrase)
                    
                    # Check if target action was selected and track secondary actions
                    action_found = False
                    params_match = False
                    iteration_secondary_actions = []
                    
                    for selected_action, parameters in selected_actions:
                        if selected_action == action_name:
                            action_found = True
                            phrase_correct += 1
                            
                            # Check parameters if expected
                            if expected_params:
                                params_match = True
                                for param_name, expected_value in expected_params.items():
                                    if param_name in parameters:
                                        actual_value = parameters[param_name]
                                        # For numbers, check if they're close enough
                                        if isinstance(expected_value, (int, float)):
                                            try:
                                                actual_float = float(actual_value)
                                                if abs(actual_float - expected_value) < 0.001:
                                                    parameter_correct += 1
                                                else:
                                                    params_match = False
                                            except:
                                                params_match = False
                                        # For strings, check exact match
                                        elif str(actual_value) == str(expected_value):
                                            parameter_correct += 1
                                        else:
                                            params_match = False
                                    else:
                                        params_match = False
                        else:
                            # This is a secondary action
                            iteration_secondary_actions.append(selected_action)
                    
                    secondary_actions_per_iteration.append(iteration_secondary_actions)
                    total_tests += 1
                    
                except Exception as e:
                    print(f"❌ Error testing phrase iteration {i+1}: {e}")
                    secondary_actions_per_iteration.append([])
                    continue
            
            # Calculate secondary action frequencies
            secondary_action_counts = {}
            for iteration_actions in secondary_actions_per_iteration:
                for action in iteration_actions:
                    secondary_action_counts[action] = secondary_action_counts.get(action, 0) + 1
            
            success_rate = (phrase_correct / iterations) * 100 if iterations > 0 else 0
            param_success_rate = (parameter_correct / iterations) * 100 if iterations > 0 and expected_params else 100
            
            results[phrase] = {
                'correct': phrase_correct,
                'total': iterations,
                'success_rate': success_rate,
                'parameter_success_rate': param_success_rate,
                'expected_params': expected_params,
                'secondary_action_counts': secondary_action_counts,
                'secondary_actions_per_iteration': secondary_actions_per_iteration
            }
            total_correct += phrase_correct
            
            # Print individual results
            phrase_display = phrase[:50] + '...' if len(phrase) > 50 else phrase
            print(f"Phrase: '{phrase_display}'")
            print(f"Target Action Selected: {phrase_correct}/{iterations} ({success_rate:.1f}%)")
            if expected_params:
                print(f"Parameter Success: {parameter_correct}/{iterations} ({param_success_rate:.1f}%)")
                print(f"Expected params: {expected_params}")
            if secondary_action_counts:
                print(f"Secondary actions triggered:")
                for action, count in secondary_action_counts.items():
                    print(f"  - {action}: {count}/{iterations} times")
            print("-" * 40)
        
        overall_success_rate = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        print(f"Overall Success Rate: {total_correct}/{total_tests} ({overall_success_rate:.1f}%)")
        
        test_passed = overall_success_rate >= 60.0
        return test_passed, {
            'action_name': action_name,
            'action_description': action_info.get('description', 'No description'),
            'total_correct': total_correct,
            'total_tests': total_tests,
            'success_rate': overall_success_rate,
            'phrase_results': results
        }
    
    def create_action_success_chart(self, action_name: str, results: Dict) -> go.Figure:
        """Create a bar chart showing success rate for each phrase of an action.
        
        Args:
            action_name: Name of the action
            results: Test results for the action
            
        Returns:
            Plotly figure object
        """
        phrases = []
        success_rates = []
        colors = []
        
        for phrase, data in results['phrase_results'].items():
            # Truncate long phrases for display
            display_phrase = phrase[:40] + '...' if len(phrase) > 40 else phrase
            phrases.append(display_phrase)
            success_rates.append(data['success_rate'])
            # Color based on success rate
            if data['success_rate'] >= 80:
                colors.append('green')
            elif data['success_rate'] >= 60:
                colors.append('yellow')
            else:
                colors.append('red')
        
        fig = go.Figure(data=[
            go.Bar(
                x=phrases,
                y=success_rates,
                marker_color=colors,
                text=[f"{rate:.1f}%" for rate in success_rates],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Success Rate: %{y:.1f}%<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=f"{action_name} - Success Rate by Phrase",
            xaxis_title="Test Phrase",
            yaxis_title="Success Rate (%)",
            yaxis_range=[0, 110],
            showlegend=False,
            height=400,
            margin=dict(b=100),
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_secondary_actions_chart(self, action_name: str, results: Dict) -> go.Figure:
        """Create a grouped bar chart showing secondary actions triggered for each phrase.
        
        Args:
            action_name: Name of the action
            results: Test results for the action
            
        Returns:
            Plotly figure object
        """
        # Collect all unique secondary actions across all phrases
        all_secondary_actions = set()
        for phrase_data in results['phrase_results'].values():
            all_secondary_actions.update(phrase_data['secondary_action_counts'].keys())
        
        if not all_secondary_actions:
            # No secondary actions triggered - create an empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="No secondary actions were triggered for any test phrase",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                title=f"{action_name} - Secondary Actions Triggered",
                height=400,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig
        
        # Prepare data for grouped bar chart
        phrases = []
        traces = []
        
        for phrase, data in results['phrase_results'].items():
            display_phrase = phrase[:30] + '...' if len(phrase) > 30 else phrase
            phrases.append(display_phrase)
        
        # Create a trace for each secondary action
        for secondary_action in sorted(all_secondary_actions):
            counts = []
            for phrase_data in results['phrase_results'].values():
                count = phrase_data['secondary_action_counts'].get(secondary_action, 0)
                total = phrase_data['total']
                # Store as percentage
                percentage = (count / total * 100) if total > 0 else 0
                counts.append(percentage)
            
            traces.append(go.Bar(
                name=secondary_action,
                x=phrases,
                y=counts,
                text=[f"{c:.0f}%" if c > 0 else "" for c in counts],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>' + f'{secondary_action}: ' + '%{y:.1f}%<extra></extra>'
            ))
        
        fig = go.Figure(data=traces)
        
        fig.update_layout(
            title=f"{action_name} - Secondary Actions Triggered by Phrase",
            xaxis_title="Test Phrase",
            yaxis_title="Trigger Rate (%)",
            barmode='group',
            height=500,
            margin=dict(b=100),
            xaxis_tickangle=-45,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_overall_summary_chart(self, test_results: Dict) -> go.Figure:
        """Create an overall summary chart showing all actions' performance.
        
        Args:
            test_results: All test results
            
        Returns:
            Plotly figure object
        """
        action_names = []
        success_rates = []
        colors = []
        
        for action_name, test_data in test_results.items():
            action_names.append(action_name)
            rate = test_data['results']['success_rate']
            success_rates.append(rate)
            
            # Color based on pass/fail
            if rate >= 60:
                colors.append('green')
            else:
                colors.append('red')
        
        fig = go.Figure(data=[
            go.Bar(
                x=action_names,
                y=success_rates,
                marker_color=colors,
                text=[f"{rate:.1f}%" for rate in success_rates],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Overall Success Rate: %{y:.1f}%<extra></extra>'
            )
        ])
        
        # Add pass threshold line
        fig.add_hline(
            y=60, 
            line_dash="dash", 
            line_color="orange",
            annotation_text="Pass Threshold (60%)"
        )
        
        fig.update_layout(
            title="Overall Vibe Test Results - All Actions",
            xaxis_title="Action",
            yaxis_title="Success Rate (%)",
            yaxis_range=[0, 110],
            showlegend=False,
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def generate_html_report(self, test_results: Dict) -> str:
        """Generate a comprehensive HTML report with all charts and results.
        
        Args:
            test_results: All test results
            
        Returns:
            HTML string containing the full report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Start building the HTML
        html_parts = [
            f"""<!DOCTYPE html>
<html>
<head>
    <title>Vibe Test Report - {timestamp}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        h1 {{
            color: #333;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .model-info {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .model-info h3 {{
            margin-top: 0;
            color: #495057;
        }}
        .model-detail {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
        }}
        .model-label {{
            font-weight: 600;
            color: #6c757d;
        }}
        .action-section {{
            margin: 40px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }}
        .action-header {{
            margin-bottom: 20px;
        }}
        .action-name {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 10px;
        }}
        .action-description {{
            color: #666;
            font-style: italic;
            margin-bottom: 10px;
        }}
        .action-stats {{
            display: flex;
            gap: 20px;
            margin-top: 15px;
        }}
        .stat-box {{
            background: white;
            padding: 10px 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
        .pass {{
            color: #28a745;
        }}
        .fail {{
            color: #dc3545;
        }}
        .chart-container {{
            margin: 20px 0;
        }}
        .summary-section {{
            margin-top: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
        }}
        .summary-title {{
            font-size: 2em;
            margin-bottom: 20px;
            text-align: center;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Vibe Test Report</h1>
        <div class="subtitle">AI Decision-Making Consistency Analysis</div>
        <div class="subtitle">Generated: {timestamp}</div>
        
        <div class="model-info">
            <h3>Test Configuration</h3>
            <div class="model-detail">
                <span class="model-label">Chat Model:</span>
                <span>{self.model}</span>
            </div>
            <div class="model-detail">
                <span class="model-label">Analysis Model:</span>
                <span>{self.analysis_model}</span>
            </div>
            <div class="model-detail">
                <span class="model-label">Test Mode:</span>
                <span>Multi-action selection (target action must be selected)</span>
            </div>
        </div>
"""
        ]
        
        # Add overall summary chart
        summary_chart = self.create_overall_summary_chart(test_results)
        summary_div_id = "overall-summary"
        html_parts.append(f'<div id="{summary_div_id}" class="chart-container"></div>')
        html_parts.append(f'<script>{summary_chart.to_html(div_id=summary_div_id, include_plotlyjs=False)[20:-8]}</script>')
        
        # Add section for each action
        for action_name, test_data in test_results.items():
            results = test_data['results']
            passed = test_data['passed']
            
            html_parts.append(f"""
        <div class="action-section">
            <div class="action-header">
                <div class="action-name">{action_name} {"✅" if passed else "❌"}</div>
                <div class="action-description">{results['action_description']}</div>
                <div class="action-stats">
                    <div class="stat-box">
                        <div class="stat-label">Overall Success Rate</div>
                        <div class="stat-value {'pass' if passed else 'fail'}">{results['success_rate']:.1f}%</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Tests Passed</div>
                        <div class="stat-value">{results['total_correct']}/{results['total_tests']}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Status</div>
                        <div class="stat-value {'pass' if passed else 'fail'}">{'PASS' if passed else 'FAIL'}</div>
                    </div>
                </div>
            </div>
""")
            
            # Add success rate chart
            success_chart = self.create_action_success_chart(action_name, results)
            success_div_id = f"success-{action_name.replace(' ', '-')}"
            html_parts.append(f'<div id="{success_div_id}" class="chart-container"></div>')
            html_parts.append(f'<script>{success_chart.to_html(div_id=success_div_id, include_plotlyjs=False)[20:-8]}</script>')
            
            # Add secondary actions chart
            secondary_chart = self.create_secondary_actions_chart(action_name, results)
            secondary_div_id = f"secondary-{action_name.replace(' ', '-')}"
            html_parts.append(f'<div id="{secondary_div_id}" class="chart-container"></div>')
            html_parts.append(f'<script>{secondary_chart.to_html(div_id=secondary_div_id, include_plotlyjs=False)[20:-8]}</script>')
            
            html_parts.append("</div>")
        
        # Add summary section
        total_actions = len(test_results)
        passed_actions = sum(1 for data in test_results.values() if data['passed'])
        
        html_parts.append(f"""
        <div class="summary-section">
            <div class="summary-title">Test Summary</div>
            <div style="display: flex; justify-content: space-around;">
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Total Actions Tested</div>
                    <div class="stat-value">{total_actions}</div>
                </div>
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Actions Passed</div>
                    <div class="stat-value pass">{passed_actions}</div>
                </div>
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Actions Failed</div>
                    <div class="stat-value fail">{total_actions - passed_actions}</div>
                </div>
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Overall Result</div>
                    <div class="stat-value {'pass' if passed_actions == total_actions else 'fail'}">
                        {'ALL PASS' if passed_actions == total_actions else f'{passed_actions}/{total_actions} PASS'}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Report generated by OllamaPy Vibe Test Runner</p>
            <p>Models: {self.model} (chat) | {self.analysis_model} (analysis)</p>
        </div>
    </div>
</body>
</html>
""")
        
        return ''.join(html_parts)
    
    def save_report(self, test_results: Dict, filename: str = None):
        """Save the HTML report to a file.
        
        Args:
            test_results: All test results
            filename: Optional filename (defaults to timestamped name)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vibe_test_report_{timestamp}.html"
        
        html_content = self.generate_html_report(test_results)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"\n📊 Report saved to: {filename}")
            print(f"   Open in your browser to view interactive charts")
        except Exception as e:
            print(f"\n❌ Error saving report: {e}")
    
    def run_all_tests(self, iterations: int = 1) -> bool:
        """Run all vibe tests for all actions that have test phrases.
        
        Args:
            iterations: Number of iterations per phrase
            
        Returns:
            True if all tests passed, False otherwise
        """
        print(f"🧪 Running vibe tests with multi-action support and visual reporting")
        print(f"Chat model: {self.model}")
        if self.analysis_model != self.model:
            print(f"Analysis model: {self.analysis_model}")
        else:
            print("Using same model for analysis and chat")
        print(f"Analysis mode: Multi-action (target must be selected)")
        print(f"Iterations: {iterations}")
        print("=" * 80)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        print(f"✅ Using chat model: {self.model}")
        if self.analysis_model != self.model:
            print(f"✅ Using analysis model: {self.analysis_model}")
        print(f"🧠 Testing AI's ability to select appropriate actions (multiple allowed)...")
        print(f"📋 Found {len(self.actions_with_tests)} actions with vibe test phrases\n")
        
        if not self.actions_with_tests:
            print("❌ No actions with vibe test phrases found!")
            return False
        
        # Run tests for each action
        test_results = {}
        all_tests_passed = True
        
        for action_name, action_info in self.actions_with_tests.items():
            test_phrases = action_info['vibe_test_phrases']
            
            if not test_phrases:
                print(f"⚠️  Skipping {action_name} - no test phrases defined")
                continue
            
            test_passed, results = self.run_action_test(
                action_name, action_info, test_phrases, iterations
            )
            
            test_results[action_name] = {
                'passed': test_passed,
                'results': results
            }
            
            if not test_passed:
                all_tests_passed = False
        
        # Store results for report generation
        self.all_test_results = test_results
        
        # Generate and save the HTML report
        self.save_report(test_results)
        
        # Final results summary
        print(f"\n📊 Final Test Results:")
        print("=" * 50)
        
        for action_name, test_data in test_results.items():
            status_icon = "✅ PASSED" if test_data['passed'] else "❌ FAILED"
            success_rate = test_data['results']['success_rate']
            print(f"{action_name} Action Test: {status_icon} ({success_rate:.1f}%)")
        
        status_icon = "✅" if all_tests_passed else "❌"
        status_text = "ALL TESTS PASSED" if all_tests_passed else "SOME TESTS FAILED"
        print(f"\nOverall Result: {status_icon} {status_text}")
        
        if not all_tests_passed:
            print("\n💡 Tips for improving results:")
            print("   • Try a different model with --model")
            print("   • Try a different analysis model with --analysis-model")
            print("   • Use a smaller, faster model for analysis (e.g., gemma2:2b)")
            print("   • Increase iterations with -n for better statistics")
            print("   • Ensure Ollama server is running optimally")
            print("   • Check action descriptions and test phrases for clarity")
        
        return all_tests_passed
    
    def run_quick_test(self) -> bool:
        """Run a quick single-iteration test for fast feedback."""
        print("🚀 Running quick vibe test (1 iteration each)...")
        return self.run_all_tests(iterations=1)
    
    def run_statistical_test(self, iterations: int = 5) -> bool:
        """Run a statistical test with multiple iterations."""
        print(f"📊 Running statistical vibe test ({iterations} iterations each)...")
        return self.run_all_tests(iterations=iterations)


def run_vibe_tests(model: str = "gemma3:4b", iterations: int = 1, analysis_model: str = None) -> bool:
    """Convenience function to run vibe tests with visual reporting.
    
    Args:
        model: The model to use for testing
        iterations: Number of iterations per test
        analysis_model: Optional separate model for action analysis (defaults to main model)
        
    Returns:
        True if all tests passed, False otherwise
    """
    runner = VibeTestRunner(model=model, analysis_model=analysis_model)
    return runner.run_all_tests(iterations=iterations)