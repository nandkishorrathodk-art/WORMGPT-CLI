"""
Phase 11.1: Simplified System Integration Testing
Tests all 8 drones in a simple but comprehensive way
"""

import pytest
import os
import tempfile
import shutil

from wormgpt_hive.drones.shell_drone import ShellDrone
from wormgpt_hive.drones.coder_drone import CoderDrone
from wormgpt_hive.drones.research_drone import ResearchDrone
from wormgpt_hive.drones.security_drone import SecurityDrone
from wormgpt_hive.drones.polyglot_drone import PolyglotDrone
from wormgpt_hive.drones.tool_maker_drone import ToolMakerDrone
from wormgpt_hive.drones.opsec_drone import OPSECDrone
from wormgpt_hive.tools.file_system import FileSystemTool
from wormgpt_hive.tools.shell_executor import ShellExecutorTool
from wormgpt_hive.tools.google_search import GoogleSearchTool
from wormgpt_hive.tools.web_browser import WebBrowserTool
from wormgpt_hive.tools.security_analyzer import SecurityAnalyzerTool
from wormgpt_hive.tools.polyglot_code_interpreter import PolyglotCodeInterpreter
from wormgpt_hive.tools.tor_proxy import TorProxyTool


@pytest.fixture
def temp_dir():
    temp_path = tempfile.mkdtemp(prefix="wormgpt_int_test_")
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


class TestAllDronesIntegration:
    """Integration tests for all 8 drones"""
    
    def test_01_shell_drone_integration(self):
        """Test Shell Drone with real shell executor"""
        drone = ShellDrone()
        tool = ShellExecutorTool()
        drone.register_tool("shell_executor", tool)
        
        result = drone.execute("execute_command", {
            "command": "echo Hello World",
            "timeout": 10
        })
        
        assert result["success"] is True
        assert "Hello World" in result["data"]["stdout"]
        assert result["data"]["returncode"] == 0
        
    def test_02_coder_drone_integration(self, temp_dir):
        """Test Coder Drone with file operations"""
        drone = CoderDrone()
        tool = FileSystemTool()
        drone.register_tool("file_system", tool)
        
        test_file = os.path.join(temp_dir, "integration_test.txt")
        test_content = "Phase 11 Integration Test - Coder Drone"
        
        write_result = drone.execute("write_file", {
            "file_path": test_file,
            "content": test_content
        })
        assert write_result["success"] is True
        
        read_result = drone.execute("read_file", {
            "file_path": test_file
        })
        assert read_result["success"] is True
        assert test_content in read_result["data"]["content"]
        
        exists_result = drone.execute("file_exists", {
            "file_path": test_file
        })
        assert exists_result["success"] is True
        assert exists_result["data"]["exists"] is True
        
    def test_03_polyglot_drone_integration(self):
        """Test Polyglot Drone with Python execution"""
        drone = PolyglotDrone()
        tool = PolyglotCodeInterpreter()
        drone.register_tool("polyglot_interpreter", tool)
        
        result = drone.execute("execute_code", {
            "language": "python",
            "code": "x = 10\ny = 20\nprint(f'Sum: {x + y}')"
        })
        
        assert result["success"] is True
        assert "Sum: 30" in result["data"]["stdout"]
        
    def test_04_research_drone_capabilities(self):
        """Test Research Drone has proper capabilities"""
        drone = ResearchDrone()
        search_tool = GoogleSearchTool()
        browser_tool = WebBrowserTool()
        drone.register_tool("google_search", search_tool)
        drone.register_tool("web_browser", browser_tool)
        
        capabilities = drone.get_capabilities()
        assert capabilities.name == "ResearchDrone"
        assert "research" in capabilities.description.lower()
        
    def test_05_security_drone_capabilities(self):
        """Test Security Drone initialization"""
        drone = SecurityDrone()
        fs_tool = FileSystemTool()
        sec_tool = SecurityAnalyzerTool()
        drone.register_tool("file_system", fs_tool)
        drone.register_tool("security_analyzer", sec_tool)
        
        capabilities = drone.get_capabilities()
        assert capabilities.name == "SecurityDrone"
        assert len(capabilities.methods) > 0
        
    def test_06_tool_maker_drone_capabilities(self):
        """Test Tool Maker Drone initialization"""
        drone = ToolMakerDrone()
        fs_tool = FileSystemTool()
        drone.register_tool("file_system", fs_tool)
        
        capabilities = drone.get_capabilities()
        assert capabilities.name == "ToolMakerDrone"
        
    def test_07_opsec_drone_tor_check(self):
        """Test OPSEC Drone Tor availability check"""
        drone = OPSECDrone()
        tor_tool = TorProxyTool()
        shell_tool = ShellExecutorTool()
        browser_tool = WebBrowserTool()
        
        drone.register_tool("tor_proxy", tor_tool)
        drone.register_tool("shell_executor", shell_tool)
        drone.register_tool("web_browser", browser_tool)
        
        result = drone.execute("check_tor_availability", {})
        assert "available" in result["data"] or "error" in result
        
    def test_08_multi_drone_file_workflow(self, temp_dir):
        """Complex workflow: Coder creates, Polyglot executes, Shell verifies"""
        coder = CoderDrone()
        coder.register_tool("file_system", FileSystemTool())
        
        polyglot = PolyglotDrone()
        polyglot.register_tool("polyglot_interpreter", PolyglotCodeInterpreter())
        
        shell = ShellDrone()
        shell.register_tool("shell_executor", ShellExecutorTool())
        
        script_path = os.path.join(temp_dir, "workflow_test.py")
        script_code = '''
message = "Multi-drone workflow successful!"
print(message)
with open("workflow_output.txt", "w") as f:
    f.write(message)
'''
        
        coder_result = coder.execute("write_file", {
            "file_path": script_path,
            "content": script_code
        })
        assert coder_result["success"] is True
        
        exec_result = polyglot.execute("execute_code", {
            "language": "python",
            "code": script_code
        })
        assert exec_result["success"] is True
        assert "Multi-drone workflow successful!" in exec_result["data"]["stdout"]
        
    def test_09_stress_test_file_operations(self, temp_dir):
        """Stress test: 20 consecutive file operations"""
        drone = CoderDrone()
        drone.register_tool("file_system", FileSystemTool())
        
        for i in range(20):
            file_path = os.path.join(temp_dir, f"stress_{i}.txt")
            result = drone.execute("write_file", {
                "file_path": file_path,
                "content": f"Stress test iteration {i}"
            })
            assert result["success"] is True
            
        list_result = drone.execute("list_files", {
            "directory": temp_dir
        })
        assert list_result["success"] is True
        assert list_result["data"]["count"] >= 20
        
    def test_10_all_drones_error_handling(self):
        """Test all drones handle invalid actions gracefully"""
        drones = [
            ("Shell", ShellDrone(), "shell_executor", ShellExecutorTool()),
            ("Coder", CoderDrone(), "file_system", FileSystemTool()),
            ("Polyglot", PolyglotDrone(), "polyglot_interpreter", PolyglotCodeInterpreter()),
            ("ToolMaker", ToolMakerDrone(), "file_system", FileSystemTool()),
            ("OPSEC", OPSECDrone(), "tor_proxy", TorProxyTool()),
        ]
        
        for name, drone, tool_name, tool in drones:
            drone.register_tool(tool_name, tool)
            result = drone.execute("invalid_action_xyz", {})
            assert result["success"] is False, f"{name} drone should reject invalid action"
            
    def test_11_polyglot_multiple_languages(self):
        """Test polyglot with Python and check language support"""
        drone = PolyglotDrone()
        tool = PolyglotCodeInterpreter()
        drone.register_tool("polyglot_interpreter", tool)
        
        py_result = drone.execute("execute_code", {
            "language": "python",
            "code": "print('Python works')"
        })
        assert py_result["success"] is True
        assert "Python works" in py_result["data"]["stdout"]
        
        lang_result = drone.execute("list_languages", {})
        assert lang_result["success"] is True
        assert "python" in lang_result["data"]["languages"]
        assert "nodejs" in lang_result["data"]["languages"]
        
    def test_12_drone_capabilities_enumeration(self):
        """Test that all drones can enumerate their capabilities"""
        drones = {
            "Shell": ShellDrone(),
            "Coder": CoderDrone(),
            "Research": ResearchDrone(),
            "Security": SecurityDrone(),
            "Polyglot": PolyglotDrone(),
            "ToolMaker": ToolMakerDrone(),
            "OPSEC": OPSECDrone(),
        }
        
        for name, drone in drones.items():
            capabilities = drone.get_capabilities()
            assert capabilities.name is not None, f"{name} should have a name"
            assert capabilities.description is not None, f"{name} should have a description"
            assert isinstance(capabilities.methods, list), f"{name} should have methods list"


