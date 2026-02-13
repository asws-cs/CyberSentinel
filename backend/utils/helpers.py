import asyncio
import json
from datetime import datetime
import uuid
import os
import shutil
from utils.logger import logger

async def run_command(command: str) -> tuple[str, str]:
    """
    Asynchronously runs a shell command and returns stdout and stderr.
    
    Args:
        command: The command to execute.
        
    Returns:
        A tuple containing stdout and stderr as strings.
    """
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode().strip(), stderr.decode().strip()
from utils.logger import logger

import shutil

def validate_tool_path(tool_path: str, tool_name: str):
    """
    Validates if a tool's executable is available in the system's PATH.
    Raises specific exceptions for different failure cases.
    """
    if not tool_path:
        raise ValueError(f"{tool_name}_PATH is not set in settings.")
    
    resolved_path = shutil.which(tool_path)
    
    if not resolved_path:
        raise FileNotFoundError(
            f"{tool_name} executable not found. "
            f"'{tool_path}' is not in the system's PATH or is not executable."
        )
    
    logger.debug(f"{tool_name} found at: {resolved_path}")

class CustomJsonEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle datetime and UUID objects.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def to_json(data: dict) -> str:
    """
    Serializes a dictionary to a JSON string with custom formatting.
    """
    return json.dumps(data, indent=4, sort_keys=True, cls=CustomJsonEncoder)

def get_timestamp() -> str:
    """
    Returns the current timestamp in a standardized format.
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
