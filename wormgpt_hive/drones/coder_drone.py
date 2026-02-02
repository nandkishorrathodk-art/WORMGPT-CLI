from typing import Any, Dict
from .base_drone import BaseDrone


class CoderDrone(BaseDrone):
    """Coder Drone: Manages file system operations for code and data files. Can read, write, edit, list, delete files and create directories. Essential for all file manipulation tasks."""

    def __init__(self):
        super().__init__("CoderDrone")

    def get_supported_actions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "read_file": {
                "description": "Reads the content of a specified file.",
                "parameters": [
                    {"name": "file_path", "type": "str", "description": "The path to the file to read."}
                ]
            },
            "write_file": {
                "description": "Writes content to a specified file. If the file exists, it will be overwritten.",
                "parameters": [
                    {"name": "file_path", "type": "str", "description": "The path to the file to write to."},
                    {"name": "content", "type": "str", "description": "The content to write to the file."},
                    {"name": "mode", "type": "str", "optional": True, "description": "The mode to open the file in (e.g., 'w' for write, 'a' for append). Defaults to 'w'."}
                ]
            },
            "list_files": {
                "description": "Lists files and directories within a specified path.",
                "parameters": [
                    {"name": "directory", "type": "str", "optional": True, "description": "The directory to list. Defaults to current directory."},
                    {"name": "pattern", "type": "str", "optional": True, "description": "A glob-style pattern to filter files (e.g., '*.py'). Defaults to '*'."},
                    {"name": "recursive", "type": "bool", "optional": True, "description": "Whether to list files recursively. Defaults to False."}
                ]
            },
            "delete_file": {
                "description": "Deletes a specified file.",
                "parameters": [
                    {"name": "file_path", "type": "str", "description": "The path to the file to delete."}
                ]
            },
            "create_directory": {
                "description": "Creates a new directory.",
                "parameters": [
                    {"name": "directory", "type": "str", "description": "The path to the directory to create."},
                    {"name": "exist_ok", "type": "bool", "optional": True, "description": "If False, an error is raised if the directory already exists. Defaults to True."}
                ]
            },
            "file_exists": {
                "description": "Checks if a file exists at the specified path.",
                "parameters": [
                    {"name": "file_path", "type": "str", "description": "The path to the file to check."}
                ]
            }
        }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "read_file":
            return self._read_file(parameters)
        elif action == "write_file":
            return self._write_file(parameters)
        elif action == "list_files":
            return self._list_files(parameters)
        elif action == "delete_file":
            return self._delete_file(parameters)
        elif action == "create_directory":
            return self._create_directory(parameters)
        elif action == "file_exists":
            return self._file_exists(parameters)
        else:
            return self._error_response(f"Unknown action: {action}")

    def _read_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["file_path"])
        if error:
            return self._error_response(error)

        fs_tool = self.tools.get("file_system")
        if not fs_tool:
            return self._error_response("FileSystemTool not registered")

        result = fs_tool.execute("read", file_path=parameters["file_path"])

        if result["success"]:
            content = result["data"]["content"]
            lines = content.count("\n") + 1
            return self._success_response(
                result["data"], f"Read {lines} lines from {parameters['file_path']}"
            )
        else:
            return result

    def _write_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["file_path", "content"])
        if error:
            return self._error_response(error)

        fs_tool = self.tools.get("file_system")
        if not fs_tool:
            return self._error_response("FileSystemTool not registered")

        result = fs_tool.execute(
            "write",
            file_path=parameters["file_path"],
            content=parameters["content"],
            mode=parameters.get("mode", "w"),
        )

        if result["success"]:
            return self._success_response(
                result["data"],
                f"Written {result['data']['bytes_written']} bytes to {parameters['file_path']}",
            )
        else:
            return result

    def _list_files(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        fs_tool = self.tools.get("file_system")
        if not fs_tool:
            return self._error_response("FileSystemTool not registered")

        result = fs_tool.execute(
            "list",
            directory=parameters.get("directory", "."),
            pattern=parameters.get("pattern", "*"),
            recursive=parameters.get("recursive", False),
        )

        if result["success"]:
            return self._success_response(
                result["data"], f"Found {result['data']['count']} files"
            )
        else:
            return result

    def _delete_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["file_path"])
        if error:
            return self._error_response(error)

        fs_tool = self.tools.get("file_system")
        if not fs_tool:
            return self._error_response("FileSystemTool not registered")

        result = fs_tool.execute("delete", file_path=parameters["file_path"])
        return result

    def _create_directory(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["directory"])
        if error:
            return self._error_response(error)

        fs_tool = self.tools.get("file_system")
        if not fs_tool:
            return self._error_response("FileSystemTool not registered")

        result = fs_tool.execute(
            "create_dir",
            directory=parameters["directory"],
            exist_ok=parameters.get("exist_ok", True),
        )
        return result

    def _file_exists(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["file_path"])
        if error:
            return self._error_response(error)

        fs_tool = self.tools.get("file_system")
        if not fs_tool:
            return self._error_response("FileSystemTool not registered")

        result = fs_tool.execute("exists", file_path=parameters["file_path"])
        return result
