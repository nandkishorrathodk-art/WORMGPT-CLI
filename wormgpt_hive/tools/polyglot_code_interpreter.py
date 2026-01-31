import subprocess
import os
import tempfile
import shutil
from typing import Dict, Any, Optional
from pathlib import Path
from .base_tool import BaseTool


class PolyglotCodeInterpreter(BaseTool):
    """Execute code in multiple programming languages (Python, Node.js, Go, Rust, Bash) with sandboxing and timeouts."""
    
    SUPPORTED_LANGUAGES = {
        "python": {
            "extension": ".py",
            "command": ["python"],
            "sandbox_dir": "sandbox/python"
        },
        "node": {
            "extension": ".js",
            "command": ["node"],
            "sandbox_dir": "sandbox/nodejs"
        },
        "nodejs": {
            "extension": ".js",
            "command": ["node"],
            "sandbox_dir": "sandbox/nodejs"
        },
        "javascript": {
            "extension": ".js",
            "command": ["node"],
            "sandbox_dir": "sandbox/nodejs"
        },
        "go": {
            "extension": ".go",
            "command": ["go", "run"],
            "sandbox_dir": "sandbox/go"
        },
        "rust": {
            "extension": ".rs",
            "command": ["rustc", "-o"],
            "sandbox_dir": "sandbox/rust",
            "compile_and_run": True
        },
        "bash": {
            "extension": ".sh",
            "command": ["bash"],
            "sandbox_dir": "sandbox/bash"
        },
        "shell": {
            "extension": ".sh",
            "command": ["bash"],
            "sandbox_dir": "sandbox/bash"
        }
    }
    
    def __init__(self, base_sandbox_dir: str = "wormgpt_hive/sandbox", default_timeout: int = 30):
        super().__init__()
        self.base_sandbox_dir = base_sandbox_dir
        self.default_timeout = default_timeout
        self._ensure_sandbox_directories()
    
    def _ensure_sandbox_directories(self):
        for lang_config in self.SUPPORTED_LANGUAGES.values():
            sandbox_path = Path(lang_config["sandbox_dir"])
            sandbox_path.mkdir(parents=True, exist_ok=True)
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        language = kwargs.get("language", "").lower()
        code = kwargs.get("code", "")
        timeout = kwargs.get("timeout", self.default_timeout)
        filename = kwargs.get("filename")
        
        if not language:
            return self._error_response("Language parameter is required")
        
        if not code:
            return self._error_response("Code parameter is required")
        
        if language not in self.SUPPORTED_LANGUAGES:
            return self._error_response(
                f"Unsupported language: {language}",
                f"Supported languages: {', '.join(set(self.SUPPORTED_LANGUAGES.keys()))}"
            )
        
        lang_config = self.SUPPORTED_LANGUAGES[language]
        
        try:
            result = self._execute_code(code, language, lang_config, timeout, filename)
            return self._success_response(
                result,
                f"Code executed successfully in {language}"
            )
        except Exception as e:
            return self._error_response(
                f"Execution failed: {str(e)}",
                details=f"Language: {language}, Timeout: {timeout}s"
            )
    
    def _execute_code(
        self, 
        code: str, 
        language: str, 
        lang_config: Dict[str, Any], 
        timeout: int,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        sandbox_dir = Path(lang_config["sandbox_dir"])
        
        if filename:
            base_filename = Path(filename).stem
        else:
            base_filename = f"code_{os.getpid()}"
        
        source_file = sandbox_dir / f"{base_filename}{lang_config['extension']}"
        
        try:
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            if lang_config.get("compile_and_run"):
                return self._compile_and_run(source_file, lang_config, timeout, sandbox_dir, base_filename)
            else:
                return self._run_interpreted(source_file, lang_config, timeout)
        
        finally:
            if source_file.exists():
                try:
                    source_file.unlink()
                except Exception:
                    pass
    
    def _run_interpreted(
        self, 
        source_file: Path, 
        lang_config: Dict[str, Any], 
        timeout: int
    ) -> Dict[str, Any]:
        command = lang_config["command"] + [str(source_file)]
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=source_file.parent
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "timed_out": False
            }
        
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "exit_code": -1,
                "timed_out": True
            }
    
    def _compile_and_run(
        self, 
        source_file: Path, 
        lang_config: Dict[str, Any], 
        timeout: int,
        sandbox_dir: Path,
        base_filename: str
    ) -> Dict[str, Any]:
        executable = sandbox_dir / base_filename
        if os.name == 'nt':
            executable = sandbox_dir / f"{base_filename}.exe"
        
        compile_command = lang_config["command"] + [str(executable), str(source_file)]
        
        try:
            compile_result = subprocess.run(
                compile_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=sandbox_dir
            )
            
            if compile_result.returncode != 0:
                return {
                    "stdout": compile_result.stdout,
                    "stderr": f"Compilation failed:\n{compile_result.stderr}",
                    "exit_code": compile_result.returncode,
                    "timed_out": False,
                    "compilation_failed": True
                }
            
            run_result = subprocess.run(
                [str(executable)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=sandbox_dir
            )
            
            return {
                "stdout": run_result.stdout,
                "stderr": run_result.stderr,
                "exit_code": run_result.returncode,
                "timed_out": False,
                "compilation_output": compile_result.stdout
            }
        
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "exit_code": -1,
                "timed_out": True
            }
        
        finally:
            if executable.exists():
                try:
                    executable.unlink()
                except Exception:
                    pass
    
    def check_language_available(self, language: str) -> Dict[str, Any]:
        if language not in self.SUPPORTED_LANGUAGES:
            return {
                "available": False,
                "error": f"Language {language} not supported"
            }
        
        lang_config = self.SUPPORTED_LANGUAGES[language]
        command = lang_config["command"][0]
        
        try:
            result = subprocess.run(
                [command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                "available": result.returncode == 0,
                "version": result.stdout.strip() if result.returncode == 0 else None,
                "error": result.stderr if result.returncode != 0 else None
            }
        
        except FileNotFoundError:
            return {
                "available": False,
                "error": f"{command} not found in PATH"
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }
    
    def get_supported_languages(self) -> list:
        return sorted(set(self.SUPPORTED_LANGUAGES.keys()))
