import time
from typing import Any, Dict
from .base_tool import BaseTool

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


class GoogleSearchTool(BaseTool):
    """Web search tool using DuckDuckGo. Performs web searches and returns results with rate limiting."""

    def __init__(self, rate_limit_delay: float = 1.0):
        super().__init__()
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        if DDGS is None:
            raise ImportError(
                "duckduckgo-search package not installed. Run: pip install duckduckgo-search"
            )

    def execute(self, **kwargs) -> Dict[str, Any]:
        query = kwargs.get("query")
        max_results = kwargs.get("max_results", 5)
        region = kwargs.get("region", "wt-wt")

        if not query:
            return self._error_response("Missing required parameter: query")

        try:
            return self.search(query, max_results, region)
        except Exception as e:
            return self._error_response(str(e), f"Query: {query}")

    def search(
        self, query: str, max_results: int = 5, region: str = "wt-wt"
    ) -> Dict[str, Any]:
        self._apply_rate_limit()

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, region=region, max_results=max_results))

            formatted_results = []
            for idx, result in enumerate(results, 1):
                formatted_results.append(
                    {
                        "position": idx,
                        "title": result.get("title", ""),
                        "link": result.get("href", ""),
                        "snippet": result.get("body", ""),
                    }
                )

            return self._success_response(
                {
                    "query": query,
                    "results": formatted_results,
                    "count": len(formatted_results),
                },
                f"Found {len(formatted_results)} results for '{query}'",
            )

        except Exception as e:
            return self._error_response(f"Search failed: {str(e)}", f"Query: {query}")

    def _apply_rate_limit(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)

        self.last_request_time = time.time()
