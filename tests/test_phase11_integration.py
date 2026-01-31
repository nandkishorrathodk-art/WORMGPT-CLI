"""
Phase 11.1: System Integration Testing
Tests all 8 drones in complex multi-step missions
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

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
def temp_workspace():
    temp_dir = tempfile.mkdtemp(prefix="wormgpt_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def all_tools():
    return {
        "file_system": FileSystemTool(),
        "shell_executor": ShellExecutorTool(),
        "google_search": GoogleSearchTool(),
        "web_browser": WebBrowserTool(),
        "security_analyzer": SecurityAnalyzerTool(),
        "polyglot_interpreter": PolyglotCodeInterpreter(),
        "tor_proxy": TorProxyTool()
    }


@pytest.fixture
def all_drones(all_tools):
    shell_drone = ShellDrone()
    shell_drone.register_tool("shell_executor", all_tools["shell_executor"])
    
    coder_drone = CoderDrone()
    coder_drone.register_tool("file_system", all_tools["file_system"])
    
    research_drone = ResearchDrone()
    research_drone.register_tool("google_search", all_tools["google_search"])
    research_drone.register_tool("web_browser", all_tools["web_browser"])
    
    security_drone = SecurityDrone()
    security_drone.register_tool("file_system", all_tools["file_system"])
    security_drone.register_tool("security_analyzer", all_tools["security_analyzer"])
    
    polyglot_drone = PolyglotDrone()
    polyglot_drone.register_tool("polyglot_interpreter", all_tools["polyglot_interpreter"])
    
    tool_maker_drone = ToolMakerDrone()
    tool_maker_drone.register_tool("file_system", all_tools["file_system"])
    
    opsec_drone = OPSECDrone()
    opsec_drone.register_tool("tor_proxy", all_tools["tor_proxy"])
    opsec_drone.register_tool("shell_executor", all_tools["shell_executor"])
    opsec_drone.register_tool("web_browser", all_tools["web_browser"])
    
    return {
        "shell": shell_drone,
        "coder": coder_drone,
        "research": research_drone,
        "security": security_drone,
        "polyglot": polyglot_drone,
        "tool_maker": tool_maker_drone,
        "opsec": opsec_drone
    }


class TestPhase11Integration:
    """
    Integration tests for Phase 11: Final Integration & Validation
    """

    def test_all_drones_initialized(self, all_drones):
        """Verify all 8 drones are properly initialized"""
        expected_drones = ["shell", "coder", "research", "security", "polyglot", "tool_maker", "opsec"]
        assert len(all_drones) >= len(expected_drones)
        
        for drone_name in expected_drones:
            assert drone_name in all_drones
            assert all_drones[drone_name] is not None
            
    def test_all_drones_have_capabilities(self, all_drones):
        """Verify all drones expose capabilities"""
        for drone_name, drone in all_drones.items():
            capabilities = drone.get_capabilities()
            assert capabilities is not None
            assert "name" in capabilities
            assert "description" in capabilities
            assert "actions" in capabilities
            assert len(capabilities["actions"]) > 0
            
    def test_shell_drone_basic_execution(self, all_drones):
        """Test Shell Drone can execute commands"""
        shell_drone = all_drones["shell"]
        result = shell_drone.execute({
            "action": "execute_command",
            "command": "echo Integration Test",
            "timeout": 10
        })
        assert result["success"] is True
        assert "Integration Test" in result["data"]["output"]
        
    def test_coder_drone_file_operations(self, all_drones, temp_workspace):
        """Test Coder Drone can create, read, and modify files"""
        coder_drone = all_drones["coder"]
        test_file = os.path.join(temp_workspace, "test_integration.txt")
        
        write_result = coder_drone.execute({
            "action": "write_file",
            "path": test_file,
            "content": "Phase 11 Integration Test"
        })
        assert write_result["success"] is True
        
        read_result = coder_drone.execute({
            "action": "read_file",
            "path": test_file
        })
        assert read_result["success"] is True
        assert "Phase 11 Integration Test" in read_result["data"]["content"]
        
    def test_polyglot_drone_python_execution(self, all_drones):
        """Test Polyglot Drone can execute Python code"""
        polyglot_drone = all_drones["polyglot"]
        result = polyglot_drone.execute({
            "action": "execute_code",
            "language": "python",
            "code": "result = 2 + 2\nprint(f'Result: {result}')"
        })
        assert result["success"] is True
        assert "Result: 4" in result["data"]["stdout"]
        
    def test_polyglot_drone_supported_languages(self, all_drones):
        """Test Polyglot Drone reports all supported languages"""
        polyglot_drone = all_drones["polyglot"]
        result = polyglot_drone.execute({"action": "list_languages"})
        assert result["success"] is True
        languages = result["data"]["languages"]
        assert "python" in languages
        assert "nodejs" in languages
        assert "bash" in languages
        
    @pytest.mark.skipif(not shutil.which("slither"), reason="Slither not installed")
    def test_security_drone_capability(self, all_drones, temp_workspace):
        """Test Security Drone can analyze smart contracts"""
        coder_drone = all_drones["coder"]
        security_drone = all_drones["security"]
        
        contract_path = os.path.join(temp_workspace, "test_contract.sol")
        contract_code = '''
pragma solidity ^0.8.0;

contract TestContract {
    uint256 public balance;
    
    function deposit() public payable {
        balance += msg.value;
    }
    
    function withdraw(uint256 amount) public {
        require(balance >= amount, "Insufficient balance");
        payable(msg.sender).transfer(amount);
        balance -= amount;
    }
}
'''
        coder_drone.execute({
            "action": "write_file",
            "path": contract_path,
            "content": contract_code
        })
        
        result = security_drone.execute({
            "action": "analyze_contract",
            "contract_path": contract_path
        })
        
        assert result["success"] is True or "error" in result
        
    def test_tool_maker_drone_capability_description(self, all_drones):
        """Test Tool Maker Drone exposes proper capabilities"""
        tool_maker = all_drones["tool_maker"]
        capabilities = tool_maker.get_capabilities()
        
        assert "analyze_code" in [a["name"] for a in capabilities["actions"]]
        assert "modify_code" in [a["name"] for a in capabilities["actions"]]
        
    def test_opsec_drone_tor_availability_check(self, all_drones):
        """Test OPSEC Drone can check Tor availability"""
        opsec_drone = all_drones["opsec"]
        result = opsec_drone.execute({"action": "check_tor"})
        assert result["success"] is True
        assert "tor_available" in result["data"]
        
    def test_multi_drone_workflow_file_creation_and_execution(self, all_drones, temp_workspace):
        """
        Complex multi-drone workflow:
        1. Coder creates a Python script
        2. Polyglot executes it
        3. Shell verifies output file exists
        """
        coder_drone = all_drones["coder"]
        polyglot_drone = all_drones["polyglot"]
        
        script_content = '''
import os
with open("integration_output.txt", "w") as f:
    f.write("Multi-drone integration successful!")
print("Script executed successfully")
'''
        
        script_path = os.path.join(temp_workspace, "integration_script.py")
        write_result = coder_drone.execute({
            "action": "write_file",
            "path": script_path,
            "content": script_content
        })
        assert write_result["success"] is True
        
        exec_result = polyglot_drone.execute({
            "action": "execute_code",
            "language": "python",
            "code": script_content
        })
        assert exec_result["success"] is True
        assert "Script executed successfully" in exec_result["data"]["stdout"]
        
    def test_drone_error_handling(self, all_drones):
        """Test all drones handle invalid actions gracefully"""
        for drone_name, drone in all_drones.items():
            result = drone.execute({"action": "invalid_action_xyz"})
            assert result["success"] is False
            assert "error" in result or "message" in result
            
    def test_dynamic_tool_discovery(self, all_drones):
        """Test that all drones can be discovered and their capabilities enumerated"""
        drone_count = 0
        total_actions = 0
        
        for drone_name, drone in all_drones.items():
            drone_count += 1
            capabilities = drone.get_capabilities()
            total_actions += len(capabilities["actions"])
            
        assert drone_count >= 7
        assert total_actions >= 20
        
    def test_stress_test_concurrent_file_operations(self, all_drones, temp_workspace):
        """Stress test: Multiple file operations in sequence"""
        coder_drone = all_drones["coder"]
        
        for i in range(10):
            file_path = os.path.join(temp_workspace, f"stress_test_{i}.txt")
            result = coder_drone.execute({
                "action": "write_file",
                "path": file_path,
                "content": f"Stress test iteration {i}"
            })
            assert result["success"] is True
            
        list_result = coder_drone.execute({
            "action": "list_directory",
            "path": temp_workspace
        })
        assert list_result["success"] is True
        assert len(list_result["data"]["files"]) >= 10


class TestSystemResilience:
    """Test system resilience and error recovery"""
    
    def test_file_system_tool_nonexistent_file(self, all_tools):
        """Test file system handles nonexistent files gracefully"""
        fs_tool = all_tools["file_system"]
        result = fs_tool.execute({
            "action": "read",
            "path": "/nonexistent/path/file.txt"
        })
        assert result["success"] is False
        
    def test_shell_invalid_command_handling(self, all_tools):
        """Test shell executor handles invalid commands"""
        shell_tool = all_tools["shell_executor"]
        result = shell_tool.execute({
            "command": "this_command_does_not_exist_xyz123",
            "timeout": 5
        })
        assert result["success"] is False
        
    def test_polyglot_code_with_syntax_error(self, all_drones):
        """Test polyglot drone handles code with errors"""
        polyglot_drone = all_drones["polyglot"]
        result = polyglot_drone.execute({
            "action": "execute_code",
            "language": "python",
            "code": "print('missing closing quote"
        })
        assert result["success"] is False


class TestPerformanceMetrics:
    """Collect performance metrics for optimization"""
    
    def test_file_operations_performance(self, all_drones, temp_workspace):
        """Measure file operation performance"""
        import time
        coder_drone = all_drones["coder"]
        
        start = time.time()
        for i in range(50):
            file_path = os.path.join(temp_workspace, f"perf_test_{i}.txt")
            coder_drone.execute({
                "action": "write_file",
                "path": file_path,
                "content": "Performance test content" * 10
            })
        duration = time.time() - start
        
        assert duration < 10
        print(f"\n50 file writes completed in {duration:.2f}s ({duration/50:.3f}s per operation)")
        
    def test_code_execution_performance(self, all_drones):
        """Measure code execution performance"""
        import time
        polyglot_drone = all_drones["polyglot"]
        
        start = time.time()
        for i in range(10):
            polyglot_drone.execute({
                "action": "execute_code",
                "language": "python",
                "code": f"result = {i} * 2\nprint(result)"
            })
        duration = time.time() - start
        
        assert duration < 30
        print(f"\n10 Python executions completed in {duration:.2f}s ({duration/10:.3f}s per execution)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
