"""Visual report generation for vibe test results using Plotly."""

from typing import Dict, List, Any
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


class VibeTestReportGenerator:
    """Generates HTML reports with Plotly visualizations for vibe test results."""
    
    def __init__(self, model: str, analysis_model: str):
        """Initialize the report generator.
        
        Args:
            model: The chat model used for testing
            analysis_model: The analysis model used for testing
        """
        self.model = model
        self.analysis_model = analysis_model
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def create_action_success_chart(self, action_name: str, results: Dict) -> str:
        """Create a bar chart showing success rate for each phrase of an action.
        
        Args:
            action_name: Name of the action
            results: Test results for the action
            
        Returns:
            HTML div containing the Plotly chart
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
        
        # Convert to HTML div
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id=f"success-{action_name.replace(' ', '-')}")
    
    def create_secondary_actions_chart(self, action_name: str, results: Dict) -> str:
        """Create a grouped bar chart showing secondary actions triggered for each phrase.
        
        Args:
            action_name: Name of the action
            results: Test results for the action
            
        Returns:
            HTML div containing the Plotly chart
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
            return fig.to_html(full_html=False, include_plotlyjs=False, 
                             div_id=f"secondary-{action_name.replace(' ', '-')}")
        
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
        
        return fig.to_html(full_html=False, include_plotlyjs=False, 
                         div_id=f"secondary-{action_name.replace(' ', '-')}")
    
    def create_overall_summary_chart(self, test_results: Dict) -> str:
        """Create an overall summary chart showing all actions' performance.
        
        Args:
            test_results: All test results
            
        Returns:
            HTML div containing the Plotly chart
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
        
        return fig.to_html(full_html=False, include_plotlyjs=False, div_id="overall-summary")
    
    def generate_html_header(self) -> str:
        """Generate the HTML header with styles and scripts.
        
        Returns:
            HTML header string
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vibe Test Report - {self.timestamp}</title>
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
            flex-wrap: wrap;
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
        .summary-stats {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 20px;
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
        <div class="subtitle">Generated: {self.timestamp}</div>
        
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
    
    def generate_action_section(self, action_name: str, test_data: Dict) -> str:
        """Generate HTML for a single action's results.
        
        Args:
            action_name: Name of the action
            test_data: Test data for the action
            
        Returns:
            HTML string for the action section
        """
        results = test_data['results']
        passed = test_data['passed']
        status_icon = "✅" if passed else "❌"
        pass_class = 'pass' if passed else 'fail'
        
        # Generate charts
        success_chart = self.create_action_success_chart(action_name, results)
        secondary_chart = self.create_secondary_actions_chart(action_name, results)
        
        return f"""
        <div class="action-section">
            <div class="action-header">
                <div class="action-name">{action_name} {status_icon}</div>
                <div class="action-description">{results['action_description']}</div>
                <div class="action-stats">
                    <div class="stat-box">
                        <div class="stat-label">Overall Success Rate</div>
                        <div class="stat-value {pass_class}">{results['success_rate']:.1f}%</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Tests Passed</div>
                        <div class="stat-value">{results['total_correct']}/{results['total_tests']}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Status</div>
                        <div class="stat-value {pass_class}">{'PASS' if passed else 'FAIL'}</div>
                    </div>
                </div>
            </div>
            <div class="chart-container">
                {success_chart}
            </div>
            <div class="chart-container">
                {secondary_chart}
            </div>
        </div>
"""
    
    def generate_summary_section(self, test_results: Dict) -> str:
        """Generate the summary section of the report.
        
        Args:
            test_results: All test results
            
        Returns:
            HTML string for the summary section
        """
        total_actions = len(test_results)
        passed_actions = sum(1 for data in test_results.values() if data['passed'])
        failed_actions = total_actions - passed_actions
        all_passed = passed_actions == total_actions
        
        return f"""
        <div class="summary-section">
            <div class="summary-title">Test Summary</div>
            <div class="summary-stats">
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
                    <div class="stat-value fail">{failed_actions}</div>
                </div>
                <div class="stat-box" style="background: rgba(255,255,255,0.9); color: #333;">
                    <div class="stat-label">Overall Result</div>
                    <div class="stat-value {'pass' if all_passed else 'fail'}">
                        {'ALL PASS' if all_passed else f'{passed_actions}/{total_actions} PASS'}
                    </div>
                </div>
            </div>
        </div>
"""
    
    def generate_footer(self) -> str:
        """Generate the HTML footer.
        
        Returns:
            HTML footer string
        """
        return f"""
        <div class="footer">
            <p>Report generated by OllamaPy Vibe Test Runner</p>
            <p>Models: {self.model} (chat) | {self.analysis_model} (analysis)</p>
        </div>
    </div>
</body>
</html>
"""
    
    def generate_full_report(self, test_results: Dict) -> str:
        """Generate the complete HTML report.
        
        Args:
            test_results: All test results
            
        Returns:
            Complete HTML report as a string
        """
        # Start with header
        html_parts = [self.generate_html_header()]
        
        # Add overall summary chart
        html_parts.append('<div class="chart-container">')
        html_parts.append(self.create_overall_summary_chart(test_results))
        html_parts.append('</div>')
        
        # Add each action section
        for action_name, test_data in test_results.items():
            html_parts.append(self.generate_action_section(action_name, test_data))
        
        # Add summary section
        html_parts.append(self.generate_summary_section(test_results))
        
        # Add footer
        html_parts.append(self.generate_footer())
        
        return ''.join(html_parts)
    
    def save_report(self, test_results: Dict, filename: str = None) -> str:
        """Save the HTML report to a file.
        
        Args:
            test_results: All test results
            filename: Optional filename (defaults to timestamped name)
            
        Returns:
            The filename where the report was saved
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vibe_test_report_{timestamp}.html"
        
        html_content = self.generate_full_report(test_results)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename