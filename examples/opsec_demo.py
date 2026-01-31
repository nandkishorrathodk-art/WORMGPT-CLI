#!/usr/bin/env python3
"""
OPSEC and Tor Proxy Demonstration

This example demonstrates the OPSEC capabilities of the WormGPT Hive Mind,
including Tor proxy integration for anonymous web requests and command execution.

REQUIREMENTS:
- Tor service must be running (usually on port 9050)
- On Linux/macOS: sudo systemctl start tor
- On Windows: Install and run Tor Browser or Tor Expert Bundle
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wormgpt_hive.tools.tor_proxy import TorProxyTool
from wormgpt_hive.drones.opsec_drone import OPSECDrone
from wormgpt_hive.tools.shell_executor import ShellExecutorTool


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_tor_proxy_tool():
    """Demonstrate Tor proxy tool functionality."""
    print_section("Tor Proxy Tool Demo")
    
    tor_tool = TorProxyTool(proxy_host="127.0.0.1", proxy_port=9050)
    
    print("1. Checking if Tor is available...")
    is_available = tor_tool.is_tor_available()
    if is_available:
        print("   ✓ Tor proxy is available at 127.0.0.1:9050")
    else:
        print("   ✗ Tor proxy is NOT available")
        print("   Please start Tor service before running this demo")
        return False
    
    print("\n2. Testing Tor connection...")
    result = tor_tool.test_connection()
    if result["success"]:
        print(f"   ✓ {result['message']}")
        print(f"   Exit IP: {result['data']['exit_ip']}")
    else:
        print(f"   ✗ {result['error']}")
        return False
    
    print("\n3. Getting Tor exit IP...")
    result = tor_tool.get_exit_ip()
    if result["success"]:
        print(f"   ✓ Tor exit IP: {result['data']['exit_ip']}")
    else:
        print(f"   ✗ {result['error']}")
    
    print("\n4. Fetching URL via Tor...")
    result = tor_tool.fetch_url("https://check.torproject.org/api/ip", parse_json=True)
    if result["success"]:
        print(f"   ✓ Fetched content via Tor")
        print(f"   Content: {result['data']['content']}")
    else:
        print(f"   ✗ {result['error']}")
    
    return True


def demo_opsec_drone():
    """Demonstrate OPSEC drone functionality."""
    print_section("OPSEC Drone Demo")
    
    drone = OPSECDrone()
    tor_tool = TorProxyTool()
    shell_tool = ShellExecutorTool()
    
    drone.register_tool("tor_proxy", tor_tool)
    drone.register_tool("shell_executor", shell_tool)
    
    print("1. Checking Tor availability...")
    result = drone.execute("check_tor_availability", {})
    if result["success"]:
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ {result['error']}")
        return
    
    print("\n2. Testing Tor connection via drone...")
    result = drone.execute("test_tor_connection", {})
    if result["success"]:
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ {result['error']}")
    
    print("\n3. Getting Tor exit IP via drone...")
    result = drone.execute("get_tor_ip", {})
    if result["success"]:
        print(f"   ✓ {result['message']}")
    else:
        print(f"   ✗ {result['error']}")
    
    print("\n4. Fetching URL via Tor (through drone)...")
    result = drone.execute("fetch_url_via_tor", {
        "url": "https://api.ipify.org?format=json",
        "parse_json": True
    })
    if result["success"]:
        print(f"   ✓ {result['message']}")
        print(f"   Response: {result['data'].get('content', {})}")
    else:
        print(f"   ✗ {result['error']}")


def demo_state_encryption():
    """Demonstrate state encryption functionality."""
    print_section("State Encryption Demo")
    
    from wormgpt_hive.shared.state_manager import StateManager
    import os
    
    print("1. Creating state manager with encryption...")
    encryption_key = "demo_encryption_key_123456789"
    state_manager = StateManager(
        file_path="demo_encrypted_state.json",
        encryption_key=encryption_key
    )
    
    if state_manager.fernet:
        print("   ✓ Encryption enabled")
    else:
        print("   ✗ Encryption not enabled")
        return
    
    print("\n2. Saving encrypted state...")
    test_state = {
        "version": "0.11.0",
        "missions": [
            {
                "id": 1,
                "goal": "Test encrypted mission",
                "status": "completed",
                "sensitive_data": "This data should be encrypted"
            }
        ]
    }
    
    success = state_manager.save_state(test_state)
    if success:
        print("   ✓ State saved with encryption")
        
        if os.path.exists("demo_encrypted_state.json"):
            with open("demo_encrypted_state.json", "rb") as f:
                encrypted_content = f.read()
                print(f"   File size: {len(encrypted_content)} bytes")
                print(f"   Content preview (hex): {encrypted_content[:50].hex()}...")
    else:
        print("   ✗ Failed to save state")
        return
    
    print("\n3. Loading encrypted state...")
    loaded_state = state_manager.load_state()
    if loaded_state.get("missions"):
        print("   ✓ State loaded and decrypted successfully")
        print(f"   Missions count: {len(loaded_state['missions'])}")
        print(f"   First mission: {loaded_state['missions'][0]['goal']}")
    else:
        print("   ✗ Failed to load state")
    
    print("\n4. Cleaning up demo file...")
    if os.path.exists("demo_encrypted_state.json"):
        os.remove("demo_encrypted_state.json")
        print("   ✓ Demo file removed")


def main():
    """Run all OPSEC demos."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  WormGPT OPSEC Capabilities Demo            ║
║                                                              ║
║  This demo showcases the operational security features:     ║
║  - Tor proxy integration for anonymous web requests         ║
║  - OPSEC drone for anonymized operations                    ║
║  - State encryption for data protection                     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    tor_available = demo_tor_proxy_tool()
    
    if tor_available:
        demo_opsec_drone()
    else:
        print("\nSkipping OPSEC drone demo (Tor not available)")
    
    demo_state_encryption()
    
    print_section("Demo Complete")
    print("All OPSEC capabilities demonstrated successfully!")
    print("\nNOTE: For production use, always:")
    print("  - Use strong encryption keys")
    print("  - Store keys securely (environment variables)")
    print("  - Verify Tor connection before sensitive operations")
    print("  - Follow responsible disclosure practices")


if __name__ == "__main__":
    main()
