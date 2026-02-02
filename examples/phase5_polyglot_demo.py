#!/usr/bin/env python3
"""
Phase 5: Dynamic Code Generation Demo
Demonstrates PolyglotDrone and ToolMakerDrone capabilities
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wormgpt_hive.drones.base_drone import DroneRegistry
from wormgpt_hive.drones.polyglot_drone import PolyglotDrone
from wormgpt_hive.drones.tool_maker_drone import ToolMakerDrone
from wormgpt_hive.tools.polyglot_code_interpreter import PolyglotCodeInterpreter
from openai import OpenAI
from wormgpt_hive.shared.config import (
    FIREWORKS_API_KEY,
    OPENROUTER_BASE_URL,
    QUEEN_MODEL,
)


def demo_polyglot_code_execution():
    """Demonstrate polyglot code execution capabilities"""
    print("\n" + "=" * 70)
    print("DEMO 1: Polyglot Code Execution")
    print("=" * 70 + "\n")

    interpreter = PolyglotCodeInterpreter()

    print("1. Executing Python code...")
    result = interpreter.execute(
        language="python", code='print("Hello from Python! 2+2 =", 2+2)'
    )
    if result["success"]:
        print(f"   Output: {result['data']['stdout'].strip()}")

    print("\n2. Executing Node.js code...")
    result = interpreter.execute(
        language="node", code='console.log("Hello from Node.js! Array:", [1,2,3]);'
    )
    if result["success"]:
        print(f"   Output: {result['data']['stdout'].strip()}")
    else:
        print("   Skipped: Node.js not available")

    print("\n3. Listing supported languages...")
    languages = interpreter.get_supported_languages()
    print(f"   Supported: {', '.join(languages)}")


def demo_polyglot_drone():
    """Demonstrate PolyglotDrone with LLM code generation"""
    print("\n" + "=" * 70)
    print("DEMO 2: PolyglotDrone with LLM Code Generation")
    print("=" * 70 + "\n")

    if not FIREWORKS_API_KEY:
        print("Skipping: FIREWORKS_API_KEY not set")
        return

    drone = PolyglotDrone()
    interpreter = PolyglotCodeInterpreter()

    client = OpenAI(api_key=FIREWORKS_API_KEY, base_url=OPENROUTER_BASE_URL)
    client.default_model = QUEEN_MODEL

    drone.register_tool("polyglot_interpreter", interpreter)
    drone.register_tool("llm_client", client)

    print("1. Generating and executing Python code to calculate fibonacci...")
    result = drone.execute(
        action="generate_and_execute",
        parameters={
            "language": "python",
            "task": "Calculate the first 10 fibonacci numbers and print them",
        },
    )

    if result["success"]:
        print(f"   Generated Code:\n{result['data']['generated_code']}\n")
        print(f"   Output: {result['data']['stdout'].strip()}")
    else:
        print(f"   Error: {result.get('error', 'Unknown')}")


def demo_tool_maker():
    """Demonstrate ToolMakerDrone dynamic tool creation"""
    print("\n" + "=" * 70)
    print("DEMO 3: ToolMakerDrone - Dynamic Tool Creation")
    print("=" * 70 + "\n")

    if not FIREWORKS_API_KEY:
        print("Skipping: FIREWORKS_API_KEY not set")
        return

    registry = DroneRegistry()
    drone = ToolMakerDrone()

    client = OpenAI(api_key=FIREWORKS_API_KEY, base_url=OPENROUTER_BASE_URL)
    client.default_model = QUEEN_MODEL

    drone.register_tool("llm_client", client)
    drone.register_tool("registry", registry)

    print("Note: This would create an actual tool file. Skipping for demo.")
    print("Demonstrating class name generation instead...\n")

    examples = ["string_reverser", "json validator", "url shortener"]

    for tool_name in examples:
        class_name = drone._generate_class_name(tool_name)
        print(f"   '{tool_name}' -> {class_name}")


def demo_code_analysis():
    """Demonstrate code analysis capabilities"""
    print("\n" + "=" * 70)
    print("DEMO 4: Code Analysis with ToolMakerDrone")
    print("=" * 70 + "\n")

    if not FIREWORKS_API_KEY:
        print("Skipping: FIREWORKS_API_KEY not set")
        return

    drone = ToolMakerDrone()
    client = OpenAI(api_key=FIREWORKS_API_KEY, base_url=OPENROUTER_BASE_URL)
    client.default_model = QUEEN_MODEL

    drone.register_tool("llm_client", client)

    print("Analyzing base_tool.py for code quality...")
    result = drone.execute(
        action="analyze_code",
        parameters={
            "file_path": "wormgpt_hive/tools/base_tool.py",
            "analysis_goal": "Assess code quality and suggest improvements",
        },
    )

    if result["success"]:
        print("\nAnalysis Result:")
        print(f"{result['data']['analysis'][:500]}...")
    else:
        print(f"Error: {result.get('error', 'Unknown')}")


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# WormGPT Hive Mind - Phase 5: Dynamic Code Generation")
    print("# Demonstrations")
    print("#" * 70)

    try:
        demo_polyglot_code_execution()
        demo_polyglot_drone()
        demo_tool_maker()
        demo_code_analysis()

        print("\n" + "=" * 70)
        print("All demos completed!")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nDemo error: {e}")
        import traceback

        traceback.print_exc()
