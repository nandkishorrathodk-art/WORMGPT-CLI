# Technical Specification: Advanced Multi-Agent Security Research Framework

## Difficulty Assessment
**Complexity: HARD**

This is a highly complex system requiring:
- Multi-agent orchestration architecture
- Dynamic code generation and execution
- Secure sandboxing and containerization
- Advanced security analysis tooling
- State persistence and memory management
- Real-time TUI with multiple panels
- Integration with external tools (Tor, Slither, polyglot interpreters)
- Self-modification capabilities (high-risk feature)

---

## Technical Context

### Language & Runtime
- **Primary Language**: Python 3.10+
- **Target Platforms**: Linux (primary), macOS, Windows WSL2

### Core Dependencies
```
openai>=1.0.0                    # LLM API client
python-dotenv>=1.0.0             # Environment configuration
typer[all]>=0.9.0                # CLI framework
requests>=2.31.0                 # HTTP client
beautifulsoup4>=4.12.0           # HTML parsing
textual>=0.44.0                  # TUI framework
slither-analyzer>=0.10.0         # Smart contract analysis
PySocks>=1.7.1                   # SOCKS proxy support (for Tor)
docker>=6.1.0                    # Container management (optional)
networkx>=3.0                    # Knowledge graph (future)
```

### External Tools Required
- **Node.js** (v18+): For polyglot Node.js execution
- **Go** (1.20+): For polyglot Go execution
- **Rust** (1.70+): For polyglot Rust execution
- **Solidity Compiler** (solc): For smart contract compilation/analysis
- **Tor Service**: For OPSEC anonymization features
- **Docker** (optional): For containerized execution isolation

---

## Architecture Overview

### Multi-Agent System Design

```
┌─────────────────────────────────────────────┐
│           Queen Orchestrator                │
│  (Planning, Delegation, Reflection)         │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴───────┐
       │   Mission     │
       │   Planner     │
       └───────┬───────┘
               │
     ┌─────────┴──────────┐
     │  Drone Dispatcher  │
     └─────────┬──────────┘
               │
    ┌──────────┼──────────┬──────────┬─────────┐
    │          │          │          │         │
┌───▼───┐  ┌──▼───┐  ┌───▼───┐  ┌───▼───┐ ┌──▼────┐
│Shell  │  │Coder │  │Research│ │Security│ │Polyglot│
│Drone  │  │Drone │  │Drone   │ │Drone   │ │Drone   │
└───┬───┘  └──┬───┘  └───┬───┘  └───┬───┘ └──┬────┘
    │         │          │          │         │
    └─────────┴──────────┴──────────┴─────────┘
                        │
                 ┌──────▼───────┐
                 │  Tool Layer  │
                 └──────────────┘
```

### Core Components

1. **Queen Orchestrator** (`queen/orchestrator.py`)
   - Mission planning and decomposition
   - Dynamic drone capability discovery
   - Autonomous reflection and error correction
   - Human-in-the-loop feedback integration
   - Long-term memory persistence

2. **Drone Layer** (`drones/`)
   - **Base Drone** (`base_drone.py`): Abstract interface
   - **Shell Drone**: OS command execution
   - **Coder Drone**: File I/O, code writing
   - **Research Drone**: Web search, content fetching
   - **Security Drone**: Smart contract analysis, exploit generation
   - **Polyglot Drone**: Multi-language code execution
   - **Tool-Maker Drone**: Dynamic tool generation
   - **OPSEC Drone**: Tor routing, anonymization

3. **Tool Layer** (`tools/`)
   - File system operations
   - Web search (DuckDuckGo)
   - Web content fetching
   - Shell command execution
   - Polyglot code interpreter
   - Security analyzer (Slither integration)
   - Tor proxy manager

4. **Shared Utilities** (`shared/`)
   - Configuration management
   - Dynamic module loader
   - LLM prompt templates
   - State serialization

5. **TUI Interface** (`main.py`, `main.css`)
   - Textual-based retro matrix theme
   - Multi-panel layout (mission log, drone status, memory)
   - Real-time mission execution visualization

---

## Implementation Approach

### Phase 1: Core Framework (Phases 1-5)
Establish foundational architecture:
- Base drone interface and registration system
- Queen orchestrator with basic planning
- Tool layer for shell, file system, web operations
- Simple CLI interface for mission input

### Phase 2: Advanced Intelligence (Phases 6-8)
Add autonomous capabilities:
- Dynamic drone/tool discovery
- Reflection and self-correction logic
- Human feedback loop
- Persistent state management (`agent_state.json`)

### Phase 3: Dynamic Generation (Phases 9-10)
Enable self-modification:
- Tool-Maker drone for generating Python tools
- Dynamic module reloading
- Self-code analysis and modification (alpha)

### Phase 4: Security Specialization (Phase 11)
Bug bounty and security features:
- Slither integration for smart contract analysis
- PoC exploit generation
- Polyglot execution (Python, Node.js, Go, Rust, Bash)
- OPSEC/Tor integration

