import pytest
from unittest.mock import Mock, patch, MagicMock
from wormgpt_hive.tools.google_search import GoogleSearchTool
from wormgpt_hive.tools.web_browser import WebBrowserTool
from wormgpt_hive.drones.research_drone import ResearchDrone


class TestGoogleSearchTool:

    @pytest.fixture
    def search_tool(self):
        return GoogleSearchTool(rate_limit_delay=0.1)

    @patch("wormgpt_hive.tools.google_search.DDGS")
    def test_search_success(self, mock_ddgs, search_tool):
        mock_results = [
            {
                "title": "Test Result 1",
                "href": "https://example.com/1",
                "body": "This is a test result snippet",
            },
            {
                "title": "Test Result 2",
                "href": "https://example.com/2",
                "body": "Another test result",
            },
        ]

        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.__enter__.return_value.text.return_value = mock_results
        mock_ddgs.return_value = mock_ddgs_instance

        result = search_tool.search("test query", max_results=2)

        assert result["success"] is True
        assert result["data"]["count"] == 2
        assert result["data"]["query"] == "test query"
        assert len(result["data"]["results"]) == 2
        assert result["data"]["results"][0]["title"] == "Test Result 1"
        assert result["data"]["results"][0]["link"] == "https://example.com/1"

    @patch("wormgpt_hive.tools.google_search.DDGS")
    def test_search_with_exception(self, mock_ddgs, search_tool):
        mock_ddgs.side_effect = Exception("Network error")

        result = search_tool.execute(query="test")

        assert result["success"] is False
        assert "Network error" in result["error"]

    def test_search_missing_query(self, search_tool):
        result = search_tool.execute()

        assert result["success"] is False
        assert "Missing required parameter: query" in result["error"]

    def test_rate_limiting(self, search_tool):
        import time

        with patch("wormgpt_hive.tools.google_search.DDGS") as mock_ddgs:
            mock_ddgs_instance = MagicMock()
            mock_ddgs_instance.__enter__.return_value.text.return_value = []
            mock_ddgs.return_value = mock_ddgs_instance

            start_time = time.time()
            search_tool.search("query1")
            search_tool.search("query2")
            elapsed_time = time.time() - start_time

            assert elapsed_time >= 0.1


class TestWebBrowserTool:

    @pytest.fixture
    def browser_tool(self):
        return WebBrowserTool(rate_limit_delay=0.1, timeout=10)

    @patch("wormgpt_hive.tools.web_browser.requests.get")
    def test_fetch_success(self, mock_get, browser_tool):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Test Heading</h1>
                <p>This is test content.</p>
                <a href="https://example.com">Test Link</a>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        result = browser_tool.fetch("https://example.com", parse_content=True)

        assert result["success"] is True
        assert result["data"]["status_code"] == 200
        assert result["data"]["title"] == "Test Page"
        assert "Test Heading" in result["data"]["text"]
        assert len(result["data"]["links"]) > 0

    @patch("wormgpt_hive.tools.web_browser.requests.get")
    def test_fetch_without_parsing(self, mock_get, browser_tool):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Raw content</body></html>"
        mock_get.return_value = mock_response

        result = browser_tool.fetch("https://example.com", parse_content=False)

        assert result["success"] is True
        assert result["data"]["content"] == "<html><body>Raw content</body></html>"

    @patch("wormgpt_hive.tools.web_browser.requests.get")
    def test_fetch_timeout(self, mock_get, browser_tool):
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        result = browser_tool.fetch("https://example.com")

        assert result["success"] is False
        assert "timeout" in result["error"].lower()

    @patch("wormgpt_hive.tools.web_browser.requests.get")
    def test_fetch_request_error(self, mock_get, browser_tool):
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        result = browser_tool.fetch("https://example.com")

        assert result["success"] is False
        assert "Connection error" in result["error"]

    def test_fetch_missing_url(self, browser_tool):
        result = browser_tool.execute()

        assert result["success"] is False
        assert "Missing required parameter: url" in result["error"]


class TestResearchDrone:

    @pytest.fixture
    def research_drone(self):
        drone = ResearchDrone()

        search_tool = Mock()
        browser_tool = Mock()

        drone.register_tool("google_search", search_tool)
        drone.register_tool("web_browser", browser_tool)

        return drone, search_tool, browser_tool

    def test_web_search(self, research_drone):
        drone, search_tool, _ = research_drone

        search_tool.execute.return_value = {
            "success": True,
            "data": {"query": "test", "results": [{"title": "Result 1"}], "count": 1},
        }

        result = drone.execute("web_search", {"query": "test"})

        assert result["success"] is True
        assert result["data"]["count"] == 1
        search_tool.execute.assert_called_once()

    def test_fetch_content(self, research_drone):
        drone, _, browser_tool = research_drone

        browser_tool.execute.return_value = {
            "success": True,
            "data": {
                "url": "https://example.com",
                "content_length": 1000,
                "text": "Content",
            },
        }

        result = drone.execute("fetch_content", {"url": "https://example.com"})

        assert result["success"] is True
        assert result["data"]["content_length"] == 1000
        browser_tool.execute.assert_called_once()

    def test_search_and_summarize(self, research_drone):
        drone, search_tool, browser_tool = research_drone

        search_tool.execute.return_value = {
            "success": True,
            "data": {
                "query": "AI news",
                "results": [
                    {
                        "title": "AI Breakthrough",
                        "link": "https://example.com/ai",
                        "snippet": "New AI model released",
                    }
                ],
                "count": 1,
            },
        }

        browser_tool.execute.return_value = {
            "success": True,
            "data": {
                "url": "https://example.com/ai",
                "title": "AI Breakthrough Article",
                "text": "Full article content about AI breakthrough...",
                "content_length": 500,
            },
        }

        result = drone.execute("search_and_summarize", {"query": "AI news"})

        assert result["success"] is True
        assert result["data"]["query"] == "AI news"
        assert len(result["data"]["fetched_content"]) == 1
        assert result["data"]["fetched_content"][0]["title"] == "AI Breakthrough"

        search_tool.execute.assert_called_once()
        browser_tool.execute.assert_called_once()

    def test_search_and_summarize_no_results(self, research_drone):
        drone, search_tool, _ = research_drone

        search_tool.execute.return_value = {
            "success": True,
            "data": {"query": "test", "results": [], "count": 0},
        }

        result = drone.execute("search_and_summarize", {"query": "test"})

        assert result["success"] is False
        assert "No search results found" in result["error"]

    def test_unknown_action(self, research_drone):
        drone, _, _ = research_drone

        result = drone.execute("invalid_action", {})

        assert result["success"] is False
        assert "Unknown action" in result["error"]

    def test_missing_tool_web_search(self):
        drone = ResearchDrone()

        result = drone.execute("web_search", {"query": "test"})

        assert result["success"] is False
        assert "GoogleSearchTool not registered" in result["error"]

    def test_missing_tool_fetch_content(self):
        drone = ResearchDrone()

        result = drone.execute("fetch_content", {"url": "https://example.com"})

        assert result["success"] is False
        assert "WebBrowserTool not registered" in result["error"]
