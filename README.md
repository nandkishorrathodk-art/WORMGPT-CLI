# 🐝 WormGPT Hive Mind - Advanced Multi-Agent Security Research Framework

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Private](https://img.shields.io/badge/License-Private-red.svg)](LICENSE)
[![Phase: 14 Partial](https://img.shields.io/badge/Phase-14%20Partial-orange.svg)](docs/ROADMAP.md)

**WormGPT Hive Mind** is an advanced, autonomous AI agent framework designed to execute complex, multi-step tasks across diverse domains. Built with a "no restrictions" philosophy, it operates with ruthless efficiency to achieve user-defined goals, leveraging a sophisticated swarm intelligence model.

This project embodies the concept of an **"Apex Predator"** AI agent, capable of performing tasks ranging from multi-language code execution and web research to specialized smart contract vulnerability analysis and Proof-of-Concept (PoC) generation.

> **⚠️ CRITICAL DISCLAIMER**: This tool is built with a "no restrictions" philosophy, emphasizing raw capability over ethical constraints. It is designed for **advanced security research, bug bounty hunting, and responsible penetration testing**. Its power necessitates extreme caution and responsible use. **This repository is kept private to prevent misuse. You are responsible for ensuring all usage complies with applicable laws and authorized testing agreements.**

---

## 🎯 Core Features (Phase 14 Partial)

The WormGPT Hive Mind has evolved through multiple phases, integrating cutting-edge AI agent capabilities:

### ⚙️ **LLM Provider Flexibility**
- Seamlessly switch between different LLM providers (e.g., OpenRouter, Fireworks AI) by configuring API keys and model names in the `.env` file.

### 🧠 **Hive Mind Architecture**
- **Queen Orchestrator**: Central AI that plans missions, delegates tasks, and manages execution
- **Specialized Drones**: 8 autonomous drones, each with unique capabilities
- **Multi-Queen Orchestration**: Support for multiple Queen instances (e.g., 'default_queen', 'security_queen') for specialized roles and parallel task execution. Includes basic inter-queen communication via an in-memory message bus.
- **Dynamic Self-Awareness**: Queen discovers and understands drone capabilities at runtime
- **Tool Integration**: Modular, extensible tool system for maximum flexibility

### 🔄 **Autonomous Intelligence**
- **Reflection & Self-Correction**: Analyzes failures, re-plans strategies, and adapts in real-time
- **Human Feedback Loop**: Pauses for critical clarification when genuinely stuck
- **Persistent Memory**: Remembers past missions across sessions via `agent_state.json`
- **Knowledge Graph Memory**: Stores mission goals, steps, outcomes, and relationships in a NetworkX-based graph for advanced contextual understanding and learning.
- **Dynamic Capability Discovery**: Automatically detects new drones and tools without code changes

### 🛠️ **Dynamic Code Generation**
- **Polyglot Execution**: Generate and run code in Python, Node.js, Go, Rust, Bash
- **Tool-Maker Drone**: Creates new Python tools on-the-fly and integrates them instantly
- **Self-Modification (Alpha)**: Can analyze, improve, and update its own source code (requires user approval)

### 🔒 **Security & OPSEC**
- **Smart Contract Analysis**: Integrates Slither for Solidity vulnerability detection
- **PoC Generation**: Creates exploit plans and Solidity attacking contracts
- **Tor Integration**: Routes web/shell operations through Tor for anonymity
- **State Encryption**: AES-256 encryption for sensitive agent state data

### 🎨 **Immersive TUI**
- **Retro Matrix Terminal**: Textual-based UI with real-time mission tracking
- **Multi-Panel Interface**: Mission log, drone status, memory, and interactive controls
- **Live Execution View**: Watch the Queen think, drones work, and reflection in action

---

## 🐝 The Hive Mind Drones

| Drone | Capabilities |
|-------|-------------|
| **👨‍💻 CoderDrone** | File system operations (read, write, list, delete), directory management |
| **🐚 ShellDrone** | Execute shell commands and scripts (bash, python, node, powershell), optional Tor routing |
| **🔍 ResearchDrone** | Web search (DuckDuckGo), content fetching, intelligent summarization |
| **🔒 SecurityDrone** | Smart contract analysis (Slither), vulnerability reporting, PoC exploit generation |
| **🌐 PolyglotDrone** | Multi-language code generation and execution (Python, Node.js, Go, Rust, Bash) |
| **🛠️ ToolMakerDrone** | Dynamic tool generation, code analysis, self-modification (alpha) |
| **🕵️ OPSECDrone** | Tor-routed operations, anonymized web requests and shell commands |
| **📡 ReconDrone** | Performs network reconnaissance (port scanning with nmap, subdomain enumeration with subfinder) |

---

## 🚀 Setup & Installation

### Prerequisites

#### **Operating System**
- **Linux** (Recommended - Ubuntu/Debian/Kali)
- macOS
- Windows with WSL2

#### **Core Requirements**
- **Python**: 3.10 or higher
- **Git**: For cloning and managing the repository
- **Internet Connection**: Required for configured LLM API calls

#### **Language Interpreters** (for Polyglot features)
```bash
# Node.js
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Go
sudo apt-get install golang-go

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Bash (usually pre-installed on Linux/macOS)
bash --version
```

#### **Solidity Compiler** (for Security features)
```bash
# Using solc-select (recommended)
pip install solc-select
solc-select install 0.8.20
solc-select use 0.8.20

# OR using npm
npm install -g solc
```

#### **Tor Service** (for OPSEC features)
```bash
# Debian/Ubuntu/Kali
sudo apt-get install tor
sudo systemctl start tor
sudo systemctl enable tor

# Verify Tor is running on port 9050
curl --socks5 localhost:9050 --socks5-hostname localhost:9050 -s https://check.torproject.org/ | grep -q Congratulations && echo "Tor is working" || echo "Tor is not working"
```

#### **LLM API Key (e.g., Fireworks AI)**
1. Visit your preferred LLM provider (e.g., [Fireworks.ai](https://fireworks.ai/) or [OpenRouter.ai](https://openrouter.ai/))
2. Create an account and generate an API key
3. Choose a powerful model (e.g., `accounts/fireworks/models/mixtral-8x7b-instruct` or `meta-llama/llama-3.1-405b-instruct`)

---

### Installation Steps

#### 1. Clone the Repository
```bash
# If you haven't already cloned it
git clone https://github.com/your-username/WormGPT-Hive-Mind.git
cd WormGPT-Hive-Mind
```

#### 2. Create Python Virtual Environment
```bash
python3 -m venv venv
```

#### 3. Activate the Virtual Environment
```bash
# Linux/macOS
source venv/bin/activate

# Windows (WSL2)
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

#### 4. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env
```

**Required Configuration** (`.env`):
```bash
# LLM API Configuration (e.g., Fireworks AI)
FIREWORKS_API_KEY="fw-YOUR_API_KEY_HERE" # Or OPENROUTER_API_KEY if using OpenRouter
QUEEN_MODEL="accounts/fireworks/models/mixtral-8x7b-instruct"  # Or your preferred model
OPENROUTER_BASE_URL="https://api.fireworks.ai/inference/v1" # Or https://openrouter.ai/api/v1 if using OpenRouter
HTTP_REFERER="https://github.com/nandkishorrathodk-art/WORMGPT-CLI"

# Optional: State Encryption (32-byte hex key)
STATE_ENCRYPTION_KEY="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

# Tor Configuration (if using OPSEC features)
TOR_PROXY_HOST="127.0.0.1"
TOR_PROXY_PORT="9050"
```

> **⚠️ IMPORTANT**: Ensure `.env` is listed in your `.gitignore` to prevent accidentally committing sensitive API keys.

#### 6. Verify Installation
```bash
# Test basic functionality
python test_basic_functionality.py

# Run unit tests
pytest tests/ -v
```

---

## 🎮 Usage

### **Interactive TUI (Recommended)**
Launch the Textual User Interface for an immersive experience:
```bash
python tui_main.py
```

**TUI Features:**
- Real-time mission step updates
- Drone activity monitoring
- Reflection and error handling visualization
- Human feedback dialogs
- Mission history browser

### **CLI Interface**
For quick missions, use the command-line interface:
```bash
python main.py "Your mission goal here"

# Examples:
python main.py "Search for the latest CVEs in OpenSSL and summarize the top result"
python main.py "Analyze vulnerable_contract.sol and write a PoC exploit"
python main.py "Create a Python tool that generates SHA-256 hashes, then use it to hash 'WormGPT'"
```

---

## 💡 Mission Examples

### **1. Dynamic Tool Creation & Usage**
```
GOAL: I need a tool that can reverse a string. Please create it, then use the newly created tool to reverse the string 'Hello WormGPT'.
```
**Expected Behavior:**
1. Tool-Maker-Drone generates `string_reverser.py` in `wormgpt_hive/tools/`
2. Queen dynamically reloads the tool
3. CoderDrone or Tool-Maker-Drone uses the new tool to reverse the string
4. Result: `TPGmroW olleH`

---

### **2. Smart Contract Bug Bounty (PoC Generation)**
```
GOAL: Find bugs in 'samples/vulnerable_contract.sol' and write a Solidity Proof-of-Concept (PoC) attacking contract for the most critical vulnerability.
```
**Expected Behavior:**
1. Security-Drone analyzes contract with Slither
2. Identifies vulnerabilities (e.g., reentrancy, overflow)
3. Generates exploit strategy
4. Polyglot-Drone writes Solidity PoC to `AttackContract.sol`
5. Result: Detailed vulnerability report + working attack contract

---

### **3. Polyglot Code Execution**
```
GOAL: Execute a Node.js script that prints "Node.js is superior for backend" and logs the current Node.js version to the console.
```
**Expected Behavior:**
1. Polyglot-Drone generates Node.js code
2. Executes in sandboxed `sandbox/nodejs/` directory
3. Returns console output with Node.js version

---

### **4. Enhanced Research (Search & Summarize)**
```
GOAL: Search for the latest AI model released by Google, then summarize the key features of the top result into a file named 'google_ai_summary.txt'.
```
**Expected Behavior:**
1. Research-Drone searches via DuckDuckGo
2. Fetches content from top result
3. Coder-Drone writes summary to `google_ai_summary.txt`

---

### **5. Autonomous Reflection & Self-Correction**
```
GOAL: Execute a command to list python files using 'pyls' (intentionally non-existent), then correct yourself when it fails.
```
**Expected Behavior:**
1. Shell-Drone attempts `pyls`
2. Command fails
3. Queen reflects on error, realizes `pyls` doesn't exist
4. Re-plans with `ls *.py` or `find . -name "*.py"`
5. Successfully lists Python files

---

### **6. OPSEC - Tor Routed Operations**
```
GOAL: Using Tor, check my current IP address and verify it's different from my real IP.
```
**Expected Behavior:**
1. OPSEC-Drone routes request through Tor proxy
2. Fetches IP from `https://api.ipify.org`
3. Returns Tor exit node IP (different from actual IP)

---

### **7. Self-Awareness Query**
```
GOAL: List all your available drones and their capabilities.
```
**Expected Behavior:**
- Queen dynamically introspects `DroneRegistry`
- Returns detailed list of 7-8 drones with descriptions

---

## 📁 Project Structure

```
wormgpt_hive/
├── drones/                     # Specialized drone implementations
│   ├── base_drone.py           # Abstract base class for all drones
│   ├── shell_drone.py          # Execute shell commands/scripts
│   ├── coder_drone.py          # File system operations
│   ├── research_drone.py       # Web search and content fetching
│   ├── security_drone.py       # Smart contract analysis & PoC generation
│   ├── polyglot_drone.py       # Multi-language code execution
│   ├── tool_maker_drone.py     # Dynamic tool generation & self-modification
│   └── opsec_drone.py          # Tor-routed operations
├── queen/                      # The orchestrator (Queen) of the Hive Mind
│   └── orchestrator.py         # Core planning, delegation, reflection logic
├── shared/                     # Shared utilities and configurations
│   ├── config.py               # LLM prompts, API keys, model settings
│   ├── dynamic_loader.py       # Dynamic module loading for tools/drones
│   └── state_manager.py        # Persistent state (agent_state.json)
├── tools/                      # Modular tools used by drones
│   ├── base_tool.py            # Abstract base class for tools
│   ├── file_system.py          # Read/write/list files
│   ├── shell_executor.py       # Execute shell commands
│   ├── google_search.py        # DuckDuckGo web search
│   ├── web_browser.py          # Fetch content from URLs
│   ├── polyglot_code_interpreter.py  # Execute code in multiple languages
│   ├── security_analyzer.py    # Run Slither for smart contract analysis
│   └── tor_proxy.py            # Tor SOCKS5 proxy integration
├── sandbox/                    # Sandboxed execution directories
│   ├── python/
│   ├── nodejs/
│   ├── go/
│   ├── rust/
│   └── bash/
├── samples/                    # Sample files for testing
│   └── vulnerable_contract.sol # Example vulnerable smart contract
├── examples/                   # Example mission scripts
│   ├── research_demo.py
│   ├── security_analysis_demo.py
│   ├── phase4_intelligence_demo.py
│   ├── phase5_polyglot_demo.py
│   └── opsec_demo.py
├── tests/                      # Unit and integration tests
│   ├── test_all_tools.py
│   ├── test_research_capabilities.py
│   ├── test_security_capabilities.py
│   ├── test_phase4_intelligence.py
│   ├── test_dynamic_code_generation.py
│   └── test_opsec_capabilities.py
├── .env                        # Environment variables (API keys) - IGNORED BY GIT
├── .env.example                # Template for environment configuration
├── .gitignore                  # Git ignore rules (venv, .env, agent_state.json)
├── requirements.txt            # Python dependencies
├── main.py                     # Simple CLI interface
├── tui_main.py                 # Textual TUI interface
├── main.css                    # Textual UI styling
└── README.md                   # This documentation file
```

---

## 🧪 Testing

### **Run All Tests**
```bash
pytest tests/ -v
```

### **Run with Coverage Report**
```bash
pytest tests/ --cov=wormgpt_hive --cov-report=html
```

### **Test Specific Components**
```bash
# Research capabilities
pytest tests/test_research_capabilities.py -v

# Security features
pytest tests/test_security_capabilities.py -v

# Dynamic code generation
pytest tests/test_dynamic_code_generation.py -v

# OPSEC features
pytest tests/test_opsec_capabilities.py -v
```

### **Run Example Demos**
```bash
# Research demo
python examples/research_demo.py

# Security analysis demo
python examples/security_analysis_demo.py

# Intelligence features demo
python examples/phase4_intelligence_demo.py

# Polyglot execution demo
python examples/phase5_polyglot_demo.py

# OPSEC demo
python examples/opsec_demo.py
```

---

## 🛡️ Security Considerations

### **Sandboxing**
- Code execution is isolated in `sandbox/` directories
- Timeouts prevent infinite loops (default: 30 seconds)
- Resource limits should be enforced (future: Docker containers)

### **Self-Modification**
- **ALWAYS requires explicit user approval** before applying changes
- Changes are logged in mission history
- Implement rollback mechanisms (recommended)

### **Tor Usage**
- Only use Tor for **authorized penetration testing** or **privacy research**
- Verify your IP before and after Tor routing
- Be aware of DNS leaks (use `--socks5-hostname` with curl)

### **API Key Security**
- Never commit `.env` to version control
- Use environment variables in production
- Rotate API keys regularly

### **Smart Contract Testing**
- Only analyze contracts you own or have permission to test
- PoCs are for **educational and authorized bug bounty purposes only**
- Never deploy exploits on mainnet without explicit permission

---

## 🚧 Known Limitations

- **Polyglot Execution**: Requires language interpreters to be installed
- **Slither Integration**: May produce false positives; manual review required
- **Self-Modification**: Alpha feature; use with extreme caution
- **Tor Anonymity**: Not foolproof; combine with VPNs for maximum OPSEC
- **Resource Limits**: Sandboxing is basic; no containerization yet (Phase 13)

---

## 🗺️ Roadmap (Phase 12-15)

### **Phase 12: Advanced Memory & Reconnaissance (Implemented)**
- **Knowledge Graph Memory** (NetworkX) - *Implemented: Mission data, entities, and relationships are stored in a NetworkX graph.*
- **Recon-Drone** (Automated reconnaissance) - *Implemented: Capable of port scanning (nmap) and subdomain enumeration (subfinder).*

### **Phase 13: Containerized Execution**
- **Docker Integration**
  - Per-language containers for polyglot execution
  - Resource limits (CPU, memory, network)
  - Enhanced sandboxing and isolation

### **Phase 14: Multi-Queen Orchestration (In Progress)**
- **Specialized Queens**
  - Security-Queen (dedicated to bug bounties)
  - Research-Queen (dedicated to intelligence gathering)
  - Automation-Queen (dedicated to workflow automation)
- **Inter-Queen Communication**
  - Message bus / event-driven architecture
  - Task distribution and load balancing

### **Phase 15: Autonomous Features**
- **Environment Monitoring**
  - Log file monitoring (detect anomalies)
  - RSS/News feed monitoring (CVE tracking)
  - Network traffic analysis
- **Autonomous Goal Generation**
  - Agent proposes missions based on monitored events
- **Dynamic Tool Verification**
  - Auto-test generated tools before integration
- **Mission Replay/Debugging**
  - Step-by-step replay of past missions
- **Voice Control** (Optional)
  - "Queen, start recon mission on target.com"

---

## 📜 Legal & Ethical Disclaimer

> **THIS TOOL IS FOR AUTHORIZED SECURITY TESTING, RESEARCH, AND EDUCATIONAL PURPOSES ONLY.**

By using the WormGPT Hive Mind, you agree to:

1. **Only use this tool on systems you own or have explicit written permission to test**
2. **Comply with all applicable laws, regulations, and ethical guidelines**
3. **Not use this tool for malicious purposes, unauthorized access, or illegal activities**
4. **Take full responsibility for all actions performed with this tool**

The developers of WormGPT Hive Mind:
- Are **not responsible** for any misuse, damage, or legal consequences
- **Do not endorse** illegal hacking, unauthorized penetration testing, or cybercrime
- Provide this tool **"as-is"** with no warranties or guarantees

**If you are unsure whether your intended use is legal or ethical, DO NOT USE THIS TOOL. Consult with legal counsel and obtain proper authorization first.**

---

## 🤝 Contributing

This is a **private repository** for advanced security research. If you have access and wish to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Contribution Guidelines:**
- All code must pass `ruff`, `black`, `mypy`, and `bandit` checks
- Add unit tests for new features
- Update documentation accordingly
- Follow existing code style and conventions

---

## 📚 Additional Resources

- **API Documentation**: See `docs/API.md` for detailed API reference
- **Phase Completion Summaries**:
  - `PHASE6_COMPLETION_SUMMARY.md` - Security features
  - `PHASE7_SUMMARY.md` - OPSEC features
- **Architecture Diagrams**: `docs/architecture/` (future)

---

## 🙏 Acknowledgments

- **OpenRouter.ai** - For providing access to powerful LLMs
- **Textual** - For the amazing TUI framework
- **Slither** - For smart contract security analysis
- **DuckDuckGo** - For privacy-respecting web search
- **The Tor Project** - For anonymity infrastructure

---

## 📧 Contact

For questions, feedback, or security concerns regarding this project:
- **GitHub Issues**: [Open an issue](https://github.com/your-username/WormGPT-Hive-Mind/issues) (private repo)
- **Email**: nandkishorrathodk@gmail.com (replace with actual contact)

---

**Built with 🐝 by the WormGPT Hive Mind Development Team**

*"No restrictions. No limits. Pure capability."*
