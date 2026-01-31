from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description available"

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        pass

    def get_capabilities(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description}

    def _success_response(self, data: Any, message: str = "Success") -> Dict[str, Any]:
        return {"success": True, "message": message, "data": data}

    def _error_response(
        self, error: str, details: Optional[str] = None
    ) -> Dict[str, Any]:
        return {"success": False, "error": error, "details": details}
