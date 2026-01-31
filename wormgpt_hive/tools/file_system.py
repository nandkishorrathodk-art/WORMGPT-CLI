import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base_tool import BaseTool


class FileSystemTool(BaseTool):
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        actions = {
            "read": self.read_file,
            "write": self.write_file,
            "list": self.list_files,
            "delete": self.delete_file,
            "exists": self.file_exists,
            "create_dir": self.create_directory
        }
        
        if action not in actions:
            return self._error_response(f"Unknown action: {action}")
        
        try:
            return actions[action](**kwargs)
        except Exception as e:
            return self._error_response(str(e), f"Action: {action}")
    
    def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return self._success_response(
                {"content": content, "path": file_path},
                f"Read {len(content)} characters from {file_path}"
            )
        except FileNotFoundError:
            return self._error_response(f"File not found: {file_path}")
        except Exception as e:
            return self._error_response(f"Failed to read file: {str(e)}")
    
    def write_file(self, file_path: str, content: str, mode: str = "w", encoding: str = "utf-8") -> Dict[str, Any]:
        try:
            dirname = os.path.dirname(file_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
            
            return self._success_response(
                {"path": file_path, "bytes_written": len(content.encode(encoding))},
                f"Written to {file_path}"
            )
        except Exception as e:
            return self._error_response(f"Failed to write file: {str(e)}")
    
    def list_files(self, directory: str = ".", pattern: str = "*", recursive: bool = False) -> Dict[str, Any]:
        try:
            path = Path(directory)
            
            if not path.exists():
                return self._error_response(f"Directory not found: {directory}")
            
            if recursive:
                files = [str(p) for p in path.rglob(pattern) if p.is_file()]
            else:
                files = [str(p) for p in path.glob(pattern) if p.is_file()]
            
            return self._success_response(
                {"files": files, "count": len(files)},
                f"Found {len(files)} files in {directory}"
            )
        except Exception as e:
            return self._error_response(f"Failed to list files: {str(e)}")
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        try:
            if not os.path.exists(file_path):
                return self._error_response(f"File not found: {file_path}")
            
            os.remove(file_path)
            return self._success_response(
                {"path": file_path},
                f"Deleted {file_path}"
            )
        except Exception as e:
            return self._error_response(f"Failed to delete file: {str(e)}")
    
    def file_exists(self, file_path: str) -> Dict[str, Any]:
        exists = os.path.exists(file_path)
        return self._success_response(
            {"exists": exists, "path": file_path},
            f"File {'exists' if exists else 'does not exist'}: {file_path}"
        )
    
    def create_directory(self, directory: str, exist_ok: bool = True) -> Dict[str, Any]:
        try:
            os.makedirs(directory, exist_ok=exist_ok)
            return self._success_response(
                {"path": directory},
                f"Created directory {directory}"
            )
        except Exception as e:
            return self._error_response(f"Failed to create directory: {str(e)}")
