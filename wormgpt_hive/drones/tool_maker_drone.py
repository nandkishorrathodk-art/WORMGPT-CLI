from typing import Any, Dict
from .base_drone import BaseDrone
from pathlib import Path
import importlib
import sys


class ToolMakerDrone(BaseDrone):
    """Tool-Maker Drone: Dynamically generates new Python tools based on descriptions, writes them to the tools directory, and integrates them into the Hive Mind for immediate use. Can also analyze and modify existing code (alpha feature)."""

    def __init__(self):
        super().__init__("ToolMakerDrone")
        self.tools_dir = Path("wormgpt_hive/tools")

    def get_supported_actions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "create_tool": {
                "description": "Generates a new Python tool class based on a description and integrates it into the system.",
                "parameters": [
                    {"name": "tool_name", "type": "str", "description": "A concise, descriptive name for the new tool (e.g., 'JSON Validator', 'URL Shortener')."},
                    {"name": "description", "type": "str", "description": "A detailed description of what the tool should do and its primary function."},
                    {"name": "capabilities", "type": "List[str]", "optional": True, "description": "List of specific capabilities or methods the tool should implement (e.g., ['validate_json', 'shorten_url'])."}
                ]
            },
            "analyze_code": {
                "description": "Analyzes a given Python code file for quality, potential bugs, performance, and security, providing suggestions for improvement.",
                "parameters": [
                    {"name": "file_path", "type": "str", "description": "The path to the Python file to analyze."},
                    {"name": "analysis_goal", "type": "str", "optional": True, "description": "A specific goal or focus for the code analysis (e.g., 'find security vulnerabilities', 'optimize performance')."}
                ]
            },
            "modify_code": {
                "description": "Modifies a specified Python code file to achieve a given modification goal. Requires explicit user approval by default.",
                "parameters": [
                    {"name": "file_path", "type": "str", "description": "The path to the Python file to modify."},
                    {"name": "modification_goal", "type": "str", "description": "A clear description of the desired modification (e.g., 'add a new function to calculate factorial')."},
                    {"name": "require_approval", "type": "bool", "optional": True, "description": "If True, the generated code modification will be presented for approval before being applied. Defaults to True."}
                ]
            },
            "reload_tool": {
                "description": "Reloads a dynamically created or modified tool module, making its new capabilities available to the system.",
                "parameters": [
                    {"name": "tool_file", "type": "str", "description": "The filename of the tool to reload (e.g., 'my_custom_tool.py')."}
                ]
            }
        }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "create_tool":
            return self._create_tool(parameters)
        elif action == "analyze_code":
            return self._analyze_code(parameters)
        elif action == "modify_code":
            return self._modify_code(parameters)
        elif action == "reload_tool":
            return self._reload_tool(parameters)
        else:
            return self._error_response(f"Unknown action: {action}")

    def _create_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["tool_name", "description"])
        if error:
            return self._error_response(error)

        tool_name = parameters["tool_name"]
        description = parameters["description"]
        capabilities = parameters.get("capabilities", [])

        llm_client = self.tools.get("llm_client")
        if not llm_client:
            return self._error_response("LLM client not registered")

        class_name = self._generate_class_name(tool_name)
        file_name = f"{tool_name.lower().replace(' ', '_')}.py"
        file_path = self.tools_dir / file_name

        if file_path.exists():
            return self._error_response(
                f"Tool file already exists: {file_path}",
                details="Use a different tool name or delete the existing file first",
            )

        tool_gen_prompt = f"""Generate a complete Python tool class that inherits from BaseTool.

TOOL NAME: {tool_name}
CLASS NAME: {class_name}
DESCRIPTION: {description}
CAPABILITIES: {', '.join(capabilities) if capabilities else 'As described'}

Requirements:
1. Inherit from BaseTool (from .base_tool import BaseTool)
2. Implement the execute(**kwargs) method that dispatches to internal methods
3. Use self._success_response() and self._error_response() for returns
4. Include comprehensive docstring for the class
5. Implement all necessary methods with error handling
6. Use type hints
7. Keep it simple and functional
8. Do NOT include any markdown formatting or code blocks
9. Output ONLY the raw Python code

Generate the complete Python code:"""

        try:
            response = llm_client.chat.completions.create(
                model=llm_client.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Python developer. Generate only raw Python code without any markdown formatting or explanations.",
                    },
                    {"role": "user", "content": tool_gen_prompt},
                ],
                temperature=0.3,
                max_tokens=3000,
            )

            generated_code = response.choices[0].message.content.strip()

            generated_code = (
                generated_code.replace("```python", "").replace("```", "").strip()
            )

            generated_code = self._ensure_proper_imports(generated_code)

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(generated_code)
            except Exception as e:
                return self._error_response(
                    f"Failed to write tool file: {str(e)}",
                    details=f"File path: {file_path}",
                )

            reload_result = self._reload_tool({"tool_file": file_name})

            if reload_result["success"]:
                return self._success_response(
                    {
                        "tool_name": tool_name,
                        "class_name": class_name,
                        "file_path": str(file_path),
                        "generated_code": generated_code,
                        "reload_result": reload_result["data"],
                    },
                    f"Tool '{tool_name}' created and loaded successfully",
                )
            else:
                try:
                    file_path.unlink()
                except:
                    pass
                return self._error_response(
                    "Tool created but failed to load",
                    details=reload_result.get("error", "Unknown reload error"),
                )

        except Exception as e:
            return self._error_response(
                f"Tool generation failed: {str(e)}", details=f"Tool name: {tool_name}"
            )

    def _reload_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["tool_file"])
        if error:
            return self._error_response(error)

        tool_file = parameters["tool_file"]
        file_path = self.tools_dir / tool_file

        if not file_path.exists():
            return self._error_response(f"Tool file not found: {file_path}")

        module_name = file_path.stem
        module_path = f"wormgpt_hive.tools.{module_name}"

        try:
            if module_path in sys.modules:
                module = importlib.reload(sys.modules[module_path])
            else:
                module = importlib.import_module(module_path)

            tool_classes = []
            for name in dir(module):
                obj = getattr(module, name)
                if (
                    isinstance(obj, type)
                    and hasattr(obj, "__bases__")
                    and any(base.__name__ == "BaseTool" for base in obj.__bases__)
                ):
                    tool_classes.append(name)

            if not tool_classes:
                return self._error_response("No BaseTool subclass found in module")

            registry = self.tools.get("registry")
            if registry:
                for class_name in tool_classes:
                    tool_class = getattr(module, class_name)
                    tool_instance = tool_class()
                    registry.register_tool(tool_instance.name, tool_instance)

            return self._success_response(
                {
                    "module": module_path,
                    "tool_classes": tool_classes,
                    "registered": bool(registry),
                },
                f"Tool reloaded: {', '.join(tool_classes)}",
            )

        except Exception as e:
            return self._error_response(
                f"Failed to reload tool: {str(e)}", details=f"Module: {module_path}"
            )

    def _analyze_code(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["file_path"])
        if error:
            return self._error_response(error)

        file_path = Path(parameters["file_path"])

        if not file_path.exists():
            return self._error_response(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            return self._error_response(f"Failed to read file: {str(e)}")

        llm_client = self.tools.get("llm_client")
        if not llm_client:
            return self._error_response("LLM client not registered")

        analysis_goal = parameters.get(
            "analysis_goal", "Analyze this code and suggest improvements"
        )

        analysis_prompt = f"""Analyze the following Python code:

FILE: {file_path}

CODE:
```python
{code}
```

ANALYSIS GOAL: {analysis_goal}

Provide a detailed analysis including:
1. Code quality assessment
2. Potential bugs or issues
3. Performance considerations
4. Security concerns
5. Suggested improvements

Analysis:"""

        try:
            response = llm_client.chat.completions.create(
                model=llm_client.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer and security analyst.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                temperature=0.5,
                max_tokens=2000,
            )

            analysis = response.choices[0].message.content.strip()

            return self._success_response(
                {
                    "file_path": str(file_path),
                    "analysis": analysis,
                    "code_length": len(code),
                    "lines": code.count("\n") + 1,
                },
                "Code analysis completed",
            )

        except Exception as e:
            return self._error_response(f"Analysis failed: {str(e)}")

    def _modify_code(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(
            parameters, ["file_path", "modification_goal"]
        )
        if error:
            return self._error_response(error)

        file_path = Path(parameters["file_path"])
        modification_goal = parameters["modification_goal"]
        require_approval = parameters.get("require_approval", True)

        if not file_path.exists():
            return self._error_response(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_code = f.read()
        except Exception as e:
            return self._error_response(f"Failed to read file: {str(e)}")

        llm_client = self.tools.get("llm_client")
        if not llm_client:
            return self._error_response("LLM client not registered")

        modification_prompt = f"""Modify the following Python code to achieve the specified goal:

FILE: {file_path}

ORIGINAL CODE:
```python
{original_code}
```

MODIFICATION GOAL: {modification_goal}

Requirements:
1. Maintain the overall structure and functionality
2. Only make changes necessary to achieve the goal
3. Preserve existing imports and class structure
4. Ensure the modified code is syntactically correct
5. Do NOT include markdown formatting or code blocks
6. Output ONLY the complete modified Python code

Modified code:"""

        try:
            response = llm_client.chat.completions.create(
                model=llm_client.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Python developer. Generate only raw Python code without any markdown formatting.",
                    },
                    {"role": "user", "content": modification_prompt},
                ],
                temperature=0.3,
                max_tokens=4000,
            )

            modified_code = response.choices[0].message.content.strip()
            modified_code = (
                modified_code.replace("```python", "").replace("```", "").strip()
            )

            if require_approval:
                return self._success_response(
                    {
                        "file_path": str(file_path),
                        "original_code": original_code,
                        "modified_code": modified_code,
                        "approval_required": True,
                        "modification_goal": modification_goal,
                    },
                    "Code modification generated - approval required before applying",
                )
            else:
                try:
                    backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                    with open(backup_path, "w", encoding="utf-8") as f:
                        f.write(original_code)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(modified_code)

                    return self._success_response(
                        {
                            "file_path": str(file_path),
                            "backup_path": str(backup_path),
                            "modified_code": modified_code,
                            "applied": True,
                        },
                        "Code modification applied successfully",
                    )
                except Exception as e:
                    return self._error_response(
                        f"Failed to write modified code: {str(e)}"
                    )

        except Exception as e:
            return self._error_response(f"Code modification failed: {str(e)}")

    def _generate_class_name(self, tool_name: str) -> str:
        words = tool_name.replace("_", " ").replace("-", " ").split()
        class_name = "".join(word.capitalize() for word in words)
        if not class_name.endswith("Tool"):
            class_name += "Tool"
        return class_name

    def _ensure_proper_imports(self, code: str) -> str:
        if (
            "from .base_tool import BaseTool" not in code
            and "from base_tool import BaseTool" not in code
        ):
            code = "from .base_tool import BaseTool\n" + code

        if "from typing import" not in code:
            code = "from typing import Any, Dict, Optional\n" + code

        return code
