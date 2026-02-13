import httpx
from typing import Dict, Any, List, Optional
from utils.logger import logger

class HeaderAnalyzer:
    def __init__(self, url: str, scan_id: Optional[str] = None):
        self.url = self._ensure_scheme(url)
        self.scan_id = scan_id
        self.security_headers = {
            "Strict-Transport-Security": False,
            "Content-Security-Policy": False,
            "X-Content-Type-Options": False,
            "X-Frame-Options": False,
            "X-XSS-Protection": False,
            "Referrer-Policy": False,
            "Permissions-Policy": False,
        }

    def _ensure_scheme(self, url: str) -> str:
        """
        Ensures the URL has a scheme (http or https). Defaults to https.
        """
        if not url.startswith(('http://', 'https://')):
            logger.info(f"No scheme found for {url}. Defaulting to https.", extra={"scan_id": self.scan_id})
            return f'https://{url}'
        return url

    async def analyze(self) -> Dict[str, Any]:
        """
        Analyzes HTTP security headers of the target URL.
        """
        logger.info(f"Starting header analysis for {self.url}", extra={"scan_id": self.scan_id})
        results: Dict[str, Any] = {
            "url": self.url,
            "present_headers": {},
            "missing_headers": [],
            "recommendations": [],
        }

        try:
            async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
                response = await client.get(self.url, timeout=10.0)
                
                headers = response.headers
                results["present_headers"] = dict(headers)

                for header in self.security_headers:
                    if header.lower() not in [h.lower() for h in headers.keys()]:
                        self.security_headers[header] = False
                        results["missing_headers"].append(header)
                        results["recommendations"].append(self._get_recommendation(header))
                    else:
                        self.security_headers[header] = True
                
                # Specific check for X-XSS-Protection as '0' is the secure value
                if 'x-xss-protection' in headers and headers['x-xss-protection'] != '0':
                    results["recommendations"].append("X-XSS-Protection header should be set to '0' to disable the browser's auditor and prevent potential bypasses.")

        except httpx.RequestError as e:
            logger.error(f"HTTP request failed for {self.url}: {e}", extra={"scan_id": self.scan_id})
            results["error"] = f"Could not connect to {self.url}. Error: {e}"
        
        logger.info(f"Header analysis finished for {self.url}.", extra={"scan_id": self.scan_id})
        return results

    def _get_recommendation(self, header: str) -> str:
        """
        Provides a brief recommendation for a missing security header.
        """
        recommendations = {
            "Strict-Transport-Security": "Enforce HTTPS to prevent man-in-the-middle attacks.",
            "Content-Security-Policy": "Define a policy to prevent XSS and data injection attacks.",
            "X-Content-Type-Options": "Set to 'nosniff' to prevent MIME-type sniffing.",
            "X-Frame-Options": "Set to 'SAMEORIGIN' or 'DENY' to prevent clickjacking.",
            "X-XSS-Protection": "Although modern browsers have their own protection, explicitly setting this to '0' is recommended.",
            "Referrer-Policy": "Control how much referrer information is sent with requests.",
            "Permissions-Policy": "Control which browser features can be used by the page.",
        }
        return recommendations.get(header, "No specific recommendation available.")

async def run_header_analysis(url: str, scan_id: Optional[str] = None) -> Dict[str, Any]:
    """
    High-level function to run an HTTP header analysis.
    """
    analyzer = HeaderAnalyzer(url, scan_id)
    return await analyzer.analyze()
