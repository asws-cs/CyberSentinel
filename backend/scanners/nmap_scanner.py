import nmap
import asyncio
from typing import Dict, Any, Optional
from utils.logger import logger

class NmapScanner:
    def __init__(self, target: str, options: str = "-sV -T4", scan_id: Optional[str] = None):
        self.target = target
        self.options = options
        self.scan_id = scan_id
        self.port_scanner = nmap.PortScanner()

    async def scan(self) -> Dict[str, Any]:
        """
        Performs an Nmap scan asynchronously.
        """
        logger.info(f"Starting Nmap scan on {self.target} with options '{self.options}'", extra={"scan_id": self.scan_id})
        try:
            # Run the scan in a separate thread to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, self._run_scan
            )
            
            return self._parse_results()
        except Exception as e:
            logger.error(f"An error occurred during Nmap scan: {e}", extra={"scan_id": self.scan_id})
            return {"error": str(e)}

    def _run_scan(self):
        """
        Synchronous method to run the Nmap scan.
        """
        self.port_scanner.scan(self.target, arguments=self.options)

    def _parse_results(self) -> Dict[str, Any]:
        """
        Parses the Nmap scan results.
        """
        results: Dict[str, Any] = {"host": self.target, "protocols": [], "open_ports": []}
        
        for host in self.port_scanner.all_hosts():
            results["hostname"] = self.port_scanner[host].hostname()
            for proto in self.port_scanner[host].all_protocols():
                results["protocols"].append(proto)
                ports = self.port_scanner[host][proto].keys()
                for port in sorted(ports):
                    state = self.port_scanner[host][proto][port]['state']
                    if state == 'open':
                        service_info = self.port_scanner[host][proto][port]
                        results["open_ports"].append(port)
                        results[f"port_{port}"] = {
                            "state": state,
                            "name": service_info.get("name", ""),
                            "product": service_info.get("product", ""),
                            "version": service_info.get("version", ""),
                            "extrainfo": service_info.get("extrainfo", ""),
                            "cpe": service_info.get("cpe", ""),
                        }
        
        logger.info(f"Nmap scan finished for {self.target}. Found {len(results['open_ports'])} open ports.", extra={"scan_id": self.scan_id})
        return results

async def run_nmap_scan(target: str, options: str = "-sV -T4", scan_id: Optional[str] = None) -> Dict[str, Any]:
    """
    High-level function to run an Nmap scan.
    """
    scanner = NmapScanner(target, options, scan_id)
    return await scanner.scan()
