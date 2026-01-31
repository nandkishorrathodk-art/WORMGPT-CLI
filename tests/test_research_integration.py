import pytest
from wormgpt_hive.tools.google_search import GoogleSearchTool
from wormgpt_hive.tools.web_browser import WebBrowserTool
from wormgpt_hive.drones.research_drone import ResearchDrone


@pytest.mark.integration
class TestResearchIntegration:
    """Integration tests for research capabilities. These tests make real network requests."""

    @pytest.fixture
    def research_system(self):
        search_tool = GoogleSearchTool(rate_limit_delay=2.0)
        browser_tool = WebBrowserTool(rate_limit_delay=2.0, timeout=15)

        research_drone = ResearchDrone()
        research_drone.register_tool("google_search", search_tool)
        research_drone.register_tool("web_browser", browser_tool)

        return research_drone, search_tool, browser_tool

    def test_real_web_search(self, research_system):
        _, search_tool, _ = research_system

        result = search_tool.search("Python programming", max_results=3)

        assert result["success"] is True
        assert result["data"]["count"] > 0
        assert len(result["data"]["results"]) > 0

        first_result = result["data"]["results"][0]
        assert "title" in first_result
        assert "link" in first_result
        assert "snippet" in first_result
        assert first_result["link"].startswith("http")

    def test_real_web_fetch(self, research_system):
        _, _, browser_tool = research_system

        result = browser_tool.fetch("https://example.com", parse_content=True)

        assert result["success"] is True
        assert result["data"]["status_code"] == 200
        assert len(result["data"]["title"]) > 0
        assert len(result["data"]["text"]) > 0
        assert "Example Domain" in result["data"]["title"]

    def test_research_drone_web_search(self, research_system):
        research_drone, _, _ = research_system

        result = research_drone.execute(
            "web_search", {"query": "artificial intelligence", "max_results": 3}
        )

        assert result["success"] is True
        assert result["data"]["count"] > 0
        assert len(result["data"]["results"]) > 0

    def test_research_drone_fetch_content(self, research_system):
        research_drone, _, _ = research_system

        result = research_drone.execute("fetch_content", {"url": "https://example.com"})

        assert result["success"] is True
        assert result["data"]["content_length"] > 0

    @pytest.mark.slow
    def test_research_drone_search_and_summarize(self, research_system):
        research_drone, _, _ = research_system

        result = research_drone.execute(
            "search_and_summarize",
            {
                "query": "Python programming language",
                "max_results": 2,
                "fetch_top_n": 1,
            },
        )

        assert result["success"] is True
        assert result["data"]["query"] == "Python programming language"
        assert result["data"]["total_results"] > 0
        assert len(result["data"]["fetched_content"]) > 0

        fetched = result["data"]["fetched_content"][0]
        assert "title" in fetched
        assert "url" in fetched
        assert "full_text" in fetched
        assert len(fetched["full_text"]) > 0
