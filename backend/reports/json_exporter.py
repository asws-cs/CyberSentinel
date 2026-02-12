from typing import List, Dict, Any

from utils.logger import logger
from utils.helpers import get_timestamp, to_json

class JSONExporter:
    def __init__(self, scan_id: str, target: str, results: List[Dict[str, Any]], risk_assessment: Dict[str, Any]):
        self.scan_id = scan_id
        self.target = target
        self.results = results
        self.risk_assessment = risk_assessment
        self.timestamp = get_timestamp()

    def export(self) -> str:
        """
        Generates a JSON report from the scan data.
        """
        logger.info(f"Generating JSON report for scan ID: {self.scan_id}")
        
        report = {
            "scan_metadata": {
                "scan_id": self.scan_id,
                "target": self.target,
                "timestamp": self.timestamp,
            },
            "risk_summary": self.risk_assessment,
            "scan_results": self.results
        }
        
        try:
            # Use a custom default to handle non-serializable objects gracefully
            return to_json(report)
        except TypeError as e:
            logger.error(f"Error serializing report to JSON: {e}")
            return to_json({"error": "Failed to generate JSON report due to serialization error."})

def generate_json_report(scan_id: str, target: str, results: List[Dict[str, Any]], risk_assessment: Dict[str, Any]) -> str:
    """
    High-level function to generate a JSON report.
    """
    exporter = JSONExporter(scan_id, target, results, risk_assessment)
    return exporter.export()