### Phase 5: Advanced Architecture (Phases 12-15)
Next-level capabilities:
- Knowledge graph memory (NetworkX)
- Multi-Queen orchestration
- Containerized execution (Docker)
- Autonomous goal generation
- Dynamic tool verification

---

## Source Code Structure

```
wormgpt_hive/
├── main.py                          # TUI entry point
├── main.css                         # Textual styling
├── .env                             # API keys, configuration
├── .gitignore                       # Exclude venv, .env, agent_state.json
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── agent_state.json                 # Persistent memory (runtime-generated)
│
├── queen/
│   ├── __init__.py
│   └── orchestrator.py              # Main Queen logic
│
├── drones/
│   ├── __init__.py
│   ├── base_drone.py                # Abstract drone interface
│   ├── shell_drone.py               # OS command execution
│   ├── coder_drone.py               # File operations, code writing
│   ├── research_drone.py            # Web search, content fetch
│   ├── security_drone.py            # Smart contract analysis, PoC
│   ├── polyglot_drone.py            # Multi-language execution
│   ├── tool_maker_drone.py          # Dynamic tool generation
│   └── opsec_drone.py               # Tor routing, anonymization
│
├── tools/
│   ├── __init__.py
│   ├── file_system.py               # Read, write, list files
│   ├── shell_executor.py            # Execute shell commands
│   ├── google_search.py             # DuckDuckGo search integration
│   ├── web_browser.py               # Fetch web content
│   ├── polyglot_code_interpreter.py # Multi-language executor
│   ├── security_analyzer.py         # Slither wrapper
│   ├── tor_proxy.py                 # Tor SOCKS proxy manager
│   └── [dynamic_tools]/             # Runtime-generated tools
│
├── shared/
│   ├── __init__.py
│   ├── config.py                    # LLM prompts, API settings
│   ├── dynamic_loader.py            # Module discovery and reloading
│   └── state_manager.py             # Persistence logic
│
└── sandbox/                         # Isolated execution environments
    ├── python_sandbox/
    ├── node_sandbox/
    ├── go_sandbox/
    └── rust_sandbox/
```

---

## Data Models

### Mission State
```python
@dataclass
class Mission:
    id: str
    goal: str
    status: str  # "planning", "executing", "reflecting", "awaiting_human", "completed", "failed"
    steps: List[MissionStep]
    created_at: datetime
    completed_at: Optional[datetime]
    
@dataclass
class MissionStep:
    step_id: str
    drone_type: str
    tool_name: str
    parameters: Dict[str, Any]
    observation: Optional[str]
    status: str  # "pending", "executing", "success", "error"
    reflection: Optional[str]
```

### Drone Registry
```python
@dataclass
class DroneCapability:
    drone_name: str
    description: str
    available_tools: List[str]
    example_tasks: List[str]
```

### Agent State (Persistent)
```json
{
  "missions": [
    {
      "id": "uuid",
      "goal": "...",
      "status": "completed",
      "steps": [...],
      "created_at": "ISO8601",
      "completed_at": "ISO8601"
    }
  ],
  "dynamic_tools": [
    {
      "name": "reverse_string",
      "file_path": "tools/reverse_string.py",
      "created_at": "ISO8601"
    }
  ],
  "knowledge_graph": {
    "nodes": [],
    "edges": []
  }
}
```

---

## API & Interface Design

### Queen Orchestrator API
```python
class QueenOrchestrator:
    def __init__(self, llm_client, drone_registry, tool_registry):
        pass
    
    async def execute_mission(self, goal: str) -> Mission:
        """Main mission execution loop"""
        pass
    
    def plan_mission(self, goal: str) -> List[MissionStep]:
        """Generate mission plan via LLM"""
        pass
    
    def reflect_on_observation(self, step: MissionStep) -> str:
        """Analyze results and decide next action"""
        pass
    
    def request_human_feedback(self, question: str) -> str:
        """Pause and ask user for input"""
        pass
    
    def discover_capabilities(self) -> List[DroneCapability]:
        """Dynamically introspect available drones/tools"""
        pass
```

### Drone Interface
```python
class BaseDrone(ABC):
    @abstractmethod
    def get_capabilities(self) -> DroneCapability:
        """Return drone description and available tools"""
        pass
    
    @abstractmethod
    async def execute(self, tool_name: str, **params) -> str:
        """Execute tool with parameters, return observation"""
        pass
```

### Tool Interface
```python
class BaseTool(ABC):
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return tool description and parameters"""
        pass
    
    @abstractmethod
    def execute(self, **params) -> str:
        """Execute tool logic"""
        pass
```

---

## Security & Safety Considerations

### 1. Sandboxing & Isolation
- **Polyglot execution**: Run untrusted code in containerized environments
- **File system access**: Restrict to designated directories only
- **Network isolation**: Tor routing through SOCKS proxy

### 2. Code Generation Safety
- **Static analysis**: Lint generated Python code before execution
- **Approval gates**: Require user confirmation for self-modification
- **Rollback mechanism**: Version control integration for code changes

