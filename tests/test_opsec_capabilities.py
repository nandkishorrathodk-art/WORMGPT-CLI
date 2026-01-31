"""
Test OPSEC capabilities including Tor proxy and OPSEC drone.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from wormgpt_hive.tools.tor_proxy import TorProxyTool
from wormgpt_hive.drones.opsec_drone import OPSECDrone


class TestTorProxyTool:
    """Test Tor proxy tool functionality."""
    
    def test_init(self):
        """Test Tor proxy tool initialization."""
        tor_tool = TorProxyTool(proxy_host="127.0.0.1", proxy_port=9050)
        
        assert tor_tool.proxy_host == "127.0.0.1"
        assert tor_tool.proxy_port == 9050
        assert tor_tool.timeout == 30
        assert tor_tool.proxies == {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
    
    @patch('wormgpt_hive.tools.tor_proxy.requests.Session')
    def test_test_connection_success(self, mock_session_class):
        """Test successful Tor connection test."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "IsTor": True,
            "IP": "185.220.101.1"
        }
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        tor_tool = TorProxyTool()
        result = tor_tool.test_connection()
        
        assert result["success"] is True
        assert result["data"]["is_tor"] is True
        assert result["data"]["exit_ip"] == "185.220.101.1"
        assert "Successfully connected to Tor" in result["message"]
    
    @patch('wormgpt_hive.tools.tor_proxy.requests.Session')
    def test_test_connection_not_using_tor(self, mock_session_class):
        """Test connection when not using Tor."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "IsTor": False,
            "IP": "1.2.3.4"
        }
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        tor_tool = TorProxyTool()
        result = tor_tool.test_connection()
        
        assert result["success"] is False
        assert "not using Tor network" in result["error"]
    
    @patch('wormgpt_hive.tools.tor_proxy.requests.Session')
    def test_get_exit_ip_success(self, mock_session_class):
        """Test getting Tor exit IP."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"ip": "185.220.101.1"}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        tor_tool = TorProxyTool()
        result = tor_tool.get_exit_ip()
        
        assert result["success"] is True
        assert result["data"]["exit_ip"] == "185.220.101.1"
        assert "Tor exit IP" in result["message"]
    
    @patch('wormgpt_hive.tools.tor_proxy.requests.Session')
    def test_fetch_url_success(self, mock_session_class):
        """Test fetching URL via Tor."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test content from website"
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        tor_tool = TorProxyTool()
        result = tor_tool.fetch_url("https://example.com")
        
        assert result["success"] is True
        assert result["data"]["url"] == "https://example.com"
        assert result["data"]["status_code"] == 200
        assert result["data"]["content"] == "Test content from website"
        assert result["data"]["via_tor"] is True
    
    @patch('wormgpt_hive.tools.tor_proxy.requests.Session')
    def test_fetch_url_json(self, mock_session_class):
        """Test fetching JSON content via Tor."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"key": "value"}'
        mock_response.json.return_value = {"key": "value"}
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        tor_tool = TorProxyTool()
        result = tor_tool.fetch_url("https://api.example.com", parse_json=True)
        
        assert result["success"] is True
        assert result["data"]["content"] == {"key": "value"}
    
    @patch('wormgpt_hive.tools.tor_proxy.socket.socket')
    def test_is_tor_available_true(self, mock_socket_class):
        """Test Tor availability check when Tor is running."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket
        
        tor_tool = TorProxyTool()
        result = tor_tool.is_tor_available()
        
        assert result is True
        mock_socket.connect_ex.assert_called_once_with(("127.0.0.1", 9050))
    
    @patch('wormgpt_hive.tools.tor_proxy.socket.socket')
    def test_is_tor_available_false(self, mock_socket_class):
        """Test Tor availability check when Tor is not running."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 1
        mock_socket_class.return_value = mock_socket
        
        tor_tool = TorProxyTool()
        result = tor_tool.is_tor_available()
        
        assert result is False


