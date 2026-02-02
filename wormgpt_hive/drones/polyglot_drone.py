from typing import Any, Dict
from .base_drone import BaseDrone


class PolyglotDrone(BaseDrone):
    """Polyglot Coder Drone: Generates and executes code in multiple programming languages (Python, Node.js, Go, Rust, Bash). Can write code to solve problems, perform calculations, or automate tasks across different language ecosystems."""

    def __init__(self):
        super().__init__("PolyglotDrone")

    def get_supported_actions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "execute_code": {
                "description": "Executes a given code snippet in a specified programming language.",
                "parameters": [
                    {"name": "language", "type": "str", "description": "The programming language (e.g., 'python', 'node', 'go', 'rust', 'bash')."},
                    {"name": "code", "type": "str", "description": "The code snippet to execute."},
                    {"name": "timeout", "type": "int", "optional": True, "description": "Maximum time in seconds to wait for code execution. Defaults to 30."},
                    {"name": "filename", "type": "str", "optional": True, "description": "Optional filename to save the code before execution."}
                ]
            },
            "generate_and_execute": {
                "description": "Generates code in a specified language to perform a given task, then executes it.",
                "parameters": [
                    {"name": "language", "type": "str", "description": "The programming language for code generation and execution."},
                    {"name": "task", "type": "str", "description": "The task for which to generate code."},
                    {"name": "timeout", "type": "int", "optional": True, "description": "Maximum time in seconds to wait for code execution. Defaults to 30."}
                ]
            },
            "check_language": {
                "description": "Checks if a specific programming language interpreter is available on the system.",
                "parameters": [
                    {"name": "language", "type": "str", "description": "The programming language to check."}
                ]
            },
            "list_languages": {
                "description": "Lists all programming languages supported by the Polyglot Code Interpreter.",
                "parameters": []
            }
        }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "execute_code":
            return self._execute_code(parameters)
        elif action == "generate_and_execute":
            return self._generate_and_execute(parameters)
        elif action == "check_language":
            return self._check_language(parameters)
        elif action == "list_languages":
            return self._list_languages(parameters)
        else:
            return self._error_response(f"Unknown action: {action}")

    def _execute_code(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["language", "code"])
        if error:
            return self._error_response(error)

        interpreter = self.tools.get("polyglot_interpreter")
        if not interpreter:
            return self._error_response("PolyglotCodeInterpreter not registered")

        result = interpreter.execute(
            language=parameters["language"],
            code=parameters["code"],
            timeout=parameters.get("timeout", 30),
            filename=parameters.get("filename"),
        )

        if result["success"]:
            exec_result = result["data"]

            if exec_result.get("timed_out"):
                return self._error_response(
                    "Code execution timed out", details=exec_result["stderr"]
                )

            if exec_result.get("compilation_failed"):
                return self._error_response(
                    "Code compilation failed", details=exec_result["stderr"]
                )

            if exec_result["exit_code"] != 0:
                return self._error_response(
                    f"Code execution failed with exit code {exec_result['exit_code']}",
                    details=f"STDOUT: {exec_result['stdout']}\nSTDERR: {exec_result['stderr']}",
                )

            return self._success_response(
                exec_result, f"Code executed successfully in {parameters['language']}"
            )
        else:
            return result

    def _generate_and_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["language", "task"])
        if error:
            return self._error_response(error)

        llm_client = self.tools.get("llm_client")
        if not llm_client:
            return self._error_response("LLM client not registered")

        language = parameters["language"]
        task = parameters["task"]

        code_gen_prompt = f"""Generate {language} code to accomplish the following task:

TASK: {task}

Requirements:
- Write clean, working {language} code
- Include error handling where appropriate
- Output results to stdout
- Do NOT include markdown formatting or code blocks
- Provide ONLY the raw code, nothing else

{language.upper()} CODE:"""

        try:
            response = llm_client.chat.completions.create(
                model=llm_client.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert programmer. Generate only raw code without any markdown formatting or explanations.",
                    },
                    {"role": "user", "content": code_gen_prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            generated_code = response.choices[0].message.content.strip()

            generated_code = (
                generated_code.replace("```python", "")
                .replace("```javascript", "")
                .replace("```js", "")
            )
            generated_code = (
                generated_code.replace("```go", "")
                .replace("```rust", "")
                .replace("```bash", "")
            )
            generated_code = generated_code.replace("```", "").strip()

            exec_result = self._execute_code(
                {
                    "language": language,
                    "code": generated_code,
                    "timeout": parameters.get("timeout", 30),
                }
            )

            if exec_result["success"]:
                exec_result["data"]["generated_code"] = generated_code
                return self._success_response(
                    exec_result["data"],
                    f"Generated and executed {language} code successfully",
                )
            else:
                return {**exec_result, "generated_code": generated_code}

        except Exception as e:
            return self._error_response(
                f"Code generation failed: {str(e)}",
                details=f"Language: {language}, Task: {task}",
            )

    def _check_language(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        error = self._validate_parameters(parameters, ["language"])
        if error:
            return self._error_response(error)

        interpreter = self.tools.get("polyglot_interpreter")
        if not interpreter:
            return self._error_response("PolyglotCodeInterpreter not registered")

        result = interpreter.check_language_available(parameters["language"])

        if result["available"]:
            return self._success_response(
                result,
                f"{parameters['language']} is available: {result.get('version', 'unknown version')}",
            )
        else:
            return self._error_response(
                f"{parameters['language']} is not available",
                details=result.get("error", "Unknown error"),
            )

    def _list_languages(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        interpreter = self.tools.get("polyglot_interpreter")
        if not interpreter:
            return self._error_response("PolyglotCodeInterpreter not registered")

        languages = interpreter.get_supported_languages()

        return self._success_response(
            {"languages": languages}, f"Found {len(languages)} supported languages"
        )
