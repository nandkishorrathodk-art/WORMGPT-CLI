import pytest
import json
import os
from unittest.mock import patch, MagicMock
from wormgpt_hive.drones.base_drone import DroneRegistry, MissionStep
from wormgpt_hive.drones.shell_drone import ShellDrone
from wormgpt_hive.drones.coder_drone import CoderDrone
from wormgpt_hive.tools.shell_executor import ShellExecutorTool
from wormgpt_hive.tools.file_system import FileSystemTool
from wormgpt_hive.queen.orchestrator import QueenOrchestrator
from wormgpt_hive.shared.state_manager import StateManager


@pytest.fixture
def setup_hive():
    registry = DroneRegistry()
    registry.clear()
    
    shell_tool = ShellExecutorTool()
    fs_tool = FileSystemTool()
    
    registry.register_tool("shell_executor", shell_tool)
    registry.register_tool("file_system", fs_tool)
    
    shell_drone = ShellDrone()
    shell_drone.register_tool("shell_executor", shell_tool)
    registry.register_drone(shell_drone)
    
    coder_drone = CoderDrone()
    coder_drone.register_tool("file_system", fs_tool)
    registry.register_drone(coder_drone)
    
    state_file = "test_agent_state.json"
    if os.path.exists(state_file):
        os.remove(state_file)
    
    state_manager = StateManager(file_path=state_file, encryption_key=None)
    queen = QueenOrchestrator(registry, state_manager)
    
    yield queen, registry, state_manager
    
    if os.path.exists(state_file):
        os.remove(state_file)
    
    registry.clear()


