import asyncio
import re
import os
from typing import Dict, Any, List, Optional
from utils.logger import logger
from utils.helpers import run_command, validate_tool_path # Import validate_tool_path
from config import settings

class DirectoryDiscovery:
    def __init__(self, target: str, scan_id: Optional[str] = None):
        self.target = self._ensure_scheme(target)
        self.scan_id = scan_id
        # In a real app, provide options for different wordlists
        self.wordlist_path = settings.DIRSEARCH_DEFAULT_WORDLIST

    def _ensure_scheme(self, url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url
        
    async def _check_wordlist(self):
        """ Checks if the default wordlist exists. """
        if not os.path.exists(self.wordlist_path):
            logger.warning(f"Wordlist not found at {self.wordlist_path}. Dir discovery may fail.", extra={"scan_id": self.scan_id})
            # In a real app, you might try other common paths or download a default list.
            return False
        return True

    async def discover(self) -> Dict[str, Any]:
        logger.info(f"Starting directory discovery on {self.target}", extra={"scan_id": self.scan_id})
        
        if not await self._check_wordlist():
            return {"error": f"Wordlist not found at {self.wordlist_path}"}

        try:
            validate_tool_path(settings.DIRSEARCH_PATH, "Dirsearch")
            logger.info("Using dirsearch for directory discovery.", extra={"scan_id": self.scan_id})
            command = f"{settings.DIRSEARCH_PATH} -u {self.target} -w {self.wordlist_path} -e php,html,js,txt --plain-text-report=-"
            stdout, stderr = await run_command(command)
            if stderr:
                logger.warning(f"Dirsearch produced stderr output: {stderr}", extra={"scan_id": self.scan_id})
            return self._parse_dirsearch_results(stdout)
        except Exception as e:
            logger.error(f"Directory discovery failed with dirsearch: {e}", extra={"scan_id": self.scan_id})
            return {"error": "Directory discovery tool failed to run."}

    def _parse_dirsearch_results(self, scan_output: str) -> Dict[str, Any]:
        discovered_paths: List[Dict[str, Any]] = []
        path_pattern = re.compile(r"(\d{3})\s+[\d.]+\w\s+-\s+(http.*)")
        for line in scan_output.splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            match = path_pattern.search(line)
            if match:
                status_code = int(match.group(1))
                path = match.group(2).strip()
                if 200 <= status_code < 400:
                    discovered_paths.append({"path": path, "status": status_code})
        logger.info(f"Directory discovery finished. Found {len(discovered_paths)} interesting paths.", extra={"scan_id": self.scan_id})
        return {"discovered_paths": discovered_paths}


    def _parse_dirsearch_results(self, scan_output: str) -> Dict[str, Any]:
        discovered_paths: List[Dict[str, Any]] = []
        path_pattern = re.compile(r"(\d{3})\s+[\d.]+\w\s+-\s+(http.*)")
        for line in scan_output.splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            match = path_pattern.search(line)
            if match:
                status_code = int(match.group(1))
                path = match.group(2).strip()
                if 200 <= status_code < 400:
                    discovered_paths.append({"path": path, "status": status_code})
        logger.info(f"Directory discovery finished. Found {len(discovered_paths)} interesting paths.", extra={"scan_id": self.scan_id})
        return {"discovered_paths": discovered_paths}


async def run_dir_discovery(target: str, scan_id: Optional[str] = None) -> Dict[str, Any]:
    discoverer = DirectoryDiscovery(target, scan_id)
    return await discoverer.discover()
