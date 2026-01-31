"""
Comprehensive tests for ShellDrone.
"""
import pytest
from unittest.mock import Mock, patch
from wormgpt_hive.drones.shell_drone import ShellDrone
from wormgpt_hive.tools.shell_executor import ShellExecutorTool


class TestShellDrone:
    """Test ShellDrone functionality."""
    
    def test_init(self):
        """Test ShellDrone initialization."""
        drone = ShellDrone()
        
        assert drone.name == "ShellDrone"
        assert "shell" in drone.description.lower()
    
    def test_execute_command_success(self):
        """Test executing a simple command."""
        drone = ShellDrone()
        
        mock_shell_tool = Mock()
        mock_shell_tool.execute.return_value = {
            "success": True,
            "data": {
                "stdout": "Command output",
                "stderr": "",
                "returncode": 0
            }
        }
        
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_command", {
            "command": "echo test"
        })
        
        assert result["success"] is True
        assert "Command executed" in result["message"]
        mock_shell_tool.execute.assert_called_once()
    
    def test_execute_command_with_cwd(self):
        """Test executing command with working directory."""
        drone = ShellDrone()
        
        mock_shell_tool = Mock()
        mock_shell_tool.execute.return_value = {
            "success": True,
            "data": {
                "stdout": "Output",
                "stderr": "",
                "returncode": 0
            }
        }
        
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_command", {
            "command": "dir",
            "cwd": "C:\\temp"
        })
        
        assert result["success"] is True
        call_args = mock_shell_tool.execute.call_args
        assert call_args[1]["cwd"] == "C:\\temp"
    
    def test_execute_command_with_timeout(self):
        """Test executing command with timeout."""
        drone = ShellDrone()
        
        mock_shell_tool = Mock()
        mock_shell_tool.execute.return_value = {
            "success": True,
            "data": {
                "stdout": "Output",
                "stderr": "",
                "returncode": 0
            }
        }
        
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_command", {
            "command": "sleep 1",
            "timeout": 30
        })
        
        assert result["success"] is True
        call_args = mock_shell_tool.execute.call_args
        assert call_args[1]["timeout"] == 30
    
    def test_execute_command_with_tor(self):
        """Test executing command through Tor."""
        drone = ShellDrone()
        
        mock_shell_tool = Mock()
        mock_shell_tool.execute.return_value = {
            "success": True,
            "data": {
                "stdout": "Tor output",
                "stderr": "",
                "returncode": 0
            }
        }
        
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_command", {
            "command": "curl https://check.torproject.org",
            "use_tor": True
        })
        
        assert result["success"] is True
        call_args = mock_shell_tool.execute.call_args
        assert call_args[1]["use_tor"] is True
    
    def test_execute_script_success(self):
        """Test executing a script."""
        drone = ShellDrone()
        
        mock_shell_tool = Mock()
        mock_shell_tool.execute_script.return_value = {
            "success": True,
            "data": {
                "stdout": "Script output",
                "stderr": "",
                "returncode": 0,
                "script_type": "python"
            }
        }
        
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_script", {
            "script_content": "print('Hello')",
            "script_type": "python"
        })
        
        assert result["success"] is True
        assert "script executed" in result["message"]
        mock_shell_tool.execute_script.assert_called_once()
    
    def test_execute_script_with_cwd(self):
        """Test executing script with working directory."""
        drone = ShellDrone()
        
        mock_shell_tool = Mock()
        mock_shell_tool.execute_script.return_value = {
            "success": True,
            "data": {
                "stdout": "Output",
                "stderr": "",
                "returncode": 0,
                "script_type": "bash"
            }
        }
        
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_script", {
            "script_content": "echo test",
            "script_type": "bash",
            "cwd": "/tmp"
        })
        
        assert result["success"] is True
        call_args = mock_shell_tool.execute_script.call_args
        assert call_args[1]["cwd"] == "/tmp"
    
    def test_missing_shell_executor_tool(self):
        """Test error when shell_executor tool not registered."""
        drone = ShellDrone()
        
        result = drone.execute("execute_command", {
            "command": "echo test"
        })
        
        assert result["success"] is False
        assert "ShellExecutorTool not registered" in result["error"]
    
    def test_missing_required_parameters_command(self):
        """Test error when required parameters are missing for command."""
        drone = ShellDrone()
        mock_shell_tool = Mock()
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_command", {})
        
        assert result["success"] is False
        assert "Missing required parameter" in result["error"]
    
    def test_missing_required_parameters_script(self):
        """Test error when required parameters are missing for script."""
        drone = ShellDrone()
        mock_shell_tool = Mock()
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_script", {"script_content": "test"})
        
        assert result["success"] is False
        assert "Missing required parameter" in result["error"]
    
    def test_unknown_action(self):
        """Test handling of unknown action."""
        drone = ShellDrone()
        mock_shell_tool = Mock()
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("unknown_action", {})
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]
    
    def test_command_with_stderr(self):
        """Test command that outputs to stderr."""
        drone = ShellDrone()
        
        mock_shell_tool = Mock()
        mock_shell_tool.execute.return_value = {
            "success": True,
            "data": {
                "stdout": "",
                "stderr": "Error message",
                "returncode": 0
            }
        }
        
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_command", {
            "command": "echo error >&2"
        })
        
        assert result["success"] is True
    
    def test_failed_command_execution(self):
        """Test handling of failed command execution."""
        drone = ShellDrone()
        
        mock_shell_tool = Mock()
        mock_shell_tool.execute.return_value = {
            "success": False,
            "error": "Command failed",
            "details": "Exit code 1"
        }
        
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_command", {
            "command": "exit 1"
        })
        
        assert result["success"] is False
    
    def test_failed_script_execution(self):
        """Test handling of failed script execution."""
        drone = ShellDrone()
        
        mock_shell_tool = Mock()
        mock_shell_tool.execute_script.return_value = {
            "success": False,
            "error": "Script failed",
            "details": "Syntax error"
        }
        
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_script", {
            "script_content": "invalid syntax",
            "script_type": "python"
        })
        
        assert result["success"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
