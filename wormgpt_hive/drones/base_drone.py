from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class DroneCapability:
    name: str
    description: str
    methods: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "methods": self.methods,
        }


@dataclass
class MissionStep:
    step_id: int
    action: str
    parameters: Dict[str, Any]
    reasoning: str
    status: str = "pending"
    observation: Optional[str] = None
    result: Optional[Any] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "action": self.action,
            "parameters": self.parameters,
            "reasoning": self.reasoning,
            "status": self.status,
            "observation": self.observation,
            "result": self.result,
            "timestamp": self.timestamp,
        }

    def mark_completed(self, observation: str, result: Any = None):
        self.status = "completed"
        self.observation = observation
        self.result = result

    def mark_failed(self, observation: str, error: Any = None):
        self.status = "failed"
        self.observation = observation
        self.result = {"error": error}


class BaseDrone(ABC):

    def __init__(self, name: str):
        self.name = name
        self.description = self.__doc__ or "No description available"
        self.tools = {}

    @abstractmethod
    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_supported_actions(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns a dictionary of supported actions with their descriptions and parameters.
        Example:
        {
            "action_name": {
                "description": "Description of action",
                "parameters": [
                    {"name": "param1", "type": "str", "description": "Desc of param1"},
                    {"name": "param2", "type": "int", "optional": true, "description": "Desc of param2"},
                ]
            }
        }
        """
        pass

    def get_capabilities(self) -> DroneCapability:
        supported_actions = self.get_supported_actions()
        methods = []
        for action_name, action_info in supported_actions.items():
            method_info = {
                "name": action_name,
                "description": action_info.get("description", "No description"),
                "parameters": action_info.get("parameters", []),
            }
            methods.append(method_info)

        return DroneCapability(
            name=self.name,
            description=self.description,
            methods=methods,
        )

    def register_tool(self, tool_name: str, tool_instance: Any):
        self.tools[tool_name] = tool_instance

    def _success_response(self, data: Any, message: str = "Success") -> Dict[str, Any]:
        return {"success": True, "message": message, "data": data, "drone": self.name}

    def _error_response(
        self, error: str, details: Optional[str] = None
    ) -> Dict[str, Any]:
        return {
            "success": False,
            "error": error,
            "details": details,
            "drone": self.name,
        }

    def _validate_parameters(
        self, parameters: Dict[str, Any], required: List[str]
    ) -> Optional[str]:
        missing = [param for param in required if param not in parameters]
        if missing:
            return f"Missing required parameters: {', '.join(missing)}"
        return None


class DroneRegistry:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DroneRegistry, cls).__new__(cls)
            cls._instance.drones = {}
            cls._instance.tools = {}
        return cls._instance

    def register_drone(self, drone: BaseDrone):
        self.drones[drone.name] = drone

    def register_tool(self, tool_name: str, tool_instance: Any):
        self.tools[tool_name] = tool_instance

    def get_drone(self, name: str) -> Optional[BaseDrone]:
        return self.drones.get(name)

    def get_tool(self, name: str) -> Optional[Any]:
        return self.tools.get(name)

    def get_all_drones(self) -> Dict[str, BaseDrone]:
        return self.drones

    def get_all_tools(self) -> Dict[str, Any]:
        return self.tools

    def get_capabilities_summary(self) -> Dict[str, Any]:
        return {
            "drones": {
                name: drone.get_capabilities().to_dict()
                for name, drone in self.drones.items()
            },
            "tools": {
                name: (
                    tool.get_capabilities()
                    if hasattr(tool, "get_capabilities")
                    else {"name": name}
                )
                for name, tool in self.tools.items()
            },
        }

    def clear(self):
        self.drones.clear()
        self.tools.clear()
