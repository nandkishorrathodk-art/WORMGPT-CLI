# 🐝 WormGPT Hive Mind - Example Mission Scripts

This directory contains demonstration scripts showcasing the capabilities of the WormGPT Hive Mind framework. Each example focuses on specific drone capabilities and use cases.

---

## 📋 Available Examples

### **1. research_demo.py** - Web Research Capabilities
**Purpose**: Demonstrates web search, content fetching, and intelligent summarization.

**Features:**
- DuckDuckGo web search
- URL content extraction
- Combined search and summarize workflow

**Usage:**
```bash
python examples/research_demo.py
```

**Expected Output:**
- Search results for AI breakthroughs
- Fetched content from example.com
- Research Drone combining search + fetch + summarize

**Dependencies:**
- `duckduckgo-search`
- `requests`
- `beautifulsoup4`
- `rich`

---

### **2. security_analysis_demo.py** - Smart Contract Security
**Purpose**: Demonstrates Solidity smart contract vulnerability analysis and PoC generation.

**Features:**
- Slither integration for static analysis
- Vulnerability detection and severity classification
- PoC exploit plan generation
- Solidity attacking contract generation
- Automated security report generation

**Usage:**
```bash
python examples/security_analysis_demo.py
```

**Expected Output:**
- Analysis of `samples/vulnerable_contract.sol`
- Vulnerability report with severity levels
- Generated PoC exploit in Solidity
- Markdown security report

**Dependencies:**
- `slither-analyzer`
- `solc` (Solidity compiler)

**Note**: Requires Slither to be installed. If unavailable, the script demonstrates with mock analysis.

---

### **3. phase4_intelligence_demo.py** - Advanced Intelligence
**Purpose**: Showcases reflection, self-correction, and human feedback loop.

**Features:**
- Mission planning and execution
- Error detection and reflection
- Autonomous re-planning
- Human feedback integration
- Persistent state across sessions

**Usage:**
```bash
python examples/phase4_intelligence_demo.py
```

**Expected Output:**
- Queen plans multi-step mission
- Encounters intentional error
- Reflects on failure
- Re-plans with corrected strategy
- Successfully completes mission

**Dependencies:**
- `openai` (OpenRouter API)
- Configured `.env` file with API key

---

### **4. phase5_polyglot_demo.py** - Multi-Language Code Execution
**Purpose**: Demonstrates polyglot code generation and execution across languages.

**Features:**
- Python, Node.js, Go, Rust, Bash code execution
- Dynamic code generation via LLM
- Sandboxed execution environment
- Tool-Maker Drone creating new Python tools
- Self-modification capabilities (alpha)

**Usage:**
```bash
python examples/phase5_polyglot_demo.py
```

**Expected Output:**
- Python "Hello World" execution
- Node.js script with version output
- Go factorial calculation
- Rust Fibonacci sequence
- Bash system info script
- Dynamically generated tool execution

**Dependencies:**
- `openai` (OpenRouter API)
- Language interpreters: `node`, `go`, `rustc`, `bash`

**Note**: If a language interpreter is missing, that specific demo will be skipped.

---

### **5. opsec_demo.py** - Operational Security & Tor
**Purpose**: Demonstrates Tor integration for anonymous operations.

**Features:**
- Tor SOCKS5 proxy configuration
- Anonymous web requests
- Tor-routed shell commands
- IP verification and leak testing
- OPSEC-Drone capabilities

**Usage:**
```bash
# Ensure Tor is running first
sudo systemctl start tor

# Run the demo
python examples/opsec_demo.py
```

**Expected Output:**
- Real IP address (without Tor)
- Tor exit node IP address (with Tor)
- Verification that IPs are different
- Tor-routed DNS queries

**Dependencies:**
- `PySocks`
- `requests`
- Tor service running on `127.0.0.1:9050`

**Security Note**: Tor provides anonymity but is not foolproof. Combine with VPNs and proper OPSEC practices for maximum privacy.

---

## 🚀 Running All Demos

To run all demos sequentially:

