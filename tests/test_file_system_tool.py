"""
Comprehensive tests for FileSystemTool.
"""
import pytest
import os
import tempfile
from pathlib import Path
from wormgpt_hive.tools.file_system import FileSystemTool


class TestFileSystemToolComprehensive:
    """Comprehensive tests for FileSystemTool."""
    
    def test_read_file_with_encoding(self):
        """Test reading file with specific encoding."""
        tool = FileSystemTool()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Test content with UTF-8")
            temp_file = f.name
        
        try:
            result = tool.read_file(temp_file, encoding='utf-8')
            
            assert result["success"] is True
            assert "Test content with UTF-8" in result["data"]["content"]
        finally:
            os.remove(temp_file)
    
    def test_read_file_error(self):
        """Test read_file error handling."""
        tool = FileSystemTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = tool.read_file(os.path.join(tmpdir, "nonexistent.txt"))
            
            assert result["success"] is False
            assert "File not found" in result["error"]
    
    def test_write_file_append_mode(self):
        """Test writing file in append mode."""
        tool = FileSystemTool()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("First line\n")
            temp_file = f.name
        
        try:
            result = tool.write_file(temp_file, "Second line\n", mode='a')
            
            assert result["success"] is True
            
            with open(temp_file, 'r') as f:
                content = f.read()
                assert "First line" in content
                assert "Second line" in content
        finally:
            os.remove(temp_file)
    
    def test_write_file_creates_directory(self):
        """Test that write_file creates parent directories."""
        tool = FileSystemTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = os.path.join(tmpdir, "subdir", "nested", "file.txt")
            
            result = tool.write_file(nested_path, "Content")
            
            assert result["success"] is True
            assert os.path.exists(nested_path)
    
    def test_list_files_with_pattern(self):
        """Test listing files with glob pattern."""
        tool = FileSystemTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(os.path.join(tmpdir, "file1.txt")).touch()
            Path(os.path.join(tmpdir, "file2.txt")).touch()
            Path(os.path.join(tmpdir, "file3.py")).touch()
            
            result = tool.list_files(tmpdir, pattern="*.txt")
            
            assert result["success"] is True
            assert result["data"]["count"] == 2
    
    def test_list_files_recursive(self):
        """Test listing files recursively."""
        tool = FileSystemTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(os.path.join(tmpdir, "file1.txt")).touch()
            
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)
            Path(os.path.join(subdir, "file2.txt")).touch()
            
            result = tool.list_files(tmpdir, pattern="*.txt", recursive=True)
            
            assert result["success"] is True
            assert result["data"]["count"] == 2
    
    def test_list_files_directory_not_found(self):
        """Test list_files with non-existent directory."""
        tool = FileSystemTool()
        
        result = tool.list_files("/nonexistent/directory/path")
        
        assert result["success"] is False
        assert "Directory not found" in result["error"]
    
    def test_delete_file_not_found(self):
        """Test deleting non-existent file."""
        tool = FileSystemTool()
        
        result = tool.delete_file("/nonexistent/file.txt")
        
        assert result["success"] is False
        assert "File not found" in result["error"]
    
    def test_file_exists_true(self):
        """Test file_exists when file exists."""
        tool = FileSystemTool()
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
        
        try:
            result = tool.file_exists(temp_file)
            
            assert result["success"] is True
            assert result["data"]["exists"] is True
        finally:
            os.remove(temp_file)
    
    def test_file_exists_false(self):
        """Test file_exists when file doesn't exist."""
        tool = FileSystemTool()
        
        result = tool.file_exists("/nonexistent/file.txt")
        
        assert result["success"] is True
        assert result["data"]["exists"] is False
    
    def test_create_directory_exist_ok(self):
        """Test creating directory when it already exists with exist_ok=True."""
        tool = FileSystemTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "testdir")
            os.makedirs(subdir)
            
            result = tool.create_directory(subdir, exist_ok=True)
            
            assert result["success"] is True
    
    def test_create_directory_error(self):
        """Test create_directory error handling."""
        tool = FileSystemTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "testdir")
            os.makedirs(subdir)
            
            result = tool.create_directory(subdir, exist_ok=False)
            
            assert result["success"] is False
            assert "Failed to create directory" in result["error"]
    
    def test_execute_unknown_action(self):
        """Test execute with unknown action."""
        tool = FileSystemTool()
        
        result = tool.execute("invalid_action", file_path="test.txt")
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]
    
    def test_execute_action_exception(self):
        """Test execute when action raises exception."""
        tool = FileSystemTool()
        
        result = tool.execute("read")
        
        assert result["success"] is False
    
    def test_write_file_encoding(self):
        """Test writing file with specific encoding."""
        tool = FileSystemTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_encoding.txt")
            
            result = tool.write_file(filepath, "Test content", encoding='utf-8')
            
            assert result["success"] is True
            assert result["data"]["bytes_written"] > 0
    
    def test_list_files_default_pattern(self):
        """Test listing files with default pattern (all files)."""
        tool = FileSystemTool()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(os.path.join(tmpdir, "file1.txt")).touch()
            Path(os.path.join(tmpdir, "file2.py")).touch()
            Path(os.path.join(tmpdir, "file3.md")).touch()
            
            result = tool.list_files(tmpdir)
            
            assert result["success"] is True
            assert result["data"]["count"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
