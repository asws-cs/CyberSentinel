import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Set, Optional
from urllib.parse import urljoin, urlparse

from utils.logger import logger

class SQLTester:
    def __init__(self, url: str, scan_id: Optional[str] = None):
        self.url = self._ensure_scheme(url)
        self.scan_id = scan_id
        self.sql_payloads = ["'", "\"", " ' OR 1=1 --"]
        self.error_messages = [
            "you have an error in your sql syntax",
            "warning: mysql",
            "unclosed quotation mark",
            "syntax error",
        ]

    def _ensure_scheme(self, url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    async def test(self) -> Dict[str, Any]:
        logger.info(f"Starting SQL injection test for {self.url}", extra={"scan_id": self.scan_id})
        vulnerable_forms: List[Dict[str, str]] = []

        try:
            async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
                response = await client.get(self.url)
                soup = BeautifulSoup(response.text, "html.parser")
                forms = soup.find_all("form")
                logger.info(f"Found {len(forms)} forms on {self.url}", extra={"scan_id": self.scan_id})

                for form in forms:
                    if await self._test_form(client, form):
                        vulnerable_forms.append({
                            "action": form.get("action"),
                            "method": form.get("method", "get").lower(),
                        })

        except httpx.RequestError as e:
            logger.error(f"Could not connect to {self.url} for SQL injection test: {e}", extra={"scan_id": self.scan_id})
            return {"error": str(e)}

        is_vulnerable = len(vulnerable_forms) > 0
        return {
            "vulnerable": is_vulnerable,
            "vulnerable_forms": vulnerable_forms,
            "summary": "Potential SQL injection vulnerability found." if is_vulnerable else "No obvious SQL injection vulnerabilities found."
        }

    async def _test_form(self, client: httpx.AsyncClient, form: BeautifulSoup) -> bool:
        action = form.get("action")
        method = form.get("method", "get").lower()
        form_url = urljoin(self.url, action)

        inputs = form.find_all(["input", "textarea"])
        
        for payload in self.sql_payloads:
            data = {}
            for i in inputs:
                name = i.get("name")
                if not name: continue
                
                # Use payload for text-like inputs, default value otherwise
                if i.get("type") in ["text", "search", "email", "password", None] and name:
                    data[name] = payload
                else:
                    data[name] = i.get("value", "")
            
            try:
                if method == "post":
                    response = await client.post(form_url, data=data)
                else:
                    response = await client.get(form_url, params=data)

                for error in self.error_messages:
                    if error in response.text.lower():
                        logger.warning(f"SQL injection vulnerability detected on {form_url} with payload '{payload}'", extra={"scan_id": self.scan_id})
                        return True
            except httpx.RequestError as e:
                logger.error(f"Request failed during form submission to {form_url}: {e}", extra={"scan_id": self.scan_id})
                continue
                
        return False

async def run_sql_test(url: str, scan_id: Optional[str] = None) -> Dict[str, Any]:
    tester = SQLTester(url, scan_id)
    return await tester.test()
