import socket
import asyncio
from urllib.parse import urlparse
import ipaddress
from utils.validators import is_valid_ip, is_valid_domain, is_valid_url
from utils.logger import logger
from typing import Optional, Dict, Any

class Target:
    def __init__(self, input_target: str, scan_id: Optional[str] = None):
        self.raw_target = input_target.strip()
        self.scan_id = scan_id
        self.normalized_target: str = ""
        self.ip_address: Optional[str] = None
        self.domain: Optional[str] = None
        self.is_local: bool = False
        self.target_type: str = "unknown"
        self._parse()

    def _parse(self):
        """
        Parses the raw target to determine its type and properties.
        """
        if is_valid_ip(self.raw_target):
            self.target_type = "ip"
            self.ip_address = self.raw_target
            self.normalized_target = self.raw_target
            try:
                ip_obj = ipaddress.ip_address(self.ip_address)
                self.is_local = ip_obj.is_private
            except ValueError:
                # Not a valid IP address or other parsing error, assume public
                self.is_local = False
        elif is_valid_url(self.raw_target):
            self.target_type = "url"
            parsed_url = urlparse(self.raw_target)
            self.domain = parsed_url.hostname
            self.normalized_target = self.raw_target
            if self.domain:
                self._resolve_dns()
        elif is_valid_domain(self.raw_target):
            self.target_type = "domain"
            self.domain = self.raw_target
            self.normalized_target = self.raw_target
            self._resolve_dns()
        else:
            logger.warning(f"Could not determine target type for: {self.raw_target}", extra={"scan_id": self.scan_id})
            raise ValueError(f"Invalid target: {self.raw_target}")

    def _resolve_dns(self):
        """
        Resolves the domain to an IP address.
        """
        if self.domain:
            try:
                self.ip_address = socket.gethostbyname(self.domain)
                logger.info(f"Resolved {self.domain} to {self.ip_address}", extra={"scan_id": self.scan_id})
                try:
                    ip_obj = ipaddress.ip_address(self.ip_address)
                    self.is_local = ip_obj.is_private
                except ValueError:
                    self.is_local = False
            except socket.gaierror:
                logger.error(f"Could not resolve DNS for domain: {self.domain}", extra={"scan_id": self.scan_id})
                self.ip_address = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the Target object.
        """
        return {
            "raw_target": self.raw_target,
            "normalized_target": self.normalized_target,
            "ip_address": self.ip_address,
            "domain": self.domain,
            "is_local": self.is_local,
            "target_type": self.target_type,
        }

async def parse_target(target_str: str, scan_id: Optional[str] = None) -> Target:
    """
    Asynchronously parse and resolve a target string.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, Target, target_str, scan_id)
