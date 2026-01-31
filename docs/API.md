# 🐝 WormGPT Hive Mind - API Documentation

This document provides comprehensive API reference for the WormGPT Hive Mind framework, covering the Queen orchestrator, drone interfaces, tool system, and core utilities.

---

## 📑 Table of Contents

1. [Core Architecture](#core-architecture)
2. [Queen Orchestrator API](#queen-orchestrator-api)
3. [Drone Interface](#drone-interface)
4. [Tool Interface](#tool-interface)
5. [State Management](#state-management)
6. [Dynamic Loader](#dynamic-loader)
7. [Data Models](#data-models)
8. [Creating Custom Drones](#creating-custom-drones)
9. [Creating Custom Tools](#creating-custom-tools)
10. [Error Handling](#error-handling)

---

## 🏗️ Core Architecture

The WormGPT Hive Mind follows a hierarchical architecture:

```
┌─────────────────────────────────────┐
│       Queen Orchestrator            │
│  (Planning & Delegation)            │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐ ┌─────▼──────┐
│   Drones    │ │   Tools    │
│ (Execution) │ │ (Actions)  │
└─────────────┘ └────────────┘
```

**Key Principles:**
- **Queen** plans missions and delegates to drones
- **Drones** execute specialized tasks using tools
- **Tools** provide low-level functionality (file I/O, web requests, etc.)
- **Registry** manages all drones and tools centrally
- **State Manager** persists mission history

---

## 👑 Queen Orchestrator API

### **Class: `QueenOrchestrator`**

**Location**: `wormgpt_hive/queen/orchestrator.py`

**Description**: The supreme orchestrator that plans missions, delegates tasks to drones, reflects on failures, and self-corrects.

### Constructor

```python
QueenOrchestrator(registry: DroneRegistry, state_manager: StateManager)
```

**Parameters:**
- `registry` (DroneRegistry): Registry containing all available drones and tools
- `state_manager` (StateManager): Manager for persistent state storage

**Example:**
```python
from wormgpt_hive.drones.base_drone import DroneRegistry
from wormgpt_hive.queen.orchestrator import QueenOrchestrator
from wormgpt_hive.shared.state_manager import StateManager

registry = DroneRegistry()
state_manager = StateManager(state_file="agent_state.json")
queen = QueenOrchestrator(registry, state_manager)
```

---

### **Method: `execute_mission()`**

```python
def execute_mission(
    self,
    goal: str,
    verbose: bool = True
) -> Dict[str, Any]
```

**Description**: Plans and executes a complete mission to achieve the specified goal.

**Parameters:**
- `goal` (str): The mission objective in natural language
- `verbose` (bool): Whether to print detailed execution logs (default: `True`)

**Returns:**
```python
{
    "success": bool,           # Whether mission succeeded
    "data": Any,               # Mission result data (if successful)
    "error": str,              # Error message (if failed)
    "details": str,            # Additional error details (if failed)
    "mission": {               # Mission metadata
        "goal": str,
        "status": str,         # "planning" | "executing" | "completed" | "failed"
        "steps": [             # List of MissionStep dictionaries
            {
                "step_id": int,
                "action": str,
                "parameters": dict,
                "reasoning": str,
                "status": str,
                "observation": str,
                "result": Any,
                "timestamp": str
            },
            ...
        ],
        "result": Any
    }
}
```

**Example:**
```python
result = queen.execute_mission(
    goal="Search for Python 3.12 features and create a summary file",
    verbose=True
)

if result["success"]:
    print(f"Mission succeeded: {result['data']}")
else:
    print(f"Mission failed: {result['error']}")
```

---

### **Internal Methods** (Advanced)

#### `_generate_plan()`
```python
def _generate_plan(
    self,
    goal: str,
    capabilities: Dict[str, Any]
) -> List[MissionStep]
```

Generates a mission plan using LLM based on goal and available capabilities.

#### `_execute_step()`
```python
def _execute_step(self, step: MissionStep) -> Dict[str, Any]
```

Executes a single mission step by delegating to appropriate drone.

#### `_reflect_on_failure()`
```python
def _reflect_on_failure(self, failed_step: MissionStep) -> Dict[str, Any]
```

Analyzes failed step and determines corrective action (replan, request feedback, continue).

#### `_request_human_feedback()`
```python
def _request_human_feedback(self, question: str) -> str
```

Pauses mission execution to request human input for clarification.

---

## 🐝 Drone Interface

### **Base Class: `BaseDrone`**

**Location**: `wormgpt_hive/drones/base_drone.py`

**Description**: Abstract base class for all specialized drones.

### Constructor

```python
class BaseDrone(ABC):
    def __init__(self, name: str):
        self.name = name
        self.description = self.__doc__  # Extracted from class docstring
        self.tools = {}
```

---

### **Abstract Method: `execute()`**

```python
@abstractmethod
def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    pass
```

**Description**: Main execution method that must be implemented by all drones.

**Parameters:**
- `action` (str): The action to perform (e.g., "read_file", "execute_command", "web_search")
- `parameters` (Dict[str, Any]): Action-specific parameters

**Returns:**
```python
{
    "success": bool,
    "message": str,         # Human-readable success message
    "data": Any,            # Action result data (if successful)
    "error": str,           # Error message (if failed)
    "details": str,         # Additional error details (if failed)
    "drone": str            # Name of the drone that executed the action
}
```

---

### **Method: `get_capabilities()`**

```python
def get_capabilities(self) -> DroneCapability
```

**Description**: Returns structured capability description for the drone.

**Returns:** `DroneCapability` object containing:
- `name` (str): Drone name
- `description` (str): Capability description from docstring
- `methods` (List[Dict]): List of available methods and their signatures

---

### **Method: `register_tool()`**

```python
def register_tool(self, tool_name: str, tool_instance: Any):
    self.tools[tool_name] = tool_instance
```

**Description**: Registers a tool instance for use by the drone.

**Example:**
```python
from wormgpt_hive.drones.coder_drone import CoderDrone
from wormgpt_hive.tools.file_system import FileSystemTool

drone = CoderDrone()
file_tool = FileSystemTool()
drone.register_tool("file_system", file_tool)
```

---

### **Available Drones**

| Drone Class | File | Key Actions |
|-------------|------|-------------|
| `CoderDrone` | `drones/coder_drone.py` | `read_file`, `write_file`, `list_files`, `delete_file`, `create_directory` |
| `ShellDrone` | `drones/shell_drone.py` | `execute_command`, `execute_script` |
| `ResearchDrone` | `drones/research_drone.py` | `web_search`, `fetch_content`, `search_and_summarize` |
| `SecurityDrone` | `drones/security_drone.py` | `analyze_contract`, `generate_poc_plan`, `write_poc_exploit`, `full_security_audit` |
| `PolyglotDrone` | `drones/polyglot_drone.py` | `execute_code`, `generate_and_execute` |
| `ToolMakerDrone` | `drones/tool_maker_drone.py` | `create_tool`, `analyze_code`, `modify_code` |
| `OPSECDrone` | `drones/opsec_drone.py` | `check_tor_status`, `get_ip_address`, `anonymous_request` |

---

## 🛠️ Tool Interface

### **Base Class: `BaseTool`**

**Location**: `wormgpt_hive/tools/base_tool.py`

**Description**: Abstract base class for all tools.

### Constructor

```python
class BaseTool(ABC):
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = self.__doc__
```

---

### **Abstract Method: `execute()`**

```python
@abstractmethod
def execute(self, **kwargs) -> Dict[str, Any]:
    pass
```

**Description**: Executes the tool's primary function with provided parameters.

**Returns:**
```python
{
    "success": bool,
    "message": str,
    "data": Any,         # Tool-specific result data
    "error": str,        # Error message (if failed)
    "details": str       # Additional error details (if failed)
}
```

---

### **Available Tools**

#### **FileSystemTool**
**Location**: `tools/file_system.py`

**Actions:**
- `read` - Read file contents
- `write` - Write content to file
- `list` - List files in directory
- `delete` - Delete a file
- `create_dir` - Create directory
- `exists` - Check if file exists

**Example:**
```python
from wormgpt_hive.tools.file_system import FileSystemTool

fs = FileSystemTool()

# Read file
result = fs.execute("read", file_path="config.txt")
if result["success"]:
    print(result["data"]["content"])

# Write file
result = fs.execute("write", file_path="output.txt", content="Hello World")

# List files
result = fs.execute("list", directory="./", pattern="*.py", recursive=True)
```

---

#### **ShellExecutorTool**
**Location**: `tools/shell_executor.py`

**Methods:**
- `execute(command, cwd=None, timeout=30, use_tor=False)` - Run shell command
- `execute_script(script_content, script_type, cwd=None)` - Run script

**Example:**
```python
from wormgpt_hive.tools.shell_executor import ShellExecutorTool

shell = ShellExecutorTool()

# Execute command
result = shell.execute(command="ls -la", cwd="/tmp")
print(result["data"]["stdout"])

# Execute Python script
result = shell.execute_script(
    script_content="print('Hello from Python')",
    script_type="python"
)
```

---

#### **GoogleSearchTool**
**Location**: `tools/google_search.py`

**Methods:**
- `search(query, max_results=5, region="wt-wt")` - Search via DuckDuckGo

**Example:**
```python
from wormgpt_hive.tools.google_search import GoogleSearchTool

search = GoogleSearchTool(rate_limit_delay=1.0)
result = search.search("Python tutorials", max_results=5)

for item in result["data"]["results"]:
    print(f"{item['title']}: {item['link']}")
```

---

#### **WebBrowserTool**
**Location**: `tools/web_browser.py`

**Methods:**
- `fetch(url, parse_content=True, use_tor=False)` - Fetch and parse web content

**Example:**
```python
from wormgpt_hive.tools.web_browser import WebBrowserTool

browser = WebBrowserTool()
result = browser.fetch("https://example.com", parse_content=True)

print(result["data"]["title"])
print(result["data"]["text"][:500])
```

---

#### **SecurityAnalyzerTool**
**Location**: `tools/security_analyzer.py`

**Actions:**
- `analyze_file` - Analyze Solidity contract with Slither
- `get_vulnerability_report` - Generate formatted report
- `check_slither_available` - Verify Slither installation

**Example:**
```python
from wormgpt_hive.tools.security_analyzer import SecurityAnalyzerTool

analyzer = SecurityAnalyzerTool()

# Analyze contract
result = analyzer.execute("analyze_file", file_path="contract.sol")

print(f"Total issues: {result['data']['total_issues']}")
for vuln in result["data"]["vulnerabilities"]:
    print(f"- {vuln['check']}: {vuln['impact']}")
```

---

#### **PolyglotCodeInterpreterTool**
**Location**: `tools/polyglot_code_interpreter.py`

**Supported Languages:**
- Python
- Node.js
- Go
- Rust
- Bash

**Methods:**
- `execute(code, language, timeout=30)` - Execute code in specified language

**Example:**
```python
from wormgpt_hive.tools.polyglot_code_interpreter import PolyglotCodeInterpreterTool

interpreter = PolyglotCodeInterpreterTool()

# Execute Node.js
result = interpreter.execute(
    code="console.log('Hello from Node.js'); console.log(process.version);",
    language="nodejs"
)

print(result["data"]["output"])
```

---

#### **TorProxyTool**
**Location**: `tools/tor_proxy.py`

**Methods:**
- `check_tor_connection()` - Verify Tor service is running
- `get_tor_ip()` - Get current Tor exit node IP
- `make_tor_request(url, method="GET", **kwargs)` - Make anonymized HTTP request

**Example:**
```python
from wormgpt_hive.tools.tor_proxy import TorProxyTool

tor = TorProxyTool()

# Check Tor status
status = tor.check_tor_connection()
print(f"Tor available: {status['data']['connected']}")

# Get Tor IP
ip_result = tor.get_tor_ip()
print(f"Tor IP: {ip_result['data']['ip']}")

# Make anonymous request
result = tor.make_tor_request("https://httpbin.org/ip")
print(result["data"]["content"])
```

---

## 💾 State Management

### **Class: `StateManager`**

**Location**: `wormgpt_hive/shared/state_manager.py`

**Description**: Manages persistent state storage with optional encryption.

### Constructor

```python
StateManager(state_file: str = "agent_state.json", encryption_key: Optional[str] = None)
```

**Parameters:**
- `state_file` (str): Path to state file
- `encryption_key` (Optional[str]): 32-byte hex key for AES encryption

---

### **Methods**

#### `save_state()`
```python
def save_state(self, state: Dict[str, Any]) -> bool
```

**Description**: Saves state to file (with encryption if key provided).

#### `load_state()`
```python
def load_state(self) -> Dict[str, Any]
```

**Description**: Loads state from file (decrypts if encrypted).

#### `add_mission_history()`
```python
def add_mission_history(self, mission: Dict[str, Any])
```

**Description**: Adds completed mission to history.

**Example:**
```python
from wormgpt_hive.shared.state_manager import StateManager

state_mgr = StateManager(state_file="custom_state.json")

# Load existing state
state = state_mgr.load_state()

# Add mission
state_mgr.add_mission_history({
    "goal": "Test mission",
    "status": "completed",
    "steps": []
})

# Save state
state_mgr.save_state(state)
```

---

## 🔄 Dynamic Loader

### **Class: `DynamicLoader`**

**Location**: `wormgpt_hive/shared/dynamic_loader.py`

**Description**: Discovers and loads drones/tools dynamically at runtime.

### **Methods**

#### `discover_and_register_all()`
```python
def discover_and_register_all(self, registry: DroneRegistry)
```

**Description**: Auto-discovers all drones and tools, registers them in the registry.

**Example:**
```python
from wormgpt_hive.drones.base_drone import DroneRegistry
from wormgpt_hive.shared.dynamic_loader import DynamicLoader

registry = DroneRegistry()
loader = DynamicLoader()

# Automatically discover and register everything
loader.discover_and_register_all(registry)

# Now registry contains all drones and tools
print(f"Loaded {len(registry.get_all_drones())} drones")
print(f"Loaded {len(registry.get_all_tools())} tools")
```

---

## 📊 Data Models

### **DroneCapability**

```python
@dataclass
class DroneCapability:
    name: str
    description: str
    methods: List[Dict[str, Any]] = field(default_factory=list)
```

**Purpose**: Represents a drone's capabilities for discovery and planning.

---

### **MissionStep**

```python
@dataclass
class MissionStep:
    step_id: int
    action: str
    parameters: Dict[str, Any]
    reasoning: str
    status: str = "pending"  # "pending" | "completed" | "failed"
    observation: Optional[str] = None
    result: Optional[Any] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
```

**Methods:**
- `mark_completed(observation, result)` - Mark step as successful
- `mark_failed(observation, error)` - Mark step as failed
- `to_dict()` - Convert to dictionary

---

## 🛠️ Creating Custom Drones

### Step 1: Create Drone Class

```python
from typing import Any, Dict
from wormgpt_hive.drones.base_drone import BaseDrone

class MyCustomDrone(BaseDrone):
    """My Custom Drone: Brief description of capabilities."""
    
    def __init__(self):
        super().__init__("MyCustomDrone")
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if action == "my_action":
            return self._my_action(parameters)
        else:
            return self._error_response(f"Unknown action: {action}")
    
    def _my_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Validate required parameters
        error = self._validate_parameters(parameters, ["required_param"])
        if error:
            return self._error_response(error)
        
        # Get registered tool
        my_tool = self.tools.get("my_tool")
        if not my_tool:
            return self._error_response("MyTool not registered")
        
        # Execute tool
        result = my_tool.execute(param=parameters["required_param"])
        
        if result["success"]:
            return self._success_response(
                result["data"],
                f"Action completed: {parameters['required_param']}"
            )
        else:
            return result
```

### Step 2: Register Drone

```python
# Option 1: Automatic discovery (if placed in drones/ directory)
from wormgpt_hive.shared.dynamic_loader import DynamicLoader
loader = DynamicLoader()
loader.discover_and_register_all(registry)

# Option 2: Manual registration
from wormgpt_hive.drones.my_custom_drone import MyCustomDrone
drone = MyCustomDrone()
registry.register_drone(drone)
```

---

## 🔧 Creating Custom Tools

### Step 1: Create Tool Class

```python
from typing import Any, Dict
from wormgpt_hive.tools.base_tool import BaseTool

class MyCustomTool(BaseTool):
    """Brief description of tool functionality."""
    
    def __init__(self):
        super().__init__()
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            # Implement tool logic
            param = kwargs.get("param")
            if not param:
                return self._error_response("Missing required parameter: param")
            
            # Perform action
            result_data = self._do_something(param)
            
            return self._success_response(
                data=result_data,
                message="Tool executed successfully"
            )
        
        except Exception as e:
            return self._error_response(
                error=str(e),
                details=f"Exception in MyCustomTool: {type(e).__name__}"
            )
    
    def _do_something(self, param: Any) -> Any:
        # Implement core functionality
        return {"result": f"Processed {param}"}
```

### Step 2: Register Tool

```python
# Option 1: Automatic discovery (if placed in tools/ directory)
loader.discover_and_register_all(registry)

# Option 2: Manual registration
from wormgpt_hive.tools.my_custom_tool import MyCustomTool
tool = MyCustomTool()
registry.register_tool("my_custom_tool", tool)

# Register with specific drone
drone.register_tool("my_custom_tool", tool)
```

---

## ⚠️ Error Handling

### Standard Response Format

All drones and tools return standardized response dictionaries:

**Success Response:**
```python
{
    "success": True,
    "message": "Human-readable success message",
    "data": {
        # Result-specific data
    },
    "drone": "DroneName"  # Only for drones
}
```

**Error Response:**
```python
{
    "success": False,
    "error": "Primary error message",
    "details": "Additional error details (optional)",
    "drone": "DroneName"  # Only for drones
}
```

### Error Handling Best Practices

```python
# In drone/tool execute method
def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Validate parameters
        error = self._validate_parameters(parameters, ["required_param"])
        if error:
            return self._error_response(error)
        
        # Execute logic
        result = self._do_work(parameters)
        
        return self._success_response(result, "Work completed successfully")
    
    except FileNotFoundError as e:
        return self._error_response(
            error=f"File not found: {str(e)}",
            details="Ensure the file path is correct and file exists"
        )
    
    except Exception as e:
        return self._error_response(
            error=str(e),
            details=f"Unexpected error: {type(e).__name__}"
        )
```

---

## 🔐 Security Considerations

### Input Validation
Always validate user-provided parameters:
```python
def _validate_parameters(self, parameters: Dict[str, Any], required: List[str]) -> Optional[str]:
    missing = [param for param in required if param not in parameters]
    if missing:
        return f"Missing required parameters: {', '.join(missing)}"
    return None
```

### Sandboxing
Use isolated execution environments for code execution:
```python
# Polyglot interpreter runs code in sandbox/ directories
interpreter.execute(code=user_code, language="python")  # Runs in sandbox/python/
```

### Tor Anonymization
Route sensitive requests through Tor:
```python
# Use OPSEC-Drone for anonymized operations
result = opsec_drone.execute("anonymous_request", {"url": "https://target.com"})
```

### State Encryption
Encrypt sensitive state data:
```python
# Use encryption key from environment variable
state_mgr = StateManager(
    state_file="agent_state.json",
    encryption_key=os.getenv("STATE_ENCRYPTION_KEY")
)
```

---

## 📚 Additional Resources

- **Main README**: `../README.md` - Full project overview
- **Examples**: `../examples/` - Working code examples
- **Tests**: `../tests/` - Unit and integration tests
- **Phase Summaries**: `../PHASE*_SUMMARY.md` - Feature documentation

---

## 🤝 Support

For questions or issues with the API:
- Open an issue on GitHub (private repo)
- Review test files for usage examples
- Check example scripts in `examples/` directory

---

**Built with 🐝 by the WormGPT Hive Mind Development Team**

*Last Updated: January 2026*
