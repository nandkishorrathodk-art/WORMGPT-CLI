from typing import Any, Dict
from .base_drone import BaseDrone


class ShellDrone(BaseDrone):
    """Shell Drone: Executes shell commands and scripts on the system. Capabilities include running arbitrary shell commands, executing scripts in various languages (bash, python, node, powershell), and optionally routing through Tor for anonymity."""

    def __init__(self):
        super().__init__("ShellDrone")

    def get_supported_actions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "execute_command": {
                "description": "Executes a single shell command.",
                "parameters": [
                    {"name": "command", "type": "str", "description": "The shell command to execute."},
                    {"name": "cwd", "type": "str", "optional": True, "description": "The current working directory for the command."},
                    {"name": "timeout", "type": "int", "optional": True, "description": "Maximum time in seconds to wait for the command to complete."},
                    {"name": "use_tor", "type": "bool", "optional": True, "description": "If true, routes the command through Tor for anonymity. Requires Tor proxy to be running."}
                ]
            },
            "execute_script": {
                "description": "Executes a script in a specified language.",
                "parameters": [
                    {"name": "script_content", "type": "str", "description": "The content of the script to execute."},
                    {"name": "script_type", "type": "str", "description": "The type of script (e.g., 'bash', 'python', 'node', 'powershell')."},
                    {"name": "cwd", "type": "str", "optional": True, "description": "The current working directory for the script."}
                ]
            }
        }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "execute_command":
            return self._execute_command(parameters)
        elif action == "execute_script":
            return self._execute_script(parameters)
        else:
            return self._error_response(f"Unknown action: {action}")

    def _execute_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["command"])
        if error:
            return self._error_response(error)

        shell_tool = self.tools.get("shell_executor")
        if not shell_tool:
            return self._error_response("ShellExecutorTool not registered")

        command = parameters["command"]
        cwd = parameters.get("cwd")
        timeout = parameters.get("timeout")
        use_tor = parameters.get("use_tor", False)

        result = shell_tool.execute(
            command=command, cwd=cwd, timeout=timeout, use_tor=use_tor
        )

        if result["success"]:
            data = result["data"]
            output = data["stdout"] if data["stdout"] else data["stderr"]
            return self._success_response(
                data,
                f"Command executed: {command[:50]}... (exit code: {data['returncode']})",
            )
        else:
            return result

    def _execute_script(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["script_content", "script_type"])
        if error:
            return self._error_response(error)

        shell_tool = self.tools.get("shell_executor")
        if not shell_tool:
            return self._error_response("ShellExecutorTool not registered")

        result = shell_tool.execute_script(
            script_content=parameters["script_content"],
            script_type=parameters["script_type"],
            cwd=parameters.get("cwd"),
        )

        if result["success"]:
            data = result["data"]
            return self._success_response(
                data,
                f"{data['script_type']} script executed (exit code: {data['returncode']})",
            )
        else:
            return result
