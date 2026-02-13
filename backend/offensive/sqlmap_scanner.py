import asyncio
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import os
import tempfile
import shutil # Import shutil for rmtree

from config import settings
from tools.subprocess_stream import SubprocessStreamer
from utils.logger import logger

class SQLMapScanner:
    def __init__(self, target: str, level: int = 1, risk: int = 1, aggressive: bool = False, scan_id: Optional[str] = None):
        self.target = target
        self.level = level
        self.risk = risk
        self.aggressive = aggressive
        self.scan_id = scan_id
        self.output_dir = tempfile.mkdtemp(prefix="sqlmap_")
        self.command = self._build_command()

    def _build_command(self) -> List[str]:
        """Builds the sqlmap command with safe arguments."""
        cmd = [
            settings.SQLMAP_PATH,
            "-u", self.target,
            "--batch",  # Non-interactive
            "--output-dir", self.output_dir,
            "--dump-format=JSON",
            f"--level={self.level}",
            f"--risk={self.risk}",
        ]

        if not self.aggressive:
            cmd.extend([
                "--dbms-fingerprint",
                "--no-cast",
                "--threads=4",
            ])
        else: # Aggressive mode
             cmd.extend([
                "--all", # This is very noisy and can be dangerous
                "--random-agent",
                "--threads=10",
             ])
        
        return cmd

    async def scan(self) -> Dict[str, Any]:
        """
        Runs the sqlmap scan and returns structured JSON results.
        Timeout is handled by the tool_controller.
        """
        logger.info(f"Starting SQLMap scan on {self.target}", extra={"scan_id": self.scan_id})
        
        try:
            # Stream output for live feedback, but we will parse the JSON file for results
            streamer = SubprocessStreamer(self.command)
            async for line in streamer.start():
                logger.debug(f"SQLMap output: {line}", extra={"scan_id": self.scan_id})

            # After command finishes, parse the JSON file for results
            result_file = self._find_json_result()
            if not result_file:
                logger.warning(f"SQLMap scan on {self.target} finished, but no JSON output file was found.", extra={"scan_id": self.scan_id})
                return {"summary": "SQLMap scan completed, but no results found.", "vulnerabilities": []}

            with open(result_file, 'r') as f:
                data = json.load(f)

            vulnerabilities = self._parse_json_output(data)
            
            summary = f"SQLMap scan completed. Found {len(vulnerabilities)} potential vulnerabilities."
            logger.info(summary, extra={"scan_id": self.scan_id})

            return {
                "summary": summary,
                "vulnerabilities": vulnerabilities,
            }

        except FileNotFoundError:
            logger.error(f"SQLMap not found at path: {settings.SQLMAP_PATH}", extra={"scan_id": self.scan_id})
            return {"error": "SQLMap tool not found."}
        except asyncio.TimeoutError:
            logger.warning(f"SQLMap scan for {self.target} timed out.", extra={"scan_id": self.scan_id})
            return {"error": "SQLMap scan timed out."}
        except Exception as e:
            logger.error(f"An error occurred during SQLMap scan: {e}", extra={"scan_id": self.scan_id})
            return {"error": str(e)}
        finally:
            self._cleanup()
            
    def _find_json_result(self) -> str | None:
        """Finds the JSON output file in the sqlmap output directory."""
        target_hostname = urlparse(self.target).hostname
        if not target_hostname:
            return None
        
        # The path is usually output_dir/target_hostname/log.json, but it can vary.
        # Let's search for the 'log' file which contains the JSON data
        for root, _, files in os.walk(self.output_dir):
            for filename in files:
                if filename == "log": # This is the file sqlmap creates with --dump-format=JSON
                    with open(os.path.join(root, filename), 'r') as f:
                         # check if it's a valid json file
                        try:
                            json.load(f)
                            f.seek(0)
                            return os.path.join(root, filename)
                        except json.JSONDecodeError:
                            continue
        return None


    def _parse_json_output(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parses the 'log' file content from sqlmap."""
        parsed_vulns = []
        
        # The 'log' file is a list of JSON objects, one for each sqlmap message
        for entry in data:
            if entry['type'] == 'vulnerable':
                # This is a simplified parser. The actual structure is more complex.
                vuln_data = entry['data']
                parsed_vulns.append({
                    "parameter": vuln_data.get('parameter'),
                    "dbms": vuln_data.get('dbms'),
                    "type": vuln_data.get('title'),
                    "payloads": [item['payload'] for item in vuln_data.get('data', {}).values()],
                })

        return parsed_vulns

    def _cleanup(self):
        """Removes the temporary sqlmap output directory."""
        try:
            shutil.rmtree(self.output_dir)
            logger.debug(f"Cleaned up temporary directory: {self.output_dir}", extra={"scan_id": self.scan_id})
        except Exception as e:
            logger.error(f"Failed to clean up temporary directory {self.output_dir}: {e}", extra={"scan_id": self.scan_id})


async def run_sqlmap_scan(target: str, aggressive: bool = False, scan_id: Optional[str] = None) -> Dict[str, Any]:
    """
    High-level function to run a SQLMap scan.
    """
    scanner = SQLMapScanner(target, aggressive=aggressive, scan_id=scan_id)
    return await scanner.scan()
