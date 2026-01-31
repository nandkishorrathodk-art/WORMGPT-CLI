#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wormgpt_hive.drones.base_drone import DroneRegistry
from wormgpt_hive.drones.shell_drone import ShellDrone
from wormgpt_hive.drones.coder_drone import CoderDrone
from wormgpt_hive.drones.research_drone import ResearchDrone
from wormgpt_hive.tools.shell_executor import ShellExecutorTool
from wormgpt_hive.tools.file_system import FileSystemTool
from wormgpt_hive.tools.google_search import GoogleSearchTool
from wormgpt_hive.tools.web_browser import WebBrowserTool
from wormgpt_hive.queen.orchestrator import QueenOrchestrator
from wormgpt_hive.shared.state_manager import StateManager


def demo_reflection_mechanism():
    print("\n" + "="*70)
    print("DEMO 1: Reflection Mechanism with Self-Correction")
    print("="*70 + "\n")
    
    registry = DroneRegistry()
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
    
    state_manager = StateManager()
    queen = QueenOrchestrator(registry, state_manager)
    
    print("Mission: Execute a command and handle potential errors")
    print("Note: The Queen will reflect on failures and decide how to proceed\n")


def demo_persistent_state():
    print("\n" + "="*70)
    print("DEMO 2: Persistent State and Mission History")
    print("="*70 + "\n")
    
    state_manager = StateManager()
    
    mission1 = {
        "goal": "Analyze security vulnerabilities in smart contract",
        "status": "completed",
        "steps": [
            {"step_id": 1, "action": "SecurityDrone.analyze_contract", "status": "completed"}
        ],
        "result": {"vulnerabilities_found": 3}
    }
    
    mission2 = {
        "goal": "Research latest AI developments",
        "status": "completed",
        "steps": [
            {"step_id": 1, "action": "ResearchDrone.search", "status": "completed"},
            {"step_id": 2, "action": "ResearchDrone.fetch_content", "status": "completed"}
        ],
        "result": {"articles_found": 10}
    }
    
    state_manager.add_mission(mission1)
    state_manager.add_mission(mission2)
    
    print("Missions saved to persistent state...")
    print("\nRetrieving mission history:\n")
    
    history = state_manager.get_mission_history(limit=5)
    
    for mission in history:
        print(f"Mission #{mission['id']}: {mission['goal']}")
        print(f"  Status: {mission['status']}")
        print(f"  Steps: {len(mission['steps'])}")
        print(f"  Timestamp: {mission['timestamp']}")
        print()
    
    print(f"Total missions in history: {len(history)}")


def demo_encrypted_state():
    print("\n" + "="*70)
    print("DEMO 3: Encrypted State for Security")
    print("="*70 + "\n")
    
    import os
    
    encrypted_file = "demo_encrypted_state.json"
    encryption_key = "demo_secure_key_12345"
    
    if os.path.exists(encrypted_file):
        os.remove(encrypted_file)
    
    state_manager = StateManager(file_path=encrypted_file, encryption_key=encryption_key)
    
    sensitive_mission = {
        "goal": "Penetration testing on target system",
        "status": "completed",
        "steps": [
            {"step_id": 1, "action": "OPSEC.enable_tor", "status": "completed"},
            {"step_id": 2, "action": "SecurityDrone.scan_ports", "status": "completed"}
        ],
        "result": {"open_ports": [22, 80, 443]}
    }
    
    state_manager.add_mission(sensitive_mission)
    
    print("Sensitive mission saved with encryption...")
    
    with open(encrypted_file, 'rb') as f:
        raw_content = f.read()
        print(f"\nRaw file content (first 100 bytes): {raw_content[:100]}")
        print("\nNotice: Mission data is encrypted and unreadable!")
    
    print("\nDecrypting and loading state...")
    state_manager2 = StateManager(file_path=encrypted_file, encryption_key=encryption_key)
    loaded_history = state_manager2.get_mission_history(1)
    
    print(f"Successfully decrypted mission: {loaded_history[0]['goal']}")
    
    os.remove(encrypted_file)


def demo_dynamic_capability_discovery():
    print("\n" + "="*70)
    print("DEMO 4: Dynamic Capability Discovery")
    print("="*70 + "\n")
    
    registry = DroneRegistry()
    
    shell_tool = ShellExecutorTool()
    fs_tool = FileSystemTool()
    search_tool = GoogleSearchTool()
    browser_tool = WebBrowserTool()
    
    registry.register_tool("shell_executor", shell_tool)
    registry.register_tool("file_system", fs_tool)
    registry.register_tool("google_search", search_tool)
    registry.register_tool("web_browser", browser_tool)
    
    shell_drone = ShellDrone()
    shell_drone.register_tool("shell_executor", shell_tool)
    registry.register_drone(shell_drone)
    
    coder_drone = CoderDrone()
    coder_drone.register_tool("file_system", fs_tool)
    registry.register_drone(coder_drone)
    
    research_drone = ResearchDrone()
    research_drone.register_tool("google_search", search_tool)
    research_drone.register_tool("web_browser", browser_tool)
    registry.register_drone(research_drone)
    
    print("Discovering capabilities at runtime...\n")
    
    capabilities = registry.get_capabilities_summary()
    
    print(f"Discovered {len(capabilities['drones'])} Drones:")
    for drone_name, drone_info in capabilities['drones'].items():
        print(f"\n  • {drone_name}")
        print(f"    Description: {drone_info['description']}")
        if drone_info.get('methods'):
            print(f"    Methods: {len(drone_info['methods'])}")
            for method in drone_info['methods'][:3]:
                print(f"      - {method.get('name', 'unknown')}")
    
    print(f"\n\nDiscovered {len(capabilities['tools'])} Tools:")
    for tool_name in capabilities['tools'].keys():
        print(f"  • {tool_name}")
    
    print("\n\nAdding a new drone dynamically...")
    
    from wormgpt_hive.drones.base_drone import BaseDrone
    
    class ExampleDrone(BaseDrone):
        """Example drone for demonstration of dynamic discovery"""
        
        def execute(self, action, parameters):
            return self._success_response({}, "Example action executed")
    
    example_drone = ExampleDrone("ExampleDrone")
    registry.register_drone(example_drone)
    
    updated_capabilities = registry.get_capabilities_summary()
    
    print(f"\nNow {len(updated_capabilities['drones'])} Drones available:")
    for drone_name in updated_capabilities['drones'].keys():
        print(f"  • {drone_name}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 4: ADVANCED INTELLIGENCE FEATURES - DEMONSTRATION")
    print("="*70)
    
    demo_reflection_mechanism()
    demo_persistent_state()
    demo_encrypted_state()
    demo_dynamic_capability_discovery()
    
    print("\n" + "="*70)
    print("ALL PHASE 4 FEATURES DEMONSTRATED")
    print("="*70 + "\n")