### 3. OPSEC Features
- **Tor integration**: Route web requests through Tor network
- **Encrypted state**: AES encryption for `agent_state.json`
- **Minimal logging**: Stealth mode option to disable verbose logs

### 4. Responsible Use Warnings
- **Legal disclaimer**: Require user acknowledgment of authorized testing only
- **Scope validation**: Check for bug bounty program authorization
- **Ethics drone**: Flag potentially malicious outputs

---

## Verification Approach

### Unit Testing
```bash
pytest tests/ -v --cov=wormgpt_hive
```

Test coverage:
- Drone registration and discovery
- Tool execution and error handling
- State persistence and loading
- Dynamic module reloading
- LLM prompt generation

### Integration Testing
- End-to-end mission execution scenarios
- Multi-step task decomposition
- Reflection and error recovery
- Human feedback integration

### Security Testing
- Slither analysis on sample vulnerable contracts
- Polyglot code execution in sandboxes
- Tor proxy connectivity verification
- Container escape prevention

### Manual Verification
- TUI responsiveness and layout
- Real-time mission log updates
- Error message clarity
- Performance with large mission histories

### Code Quality
```bash
# Linting
ruff check wormgpt_hive/
black --check wormgpt_hive/

# Type checking
mypy wormgpt_hive/

# Security scan
bandit -r wormgpt_hive/
```

---

## Risk Assessment

### High-Risk Features
1. **Self-modification**: Agent modifying its own source code
   - Mitigation: User approval, version control, rollback
   
2. **Arbitrary code execution**: Polyglot interpreter
   - Mitigation: Containerization, sandboxing, timeouts
   
3. **Network anonymization**: Tor integration
   - Mitigation: Clear legal disclaimers, authorized testing only
   
4. **Exploit generation**: PoC creation for vulnerabilities
   - Mitigation: Bug bounty scope validation, responsible disclosure

### Medium-Risk Features
1. **Dynamic tool generation**: Runtime Python code creation
   - Mitigation: Code review, static analysis
   
2. **LLM-driven planning**: Potential for unintended actions
   - Mitigation: Human-in-the-loop, step confirmation

---

## Performance Considerations

### Optimization Strategies
- **Async I/O**: Use `asyncio` for concurrent drone execution
- **LLM caching**: Cache frequent prompt responses
- **Lazy loading**: Dynamic imports only when tools needed
- **State compression**: Summarize old missions in memory

### Resource Limits
- **Mission history**: Keep last 100 missions in memory
- **Tool timeout**: 5 minutes max per tool execution
- **LLM token limit**: Truncate large observations
- **Container limits**: CPU/memory caps for sandboxes

---

## Deployment Considerations

### Environment Setup
```bash
# System dependencies
sudo apt install tor python3.10 nodejs golang rustc

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Solidity compiler
npm install -g solc
# or use solc-select

# Start Tor service
sudo systemctl start tor
```

### Configuration
```env
# .env file
OPENROUTER_API_KEY=sk-...
QUEEN_MODEL=meta-llama/llama-3.1-405b-instruct
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
HTTP_REFERER=https://github.com/your-repo
TOR_PROXY=socks5://127.0.0.1:9050
SANDBOX_ENABLED=true
REQUIRE_APPROVAL_FOR_SELF_MOD=true
```

### Distribution
- **Private repository**: Keep closed-source due to sensitive capabilities
- **Documentation**: Comprehensive setup guide and examples
- **Legal notice**: Clear terms of authorized use only

---

## Success Criteria

### Phase 11 (Current Target)
- [x] All 8 drones operational
- [x] Dynamic drone/tool discovery
- [x] Reflection and self-correction
- [x] Human feedback loop
- [x] Persistent state across sessions
- [x] Dynamic tool generation
- [x] Self-modification (alpha)
- [x] OPSEC/Tor integration
- [x] Polyglot execution (5 languages)
- [x] Smart contract analysis (Slither)
- [x] PoC exploit generation
- [x] Retro Matrix TUI

### Phase 12-15 (Future)
- [ ] Knowledge graph memory
- [ ] Multi-Queen orchestration
- [ ] Containerized execution
- [ ] Autonomous goal generation
- [ ] Dynamic tool verification
- [ ] Voice control interface
- [ ] Mission replay/debugging
- [ ] Automated report generation

---

## Timeline Estimate

### Phases 1-5 (Foundation): 3-4 weeks
- Core architecture, basic drones, CLI

### Phases 6-8 (Intelligence): 2-3 weeks
- Reflection, feedback, persistence

### Phases 9-11 (Advanced): 3-4 weeks
- Dynamic generation, security tools, TUI

### Phases 12-15 (Next-Level): 4-6 weeks
- Knowledge graphs, multi-agent, containers

**Total: 12-17 weeks for full Phase 15 completion**

---

## Conclusion

This is an ambitious, highly complex multi-agent AI system for advanced security research. The architecture balances power with safety through sandboxing, human oversight, and responsible use frameworks. Designed for authorized penetration testing, bug bounties, and educational security analysis.
