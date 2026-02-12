import asyncio
import json
from datetime import datetime
import uuid
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
