import socket
import requests
from typing import Any, Dict, Optional
from .base_tool import BaseTool

try:
    import socks
except ImportError:
    socks = None


class TorProxyTool(BaseTool):
    """Tool for routing network requests through Tor SOCKS5 proxy for anonymity."""
    
    def __init__(self, proxy_host: str = "127.0.0.1", proxy_port: int = 9050, timeout: int = 30):
        super().__init__()
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.timeout = timeout
        self.proxies = {
            'http': f'socks5h://{proxy_host}:{proxy_port}',
            'https': f'socks5h://{proxy_host}:{proxy_port}'
        }
        
        if socks is None:
            raise ImportError("PySocks package not installed. Run: pip install PySocks")
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        operation = kwargs.get("operation", "test_connection")
        
        if operation == "test_connection":
            return self.test_connection()
        elif operation == "get_ip":
            return self.get_exit_ip()
        elif operation == "fetch_url":
            url = kwargs.get("url")
            if not url:
                return self._error_response("Missing required parameter: url")
            return self.fetch_url(url)
        else:
            return self._error_response(f"Unknown operation: {operation}")
    
    def test_connection(self) -> Dict[str, Any]:
        try:
            session = requests.Session()
            session.proxies = self.proxies
            
            response = session.get(
                "https://check.torproject.org/api/ip",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            is_tor = data.get("IsTor", False)
            ip = data.get("IP", "unknown")
            
            if is_tor:
                return self._success_response(
                    {
                        "connected": True,
                        "is_tor": True,
                        "exit_ip": ip
                    },
                    f"Successfully connected to Tor network (Exit IP: {ip})"
                )
            else:
                return self._error_response(
                    "Connected but not using Tor network",
                    f"Current IP: {ip}"
                )
        
        except requests.exceptions.ConnectionError:
            return self._error_response(
                "Failed to connect to Tor proxy",
                f"Check if Tor service is running on {self.proxy_host}:{self.proxy_port}"
            )
        except requests.exceptions.Timeout:
            return self._error_response(
                f"Connection timeout after {self.timeout}s",
                "Tor network may be slow or unavailable"
            )
        except Exception as e:
            return self._error_response(
                f"Unexpected error: {str(e)}",
                "Failed to test Tor connection"
            )
    
    def get_exit_ip(self) -> Dict[str, Any]:
        try:
            session = requests.Session()
            session.proxies = self.proxies
            
            response = session.get(
                "https://api.ipify.org?format=json",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            exit_ip = data.get("ip", "unknown")
            
            return self._success_response(
                {
                    "exit_ip": exit_ip,
                    "provider": "ipify"
                },
                f"Tor exit IP: {exit_ip}"
            )
        
        except Exception as e:
            return self._error_response(
                f"Failed to get exit IP: {str(e)}",
                "Could not determine Tor exit node IP"
            )
    
    def fetch_url(self, url: str, parse_json: bool = False) -> Dict[str, Any]:
        try:
            session = requests.Session()
            session.proxies = self.proxies
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0"
            })
            
            response = session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            if parse_json:
                try:
                    content = response.json()
                except ValueError:
                    return self._error_response(
                        "Response is not valid JSON",
                        f"URL: {url}"
                    )
            else:
                content = response.text
            
            return self._success_response(
                {
                    "url": url,
                    "status_code": response.status_code,
                    "content": content,
                    "content_length": len(response.text),
                    "via_tor": True
                },
                f"Fetched {url} via Tor ({len(response.text)} bytes)"
            )
        
        except requests.exceptions.ConnectionError:
            return self._error_response(
                "Failed to connect via Tor",
                f"URL: {url}"
            )
        except requests.exceptions.Timeout:
            return self._error_response(
                f"Request timeout after {self.timeout}s",
                f"URL: {url}"
            )
        except requests.exceptions.RequestException as e:
            return self._error_response(
                f"Request failed: {str(e)}",
                f"URL: {url}"
            )
        except Exception as e:
            return self._error_response(
                f"Unexpected error: {str(e)}",
                f"URL: {url}"
            )
    
    def is_tor_available(self) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.proxy_host, self.proxy_port))
            sock.close()
            return result == 0
        except Exception:
            return False
