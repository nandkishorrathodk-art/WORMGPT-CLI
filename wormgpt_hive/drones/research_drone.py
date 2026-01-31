from typing import Any, Dict
from .base_drone import BaseDrone


class ResearchDrone(BaseDrone):
    """Research Drone: Performs web research including searching the web, fetching content from URLs, and summarizing information. Capabilities include DuckDuckGo web search, content extraction from web pages, and intelligent summarization."""
    
    def __init__(self):
        super().__init__("ResearchDrone")
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "web_search":
            return self._web_search(parameters)
        elif action == "fetch_content":
            return self._fetch_content(parameters)
        elif action == "search_and_summarize":
            return self._search_and_summarize(parameters)
        else:
            return self._error_response(f"Unknown action: {action}")
    
    def _web_search(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["query"])
        if error:
            return self._error_response(error)
        
        search_tool = self.tools.get("google_search")
        if not search_tool:
            return self._error_response("GoogleSearchTool not registered")
        
        query = parameters["query"]
        max_results = parameters.get("max_results", 5)
        region = parameters.get("region", "wt-wt")
        
        result = search_tool.execute(
            query=query,
            max_results=max_results,
            region=region
        )
        
        if result["success"]:
            data = result["data"]
            return self._success_response(
                data,
                f"Found {data['count']} results for '{query}'"
            )
        else:
            return result
    
    def _fetch_content(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["url"])
        if error:
            return self._error_response(error)
        
        browser_tool = self.tools.get("web_browser")
        if not browser_tool:
            return self._error_response("WebBrowserTool not registered")
        
        url = parameters["url"]
        parse_content = parameters.get("parse_content", True)
        
        result = browser_tool.execute(
            url=url,
            parse_content=parse_content
        )
        
        if result["success"]:
            data = result["data"]
            return self._success_response(
                data,
                f"Fetched content from {url} ({data['content_length']} characters)"
            )
        else:
            return result
    
    def _search_and_summarize(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["query"])
        if error:
            return self._error_response(error)
        
        search_tool = self.tools.get("google_search")
        browser_tool = self.tools.get("web_browser")
        
        if not search_tool:
            return self._error_response("GoogleSearchTool not registered")
        if not browser_tool:
            return self._error_response("WebBrowserTool not registered")
        
        query = parameters["query"]
        max_results = parameters.get("max_results", 3)
        fetch_top_n = parameters.get("fetch_top_n", 1)
        
        search_result = search_tool.execute(query=query, max_results=max_results)
        
        if not search_result["success"]:
            return search_result
        
        search_data = search_result["data"]
        results = search_data["results"]
        
        if not results:
            return self._error_response("No search results found", f"Query: {query}")
        
        fetched_content = []
        for idx, result in enumerate(results[:fetch_top_n]):
            url = result["link"]
            
            fetch_result = browser_tool.execute(url=url, parse_content=True)
            
            if fetch_result["success"]:
                content_data = fetch_result["data"]
                fetched_content.append({
                    "position": idx + 1,
                    "title": result["title"],
                    "url": url,
                    "snippet": result["snippet"],
                    "full_text": content_data["text"][:5000],
                    "page_title": content_data["title"]
                })
        
        summary_data = {
            "query": query,
            "search_results": results,
            "fetched_content": fetched_content,
            "total_results": len(results),
            "fetched_count": len(fetched_content)
        }
        
        return self._success_response(
            summary_data,
            f"Searched '{query}' and fetched {len(fetched_content)} articles"
        )
