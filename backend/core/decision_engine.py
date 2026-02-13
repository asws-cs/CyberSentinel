from core.target_parser import Target
from utils.logger import logger
from typing import List, Dict, Any, Optional

class DecisionEngine:
    def __init__(self, target: Target, scan_id: str, scan_mode: str = "defensive", scan_depth: str = "normal", aggressive: bool = False, selected_tools: Optional[List[str]] = None):
        self.target = target
        self.scan_id = scan_id
        self.scan_mode = scan_mode
        self.scan_depth = scan_depth
        self.aggressive = aggressive
        self.selected_tools = selected_tools or []
        self.tool_pipeline: List[Dict[str, Any]] = []

    def build_pipeline(self):
        """
        Builds the tool pipeline based on user-selected tools and scan parameters.
        """
        logger.info(f"Building tool pipeline for {self.target.normalized_target} with tools: {self.selected_tools}", extra={"scan_id": self.scan_id})
        
        for tool_name in self.selected_tools:
            tool_builder = getattr(self, f"_add_{tool_name}", None)
            if tool_builder:
                tool_builder()
            else:
                logger.warning(f"No builder method found for tool: {tool_name}", extra={"scan_id": self.scan_id})
        
        # Always add vulnerability analysis at the end if relevant tools were run
        if any(t in self.selected_tools for t in ["nmap_scan", "header_analysis"]):
             self.tool_pipeline.append({"name": "vulnerability_analysis", "params": {}})


        logger.info(f"Tool pipeline built: {[tool['name'] for tool in self.tool_pipeline]}", extra={"scan_id": self.scan_id})
        return self.tool_pipeline

    def _add_nmap_scan(self):
        options = "-A -T4" if self.aggressive else "-sV -T4"
        self.tool_pipeline.append({"name": "nmap_scan", "params": {"target": self.target.ip_address, "options": options}})

    def _add_ssl_scan(self):
        self.tool_pipeline.append({"name": "ssl_scan", "params": {"target": self.target.domain or self.target.ip_address}})

    def _add_header_analysis(self):
        self.tool_pipeline.append({"name": "header_analysis", "params": {"url": self.target.normalized_target}})

    def _add_dir_discovery(self):
        self.tool_pipeline.append({"name": "dir_discovery", "params": {"target": self.target.normalized_target}})
        


    def _add_sql_injection_test(self):
        self.tool_pipeline.append({"name": "sql_injection_test", "params": {"url": self.target.normalized_target}})
        
    def _add_sqlmap_scan(self):
        if self.scan_mode == 'offensive':
            self.tool_pipeline.append({"name": "sqlmap_scan", "params": {"target": self.target.normalized_target, "aggressive": self.aggressive}})

    def _add_xss_test(self):
        self.tool_pipeline.append({"name": "xss_test", "params": {"url": self.target.normalized_target}})

    def _add_xsser_scan(self):
        if self.scan_mode == 'offensive':
            self.tool_pipeline.append({"name": "xsser_scan", "params": {"target": self.target.normalized_target, "aggressive": self.aggressive}})

    def _add_nikto_scan(self):
        if self.scan_depth == 'deep':
            self.tool_pipeline.append({"name": "nikto_scan", "params": {"target": self.target.normalized_target}})


def get_scan_pipeline(
    target_str: str, 
    scan_id: str,
    scan_mode: str, 
    scan_depth: str,
    aggressive: bool,
    tools: List[str]
) -> List[Dict[str, Any]]:
    """
    Top-level function to get a scan pipeline for a given target.
    """
    target = Target(target_str)
    engine = DecisionEngine(target, scan_id, scan_mode, scan_depth, aggressive, tools)
    return engine.build_pipeline()
