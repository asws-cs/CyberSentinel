from typing import List, Dict, Any, Tuple

class RiskEngine:
    def __init__(self, scan_results: List[Dict[str, Any]]):
        self.scan_results = scan_results
        self.total_risk_score = 0
        self.severity = "Low"
        self.risk_breakdown: Dict[str, int] = {}

    def calculate_risk(self) -> Tuple[int, str, Dict[str, int]]:
        """
        Calculates the total risk score and severity based on scan results.
        """
        for result in self.scan_results:
            tool_name = result.get("tool_name", "unknown")
            findings = result.get("findings", {})
            
            risk_score = self._calculate_tool_risk(tool_name, findings)
            self.risk_breakdown[tool_name] = risk_score
            self.total_risk_score += risk_score

        self._determine_severity()
        
        # Clamp score between 0 and 100
        self.total_risk_score = max(0, min(self.total_risk_score, 100))

        return self.total_risk_score, self.severity, self.risk_breakdown

    def _calculate_tool_risk(self, tool_name: str, findings: Dict[str, Any]) -> int:
        """
        Calculates risk for a single tool's output.
        This is a simplified model. A real-world engine would be far more complex.
        """
        score = 0
        if tool_name == "nmap_scan":
            open_ports = findings.get("open_ports", [])
            if any(p in [21, 22, 23, 25, 110, 139, 445] for p in open_ports):
                score += 15
            if 80 in open_ports and 443 not in open_ports:
                score += 10  # HTTP without HTTPS
            score += len(open_ports) * 1 # Add 1 point for each open port
            
        elif tool_name == "ssl_scan":
            if findings.get("vulnerabilities"):
                score += 20 * len(findings.get("vulnerabilities", []))

        elif tool_name == "header_analysis":
            missing_headers = findings.get("missing_headers", [])
            score += len(missing_headers) * 5

        elif tool_name == "sql_injection_test":
            if findings.get("vulnerable"):
                score += 80
                
        elif tool_name == "xss_test":
            if findings.get("vulnerable"):
                score += 60
                
        elif tool_name == "dir_discovery":
            # Risk based on the sensitivity of discovered paths
            sensitive_paths = ["/admin", "/login", "/.git", "/.env"]
            discovered = findings.get("discovered_paths", [])
            if any(p in path for p in sensitive_paths for path in discovered):
                score += 25
        return score

    def _determine_severity(self):
        """
        Determines the overall severity level based on the total risk score.
        """
        if self.total_risk_score >= 81:
            self.severity = "Critical"
        elif self.total_risk_score >= 61:
            self.severity = "High"
        elif self.total_risk_score >= 31:
            self.severity = "Medium"
        else:
            self.severity = "Low"

def get_risk_assessment(scan_results: List[Dict[str, Any]]) -> Tuple[int, str, Dict[str, int]]:
    """
    Analyzes a list of scan results and returns a risk assessment.
    """
    engine = RiskEngine(scan_results)
    return engine.calculate_risk()
