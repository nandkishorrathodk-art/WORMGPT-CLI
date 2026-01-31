import time
import requests
from typing import Any, Dict
from .base_tool import BaseTool

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class WebBrowserTool(BaseTool):
    """Web browser tool for fetching and parsing web content. Supports rate limiting and content extraction."""

    def __init__(self, rate_limit_delay: float = 1.0, timeout: int = 30):
        super().__init__()
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        self.last_request_time = 0

        if BeautifulSoup is None:
            raise ImportError(
                "beautifulsoup4 package not installed. Run: pip install beautifulsoup4"
            )

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        url = kwargs.get("url")
        parse_content = kwargs.get("parse_content", True)

        if not url:
            return self._error_response("Missing required parameter: url")

        try:
            return self.fetch(url, parse_content)
        except Exception as e:
            return self._error_response(str(e), f"URL: {url}")

    def fetch(self, url: str, parse_content: bool = True) -> Dict[str, Any]:
        self._apply_rate_limit()

        try:
            response = requests.get(
                url, headers=self.headers, timeout=self.timeout, allow_redirects=True
            )
            response.raise_for_status()

            if parse_content:
                parsed_data = self._parse_html(response.text, url)
                return self._success_response(
                    {
                        "url": url,
                        "status_code": response.status_code,
                        "title": parsed_data["title"],
                        "text": parsed_data["text"],
                        "links": parsed_data["links"],
                        "content_length": len(parsed_data["text"]),
                    },
                    f"Fetched and parsed {url} ({len(parsed_data['text'])} characters)",
                )
            else:
                return self._success_response(
                    {
                        "url": url,
                        "status_code": response.status_code,
                        "content": response.text,
                        "content_length": len(response.text),
                    },
                    f"Fetched {url} ({len(response.text)} characters)",
                )

        except requests.exceptions.Timeout:
            return self._error_response(
                f"Request timeout after {self.timeout}s", f"URL: {url}"
            )
        except requests.exceptions.RequestException as e:
            return self._error_response(f"Request failed: {str(e)}", f"URL: {url}")
        except Exception as e:
            return self._error_response(f"Unexpected error: {str(e)}", f"URL: {url}")

    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")

        for script in soup(["script", "style", "meta", "noscript"]):
            script.decompose()

        title = soup.find("title")
        title_text = title.get_text().strip() if title else ""

        text = soup.get_text(separator="\n", strip=True)

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        text = "\n".join(lines)

        links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text().strip()

            if href.startswith("http"):
                links.append({"text": link_text, "url": href})

        return {"title": title_text, "text": text[:10000], "links": links[:50]}

    def _apply_rate_limit(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)

        self.last_request_time = time.time()
