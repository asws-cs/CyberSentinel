import re
import ipaddress
from urllib.parse import urlparse

from pydantic import BaseModel, validator, Field

class TargetInput(BaseModel):
    """
    Pydantic model for validating scan targets.
    """
    target: str = Field(..., min_length=1, description="Target URL, domain, or IP address")

    @validator('target')
    def validate_target(cls, value):
        """
        Validates that the target is a valid URL, domain, or IP address.
        """
        value = value.strip()
        if not is_valid_ip(value) and not is_valid_domain(value) and not is_valid_url(value):
            raise ValueError("Input must be a valid URL, domain, or IP address.")
        return value

def is_valid_ip(ip_string: str) -> bool:
    """
    Check if the given string is a valid IP address (IPv4 or IPv6).
    """
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False

def is_valid_domain(domain_string: str) -> bool:
    """
    Check if the given string is a valid domain name.
    """
    # Regex for a valid domain name
    domain_regex = re.compile(
        r'^(?:[a-zA-Z0-9]'  # First character
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'  # Subdomains
        r'+[a-zA-Z]{2,6}$'  # Top-level domain
    )
    return re.match(domain_regex, domain_string) is not None

def is_valid_url(url_string: str) -> bool:
    """
    Check if the given string is a valid URL.
    """
    try:
        result = urlparse(url_string)
        # Check if scheme and netloc are present
        return all([result.scheme, result.netloc])
    except:
        return False

def sanitize_input(input_string: str) -> str:
    """
    Basic sanitization to remove potentially harmful characters.
    This is not a substitute for proper input validation and output encoding.
    """
    # Remove characters that are often used in command injection attacks
    sanitized = re.sub(r'[;`|&<>()$!#*]', '', input_string)
    return sanitized.strip()
