from typing import Any, Dict
from .base_drone import BaseDrone


class OPSECDrone(BaseDrone):
    """OPSEC Drone: Provides operational security capabilities including Tor network routing for web requests and commands, IP verification, and anonymized operations. Can test Tor connectivity, fetch content anonymously, and execute commands with enhanced privacy."""

    def __init__(self):
        super().__init__("OPSECDrone")

    def get_supported_actions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "test_tor_connection": {
                "description": "Tests if Tor proxy is configured correctly and connected to the Tor network.",
                "parameters": []
            },
            "get_tor_ip": {
                "description": "Retrieves the current IP address as seen from the Tor network (Tor exit node IP).",
                "parameters": []
            },
            "fetch_url_via_tor": {
                "description": "Fetches content from a specified URL routing the request through the Tor network.",
                "parameters": [
                    {"name": "url", "type": "str", "description": "The URL to fetch content from."},
                    {"name": "parse_json", "type": "bool", "optional": True, "description": "If True, attempts to parse the response as JSON. Defaults to False."}
                ]
            },
            "execute_command_via_tor": {
                "description": "Executes a shell command, routing its network traffic through the Tor network.",
                "parameters": [
                    {"name": "command", "type": "str", "description": "The shell command to execute."},
                    {"name": "cwd", "type": "str", "optional": True, "description": "The current working directory for the command."},
                    {"name": "timeout", "type": "int", "optional": True, "description": "Maximum time in seconds to wait for the command to complete."}
                ]
            },
            "check_tor_availability": {
                "description": "Checks if the Tor proxy service is running and accessible.",
                "parameters": []
            }
        }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "test_tor_connection":
            return self._test_tor_connection(parameters)
        elif action == "get_tor_ip":
            return self._get_tor_ip(parameters)
        elif action == "fetch_url_via_tor":
            return self._fetch_url_via_tor(parameters)
        elif action == "execute_command_via_tor":
            return self._execute_command_via_tor(parameters)
        elif action == "check_tor_availability":
            return self._check_tor_availability(parameters)
        else:
            return self._error_response(f"Unknown action: {action}")

    def _test_tor_connection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        tor_proxy = self.tools.get("tor_proxy")
        if not tor_proxy:
            return self._error_response("TorProxyTool not registered")

        result = tor_proxy.execute(operation="test_connection")

        if result["success"]:
            data = result["data"]
            if data.get("is_tor"):
                return self._success_response(
                    data, f"Tor connection verified (Exit IP: {data.get('exit_ip')})"
                )
            else:
                return self._error_response(
                    "Not using Tor network", f"Current IP: {data.get('exit_ip')}"
                )
        else:
            return result

    def _get_tor_ip(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        tor_proxy = self.tools.get("tor_proxy")
        if not tor_proxy:
            return self._error_response("TorProxyTool not registered")

        result = tor_proxy.execute(operation="get_ip")

        if result["success"]:
            data = result["data"]
            return self._success_response(data, f"Tor exit IP: {data.get('exit_ip')}")
        else:
            return result

    def _fetch_url_via_tor(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["url"])
        if error:
            return self._error_response(error)

        tor_proxy = self.tools.get("tor_proxy")
        if not tor_proxy:
            return self._error_response("TorProxyTool not registered")

        if not tor_proxy.is_tor_available():
            return self._error_response(
                "Tor service not available",
                f"Check if Tor is running on {tor_proxy.proxy_host}:{tor_proxy.proxy_port}",
            )

        url = parameters["url"]
        parse_json = parameters.get("parse_json", False)

        result = tor_proxy.fetch_url(url, parse_json)

        if result["success"]:
            data = result["data"]
            content_preview = str(data.get("content", ""))[:200]
            return self._success_response(
                data, f"Fetched {url} via Tor ({data.get('content_length')} bytes)"
            )
        else:
            return result

    def _execute_command_via_tor(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["command"])
        if error:
            return self._error_response(error)

        tor_proxy = self.tools.get("tor_proxy")
        if not tor_proxy:
            return self._error_response("TorProxyTool not registered")

        if not tor_proxy.is_tor_available():
            return self._error_response(
                "Tor service not available",
                f"Check if Tor is running on {tor_proxy.proxy_host}:{tor_proxy.proxy_port}",
            )

        shell_tool = self.tools.get("shell_executor")
        if not shell_tool:
            return self._error_response("ShellExecutorTool not registered")

        command = parameters["command"]
        cwd = parameters.get("cwd")
        timeout = parameters.get("timeout")

        env_with_tor = {
            "HTTP_PROXY": f"socks5h://{tor_proxy.proxy_host}:{tor_proxy.proxy_port}",
            "HTTPS_PROXY": f"socks5h://{tor_proxy.proxy_host}:{tor_proxy.proxy_port}",
            "http_proxy": f"socks5h://{tor_proxy.proxy_host}:{tor_proxy.proxy_port}",
            "https_proxy": f"socks5h://{tor_proxy.proxy_host}:{tor_proxy.proxy_port}",
        }

        result = shell_tool.execute(
            command=command, cwd=cwd, timeout=timeout, env_vars=env_with_tor
        )

        if result["success"]:
            data = result["data"]
            output = data["stdout"] if data["stdout"] else data["stderr"]
            return self._success_response(
                data,
                f"Command executed via Tor: {command[:50]}... (exit code: {data['returncode']})",
            )
        else:
            return result

    def _check_tor_availability(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        tor_proxy = self.tools.get("tor_proxy")
        if not tor_proxy:
            return self._error_response("TorProxyTool not registered")

        is_available = tor_proxy.is_tor_available()

        if is_available:
            return self._success_response(
                {
                    "available": True,
                    "host": tor_proxy.proxy_host,
                    "port": tor_proxy.proxy_port,
                },
                f"Tor proxy is available at {tor_proxy.proxy_host}:{tor_proxy.proxy_port}",
            )
        else:
            return self._error_response(
                "Tor proxy not available",
                f"No service listening on {tor_proxy.proxy_host}:{tor_proxy.proxy_port}",
            )