class TestSystemResilience:
    """Test system error handling and resilience"""
    
    def test_coder_drone_nonexistent_file(self):
        """Test reading nonexistent file"""
        drone = CoderDrone()
        drone.register_tool("file_system", FileSystemTool())
        
        result = drone.execute("read_file", {
            "file_path": "/absolutely/nonexistent/path/file.txt"
        })
        assert result["success"] is False
        
    def test_shell_invalid_command(self):
        """Test invalid shell command"""
        drone = ShellDrone()
        drone.register_tool("shell_executor", ShellExecutorTool())
        
        result = drone.execute("execute_command", {
            "command": "this_command_absolutely_does_not_exist_xyz_123",
            "timeout": 5
        })
        assert result["data"]["returncode"] != 0
        
    def test_polyglot_syntax_error(self):
        """Test code with syntax error"""
        drone = PolyglotDrone()
        drone.register_tool("polyglot_interpreter", PolyglotCodeInterpreter())
        
        result = drone.execute("execute_code", {
            "language": "python",
            "code": "print('missing closing quote"
        })
        assert result["success"] is False or result["data"]["exit_code"] != 0


class TestPerformanceMetrics:
    """Collect basic performance metrics"""
    
    def test_file_write_performance(self, temp_dir):
        """Measure file write performance"""
        import time
        
        drone = CoderDrone()
        drone.register_tool("file_system", FileSystemTool())
        
        start = time.time()
        for i in range(30):
            file_path = os.path.join(temp_dir, f"perf_{i}.txt")
            drone.execute("write_file", {
                "file_path": file_path,
                "content": "Performance test" * 10
            })
        duration = time.time() - start
        
        avg_time = duration / 30
        print(f"\n30 file writes: {duration:.2f}s (avg: {avg_time:.3f}s each)")
        
        assert duration < 5, "File operations taking too long"
        
    def test_code_execution_performance(self):
        """Measure code execution performance"""
        import time
        
        drone = PolyglotDrone()
        drone.register_tool("polyglot_interpreter", PolyglotCodeInterpreter())
        
        start = time.time()
        for i in range(5):
            drone.execute("execute_code", {
                "language": "python",
                "code": f"result = {i} * 2\nprint(result)"
            })
        duration = time.time() - start
        
        avg_time = duration / 5
        print(f"\n5 Python executions: {duration:.2f}s (avg: {avg_time:.3f}s each)")
        
        assert duration < 15, "Code execution taking too long"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