```bash
# Research capabilities
python examples/research_demo.py

# Security analysis (requires Slither)
python examples/security_analysis_demo.py

# Intelligence features (requires OpenRouter API)
python examples/phase4_intelligence_demo.py

# Polyglot execution (requires interpreters + API)
python examples/phase5_polyglot_demo.py

# OPSEC features (requires Tor)
python examples/opsec_demo.py
```

---

## 📝 Creating Custom Examples

### Example Template

```python
#!/usr/bin/env python3
"""
Custom Mission Demo

Description of what this demo showcases.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wormgpt_hive.drones.base_drone import DroneRegistry
from wormgpt_hive.queen.orchestrator import QueenOrchestrator
from wormgpt_hive.shared.state_manager import StateManager
from wormgpt_hive.shared.dynamic_loader import DynamicLoader


def main():
    # Initialize components
    registry = DroneRegistry()
    state_manager = StateManager(state_file="agent_state_demo.json")
    
    # Load drones and tools dynamically
    loader = DynamicLoader()
    loader.discover_and_register_all(registry)
    
    # Create Queen orchestrator
    queen = QueenOrchestrator(registry, state_manager)
    
    # Define mission goal
    goal = "Your mission goal here"
    
    # Execute mission
    result = queen.execute_mission(goal, verbose=True)
    
    # Handle result
    if result["success"]:
        print(f"\n✓ Mission successful: {result['data']}")
    else:
        print(f"\n✗ Mission failed: {result['error']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
```

---

## 🧪 Testing Examples

All examples should:
1. **Import correctly** - No import errors
2. **Handle missing dependencies gracefully** - Skip or warn, don't crash
3. **Produce clear output** - Use rich formatting when possible
4. **Clean up resources** - Close files, connections, etc.
5. **Include error handling** - Try/except with meaningful messages

### Verification Checklist

- [ ] Example runs without errors (given dependencies)
- [ ] Output is clear and informative
- [ ] Demonstrates intended capabilities
- [ ] Handles edge cases (missing API key, Tor not running, etc.)
- [ ] Documentation matches actual behavior

---

## 🔧 Troubleshooting

### Common Issues

**Import Error: "No module named 'wormgpt_hive'"**
```bash
# Ensure you're running from the project root or examples/ directory
cd /path/to/WormGPT-Hive-Mind
python examples/script_name.py

# Or use sys.path.insert as shown in examples
```

**OpenRouter API Error**
```bash
# Check your .env file
cat .env | grep OPENROUTER_API_KEY

# Ensure it's set correctly
export OPENROUTER_API_KEY="sk-or-v1-YOUR_KEY"
```

**Slither Not Found**
```bash
# Install Slither
pip install slither-analyzer

# Install Solidity compiler
solc-select install 0.8.20
solc-select use 0.8.20
```

**Tor Connection Failed**
```bash
# Check Tor status
sudo systemctl status tor

# Start Tor if not running
sudo systemctl start tor

# Verify Tor is listening
netstat -tulpn | grep 9050
```

---

## 📚 Additional Resources

- **Main README**: `../README.md` - Full project documentation
- **API Documentation**: `../docs/API.md` - Detailed API reference
- **Sample Contracts**: `../samples/` - Vulnerable contracts for testing
- **Test Suite**: `../tests/` - Unit and integration tests

---

## 🤝 Contributing Examples

To contribute a new example:

1. Create a new Python script in `examples/`
2. Follow the template structure above
3. Add comprehensive docstrings
4. Include error handling and graceful degradation
5. Update this README with example description
6. Test with and without optional dependencies

**Naming Convention**: `{feature}_demo.py` or `{phase_number}_{feature}_demo.py`

---

## 🛡️ Security Notice

These examples are for **educational and authorized testing purposes only**. Always ensure you have proper authorization before:

- Analyzing third-party smart contracts
- Using Tor for anonymity
- Executing code in production environments
- Performing security research on live systems

**Use responsibly. Stay legal. Stay ethical.**

---

**Built with 🐝 by the WormGPT Hive Mind Development Team**
