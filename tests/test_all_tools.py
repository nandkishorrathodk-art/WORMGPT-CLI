"""Comprehensive unit tests for all tools."""

import pytest
import os
import tempfile
from pathlib import Path

from wormgpt_hive.tools.file_system import FileSystemTool
from wormgpt_hive.tools.shell_executor import ShellExecutorTool
from wormgpt_hive.tools.google_search import GoogleSearchTool
from wormgpt_hive.tools.web_browser import WebBrowserTool


class TestFileSystemTool:
    """Tests for FileSystemTool."""

    @pytest.fixture
    def fs_tool(self):
        return FileSystemTool()

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_write_file(self, fs_tool, temp_dir):
        """Test writing a file."""
        filepath = os.path.join(temp_dir, "test.txt")
        content = "Hello, World!"

        result = fs_tool.execute("write", file_path=filepath, content=content)

        assert result["success"] is True
        assert os.path.exists(filepath)

        with open(filepath, "r") as f:
            assert f.read() == content

    def test_read_file(self, fs_tool, temp_dir):
        """Test reading a file."""
        filepath = os.path.join(temp_dir, "test.txt")
        content = "Test content"

        with open(filepath, "w") as f:
            f.write(content)

        result = fs_tool.execute("read", file_path=filepath)

        assert result["success"] is True
        assert result["data"]["content"] == content

    def test_read_nonexistent_file(self, fs_tool):
        """Test reading a file that doesn't exist."""
        result = fs_tool.execute("read", file_path="/nonexistent/file.txt")

        assert result["success"] is False
        assert "error" in result

    def test_list_directory(self, fs_tool, temp_dir):
        """Test listing directory contents."""
        Path(temp_dir, "file1.txt").write_text("test")
        Path(temp_dir, "file2.py").write_text("test")
        os.makedirs(os.path.join(temp_dir, "subdir"))

        result = fs_tool.execute("list", directory=temp_dir)

        assert result["success"] is True
        files = result["data"]["files"]
        assert any("file1.txt" in f for f in files)
        assert any("file2.py" in f for f in files)

    def test_delete_file(self, fs_tool, temp_dir):
        """Test deleting a file."""
        filepath = os.path.join(temp_dir, "delete_me.txt")
        Path(filepath).write_text("test")

        result = fs_tool.execute("delete", file_path=filepath)

        assert result["success"] is True
        assert not os.path.exists(filepath)

    def test_invalid_action(self, fs_tool):
        """Test calling an invalid action."""
        result = fs_tool.execute("invalid_action")

        assert result["success"] is False
        assert "Unknown action" in result.get("error", "")


class TestShellExecutorTool:
    """Tests for ShellExecutorTool."""

    @pytest.fixture
    def shell_tool(self):
        return ShellExecutorTool()

    def test_execute_simple_command_windows(self, shell_tool):
        """Test executing a simple command on Windows."""
        result = shell_tool.execute("echo Hello")

        assert result["success"] is True
        assert "Hello" in result["data"]["stdout"]

    def test_execute_with_timeout(self, shell_tool):
        """Test command execution with timeout."""
        result = shell_tool.execute("echo test", timeout=5)

        assert result["success"] is True
        assert result["data"]["returncode"] == 0

    def test_execute_invalid_command(self, shell_tool):
        """Test executing an invalid command."""
        result = shell_tool.execute("nonexistentcommand12345")

        assert result["success"] is False or result["data"]["returncode"] != 0


class TestGoogleSearchTool:
    """Tests for GoogleSearchTool."""

    @pytest.fixture
    def search_tool(self):
        return GoogleSearchTool()

    def test_search_returns_results(self, search_tool):
        """Test that search returns results."""
        result = search_tool.execute(query="Python programming", max_results=3)

        assert result["success"] is True
        assert "results" in result["data"]
        assert len(result["data"]["results"]) <= 3

    def test_search_with_empty_query(self, search_tool):
        """Test search with empty query."""
        result = search_tool.execute(query="", max_results=5)

        assert result["success"] is False


class TestWebBrowserTool:
    """Tests for WebBrowserTool."""

    @pytest.fixture
    def browser_tool(self):
        return WebBrowserTool()

    def test_fetch_valid_url(self, browser_tool):
        """Test fetching a valid URL."""
        result = browser_tool.execute(url="https://example.com")

        assert result["success"] is True
        assert "text" in result["data"]
        assert len(result["data"]["text"]) > 0

    def test_fetch_invalid_url(self, browser_tool):
        """Test fetching an invalid URL."""
        result = browser_tool.execute(
            url="https://this-domain-definitely-does-not-exist-12345.com"
        )

        assert result["success"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
