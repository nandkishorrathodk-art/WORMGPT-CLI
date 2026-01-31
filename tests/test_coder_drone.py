"""
Comprehensive tests for CoderDrone.
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock
from wormgpt_hive.drones.coder_drone import CoderDrone
from wormgpt_hive.tools.file_system import FileSystemTool


class TestCoderDrone:
    """Test CoderDrone functionality."""
    
    def test_init(self):
        """Test CoderDrone initialization."""
        drone = CoderDrone()
        
        assert drone.name == "CoderDrone"
        assert "file" in drone.description.lower()
    
    def test_write_file_action(self):
        """Test writing a file via CoderDrone."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            
            result = drone.execute("write_file", {
                "file_path": filepath,
                "content": "Test content"
            })
            
            assert result["success"] is True
            assert os.path.exists(filepath)
            
            with open(filepath, "r") as f:
                assert f.read() == "Test content"
    
    def test_read_file_action(self):
        """Test reading a file via CoderDrone."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            
            with open(filepath, "w") as f:
                f.write("Test content to read")
            
            result = drone.execute("read_file", {
                "file_path": filepath
            })
            
            assert result["success"] is True
            assert "Test content to read" in result["data"]["content"]
    
    def test_file_exists_action(self):
        """Test checking if a file exists via CoderDrone."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            
            with open(filepath, "w") as f:
                f.write("Test content")
            
            result = drone.execute("file_exists", {
                "file_path": filepath
            })
            
            assert result["success"] is True
            assert result["data"]["exists"] is True
    
    def test_list_files_action(self):
        """Test listing files via CoderDrone."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file1.txt").touch()
            Path(tmpdir, "file2.txt").touch()
            Path(tmpdir, "subdir").mkdir()
            Path(tmpdir, "subdir", "file3.txt").touch()
            
            result = drone.execute("list_files", {
                "directory": tmpdir
            })
            
            assert result["success"] is True
            assert len(result["data"]["files"]) >= 2
    
    def test_delete_file_action(self):
        """Test deleting a file via CoderDrone."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            
            with open(filepath, "w") as f:
                f.write("To be deleted")
            
            assert os.path.exists(filepath)
            
            result = drone.execute("delete_file", {
                "file_path": filepath
            })
            
            assert result["success"] is True
            assert not os.path.exists(filepath)
    
    def test_create_directory_action(self):
        """Test creating a directory via CoderDrone."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dirpath = os.path.join(tmpdir, "newdir")
            
            result = drone.execute("create_directory", {
                "directory": dirpath
            })
            
            assert result["success"] is True
            assert os.path.exists(dirpath)
            assert os.path.isdir(dirpath)
    
    def test_write_file_with_append_mode(self):
        """Test writing to a file in append mode via CoderDrone."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            
            with open(filepath, "w") as f:
                f.write("Original content")
            
            result = drone.execute("write_file", {
                "file_path": filepath,
                "content": "\nAppended content",
                "mode": "a"
            })
            
            assert result["success"] is True
            
            with open(filepath, "r") as f:
                content = f.read()
                assert "Original content" in content
                assert "Appended content" in content
    
    def test_missing_file_system_tool(self):
        """Test error when file_system tool not registered."""
        drone = CoderDrone()
        
        result = drone.execute("write_file", {
            "file_path": "test.txt",
            "content": "Test"
        })
        
        assert result["success"] is False
        assert "FileSystemTool not registered" in result["error"]
    
    def test_missing_required_parameters(self):
        """Test error when required parameters are missing."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        result = drone.execute("write_file", {})
        
        assert result["success"] is False
        assert "Missing required parameter" in result["error"]
    
    def test_unknown_action(self):
        """Test handling of unknown action."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        result = drone.execute("unknown_action", {})
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]
    
    def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        result = drone.execute("read_file", {
            "file_path": "/nonexistent/file.txt"
        })
        
        assert result["success"] is False
    
    def test_file_not_exists(self):
        """Test checking if a file does not exist."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        result = drone.execute("file_exists", {
            "file_path": "/nonexistent/file.txt"
        })
        
        assert result["success"] is True
        assert result["data"]["exists"] is False
    
    def test_create_nested_directory(self):
        """Test creating nested directories."""
        drone = CoderDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dirpath = os.path.join(tmpdir, "level1", "level2", "level3")
            
            result = drone.execute("create_directory", {
                "directory": dirpath
            })
            
            assert result["success"] is True
            assert os.path.exists(dirpath)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
