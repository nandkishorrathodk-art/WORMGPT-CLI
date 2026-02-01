"""
Comprehensive tests for ShellExecutorTool.
"""
import pytest
import platform
from unittest.mock import patch, Mock
from wormgpt_hive.tools.shell_executor import ShellExecutorTool


class TestShellExecutorTool:
    """Test ShellExecutorTool functionality."""
    
    def test_init(self):
        """Test ShellExecutorTool initialization."""
        tool = ShellExecutorTool(timeout=60)
        
        assert tool.timeout == 60
        assert tool.is_windows == (platform.system() == "Windows")
    
    def test_execute_with_tor_curl(self):
        """Test executing curl command with Tor."""
        tool = ShellExecutorTool()
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "output"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool.execute("curl https://example.com", use_tor=True)
            
            assert result["success"] is True
            call_args = mock_run.call_args
            assert "--socks5-hostname" in call_args[0][0]
    
    def test_execute_with_tor_wget(self):
        """Test executing wget command with Tor."""
        tool = ShellExecutorTool()
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "output"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool.execute("wget https://example.com", use_tor=True)
            
            assert result["success"] is True
            call_args = mock_run.call_args
            assert "use_proxy=yes" in call_args[0][0]
    
    def test_execute_with_tor_other_command(self):
        """Test executing non-curl/wget command with Tor (should not modify)."""
        tool = ShellExecutorTool()
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "output"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool.execute("echo test", use_tor=True)
            
            assert result["success"] is True
            call_args = mock_run.call_args
            assert call_args[0][0] == "echo test"
    
    def test_execute_with_custom_timeout(self):
        """Test executing command with custom timeout."""
        tool = ShellExecutorTool(timeout=30)
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "output"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool.execute("echo test", timeout=60)
            
            assert result["success"] is True
            call_args = mock_run.call_args
            assert call_args[1]["timeout"] == 60
    
    def test_execute_script_python(self):
        """Test executing Python script."""
        tool = ShellExecutorTool()
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "Hello from Python"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool.execute_script("print('Hello from Python')", script_type="python")
            
            assert result["success"] is True
            assert result["data"]["script_type"] == "python"
    
    def test_execute_script_node(self):
        """Test executing Node.js script."""
        tool = ShellExecutorTool()
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "Hello from Node"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool.execute_script("console.log('Hello from Node')", script_type="node")
            
            assert result["success"] is True
            assert result["data"]["script_type"] == "node"
    
    def test_execute_script_powershell(self):
        """Test executing PowerShell script."""
        tool = ShellExecutorTool()
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "Hello from PowerShell"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool.execute_script("Write-Host 'Hello from PowerShell'", script_type="powershell")
            
            assert result["success"] is True
            assert result["data"]["script_type"] == "powershell"
    
    def test_execute_script_bash(self):
        """Test executing bash script."""
        tool = ShellExecutorTool()
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "Hello from Bash"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool.execute_script("echo 'Hello from Bash'", script_type="bash")
            
            assert result["success"] is True
            assert result["data"]["script_type"] == "bash"
    
    def test_execute_script_unsupported_type(self):
        """Test executing script with unsupported type."""
        tool = ShellExecutorTool()
        
        result = tool.execute_script("print('test')", script_type="ruby")
        
        assert result["success"] is False
        assert "Unsupported script type" in result["error"]
    
    def test_execute_script_with_error(self):
        """Test executing script that raises exception."""
        tool = ShellExecutorTool()
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Script execution failed")
            
            result = tool.execute_script("invalid script", script_type="python")
            
            assert result["success"] is False
            assert "Failed to execute script" in result["error"]
    
    def test_wrap_with_tor_curl(self):
        """Test _wrap_with_tor with curl command."""
        tool = ShellExecutorTool()
        
        wrapped = tool._wrap_with_tor("curl https://example.com")
        
        assert "curl https://example.com" in wrapped
        assert "--socks5-hostname" in wrapped
    
    def test_wrap_with_tor_wget(self):
        """Test _wrap_with_tor with wget command."""
        tool = ShellExecutorTool()
        
        wrapped = tool._wrap_with_tor("wget https://example.com")
        
        assert "wget https://example.com" in wrapped
        assert "use_proxy=yes" in wrapped
        assert "http_proxy=" in wrapped
    
    def test_wrap_with_tor_other(self):
        """Test _wrap_with_tor with non-curl/wget command."""
        tool = ShellExecutorTool()
        
        wrapped = tool._wrap_with_tor("echo test")
        
        assert wrapped == "echo test"
    
    def test_execute_with_cwd(self):
        """Test executing command with custom working directory."""
        tool = ShellExecutorTool()
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "output"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool.execute("echo test", cwd="/tmp")
            
            assert result["success"] is True
            call_args = mock_run.call_args
            assert call_args[1]["cwd"] == "/tmp"
    
    def test_execute_script_with_cwd(self):
        """Test executing script with custom working directory."""
        tool = ShellExecutorTool()
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.stdout = "output"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool.execute_script("print('test')", script_type="python", cwd="/tmp")
            
            assert result["success"] is True
            call_args = mock_run.call_args
            assert call_args[1]["cwd"] == "/tmp"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
