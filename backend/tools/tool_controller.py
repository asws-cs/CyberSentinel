import asyncio
import uuid
import shutil
import json # Import json for message serialization
from typing import List, Dict, Any, Set

from utils.logger import logger
from tools.live_output import get_live_output_publisher
from tools.subprocess_stream import SubprocessStreamer

# Import all scanner and offensive functions
from scanners import nmap_scanner, ssl_scanner, header_analyzer, vuln_analyzer
from offensive import sql_tester, dir_discovery, xss_tester, sqlmap_scanner, xss_scanner
from config import settings

AVAILABLE_TOOLS: Set[str] = set()

def check_tool_availability():
    """Checks for the presence of required command-line tools."""
    global AVAILABLE_TOOLS
    tool_paths = {
        "nmap_scan": settings.NMAP_PATH,
        "ssl_scan": settings.SSLSCAN_PATH,
        "nikto_scan": settings.NIKTO_PATH,
        "sqlmap_scan": settings.SQLMAP_PATH,
        "xsser_scan": settings.XSSER_PATH,
    }
    for tool_name, path in tool_paths.items():
        if shutil.which(path):
            AVAILABLE_TOOLS.add(tool_name)
        else:
            logger.warning(f"Tool '{tool_name}' not found at path: {path}. This tool will be unavailable.")

# Run check on startup
check_tool_availability()


