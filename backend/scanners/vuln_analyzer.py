from typing import Dict, Any, List
from utils.logger import logger

class VulnerabilityAnalyzer:
    def __init__(self, scan_results: List[Dict[str, Any]]):
        self.scan_results = scan_results
        # In a real application, this would be a comprehensive, up-to-date database.
        self.vulnerability_db = {
            "apache": {
                "2.4.49": "CVE-2021-41773: Path Traversal and File Disclosure",
                "2.4.50": "CVE-2021-42013: Path Traversal and RCE",
            },
            "openssh": {
                "8.5p1": "CVE-2021-28041: Double Free vulnerability",
            },
            "nginx": {
                "1.20.1": "Multiple vulnerabilities in njs module"
            }
        }

    async def analyze(self) -> Dict[str, Any]:
        """
        Analyzes Nmap results to find potential vulnerabilities based on service versions.
        """
        logger.info("Starting vulnerability analysis based on service versions.")
        vulnerabilities_found: List[str] = []

        nmap_results = next((r for r in self.scan_results if r.get("tool_name") == "nmap_scan"), None)

        if not nmap_results or "findings" not in nmap_results:
            logger.info("No Nmap results found to analyze for vulnerabilities.")
            return {"vulnerabilities_found": []}

        findings = nmap_results["findings"]
        for key, value in findings.items():
            if key.startswith("port_") and isinstance(value, dict):
                product = value.get("product", "").lower()
                version = value.get("version", "")
                
                if not product or not version:
                    continue

                # Check for product family (e.g., "Apache httpd" -> "apache")
                for db_product, cves in self.vulnerability_db.items():
                    if db_product in product:
                        if version in cves:
                            vulnerability_info = f"Port {key.split('_')[1]} ({product} {version}): {cves[version]}"
                            vulnerabilities_found.append(vulnerability_info)
                            logger.warning(f"Potential vulnerability found: {vulnerability_info}")
        
        logger.info(f"Vulnerability analysis finished. Found {len(vulnerabilities_found)} potential issues.")
        return {"vulnerabilities_found": vulnerabilities_found}

async def run_vulnerability_analysis(scan_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    High-level function to run a vulnerability analysis.
    """
    analyzer = VulnerabilityAnalyzer(scan_results)
    return await analyzer.analyze()
