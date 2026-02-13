import asyncio
from typing import Dict, Any, List, Optional
import re

from config import settings
from tools.subprocess_stream import SubprocessStreamer
from utils.logger import logger

class XSSerScanner:
    def __init__(self, target: str, aggressive: bool = False, scan_id: Optional[str] = None):
        self.target = target
        self.aggressive = aggressive
        self.scan_id = scan_id
        self.command = self._build_command()

    def _build_command(self) -> List[str]:
        """Builds the XSSer command with appropriate arguments."""
        cmd = [
            settings.XSSER_PATH,
            "-u", self.target,
            "--no-head", # Don't print header
        ]

        if not self.aggressive:
            cmd.extend([
                # Focus on reflected XSS
                "--Crawl", # Crawl the site, but with a small depth
                "--depth=2",
                "--Cw=1" # crawl width
            ])
        else: # Aggressive mode
             cmd.extend([
                "--Crawl",
                "--depth=4",
                "--Cw=2",
                "--XSS", # Check for XSS in every link
                "--DS", # Check for DOM XSS
             ])
        
        return cmd

    async def scan(self) -> Dict[str, Any]:
        """
        Runs the XSSer scan and streams the output.
        Returns structured data of found vulnerabilities.
        """
        logger.info(f"Starting XSSer scan on {self.target}", extra={"scan_id": self.scan_id})
        
        found_vulns: List[Dict[str, Any]] = []
        
        try:
            streamer = SubprocessStreamer(self.command)
            async for line in streamer.start():
                parsed_line = self._parse_output(line)
                if parsed_line:
                    found_vulns.append(parsed_line)
                    logger.debug(f"XSSer found: {parsed_line}", extra={"scan_id": self.scan_id})

            summary = f"XSSer scan completed. Found {len(found_vulns)} potential vulnerabilities."
            logger.info(summary, extra={"scan_id": self.scan_id})

            return {
                "summary": summary,
                "vulnerabilities": found_vulns,
            }

        except FileNotFoundError:
            logger.error(f"XSSer not found at path: {settings.XSSER_PATH}", extra={"scan_id": self.scan_id})
            return {"error": "XSSer tool not found."}
        except asyncio.TimeoutError:
            logger.warning(f"XSSer scan for {self.target} timed out.", extra={"scan_id": self.scan_id})
            return {"error": "XSSer scan timed out."}
        except Exception as e:
            logger.error(f"An error occurred during XSSer scan: {e}", extra={"scan_id": self.scan_id})
            return {"error": str(e)}

    def _parse_output(self, line: str) -> Dict[str, Any] | None:
        """Parses a single line of XSSer output."""
        line = line.strip()
        
        # Look for lines indicating a vulnerability
        # Example: [+] Payload: ...
        if line.startswith("[+] Payload:"):
            payload = line.replace("[+] Payload:", "").strip()
            return {"type": "Reflected XSS", "payload": payload}
            
        # Example: DOM XSS found in ...
        if "DOM XSS found" in line:
            return {"type": "DOM XSS", "details": line}
            
        return None


async def run_xsser_scan(target: str, aggressive: bool = False, scan_id: Optional[str] = None) -> Dict[str, Any]:
    """
    High-level function to run an XSSer scan.
    """
    scanner = XSSerScanner(target, aggressive=aggressive, scan_id=scan_id)
    return await scanner.scan()
