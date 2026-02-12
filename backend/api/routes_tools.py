from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from security.legal_guard import get_legal_disclaimer_text
from monitoring.resource_monitor import get_resource_metrics
from tools.tool_controller import ToolController

router = APIRouter()

TOOL_DESCRIPTIONS = {
    "nmap_scan": {
        "description": "Performs a port scan using Nmap to discover open ports and services.",
        "params": {"target": "string (IP address)", "options": "string (Nmap options)"}
    },
    "ssl_scan": {
        "description": "Inspects SSL/TLS certificate and configuration for vulnerabilities.",
        "params": {"target": "string (domain or IP)"}
    },
    "header_analysis": {
        "description": "Analyzes HTTP security headers for misconfigurations.",
        "params": {"url": "string"}
    },
    "vulnerability_analysis": {
        "description": "Passively checks for known vulnerabilities based on service versions.",
        "params": "Internal, uses results from other scans."
    },
    "sql_injection_test": {
        "description": "Performs a non-destructive test for basic SQL injection vulnerabilities.",
        "params": {"url": "string"}
    },
    "xss_test": {
        "description": "Performs a non-destructive test for basic reflected XSS vulnerabilities.",
        "params": {"url": "string"}
    },
    "dir_discovery": {
        "description": "Discovers hidden directories and files using a wordlist.",
        "params": {"target": "string (URL)"}
    },
    "nikto_scan": {
        "description": "Runs an informational web server scan with Nikto.",
        "params": {"target": "string (URL)"}
    }
}

@router.get("/", response_model=List[str])
async def get_all_tools():
    """
    Get a list of all available tool names.
    """
    # We can get the tool names directly from our dummy controller's map
    return list(ToolController(scan_id="dummy").tool_functions.keys())

@router.get("/{tool_name}", response_model=Dict[str, Any])
async def get_tool_details(tool_name: str):
    """
    Get the description and parameters for a specific tool.
    """
    if tool_name not in TOOL_DESCRIPTIONS:
        raise HTTPException(status_code=404, detail="Tool not found.")
    return TOOL_DESCRIPTIONS[tool_name]

@router.get("/legal/disclaimer", response_model=Dict[str, str])
async def get_legal_notice():
    """
    Get the legal disclaimer text required for offensive scans.
    """
    return {"disclaimer": get_legal_disclaimer_text()}
    
@router.get("/monitoring/resources", response_model=Dict[str, Any])
async def get_system_resources():
    """
    Get current system resource usage metrics.
    """
    return get_resource_metrics()
