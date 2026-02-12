from core.target_parser import Target
from utils.logger import logger
from typing import List, Dict, Any

class DecisionEngine:
    def __init__(self, target: Target, scan_mode: str = "defensive", scan_depth: str = "normal"):
        self.target = target
        self.scan_mode = scan_mode
        self.scan_depth = scan_depth
        self.tool_pipeline: List[Dict[str, Any]] = []

    def build_pipeline(self):
        """
        Builds the tool pipeline based on scan parameters.
        """
        logger.info(f"Building tool pipeline for {self.target.normalized_target} with mode '{self.scan_mode}' and depth '{self.scan_depth}'")
        
        if self.scan_mode == "defensive":
            self._build_defensive_pipeline()
        elif self.scan_mode == "offensive":
            self._build_offensive_pipeline()
        else:
            logger.warning(f"Unknown scan mode: {self.scan_mode}. Defaulting to defensive.")
            self._build_defensive_pipeline()
            
        logger.info(f"Tool pipeline built: {[tool['name'] for tool in self.tool_pipeline]}")
        return self.tool_pipeline

    def _build_defensive_pipeline(self):
        """
        Builds a pipeline for defensive scanning.
        """
        self.tool_pipeline.extend([
            {"name": "nmap_scan", "params": {"target": self.target.ip_address, "options": "-sV -T4"}},
            {"name": "ssl_scan", "params": {"target": self.target.domain or self.target.ip_address}},
            {"name": "header_analysis", "params": {"url": self.target.normalized_target}},
            {"name": "vulnerability_analysis", "params": {"target": self.target.normalized_target}},
        ])

    def _build_offensive_pipeline(self):
        """
        Builds a pipeline for controlled offensive testing.
        """
        # Require user confirmation for offensive scans (will be enforced at API level)
        logger.info("Building offensive pipeline. User confirmation is required.")
        
        self.tool_pipeline.extend([
            {"name": "nmap_scan", "params": {"target": self.target.ip_address, "options": "-A -T4"}},
            {"name": "dir_discovery", "params": {"target": self.target.normalized_target}},
            {"name": "sql_injection_test", "params": {"url": self.target.normalized_target}},
            {"name": "xss_test", "params": {"url": self.target.normalized_target}},
        ])
        
        # Add Nikto for informational scans in deeper scans
        if self.scan_depth == 'deep':
            self.tool_pipeline.append({"name": "nikto_scan", "params": {"target": self.target.normalized_target}})

def get_scan_pipeline(target_str: str, scan_mode: str, scan_depth: str) -> List[Dict[str, Any]]:
    """
    Top-level function to get a scan pipeline for a given target.
    """
    target = Target(target_str)
    engine = DecisionEngine(target, scan_mode, scan_depth)
    return engine.build_pipeline()
