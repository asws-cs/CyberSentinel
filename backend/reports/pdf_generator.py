import weasyprint
import asyncio
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import List, Dict, Any
import os

from utils.logger import logger
from utils.helpers import get_timestamp

class PDFGenerator:
    def __init__(self, scan_id: str, target: str, results: List[Dict[str, Any]], risk_assessment: Dict[str, Any]):
        self.scan_id = scan_id
        self.target = target
        self.results = results
        self.risk_assessment = risk_assessment
        self.timestamp = get_timestamp()
        
        # Setup Jinja2 environment
        # In a real app, templates would be in a dedicated 'templates' folder
        template_dir = os.path.dirname(__file__)
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _create_html_template(self):
        """ Creates a basic HTML template file for the report. """
        template_string = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CyberSentinel Scan Report</title>
            <style>
                body { font-family: sans-serif; margin: 2em; color: #333; }
                h1, h2, h3 { color: #1a237e; border-bottom: 2px solid #1a237e; padding-bottom: 5px; }
                h1 { font-size: 2.5em; text-align: center; margin-bottom: 1em; }
                h2 { font-size: 1.8em; margin-top: 1.5em; }
                .summary { background-color: #e8eaf6; padding: 1.5em; border-radius: 8px; margin-bottom: 2em; }
                .risk-score { text-align: center; }
                .risk-score .score { font-size: 4em; font-weight: bold; color: {{ risk_color }}; }
                .risk-score .severity { font-size: 1.5em; color: {{ risk_color }}; }
                .metadata { word-wrap: break-word; }
                .tool-section { margin-top: 1.5em; border: 1px solid #ccc; border-radius: 8px; overflow: hidden; }
                .tool-header { background-color: #3f51b5; color: white; padding: 10px; font-size: 1.2em; }
                .tool-content { padding: 15px; }
                pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }
                ul { padding-left: 20px; }
                li { margin-bottom: 0.5em; }
            </style>
        </head>
        <body>
            <h1>CyberSentinel Scan Report</h1>
            <div class="summary">
                <h2>Executive Summary</h2>
                <div class="metadata">
                    <p><strong>Target:</strong> {{ target }}</p>
                    <p><strong>Scan ID:</strong> {{ scan_id }}</p>
                    <p><strong>Timestamp:</strong> {{ timestamp }}</p>
                </div>
                <div class="risk-score">
                    <div class="score">{{ risk_assessment.total_risk_score }}</div>
                    <div class="severity">{{ risk_assessment.severity }}</div>
                </div>
            </div>

            <h2>Technical Findings</h2>
            {% for result in results %}
            <div class="tool-section">
                <div class="tool-header">{{ result.tool_name | title | replace('_', ' ') }}</div>
                <div class="tool-content">
                    {% if result.error %}
                        <p><strong>Error:</strong> {{ result.error }}</p>
                    {% elif result.findings %}
                        <ul>
                        {% for key, value in result.findings.items() %}
                           <li><strong>{{ key | title | replace('_', ' ') }}:</strong>
                           {% if value is mapping %}
                                <ul>
                                {% for sub_key, sub_value in value.items() %}
                                    <li><strong>{{ sub_key | title }}:</strong> <pre>{{ sub_value | tojson(indent=2) }}</pre></li>
                                {% endfor %}
                                </ul>
                           {% elif value is iterable and value is not string %}
                                <ul>
                                {% for item in value %}
                                    <li><pre>{{ item }}</pre></li>
                                {% endfor %}
                                </ul>
                           {% else %}
                                <pre>{{ value }}</pre>
                           {% endif %}
                           </li>
                        {% endfor %}
                        </ul>
                    {% else %}
                        <p>No findings for this tool.</p>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </body>
        </html>
        """
        with open(os.path.join(os.path.dirname(__file__), "report_template.html"), "w") as f:
            f.write(template_string)

    def _get_risk_color(self, severity: str) -> str:
        return {
            "Critical": "#d32f2f",
            "High": "#f57c00",
            "Medium": "#fbc02d",
            "Low": "#388e3c",
        }.get(severity, "#757575")

    def generate(self) -> bytes:
        logger.info(f"Generating PDF report for scan ID: {self.scan_id}")
        self._create_html_template()
        template = self.jinja_env.get_template("report_template.html")
        
        render_context = {
            "scan_id": self.scan_id,
            "target": self.target,
            "timestamp": self.timestamp,
            "results": self.results,
            "risk_assessment": self.risk_assessment,
            "risk_color": self._get_risk_color(self.risk_assessment.get("severity", "Low"))
        }

        html_out = template.render(render_context)
        
        try:
            pdf_bytes = weasyprint.HTML(string=html_out).write_pdf()
            # Clean up template file
            os.remove(os.path.join(os.path.dirname(__file__), "report_template.html"))
            return pdf_bytes
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            # Clean up template file even on error
            os.remove(os.path.join(os.path.dirname(__file__), "report_template.html"))
            raise


async def generate_pdf_report(scan_id: str, target: str, results: List[Dict[str, Any]], risk_assessment: Dict[str, Any]) -> bytes:
    """
    High-level function to generate a PDF report.
    """
    generator = PDFGenerator(scan_id, target, results, risk_assessment)
    # Run synchronous PDF generation in an executor to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generator.generate)
