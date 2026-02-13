import asyncio
import re
from typing import Dict, Any, List, Optional
from utils.logger import logger
from utils.helpers import run_command
from config import settings

class SSLScanner:
    def __init__(self, target: str, scan_id: Optional[str] = None):
        self.target = target
        self.scan_id = scan_id

    async def scan(self) -> Dict[str, Any]:
        """
        Performs an SSL scan using sslscan.
        """
        logger.info(f"Starting SSL scan on {self.target}", extra={"scan_id": self.scan_id})
        command = f"{settings.SSLSCAN_PATH} --no-colour {self.target}"
        
        stdout, stderr = await run_command(command)
        
        if stderr:
            logger.error(f"SSLScan returned an error for {self.target}: {stderr}", extra={"scan_id": self.scan_id})

        return self._parse_results(stdout)

    def _parse_results(self, scan_output: str) -> Dict[str, Any]:
        """
        Parses the text output from sslscan into a structured format.
        """
        results: Dict[str, Any] = {
            "target": self.target,
            "sslv2_enabled": False,
            "sslv3_enabled": False,
            "tlsv1_0_enabled": False,
            "tlsv1_1_enabled": False,
            "heartbleed_vulnerable": False,
            "supported_ciphers": [],
            "vulnerabilities": []
        }

        if "SSLv2" in scan_output and "enabled" in scan_output:
            results["sslv2_enabled"] = True
            results["vulnerabilities"].append("SSLv2 is enabled, which is insecure.")
        if "SSLv3" in scan_output and "enabled" in scan_output:
            results["sslv3_enabled"] = True
            results["vulnerabilities"].append("SSLv3 is enabled, which is insecure.")
        if "TLSv1.0" in scan_output and "enabled" in scan_output:
            results["tlsv1_0_enabled"] = True
            results["vulnerabilities"].append("TLSv1.0 is enabled, which is considered weak.")
        if "TLSv1.1" in scan_output and "enabled" in scan_output:
            results["tlsv1_1_enabled"] = True
            results["vulnerabilities"].append("TLSv1.1 is enabled, which is considered weak.")
            
        if "Heartbleed" in scan_output and "vulnerable" in scan_output:
            results["heartbleed_vulnerable"] = True
            results["vulnerabilities"].append("Vulnerable to Heartbleed attack.")

        # Extract accepted ciphers
        cipher_pattern = re.compile(r"Accepted\s+(TLSv[\d.]+)\s+[\d\s]+bits\s+(.*)")
        for line in scan_output.splitlines():
            match = cipher_pattern.search(line)
            if match:
                results["supported_ciphers"].append(f"{match.group(1)}: {match.group(2).strip()}")

        logger.info(f"SSL scan finished for {self.target}.", extra={"scan_id": self.scan_id})
        return results

async def run_ssl_scan(target: str, scan_id: Optional[str] = None) -> Dict[str, Any]:
    """
    High-level function to run an SSL scan.
    """
    scanner = SSLScanner(target, scan_id)
    return await scanner.scan()
