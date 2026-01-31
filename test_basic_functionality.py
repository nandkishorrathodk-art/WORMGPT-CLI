#!/usr/bin/env python3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, ".")

from wormgpt_hive.drones.base_drone import DroneRegistry
from wormgpt_hive.drones.shell_drone import ShellDrone
from wormgpt_hive.drones.coder_drone import CoderDrone
from wormgpt_hive.tools.shell_executor import ShellExecutorTool
from wormgpt_hive.tools.file_system import FileSystemTool

print("\n" + "=" * 60)
print("Testing WormGPT Hive Mind - Basic Functionality")
print("=" * 60 + "\n")

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

print("Test 1: Registry Setup")
print(f"  Drones registered: {len(registry.get_all_drones())}")
print(f"  Tools registered: {len(registry.get_all_tools())}")
print("  ✓ PASSED\n")

print("Test 2: CoderDrone - Write File")
test_file = "test_basic_output.txt"
test_content = "Hello from WormGPT Hive Mind!"

result = coder_drone.execute(
    "write_file", {"file_path": test_file, "content": test_content}
)

if result["success"]:
    print("  ✓ PASSED: File written successfully")
    print(f"    Path: {result['data']['path']}")
    print(f"    Bytes: {result['data']['bytes_written']}\n")
else:
    print(f"  ✗ FAILED: {result['error']}\n")
    sys.exit(1)

print("Test 3: CoderDrone - Read File")
result = coder_drone.execute("read_file", {"file_path": test_file})

if result["success"]:
    content = result["data"]["content"]
    if content == test_content:
        print("  ✓ PASSED: File read successfully")
        print(f"    Content: '{content}'\n")
    else:
        print("  ✗ FAILED: Content mismatch")
        print(f"    Expected: '{test_content}'")
        print(f"    Got: '{content}'\n")
        sys.exit(1)
else:
    print(f"  ✗ FAILED: {result['error']}\n")
    sys.exit(1)

print("Test 4: ShellDrone - Execute Command")
result = shell_drone.execute("execute_command", {"command": "echo Hello WormGPT"})

if result["success"]:
    stdout = result["data"]["stdout"].strip()
    print("  ✓ PASSED: Command executed successfully")
    print(f"    Output: '{stdout}'\n")
else:
    print(f"  ✗ FAILED: {result['error']}\n")
    sys.exit(1)

print("Test 5: CoderDrone - Delete File")
result = coder_drone.execute("delete_file", {"file_path": test_file})

if result["success"]:
    print("  ✓ PASSED: File deleted successfully\n")
else:
    print(f"  ✗ FAILED: {result['error']}\n")
    sys.exit(1)

print("Test 6: Capability Discovery")
capabilities = registry.get_capabilities_summary()
print(f"  Drones: {list(capabilities['drones'].keys())}")
print(f"  Tools: {list(capabilities['tools'].keys())}")
print("  ✓ PASSED\n")

print("=" * 60)
print("✓ ALL TESTS PASSED")
print("=" * 60 + "\n")