class TestReflectionMechanism:
    
    def test_reflection_on_failed_step(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        failed_step = MissionStep(
            step_id=1,
            action="ShellDrone.execute_command",
            parameters={"command": "nonexistent_command_xyz"},
            reasoning="Test failed command"
        )
        failed_step.mark_failed("Command not found: nonexistent_command_xyz")
        
        with patch.object(queen.client.chat.completions, 'create') as mock_llm:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps({
                "success": False,
                "root_cause": "Command does not exist",
                "next_action": "continue"
            })
            mock_llm.return_value = mock_response
            
            queen.current_mission = {"goal": "Test reflection"}
            reflection = queen._reflect_on_failure(failed_step)
            
            assert reflection is not None
            assert reflection.get("success") == False
            assert reflection.get("next_action") in ["continue", "retry", "replan", "request_human_feedback"]
    
    def test_reflection_triggers_replan(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        failed_step = MissionStep(
            step_id=1,
            action="CoderDrone.write_file",
            parameters={"path": "/invalid/path/file.txt", "content": "test"},
            reasoning="Write to invalid path"
        )
        failed_step.mark_failed("Permission denied")
        
        with patch.object(queen.client.chat.completions, 'create') as mock_llm:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps({
                "success": False,
                "root_cause": "Invalid file path or insufficient permissions",
                "next_action": "replan",
                "revised_plan": [
                    {
                        "step_id": 2,
                        "action": "CoderDrone.write_file",
                        "parameters": {"path": "test_file.txt", "content": "test"},
                        "reasoning": "Use valid local path instead"
                    }
                ]
            })
            mock_llm.return_value = mock_response
            
            queen.current_mission = {"goal": "Test replan"}
            reflection = queen._reflect_on_failure(failed_step)
            
            assert reflection.get("next_action") == "replan"
            assert "revised_plan" in reflection
            assert len(reflection["revised_plan"]) > 0


class TestHumanFeedbackLoop:
    
    def test_human_feedback_request(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        queen.current_mission = {"goal": "Test human feedback"}
        question = "Which file should I edit?"
        
        with patch('builtins.input', return_value='config.py'):
            feedback = queen._request_human_feedback(question)
            
            assert feedback == "config.py"
    
    def test_mission_pauses_for_feedback(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        failed_step = MissionStep(
            step_id=1,
            action="CoderDrone.read_file",
            parameters={"path": "unknown_file.txt"},
            reasoning="Read unknown file"
        )
        failed_step.mark_failed("File not found")
        
        with patch.object(queen.client.chat.completions, 'create') as mock_llm:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps({
                "success": False,
                "root_cause": "File does not exist",
                "next_action": "request_human_feedback",
                "question": "Which file did you want me to read?"
            })
            mock_llm.return_value = mock_response
            
            queen.current_mission = {"goal": "Test feedback integration"}
            
            with patch('builtins.input', return_value='config.txt'):
                reflection = queen._reflect_on_failure(failed_step)
                
                assert reflection.get("next_action") == "request_human_feedback"
                assert "question" in reflection


class TestPersistentState:
    
    def test_state_persistence_across_sessions(self, setup_hive):
        queen1, registry, state_manager1 = setup_hive
        
        mission_data = {
            "goal": "Test persistence",
            "status": "completed",
            "steps": [
                {
                    "step_id": 1,
                    "action": "ShellDrone.execute_command",
                    "parameters": {"command": "echo 'test'"},
                    "reasoning": "Test command",
                    "status": "completed"
                }
            ],
            "result": {"total_steps": 1, "successful_steps": 1}
        }
        
        state_manager1.add_mission(mission_data)
        
        state_manager2 = StateManager(file_path=state_manager1.file_path, encryption_key=None)
        history = state_manager2.get_mission_history(limit=5)
        
        assert len(history) > 0
        assert history[-1]["goal"] == "Test persistence"
        assert history[-1]["status"] == "completed"
    
    def test_mission_history_loaded_on_startup(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        for i in range(3):
            mission = {
                "goal": f"Test mission {i+1}",
                "status": "completed",
                "steps": [],
                "result": {}
            }
            state_manager.add_mission(mission)
        
        history = queen.get_mission_history(limit=5)
        
        assert len(history) == 3
        assert history[0]["goal"] == "Test mission 1"
        assert history[-1]["goal"] == "Test mission 3"
    
    def test_encrypted_state_persistence(self):
        state_file = "test_encrypted_state.json"
        encryption_key = "test_encryption_key_12345"
        
        if os.path.exists(state_file):
            os.remove(state_file)
        
        state_manager = StateManager(file_path=state_file, encryption_key=encryption_key)
        
        mission = {
            "goal": "Encrypted mission",
            "status": "completed",
            "steps": [],
            "result": {}
        }
        
        state_manager.add_mission(mission)
        
        with open(state_file, 'rb') as f:
            raw_content = f.read()
            
        assert b"Encrypted mission" not in raw_content
        
        state_manager2 = StateManager(file_path=state_file, encryption_key=encryption_key)
        history = state_manager2.get_mission_history(1)
        
        assert len(history) > 0
        assert history[0]["goal"] == "Encrypted mission"
        
        if os.path.exists(state_file):
            os.remove(state_file)


class TestDynamicCapabilityDiscovery:
    
    def test_capability_discovery_at_runtime(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        capabilities = registry.get_capabilities_summary()
        
        assert "drones" in capabilities
        assert "tools" in capabilities
        assert "ShellDrone" in capabilities["drones"]
        assert "CoderDrone" in capabilities["drones"]
    
    def test_new_drone_detected_dynamically(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        from wormgpt_hive.drones.base_drone import BaseDrone
        
        class TestDrone(BaseDrone):
            """Test drone for dynamic discovery"""
            
            def execute(self, action, parameters):
                return self._success_response({}, "Test action")
        
        test_drone = TestDrone("TestDrone")
        registry.register_drone(test_drone)
        
        capabilities = registry.get_capabilities_summary()
        
        assert "TestDrone" in capabilities["drones"]
        assert capabilities["drones"]["TestDrone"]["description"] == "Test drone for dynamic discovery"
    
    def test_capability_description_includes_methods(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        shell_drone = registry.get_drone("ShellDrone")
        capabilities = shell_drone.get_capabilities()
        
        assert capabilities.name == "ShellDrone"
        assert capabilities.description is not None
        assert len(capabilities.methods) > 0
    
    def test_queen_uses_discovered_capabilities_in_planning(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        with patch.object(queen.client.chat.completions, 'create') as mock_llm:
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps([
                {
                    "step_id": 1,
                    "action": "ShellDrone.execute_command",
                    "parameters": {"command": "echo 'test'"},
                    "reasoning": "Test command"
                }
            ])
            mock_llm.return_value = mock_response
            
            capabilities = registry.get_capabilities_summary()
            plan = queen._generate_plan("Execute a test command", capabilities)
            
            assert plan is not None
            assert len(plan) > 0
            assert mock_llm.called
            
            call_args = mock_llm.call_args[1]
            user_message = call_args["messages"][1]["content"]
            assert "AVAILABLE CAPABILITIES" in user_message


class TestIntegratedIntelligence:
    
    def test_end_to_end_reflection_and_recovery(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        with patch.object(queen.client.chat.completions, 'create') as mock_llm:
            plan_response = MagicMock()
            plan_response.choices[0].message.content = json.dumps([
                {
                    "step_id": 1,
                    "action": "ShellDrone.execute_command",
                    "parameters": {"command": "invalid_command_xyz"},
                    "reasoning": "Test invalid command"
                }
            ])
            
            reflection_response = MagicMock()
            reflection_response.choices[0].message.content = json.dumps({
                "success": False,
                "root_cause": "Command not found",
                "next_action": "continue"
            })
            
            mock_llm.side_effect = [plan_response, reflection_response]
            
            result = queen.execute_mission("Execute an invalid command", verbose=False)
            
            assert result is not None
            assert "mission" in result
            
            history = state_manager.get_mission_history(1)
            assert len(history) > 0
    
    def test_mission_with_successful_recovery(self, setup_hive):
        queen, registry, state_manager = setup_hive
        
        with patch.object(queen.client.chat.completions, 'create') as mock_llm:
            plan_response = MagicMock()
            plan_response.choices[0].message.content = json.dumps([
                {
                    "step_id": 1,
                    "action": "CoderDrone.write_file",
                    "parameters": {"path": "test_recovery.txt", "content": "test"},
                    "reasoning": "Create test file"
                }
            ])
            
            mock_llm.return_value = plan_response
            
            result = queen.execute_mission("Create a test file", verbose=False)
            
            assert result is not None
            
            if os.path.exists("test_recovery.txt"):
                os.remove("test_recovery.txt")
