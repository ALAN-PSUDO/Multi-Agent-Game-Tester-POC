"""Report generation utilities."""

from typing import Dict, Any
import json
from datetime import datetime
from pathlib import Path
from loguru import logger


class ReportGenerator:
    """Generate reports in various formats."""
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_json_report(self, report_data: Dict[str, Any], filename: str = None) -> str:
        """
        Generate JSON report.
        
        Args:
            report_data: Report data dictionary
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to generated report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_test_report_{timestamp}.json"
            
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"JSON report saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate JSON report: {e}")
            return ""
            
    def generate_text_report(self, report_data: Dict[str, Any], filename: str = None) -> str:
        """
        Generate human-readable text report.
        
        Args:
            report_data: Report data dictionary
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to generated report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_test_report_{timestamp}.txt"
            
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("MULTI-AGENT GAME TESTING REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                # Game information
                f.write(f"Game URL: {report_data.get('game_url', 'N/A')}\n")
                f.write(f"Test Time: {datetime.fromtimestamp(report_data.get('timestamp', 0))}\n")
                f.write(f"Duration: {report_data.get('elapsed_time', 0):.2f} seconds\n\n")
                
                # Summary
                f.write("-" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("-" * 80 + "\n")
                summary = report_data.get('summary', {})
                f.write(f"Game Type: {summary.get('game_type', 'Unknown')}\n")
                f.write(f"Success Rate: {summary.get('overall_success_rate', 0):.2%}\n")
                f.write(f"Health Score: {summary.get('health_score', 0):.1f}/100\n")
                f.write(f"Recommendation: {summary.get('recommendation', 'N/A')}\n\n")
                
                # Phase results
                phases = report_data.get('phases', {})
                
                f.write("-" * 80 + "\n")
                f.write("EXPLORATION PHASE\n")
                f.write("-" * 80 + "\n")
                exploration = phases.get('exploration', {})
                f.write(f"Elements Discovered: {exploration.get('elements_discovered', 0)}\n")
                f.write(f"Game Controls Found: {exploration.get('game_controls', 0)}\n\n")
                
                f.write("-" * 80 + "\n")
                f.write("EXECUTION PHASE\n")
                f.write("-" * 80 + "\n")
                execution = phases.get('execution', {})
                f.write(f"Total Actions: {execution.get('total_actions', 0)}\n")
                f.write(f"Successful Actions: {execution.get('successful_actions', 0)}\n")
                f.write(f"Success Rate: {execution.get('success_rate', 0):.2%}\n\n")
                
                f.write("-" * 80 + "\n")
                f.write("VALIDATION PHASE\n")
                f.write("-" * 80 + "\n")
                validation = phases.get('validation', {})
                f.write(f"Health Score: {validation.get('health_score', 0):.1f}/100\n")
                f.write(f"Anomalies Detected: {validation.get('anomalies', 0)}\n\n")
                
                f.write("-" * 80 + "\n")
                f.write("LEARNING PHASE\n")
                f.write("-" * 80 + "\n")
                learning = phases.get('learning', {})
                f.write(f"New Patterns Learned: {learning.get('patterns_learned', 0)}\n")
                f.write(f"Total Patterns in Database: {learning.get('total_patterns', 0)}\n\n")
                
                f.write("=" * 80 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 80 + "\n")
            
            logger.info(f"Text report saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate text report: {e}")
            return ""
            
    def generate_html_report(self, report_data: Dict[str, Any], filename: str = None) -> str:
        """
        Generate HTML report.
        
        Args:
            report_data: Report data dictionary
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to generated report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_test_report_{timestamp}.html"
            
        filepath = self.output_dir / filename
        
        try:
            summary = report_data.get('summary', {})
            phases = report_data.get('phases', {})
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Game Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        .metric {{ display: inline-block; margin: 15px; padding: 15px; background-color: #f9f9f9; border-radius: 5px; min-width: 200px; }}
        .metric-label {{ font-weight: bold; color: #666; }}
        .metric-value {{ font-size: 24px; color: #4CAF50; margin-top: 5px; }}
        .success {{ color: #4CAF50; }}
        .warning {{ color: #FF9800; }}
        .error {{ color: #F44336; }}
        .phase {{ margin: 20px 0; padding: 15px; background-color: #fafafa; border-left: 4px solid #4CAF50; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Multi-Agent Game Testing Report</h1>
        
        <div class="metric">
            <div class="metric-label">Game URL</div>
            <div style="margin-top: 5px; font-size: 14px;">{report_data.get('game_url', 'N/A')}</div>
        </div>
        
        <div class="metric">
            <div class="metric-label">Test Duration</div>
            <div class="metric-value">{report_data.get('elapsed_time', 0):.2f}s</div>
        </div>
        
        <h2>Summary</h2>
        <div class="metric">
            <div class="metric-label">Game Type</div>
            <div class="metric-value" style="font-size: 18px;">{summary.get('game_type', 'Unknown')}</div>
        </div>
        
        <div class="metric">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value {'success' if summary.get('overall_success_rate', 0) > 0.7 else 'warning'}">{summary.get('overall_success_rate', 0):.1%}</div>
        </div>
        
        <div class="metric">
            <div class="metric-label">Health Score</div>
            <div class="metric-value {'success' if summary.get('health_score', 0) > 70 else 'warning'}">{summary.get('health_score', 0):.1f}/100</div>
        </div>
        
        <h2>Phase Results</h2>
        
        <div class="phase">
            <h3>Exploration Phase</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Elements Discovered</td>
                    <td>{phases.get('exploration', {}).get('elements_discovered', 0)}</td>
                </tr>
                <tr>
                    <td>Game Controls Found</td>
                    <td>{phases.get('exploration', {}).get('game_controls', 0)}</td>
                </tr>
            </table>
        </div>
        
        <div class="phase">
            <h3>Execution Phase</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Actions</td>
                    <td>{phases.get('execution', {}).get('total_actions', 0)}</td>
                </tr>
                <tr>
                    <td>Successful Actions</td>
                    <td>{phases.get('execution', {}).get('successful_actions', 0)}</td>
                </tr>
                <tr>
                    <td>Success Rate</td>
                    <td>{phases.get('execution', {}).get('success_rate', 0):.1%}</td>
                </tr>
            </table>
        </div>
        
        <div class="phase">
            <h3>Validation Phase</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Health Score</td>
                    <td>{phases.get('validation', {}).get('health_score', 0):.1f}/100</td>
                </tr>
                <tr>
                    <td>Anomalies Detected</td>
                    <td>{phases.get('validation', {}).get('anomalies', 0)}</td>
                </tr>
            </table>
        </div>
        
        <h2>Recommendation</h2>
        <p style="padding: 15px; background-color: #e8f5e9; border-left: 4px solid #4CAF50; margin: 20px 0;">
            {summary.get('recommendation', 'No recommendation available')}
        </p>
    </div>
</body>
</html>
"""
            
            with open(filepath, 'w') as f:
                f.write(html_content)
            
            logger.info(f"HTML report saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return ""
