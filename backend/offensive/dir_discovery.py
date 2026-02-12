import asyncio
import re
import os
from typing import Dict, Any, List
from utils.logger import logger
from utils.helpers import run_command
from config import settings

class DirectoryDiscovery:
    def __init__(self, target: str):
        self.target = self._ensure_scheme(target)
        # In a real app, provide options for different wordlists
        self.wordlist_path = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt" # A common default

    def _ensure_scheme(self, url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url
        
    async def _check_wordlist(self):
        """ Checks if the default wordlist exists. """
        if not os.path.exists(self.wordlist_path):
            logger.warning(f"Wordlist not found at {self.wordlist_path}. Dir discovery may fail.")
            # In a real app, you might try other common paths or download a default list.
            return False
        return True

    async def discover(self) -> Dict[str, Any]:
        logger.info(f"Starting directory discovery on {self.target}")
        
        if not await self._check_wordlist():
            return {"error": f"Wordlist not found at {self.wordlist_path}"}

        # Prefer gobuster for its speed and simple output, fall back to dirsearch
        try:
            # Check if gobuster is installed
            stdout, stderr = await run_command("command -v gobuster")
            if stdout:
                logger.info("Using gobuster for directory discovery.")
                # Gobuster command: dir mode, -u for URL, -w for wordlist, -q for quiet, -n for no progress, -t for threads
                command = f"{settings.GOBUSTER_PATH} dir -u {self.target} -w {self.wordlist_path} -q -n -t 20"
                stdout, stderr = await run_command(command)
                return self._parse_gobuster_results(stdout)
        except Exception:
            logger.info("Gobuster not found or failed, falling back to dirsearch.")

        try:
            # Fallback to dirsearch
            command = f"{settings.DIRSEARCH_PATH} -u {self.target} -w {self.wordlist_path} -e php,html,js,txt --plain-text-report=-"
            stdout, stderr = await run_command(command)
            return self._parse_dirsearch_results(stdout)
        except Exception as e:
            logger.error(f"Directory discovery failed with both gobuster and dirsearch: {e}")
            return {"error": "Directory discovery tool failed to run."}


    def _parse_gobuster_results(self, scan_output: str) -> Dict[str, Any]:
        discovered_paths: List[Dict[str, Any]] = []
        path_pattern = re.compile(r"(.+) \(Status: (\d{3})\)")
        for line in scan_output.splitlines():
            match = path_pattern.match(line)
            if match:
                path = match.group(1).strip()
                status_code = int(match.group(2))
                discovered_paths.append({"path": f"{self.target}{path}", "status": status_code})
        logger.info(f"Directory discovery finished. Found {len(discovered_paths)} interesting paths.")
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
        logger.info(f"Directory discovery finished. Found {len(discovered_paths)} interesting paths.")
        return {"discovered_paths": discovered_paths}


async def run_dir_discovery(target: str) -> Dict[str, Any]:
    discoverer = DirectoryDiscovery(target)
    return await discoverer.discover()
