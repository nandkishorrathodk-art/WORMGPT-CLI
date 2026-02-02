#!/usr/bin/env python3
import sys

sys.path.insert(0, ".")

from wormgpt_hive.drones.base_drone import DroneRegistry
from wormgpt_hive.drones.shell_drone import ShellDrone
from wormgpt_hive.drones.coder_drone import CoderDrone
from wormgpt_hive.tools.shell_executor import ShellExecutorTool
from wormgpt_hive.tools.file_system import FileSystemTool
from wormgpt_hive.queen.orchestrator import QueenOrchestrator
from wormgpt_hive.shared.state_manager import StateManager
from wormgpt_hive.shared.config import FIREWORKS_API_KEY

if not FIREWORKS_API_KEY:
    print("ERROR: FIREWORKS_API_KEY not set in .env file")
    sys.exit(1)

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

print("\n" + "=" * 60)
print("Testing WormGPT Hive Mind - Simple Mission")
print("=" * 60 + "\n")

goal = "Create a file named test_output.txt with the content 'Hello from WormGPT Hive Mind!' and then read it back to verify"

print(f"GOAL: {goal}\n")

result = queen.execute_mission(goal, verbose=True)

print("\n" + "=" * 60)
if result["success"]:
    print("✓ TEST PASSED: Mission completed successfully")
else:
    print("✗ TEST FAILED: Mission completed with errors")
print("=" * 60)
