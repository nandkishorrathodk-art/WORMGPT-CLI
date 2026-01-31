import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wormgpt_hive.tools.polyglot_code_interpreter import PolyglotCodeInterpreter


@pytest.fixture
def interpreter():
    return PolyglotCodeInterpreter()


def test_python_execution(interpreter):
    result = interpreter.execute(
        language="python",
        code="print('Hello from Python')",
        timeout=10
    )
    
    assert result["success"] is True
    assert "Hello from Python" in result["data"]["stdout"]
    assert result["data"]["exit_code"] == 0


def test_python_with_calculation(interpreter):
    code = """
result = 2 + 2
print(f"Result: {result}")
"""
    
    result = interpreter.execute(
        language="python",
        code=code,
        timeout=10
    )
    
    assert result["success"] is True
    assert "Result: 4" in result["data"]["stdout"]


def test_bash_execution(interpreter):
    result = interpreter.execute(
        language="bash",
        code='echo "Hello from Bash"',
        timeout=10
    )
    
    assert result["success"] is True
    assert "Hello from Bash" in result["data"]["stdout"]


def test_nodejs_if_available(interpreter):
    check = interpreter.check_language_available("node")
    
    if check["available"]:
        result = interpreter.execute(
            language="node",
            code="console.log('Hello from Node.js');",
            timeout=10
        )
        
        assert result["success"] is True
        assert "Hello from Node.js" in result["data"]["stdout"]
    else:
        pytest.skip("Node.js not available")


def test_go_if_available(interpreter):
    check = interpreter.check_language_available("go")
    
    if check["available"]:
        code = """package main

import "fmt"

func main() {
    fmt.Println("Hello from Go")
}
"""
        
        result = interpreter.execute(
            language="go",
            code=code,
            timeout=15
        )
        
        assert result["success"] is True
        assert "Hello from Go" in result["data"]["stdout"]
    else:
        pytest.skip("Go not available")


def test_rust_if_available(interpreter):
    check = interpreter.check_language_available("rust")
    
    if check["available"]:
        code = """fn main() {
    println!("Hello from Rust");
}
"""
        
        result = interpreter.execute(
            language="rust",
            code=code,
            timeout=20
        )
        
        assert result["success"] is True
        assert "Hello from Rust" in result["data"]["stdout"]
    else:
        pytest.skip("Rust not available")


def test_timeout_handling(interpreter):
    code = """
import time
time.sleep(100)
print("This should not print")
"""
    
    result = interpreter.execute(
        language="python",
        code=code,
        timeout=2
    )
    
    assert result["success"] is True
    assert result["data"]["timed_out"] is True


def test_syntax_error_handling(interpreter):
    code = """
print("Missing closing parenthesis"
"""
    
    result = interpreter.execute(
        language="python",
        code=code,
        timeout=10
    )
    
    assert result["success"] is True
    assert result["data"]["exit_code"] != 0
    assert len(result["data"]["stderr"]) > 0


def test_unsupported_language(interpreter):
    result = interpreter.execute(
        language="cobol",
        code="DISPLAY 'Hello'.",
        timeout=10
    )
    
    assert result["success"] is False
    assert "Unsupported language" in result["error"]


def test_missing_parameters(interpreter):
    result = interpreter.execute(language="python")
    
    assert result["success"] is False
    assert "Code parameter is required" in result["error"]


def test_get_supported_languages(interpreter):
    languages = interpreter.get_supported_languages()
    
    assert isinstance(languages, list)
    assert "python" in languages
    assert "bash" in languages
    assert len(languages) > 0


def test_check_python_available(interpreter):
    result = interpreter.check_language_available("python")
    
    assert result["available"] is True
    assert "version" in result or result["available"] is True


def test_sandbox_isolation(interpreter):
    result1 = interpreter.execute(
        language="python",
        code="x = 42\nprint(x)",
        timeout=10
    )
    
    result2 = interpreter.execute(
        language="python",
        code="print(x)",
        timeout=10
    )
    
    assert result1["success"] is True
    assert "42" in result1["data"]["stdout"]
    
    assert result2["success"] is True
    assert result2["data"]["exit_code"] != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