class TestOPSECDrone:
    """Test OPSEC drone functionality."""
    
    def test_init(self):
        """Test OPSEC drone initialization."""
        drone = OPSECDrone()
        
        assert drone.name == "OPSECDrone"
        assert "operational security" in drone.description.lower()
    
    def test_test_tor_connection_success(self):
        """Test Tor connection test via drone."""
        drone = OPSECDrone()
        
        mock_tor_tool = Mock()
        mock_tor_tool.execute.return_value = {
            "success": True,
            "data": {
                "is_tor": True,
                "exit_ip": "185.220.101.1"
            }
        }
        
        drone.register_tool("tor_proxy", mock_tor_tool)
        
        result = drone.execute("test_tor_connection", {})
        
        assert result["success"] is True
        assert "Tor connection verified" in result["message"]
        mock_tor_tool.execute.assert_called_once_with(operation="test_connection")
    
    def test_get_tor_ip_success(self):
        """Test getting Tor IP via drone."""
        drone = OPSECDrone()
        
        mock_tor_tool = Mock()
        mock_tor_tool.execute.return_value = {
            "success": True,
            "data": {
                "exit_ip": "185.220.101.1"
            }
        }
        
        drone.register_tool("tor_proxy", mock_tor_tool)
        
        result = drone.execute("get_tor_ip", {})
        
        assert result["success"] is True
        assert "185.220.101.1" in result["message"]
    
    def test_fetch_url_via_tor_success(self):
        """Test fetching URL via Tor through drone."""
        drone = OPSECDrone()
        
        mock_tor_tool = Mock()
        mock_tor_tool.is_tor_available.return_value = True
        mock_tor_tool.fetch_url.return_value = {
            "success": True,
            "data": {
                "url": "https://example.com",
                "content": "Test content",
                "content_length": 12,
                "via_tor": True
            }
        }
        
        drone.register_tool("tor_proxy", mock_tor_tool)
        
        result = drone.execute("fetch_url_via_tor", {"url": "https://example.com"})
        
        assert result["success"] is True
        assert "via Tor" in result["message"]
        mock_tor_tool.fetch_url.assert_called_once_with("https://example.com", False)
    
    def test_fetch_url_via_tor_not_available(self):
        """Test fetching URL when Tor is not available."""
        drone = OPSECDrone()
        
        mock_tor_tool = Mock()
        mock_tor_tool.is_tor_available.return_value = False
        mock_tor_tool.proxy_host = "127.0.0.1"
        mock_tor_tool.proxy_port = 9050
        
        drone.register_tool("tor_proxy", mock_tor_tool)
        
        result = drone.execute("fetch_url_via_tor", {"url": "https://example.com"})
        
        assert result["success"] is False
        assert "Tor service not available" in result["error"]
    
    def test_execute_command_via_tor_success(self):
        """Test executing command via Tor through drone."""
        drone = OPSECDrone()
        
        mock_tor_tool = Mock()
        mock_tor_tool.is_tor_available.return_value = True
        mock_tor_tool.proxy_host = "127.0.0.1"
        mock_tor_tool.proxy_port = 9050
        
        mock_shell_tool = Mock()
        mock_shell_tool.execute.return_value = {
            "success": True,
            "data": {
                "stdout": "Command output",
                "stderr": "",
                "returncode": 0
            }
        }
        
        drone.register_tool("tor_proxy", mock_tor_tool)
        drone.register_tool("shell_executor", mock_shell_tool)
        
        result = drone.execute("execute_command_via_tor", {"command": "curl https://check.torproject.org"})
        
        assert result["success"] is True
        assert "via Tor" in result["message"]
        
        call_args = mock_shell_tool.execute.call_args
        assert call_args[1]["command"] == "curl https://check.torproject.org"
        assert "HTTP_PROXY" in call_args[1]["env_vars"]
    
    def test_check_tor_availability_available(self):
        """Test checking Tor availability when available."""
        drone = OPSECDrone()
        
        mock_tor_tool = Mock()
        mock_tor_tool.is_tor_available.return_value = True
        mock_tor_tool.proxy_host = "127.0.0.1"
        mock_tor_tool.proxy_port = 9050
        
        drone.register_tool("tor_proxy", mock_tor_tool)
        
        result = drone.execute("check_tor_availability", {})
        
        assert result["success"] is True
        assert result["data"]["available"] is True
    
    def test_check_tor_availability_not_available(self):
        """Test checking Tor availability when not available."""
        drone = OPSECDrone()
        
        mock_tor_tool = Mock()
        mock_tor_tool.is_tor_available.return_value = False
        mock_tor_tool.proxy_host = "127.0.0.1"
        mock_tor_tool.proxy_port = 9050
        
        drone.register_tool("tor_proxy", mock_tor_tool)
        
        result = drone.execute("check_tor_availability", {})
        
        assert result["success"] is False
        assert "not available" in result["error"]
    
    def test_unknown_action(self):
        """Test handling of unknown action."""
        drone = OPSECDrone()
        
        result = drone.execute("unknown_action", {})
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]
    
    def test_missing_required_parameter(self):
        """Test handling of missing required parameters."""
        drone = OPSECDrone()
        
        mock_tor_tool = Mock()
        drone.register_tool("tor_proxy", mock_tor_tool)
        
        result = drone.execute("fetch_url_via_tor", {})
        
        assert result["success"] is False
        assert "Missing required parameter" in result["error"]


class TestStateEncryption:
    """Test state encryption capabilities."""
    
    def test_state_encryption_enabled(self):
        """Test that state manager can encrypt data."""
        from wormgpt_hive.shared.state_manager import StateManager
        
        encryption_key = "test_encryption_key_12345678"
        state_manager = StateManager(
            file_path="test_encrypted_state.json",
            encryption_key=encryption_key
        )
        
        assert state_manager.fernet is not None
    
    def test_state_encryption_disabled(self):
        """Test that state manager works without encryption."""
        from wormgpt_hive.shared.state_manager import StateManager
        
        state_manager = StateManager(
            file_path="test_plain_state.json",
            encryption_key=None
        )
        
        assert state_manager.fernet is None
    
    @patch('wormgpt_hive.shared.state_manager.os.path.exists')
    @patch('builtins.open', create=True)
    def test_save_and_load_encrypted_state(self, mock_open, mock_exists):
        """Test saving and loading encrypted state."""
        from wormgpt_hive.shared.state_manager import StateManager
        
        encryption_key = "test_encryption_key_12345678"
        state_manager = StateManager(
            file_path="test_encrypted_state.json",
            encryption_key=encryption_key
        )
        
        test_state = {
            "version": "0.11.0",
            "missions": [
                {
                    "id": 1,
                    "goal": "Test mission",
                    "status": "completed"
                }
            ]
        }
        
        state_manager.save_state(test_state)
        
        mock_open.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
