import subprocess
import shlex
import platform
from typing import Any, Dict, Optional
from .base_tool import BaseTool


class ShellExecutorTool(BaseTool):
    
    def __init__(self, timeout: int = 30):
        super().__init__()
        self.timeout = timeout
        self.is_windows = platform.system() == "Windows"
    
    def execute(self, command: str, cwd: Optional[str] = None, timeout: Optional[int] = None, 
                shell: bool = True, use_tor: bool = False) -> Dict[str, Any]:
        try:
            actual_timeout = timeout or self.timeout
            
            if use_tor:
                command = self._wrap_with_tor(command)
            
            if self.is_windows and not shell:
                args = command
            elif not self.is_windows and not shell:
                args = shlex.split(command)
            else:
                args = command
            
            result = subprocess.run(
                args,
                shell=shell,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=actual_timeout
            )
            
            return self._success_response(
                {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "command": command
                },
                f"Command executed with exit code {result.returncode}"
            )
        
        except subprocess.TimeoutExpired:
            return self._error_response(
                f"Command timed out after {actual_timeout} seconds",
                f"Command: {command}"
            )
        except Exception as e:
            return self._error_response(
                f"Failed to execute command: {str(e)}",
                f"Command: {command}"
            )
    
    def _wrap_with_tor(self, command: str) -> str:
        from ..shared.config import TOR_PROXY_HOST, TOR_PROXY_PORT
        
        if "curl" in command:
            return f"{command} --socks5-hostname {TOR_PROXY_HOST}:{TOR_PROXY_PORT}"
        elif "wget" in command:
            return f"{command} -e use_proxy=yes -e http_proxy={TOR_PROXY_HOST}:{TOR_PROXY_PORT}"
        else:
            return command
    
    def execute_script(self, script_content: str, script_type: str = "bash", 
                       cwd: Optional[str] = None) -> Dict[str, Any]:
        try:
            interpreters = {
                "bash": "bash" if not self.is_windows else "cmd /c",
                "python": "python",
                "node": "node",
                "powershell": "powershell -Command"
            }
            
            if script_type not in interpreters:
                return self._error_response(f"Unsupported script type: {script_type}")
            
            interpreter = interpreters[script_type]
            
            result = subprocess.run(
                f"{interpreter}",
                input=script_content,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return self._success_response(
                {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "script_type": script_type
                },
                f"Script executed with exit code {result.returncode}"
            )
        
        except Exception as e:
            return self._error_response(
                f"Failed to execute script: {str(e)}",
                f"Script type: {script_type}"
            )