class ToolController:
    def __init__(self, scan_id: str):
        self.scan_id = scan_id
        # Change channel name to match LiveFeedHandler
        self.output_channel = f"scan_live_feed:{self.scan_id}" 
        self.publisher = get_live_output_publisher()
        self.results: List[Dict[str, Any]] = []

        # Mapping of tool names to their functions
        self.tool_functions = {
            "nmap_scan": self._run_nmap,
            "ssl_scan": self._run_sslscan,
            "header_analysis": header_analyzer.run_header_analysis,
            "vulnerability_analysis": self._run_vuln_analysis,
            "sql_injection_test": sql_tester.run_sql_test,
            "xss_test": xss_tester.run_xss_test,
            "dir_discovery": self._run_dir_discovery,
            "nikto_scan": self._run_nikto,
            "sqlmap_scan": self._run_sqlmap,
            "xsser_scan": self._run_xsser,
        }

    async def run_pipeline(self, pipeline: List[Dict[str, Any]], timeout: int = 3600):
        logger.info(f"[{self.scan_id}] Starting tool pipeline execution with timeout {timeout}s.", extra={"scan_id": self.scan_id})
        await self.publisher.publish(self.output_channel, json.dumps({"level": "INFO", "message": f"Starting scan {self.scan_id}..."}))

        try:
            async with asyncio.timeout(timeout):
                for tool_spec in pipeline:
                    tool_name = tool_spec["name"]
                    params = tool_spec["params"]
                    
                    if tool_name not in self.tool_functions:
                        logger.warning(f"[{self.scan_id}] Tool '{tool_name}' not recognized. Skipping.", extra={"scan_id": self.scan_id})
                        await self.publisher.publish(self.output_channel, json.dumps({"level": "WARNING", "message": f"Tool '{tool_name}' not recognized. Skipping."}))
                        continue
                    
                    if tool_name in ["nmap_scan", "ssl_scan", "nikto_scan", "sqlmap_scan", "xsser_scan"] and tool_name not in AVAILABLE_TOOLS:
                        logger.warning(f"[{self.scan_id}] Tool '{tool_name}' is not available. Skipping.", extra={"scan_id": self.scan_id})
                        await self.publisher.publish(self.output_channel, json.dumps({"level": "WARNING", "message": f"SKIPPED: Tool '{tool_name}' is not installed or configured correctly."}))
                        continue

                    await self.publisher.publish(self.output_channel, json.dumps({"level": "INFO", "message": f"\n--- Running {tool_name} ---"}))
                    logger.info(f"[{self.scan_id}] Running tool: {tool_name} with params: {params}", extra={"scan_id": self.scan_id})

                    try:
                        if tool_name == "vulnerability_analysis":
                            # Pass scan_id to vuln_analyzer
                            result_data = await self.tool_functions[tool_name](self.results, self.scan_id)
                        else:
                            # Pass scan_id to individual tool functions
                            params_with_scan_id = {**params, "scan_id": self.scan_id}
                            result_data = await self.tool_functions[tool_name](**params_with_scan_id)
                        
                        result = {"tool_name": tool_name, "findings": result_data}
                        self.results.append(result)

                        summary = result_data.get("summary", f"Completed. Found {len(result_data.get('vulnerabilities', []))} issues.")
                        await self.publisher.publish(self.output_channel, json.dumps({"level": "INFO", "message": f"{tool_name}: {summary}"}))

                    except asyncio.TimeoutError:
                        error_msg = f"Tool '{tool_name}' timed out."
                        logger.warning(f"[{self.scan_id}] {error_msg}", extra={"scan_id": self.scan_id})
                        await self.publisher.publish(self.output_channel, json.dumps({"level": "ERROR", "message": f"ERROR: {error_msg}"}))
                        self.results.append({"tool_name": tool_name, "error": "Timeout"})
                    except Exception as e:
                        error_msg = f"Error running tool '{tool_name}': {e}"
                        logger.error(f"[{self.scan_id}] {error_msg}", exc_info=True, extra={"scan_id": self.scan_id})
                        await self.publisher.publish(self.output_channel, json.dumps({"level": "ERROR", "message": f"ERROR: {error_msg}"}))
                        self.results.append({"tool_name": tool_name, "error": str(e)})

        except asyncio.TimeoutError:
            logger.warning(f"[{self.scan_id}] The entire scan pipeline timed out after {timeout} seconds.", extra={"scan_id": self.scan_id})
            await self.publisher.publish(self.output_channel, json.dumps({"level": "WARNING", "message": f"--- SCAN TIMEOUT: The scan exceeded the maximum duration of {timeout} seconds. ---"}))

        await self.publisher.publish(self.output_channel, json.dumps({"level": "INFO", "message": f"--- Scan {self.scan_id} finished ---"}))
        logger.info(f"[{self.scan_id}] Tool pipeline execution finished.", extra={"scan_id": self.scan_id})
        return self.results
        
    async def _stream_cli_tool(self, command: List[str], tool_name: str, scan_id: str):
        """ Helper to stream CLI tool output and return a placeholder result. """
        streamer = SubprocessStreamer(command)
        async for line in streamer.start():
            # Only publish specific output lines from cli tools, not all raw output
            # Need to refine filtering here, for now pass all but in real implementation, filter
            # Also, wrap in JSON as expected by frontend
            await self.publisher.publish(self.output_channel, json.dumps({"level": "DEBUG", "message": line}))
        return {"summary": f"{tool_name} scan completed. Check logs for details."}

    async def _run_nmap(self, target: str, options: str, scan_id: str):
        # nmap_scanner has its own streaming logic, so we don't use _stream_cli_tool
        return await nmap_scanner.run_nmap_scan(target, options, scan_id)

    async def _run_sslscan(self, target: str, scan_id: str):
        # ssl_scanner has its own streaming, but we'll wrap it for consistency
        return await ssl_scanner.run_ssl_scan(target, scan_id)

    async def _run_dir_discovery(self, target: str, scan_id: str):
        # This one has its own logic for directory discovery
        return await dir_discovery.run_dir_discovery(target, scan_id)

    async def _run_nikto(self, target: str, scan_id: str):
        command = [settings.NIKTO_PATH, "-h", target]
        # Pass scan_id to _stream_cli_tool
        return await self._stream_cli_tool(command, "nikto_scan", scan_id)



    async def _run_sqlmap(self, target: str, scan_id: str, aggressive: bool = False):
        return await sqlmap_scanner.run_sqlmap_scan(target, scan_id, aggressive)

    async def _run_xsser(self, target: str, scan_id: str, aggressive: bool = False):
        return await xss_scanner.run_xsser_scan(target, scan_id, aggressive)
        
    async def _run_vuln_analysis(self, full_results: List[Dict[str, Any]], scan_id: str):
        return await vuln_analyzer.run_vulnerability_analysis(full_results, scan_id)


async def execute_scan(pipeline: List[Dict[str, Any]], timeout: int = 3600) -> tuple[str, List[Dict[str, Any]]]:
    """
    Executes a full scan pipeline, returns the scan ID and results.
    """
    scan_id = str(uuid.uuid4())
    controller = ToolController(scan_id)
    results = await controller.run_pipeline(pipeline, timeout)
    return scan_id, results
