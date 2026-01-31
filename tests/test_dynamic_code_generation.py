import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wormgpt_hive.drones.polyglot_drone import PolyglotDrone
from wormgpt_hive.drones.tool_maker_drone import ToolMakerDrone
from wormgpt_hive.tools.polyglot_code_interpreter import PolyglotCodeInterpreter
from wormgpt_hive.drones.base_drone import DroneRegistry


@pytest.fixture
def polyglot_interpreter():
    return PolyglotCodeInterpreter()


@pytest.fixture
def polyglot_drone(polyglot_interpreter):
    drone = PolyglotDrone()
    drone.register_tool("polyglot_interpreter", polyglot_interpreter)
    return drone


@pytest.fixture
def tool_maker_drone():
    drone = ToolMakerDrone()
    return drone


def test_polyglot_drone_execute_python(polyglot_drone):
    result = polyglot_drone.execute(
        action="execute_code",
        parameters={
            "language": "python",
            "code": "print('Test execution')"
        }
    )
    
    assert result["success"] is True
    assert result["drone"] == "PolyglotDrone"
    assert "Test execution" in result["data"]["stdout"]


def test_polyglot_drone_execute_bash(polyglot_drone):
    result = polyglot_drone.execute(
        action="execute_code",
        parameters={
            "language": "bash",
            "code": "echo 'Bash test'"
        }
    )
    
    assert result["success"] is True
    assert "Bash test" in result["data"]["stdout"]


def test_polyglot_drone_code_with_error(polyglot_drone):
    result = polyglot_drone.execute(
        action="execute_code",
        parameters={
            "language": "python",
            "code": "print('Unclosed string"
        }
    )
    
    assert result["success"] is False
    assert "exit code" in result["error"].lower()


def test_polyglot_drone_list_languages(polyglot_drone):
    result = polyglot_drone.execute(
        action="list_languages",
        parameters={}
    )
    
    assert result["success"] is True
    assert "languages" in result["data"]
    assert isinstance(result["data"]["languages"], list)
    assert "python" in result["data"]["languages"]


def test_polyglot_drone_check_language(polyglot_drone):
    result = polyglot_drone.execute(
        action="check_language",
        parameters={"language": "python"}
    )
    
    assert result["success"] is True


def test_polyglot_drone_generate_and_execute_mock():
    drone = PolyglotDrone()
    interpreter = PolyglotCodeInterpreter()
    drone.register_tool("polyglot_interpreter", interpreter)
    
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "print('Generated code')"
    mock_llm.chat.completions.create.return_value = mock_response
    mock_llm.default_model = "test-model"
    
    drone.register_tool("llm_client", mock_llm)
    
    result = drone.execute(
        action="generate_and_execute",
        parameters={
            "language": "python",
            "task": "print a greeting message"
        }
    )
    
    assert result["success"] is True
    assert "generated_code" in result["data"]


def test_tool_maker_drone_class_name_generation(tool_maker_drone):
    assert tool_maker_drone._generate_class_name("string_reverser") == "StringReverserTool"
    assert tool_maker_drone._generate_class_name("data processor") == "DataProcessorTool"
    assert tool_maker_drone._generate_class_name("my-custom-tool") == "MyCustomToolTool"


def test_tool_maker_drone_ensure_imports(tool_maker_drone):
    code_without_imports = """
class TestTool:
    pass
"""
    
    code_with_imports = tool_maker_drone._ensure_proper_imports(code_without_imports)
    
    assert "from .base_tool import BaseTool" in code_with_imports
    assert "from typing import" in code_with_imports


def test_tool_maker_drone_analyze_code(tool_maker_drone):
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "This code is well-structured."
    mock_llm.chat.completions.create.return_value = mock_response
    mock_llm.default_model = "test-model"
    
    tool_maker_drone.register_tool("llm_client", mock_llm)
    
    test_file = Path("wormgpt_hive/tools/base_tool.py")
    
    if test_file.exists():
        result = tool_maker_drone.execute(
            action="analyze_code",
            parameters={
                "file_path": str(test_file),
                "analysis_goal": "Review code quality"
            }
        )
        
        assert result["success"] is True
        assert "analysis" in result["data"]


def test_tool_maker_drone_modify_code_with_approval(tool_maker_drone):
    mock_llm = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """from .base_tool import BaseTool

class ImprovedTool(BaseTool):
    def execute(self, **kwargs):
        return self._success_response({}, "Improved")
"""
    mock_llm.chat.completions.create.return_value = mock_response
    mock_llm.default_model = "test-model"
    
    tool_maker_drone.register_tool("llm_client", mock_llm)
    
    test_file = Path("wormgpt_hive/tools/base_tool.py")
    
    if test_file.exists():
        result = tool_maker_drone.execute(
            action="modify_code",
            parameters={
                "file_path": str(test_file),
                "modification_goal": "Add a helper method",
                "require_approval": True
            }
        )
        
        assert result["success"] is True
        assert result["data"]["approval_required"] is True
        assert "modified_code" in result["data"]
        assert "original_code" in result["data"]


def test_tool_maker_drone_reload_existing_tool(tool_maker_drone):
    registry = DroneRegistry()
    tool_maker_drone.register_tool("registry", registry)
    
    result = tool_maker_drone.execute(
        action="reload_tool",
        parameters={"tool_file": "file_system.py"}
    )
    
    assert result["success"] is True
    assert "tool_classes" in result["data"]


def test_polyglot_drone_missing_parameters(polyglot_drone):
    result = polyglot_drone.execute(
        action="execute_code",
        parameters={"language": "python"}
    )
    
    assert result["success"] is False
    assert "Missing required parameters" in result["error"]


def test_polyglot_drone_unknown_action(polyglot_drone):
    result = polyglot_drone.execute(
        action="unknown_action",
        parameters={}
    )
    
    assert result["success"] is False
    assert "Unknown action" in result["error"]


def test_tool_maker_drone_unknown_action(tool_maker_drone):
    result = tool_maker_drone.execute(
        action="invalid_action",
        parameters={}
    )
    
    assert result["success"] is False
    assert "Unknown action" in result["error"]


def test_integration_polyglot_python_math(polyglot_drone):
    result = polyglot_drone.execute(
        action="execute_code",
        parameters={
            "language": "python",
            "code": """
import math
result = math.sqrt(16)
print(f"Square root of 16 is {result}")
"""
        }
    )
    
    assert result["success"] is True
    assert "Square root of 16 is 4" in result["data"]["stdout"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
