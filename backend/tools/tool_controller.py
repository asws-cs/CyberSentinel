import asyncio
import uuid
from typing import List, Dict, Any

from utils.logger import logger
from tools.live_output import get_live_output_publisher
from tools.subprocess_stream import stream_command

# Import all scanner and offensive functions
from scanners import nmap_scanner, ssl_scanner, header_analyzer, vuln_analyzer
from offensive import sql_tester, dir_discovery, xss_tester
from config import settings

class ToolController:
    def __init__(self, scan_id: str):
        self.scan_id = scan_id
        self.output_channel = f"scan_output:{self.scan_id}"
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
        }

    async def run_pipeline(self, pipeline: List[Dict[str, Any]]):
        logger.info(f"[{self.scan_id}] Starting tool pipeline execution.")
        await self.publisher.publish(self.output_channel, f"Starting scan {self.scan_id}...")

        for tool_spec in pipeline:
            tool_name = tool_spec["name"]
            params = tool_spec["params"]
            
            if tool_name not in self.tool_functions:
                logger.warning(f"[{self.scan_id}] Tool '{tool_name}' not recognized. Skipping.")
                continue

            await self.publisher.publish(self.output_channel, f"\n--- Running {tool_name} ---")
            logger.info(f"[{self.scan_id}] Running tool: {tool_name} with params: {params}")

            try:
                # The 'vulnerability_analysis' tool requires the results of other tools
                if tool_name == "vulnerability_analysis":
                    result_data = await self.tool_functions[tool_name](self.results)
                else:
                    result_data = await self.tool_functions[tool_name](**params)
                
                result = {"tool_name": tool_name, "findings": result_data}
                self.results.append(result)

                # Log a summary to the live output
                summary = result_data.get("summary", f"Completed. Found {len(result_data.get('vulnerabilities_found', []))} issues.")
                await self.publisher.publish(self.output_channel, f"{tool_name}: {summary}")

            except Exception as e:
                error_msg = f"Error running tool '{tool_name}': {e}"
                logger.error(f"[{self.scan_id}] {error_msg}")
                await self.publisher.publish(self.output_channel, f"ERROR: {error_msg}")
                self.results.append({"tool_name": tool_name, "error": str(e)})

        await self.publisher.publish(self.output_channel, f"\n--- Scan {self.scan_id} finished ---")
        logger.info(f"[{self.scan_id}] Tool pipeline execution finished.")
        return self.results
        
    async def _stream_cli_tool(self, command: str, tool_name: str):
        """ Helper to stream CLI tool output and return a placeholder result. """
        async for line in stream_command(command):
            await self.publisher.publish(self.output_channel, line)
        return {"summary": f"{tool_name} scan completed. Check logs for details."}

    async def _run_nmap(self, target: str, options: str):
        command = f"{settings.NMAP_PATH} {options} {target}"
        async for line in stream_command(command):
            await self.publisher.publish(self.output_channel, line)
        # After streaming, run the parser for structured data
        return await nmap_scanner.run_nmap_scan(target, options)

    async def _run_sslscan(self, target: str):
        command = f"{settings.SSLSCAN_PATH} --no-colour {target}"
        async for line in stream_command(command):
            await self.publisher.publish(self.output_channel, line)
        return await ssl_scanner.run_ssl_scan(target)

    async def _run_dir_discovery(self, target: str):
        # This one has its own logic to try gobuster then dirsearch
        return await dir_discovery.run_dir_discovery(target)

    async def _run_nikto(self, target: str):
        command = f"{settings.NIKTO_PATH} -h {target}"
        return await self._stream_cli_tool(command, "nikto_scan")
        
    async def _run_vuln_analysis(self, full_results: List[Dict[str, Any]]):
        return await vuln_analyzer.run_vulnerability_analysis(full_results)


async def execute_scan(pipeline: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
    """
    Executes a full scan pipeline, returns the scan ID and results.
    """
    scan_id = str(uuid.uuid4())
    controller = ToolController(scan_id)
    results = await controller.run_pipeline(pipeline)
    return scan_id, results
