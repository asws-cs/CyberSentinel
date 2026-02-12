import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urljoin, urlparse, unquote

from utils.logger import logger

class XSSTester:
    def __init__(self, url: str):
        self.url = self._ensure_scheme(url)
        # A unique, safe payload to check for reflection
        self.payload = "<script>cybersentinel-xss-test</script>"
        self.reflection_tag = "cybersentinel-xss-test"

    def _ensure_scheme(self, url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    async def test(self) -> Dict[str, Any]:
        logger.info(f"Starting XSS test for {self.url}")
        vulnerable_points: List[Dict[str, str]] = []

        try:
            async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
                # 1. Test URL parameters
                if await self._test_url_parameters(client):
                    vulnerable_points.append({"type": "URL Parameter", "location": self.url})

                # 2. Test forms
                response = await client.get(self.url)
                soup = BeautifulSoup(response.text, "html.parser")
                forms = soup.find_all("form")
                logger.info(f"Found {len(forms)} forms to test for XSS on {self.url}")
                for form in forms:
                    if await self._test_form(client, form):
                        vulnerable_points.append({
                            "type": "Form Input",
                            "action": form.get("action"),
                            "method": form.get("method", "get").lower(),
                        })

        except httpx.RequestError as e:
            logger.error(f"Could not connect to {self.url} for XSS test: {e}")
            return {"error": str(e)}

        is_vulnerable = len(vulnerable_points) > 0
        return {
            "vulnerable": is_vulnerable,
            "vulnerable_points": vulnerable_points,
            "summary": "Potential reflected XSS vulnerability found." if is_vulnerable else "No obvious reflected XSS vulnerabilities found."
        }

    async def _test_url_parameters(self, client: httpx.AsyncClient) -> bool:
        parsed_url = urlparse(self.url)
        query_params = parsed_url.query.split('&')
        
        for i, param in enumerate(query_params):
            if '=' not in param: continue
            
            key, value = param.split('=', 1)
            # Inject payload into one parameter at a time
            test_params = list(query_params)
            test_params[i] = f"{key}={self.payload}"
            test_query = '&'.join(test_params)
            test_url = parsed_url._replace(query=test_query).geturl()
            
            try:
                response = await client.get(test_url)
                if self.reflection_tag in unquote(response.text):
                    logger.warning(f"Reflected XSS detected in URL parameter '{key}' at {test_url}")
                    return True
            except httpx.RequestError:
                continue
        return False

    async def _test_form(self, client: httpx.AsyncClient, form: BeautifulSoup) -> bool:
        action = form.get("action")
        method = form.get("method", "get").lower()
        form_url = urljoin(self.url, action)
        inputs = form.find_all(["input", "textarea"])

        data = {}
        injected_field = None
        for i in inputs:
            name = i.get("name")
            if not name: continue
            
            # Inject payload into the first text-like input found
            if not injected_field and i.get("type") in ["text", "search", "email", None]:
                data[name] = self.payload
                injected_field = name
            else:
                data[name] = i.get("value", "")
        
        if not injected_field: return False

        try:
            if method == "post":
                response = await client.post(form_url, data=data)
            else:
                response = await client.get(form_url, params=data)
            
            if self.reflection_tag in unquote(response.text):
                logger.warning(f"Reflected XSS detected in form input '{injected_field}' at {form_url}")
                return True
        except httpx.RequestError as e:
            logger.error(f"Request failed during XSS form submission to {form_url}: {e}")

        return False


async def run_xss_test(url: str) -> Dict[str, Any]:
    tester = XSSTester(url)
    return await tester.test()
