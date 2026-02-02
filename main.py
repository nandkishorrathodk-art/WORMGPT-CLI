#!/usr/bin/env python3
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from wormgpt_hive.drones.base_drone import DroneRegistry
from wormgpt_hive.drones.shell_drone import ShellDrone
from wormgpt_hive.drones.coder_drone import CoderDrone
from wormgpt_hive.drones.research_drone import ResearchDrone
from wormgpt_hive.drones.polyglot_drone import PolyglotDrone
from wormgpt_hive.drones.tool_maker_drone import ToolMakerDrone
from wormgpt_hive.drones.opsec_drone import OPSECDrone
from wormgpt_hive.drones.recon_drone import ReconDrone
from wormgpt_hive.tools.shell_executor import ShellExecutorTool
from wormgpt_hive.tools.file_system import FileSystemTool
from wormgpt_hive.tools.google_search import GoogleSearchTool
from wormgpt_hive.tools.web_browser import WebBrowserTool
from wormgpt_hive.tools.polyglot_code_interpreter import PolyglotCodeInterpreter
from wormgpt_hive.tools.tor_proxy import TorProxyTool
from wormgpt_hive.queen.orchestrator import QueenOrchestrator
from wormgpt_hive.queen.queen_registry import QueenRegistry
from wormgpt_hive.shared.state_manager import StateManager
from wormgpt_hive.shared.config import (
    FIREWORKS_API_KEY,
    TOR_PROXY_HOST,
    TOR_PROXY_PORT,
)

app = typer.Typer()
console = Console()

# Initialize DroneRegistry and QueenRegistry once globally
global_drone_registry = DroneRegistry()
global_queen_registry = QueenRegistry()


def initialize_hive(queen_id: str = "default_queen") -> tuple[QueenOrchestrator, DroneRegistry, QueenRegistry]:
    """Initialize the WormGPT Hive Mind with drones and tools."""

    if not FIREWORKS_API_KEY:
        console.print(
            "[bold red]ERROR:[/bold red] FIREWORKS_API_KEY not set in .env file"
        )
        raise typer.Exit(1)

    # Use global drone registry
    registry = global_drone_registry
    
    # Register tools only once
    if not registry.get_tool("shell_executor"):
        shell_tool = ShellExecutorTool()
        fs_tool = FileSystemTool()
        search_tool = GoogleSearchTool()
        browser_tool = WebBrowserTool()
        polyglot_tool = PolyglotCodeInterpreter()
        tor_tool = TorProxyTool(proxy_host=TOR_PROXY_HOST, proxy_port=TOR_PROXY_PORT)

        registry.register_tool("shell_executor", shell_tool)
        registry.register_tool("file_system", fs_tool)
        registry.register_tool("google_search", search_tool)
        registry.register_tool("web_browser", browser_tool)
        registry.register_tool("polyglot_interpreter", polyglot_tool)
        registry.register_tool("tor_proxy", tor_tool)

    # Register drones only once
    if not registry.get_drone("ShellDrone"):
        shell_drone = ShellDrone()
        shell_drone.register_tool("shell_executor", registry.get_tool("shell_executor"))
        registry.register_drone(shell_drone)

        coder_drone = CoderDrone()
        coder_drone.register_tool("file_system", registry.get_tool("file_system"))
        registry.register_drone(coder_drone)

        research_drone = ResearchDrone()
        research_drone.register_tool("google_search", registry.get_tool("google_search"))
        research_drone.register_tool("web_browser", registry.get_tool("web_browser"))
        registry.register_drone(research_drone)

        polyglot_drone = PolyglotDrone()
        polyglot_drone.register_tool("polyglot_interpreter", registry.get_tool("polyglot_interpreter"))
        # LLM client will be registered later inside queen creation for default_queen
        registry.register_drone(polyglot_drone)

        tool_maker_drone = ToolMakerDrone()
        # LLM client will be registered later inside queen creation for default_queen
        tool_maker_drone.register_tool("registry", registry)
        registry.register_drone(tool_maker_drone)

        opsec_drone = OPSECDrone()
        opsec_drone.register_tool("tor_proxy", registry.get_tool("tor_proxy"))
        opsec_drone.register_tool("shell_executor", registry.get_tool("shell_executor"))
        registry.register_drone(opsec_drone)

        recon_drone = ReconDrone()
        registry.register_drone(recon_drone)


    # Use global queen registry
    queen_registry = global_queen_registry

    # Create and register Queens only if they don't exist
    if not queen_registry.get_queen("default_queen"):
        state_manager_default = StateManager(file_path="agent_state_default.json")
        default_queen = QueenOrchestrator(
            registry, 
            state_manager_default, 
            queen_id="default_queen", 
            queen_registry=queen_registry,
            message_bus=queen_registry.message_bus
        )
        # Register LLM client for this queen's polyglot and tool_maker drones
        polyglot_drone = registry.get_drone("PolyglotDrone")
        if polyglot_drone:
            polyglot_drone.register_tool("llm_client", default_queen.client)
        tool_maker_drone = registry.get_drone("ToolMakerDrone")
        if tool_maker_drone:
            tool_maker_drone.register_tool("llm_client", default_queen.client)
        
        queen_registry.register_queen("default_queen", default_queen)

    if not queen_registry.get_queen("security_queen"):
        state_manager_security = StateManager(file_path="agent_state_security.json")
        security_queen = QueenOrchestrator(
            registry, 
            state_manager_security, 
            queen_id="security_queen", 
            queen_registry=queen_registry,
            message_bus=queen_registry.message_bus
        )
        # Register LLM client for this queen's polyglot and tool_maker drones
        polyglot_drone = registry.get_drone("PolyglotDrone")
        if polyglot_drone:
            polyglot_drone.register_tool("llm_client", security_queen.client)
        tool_maker_drone = registry.get_drone("ToolMakerDrone")
        if tool_maker_drone:
            tool_maker_drone.register_tool("llm_client", security_queen.client)

        queen_registry.register_queen("security_queen", security_queen)

    active_queen = queen_registry.get_queen(queen_id)
    if not active_queen:
        console.print(
            f"[bold red]ERROR:[/bold red] Queen with ID '{queen_id}' not found."
        )
        raise typer.Exit(1)

    return active_queen, registry, queen_registry


def print_banner():
    """Print the WormGPT Hive Mind banner."""
    banner = """
╦ ╦╔═╗╦═╗╔╦╗╔═╗╔═╗╔╦╗  ╦ ╦╦╦  ╦╔═╗  ╔╦╗╦╔╗╔╔╦╗
║║║║ ║╠╦╝║║║║ ╦╠═╝ ║   ╠═╣║╚╗╔╝║╣   ║║║║║║ ║║
╚╩╝╚═╝╩╚═╩ ╩╚═╝╩   ╩   ╩ ╩╩ ╚╝ ╚═╝  ╩ ╩╩╝╚╝═╩╝
    
    Advanced AI Agent Framework - Phase 7
    No Restrictions. Ruthless Efficiency. Maximum OPSEC.
    """
    console.print(Panel(banner, style="bold green", border_style="green"))


@app.command()
def mission(
    goal: Optional[str] = typer.Argument(None, help="Mission goal to execute"),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Interactive mode"
    ),
    queen_id: str = typer.Option(
        "default_queen", "--queen-id", "-q", help="ID of the Queen to use for the mission"
    ),
):
    """Execute a mission with the WormGPT Hive Mind."""

    print_banner()

    console.print(f"\n[bold cyan]Initializing Hive Mind for Queen '{queen_id}'...[/bold cyan]")
    queen, registry, queen_registry = initialize_hive(queen_id)

    capabilities = registry.get_capabilities_summary()
    drone_count = len(capabilities["drones"])
    tool_count = len(capabilities["tools"])

    console.print(f"[green]✓[/green] {drone_count} Drones online")
    console.print(f"[green]✓[/green] {tool_count} Tools loaded")
    console.print(f"[green]✓[/green] Queen '{queen.queen_id}' ready\n")

    if interactive or not goal:
        console.print("[bold yellow]INTERACTIVE MODE[/bold yellow]")
        console.print(
            "Enter mission goals (type 'exit' to quit, 'history' to view past missions, 'queens' to list queens)\n"
        )

        while True:
            goal = Prompt.ask(f"[bold cyan]Queen '{queen.queen_id}' Mission Goal[/bold cyan]")

            if goal.lower() == "exit":
                console.print(
                    "\n[bold green]Shutting down Hive Mind. Goodbye.[/bold green]"
                )
                break

            if goal.lower() == "history":
                history = queen.get_mission_history(5)
                if history:
                    console.print("\n[bold]Recent Missions:[/bold]")
                    for mission_entry in history:
                        status_color = (
                            "green"
                            if mission_entry.get("status") == "completed"
                            else "yellow"
                        )
                        console.print(
                            f"  [{status_color}]•[/{status_color}] {mission_entry.get('goal')}"
                        )
                else:
                    console.print("\n[yellow]No mission history available[/yellow]")
                console.print()
                continue
            
            if goal.lower() == "queens":
                console.print("\n[bold]Available Queens:[/bold]")
                for q_id, q_instance in queen_registry.get_all_queens().items():
                    console.print(f"  - [cyan]{q_id}[/cyan] ({'Active' if q_id == queen.queen_id else 'Inactive'})")
                console.print("\nTo switch active Queen, restart the mission with --queen-id <id>")
                continue


            if not goal.strip():
                continue

            try:
                result = queen.execute_mission(goal, verbose=True)

                if result["success"]:
                    console.print(
                        "\n[bold green]✓ Mission completed successfully[/bold green]\n"
                    )
                else:
                    console.print(
                        "\n[bold yellow]⚠ Mission completed with errors[/bold yellow]\n"
                    )
                
                messages = queen.receive_messages({})
                if messages.get("messages"):
                    console.print("\n[bold]Received Messages:[/bold]")
                    for msg in messages["messages"]:
                        console.print(f"  - {msg}")

            except KeyboardInterrupt:
                console.print("\n\n[yellow]Mission interrupted by user[/yellow]\n")
                continue
            except Exception as e:
                console.print(f"\n[bold red]ERROR:[/bold red] {str(e)}\n")
                continue
    else:
        console.print(f"[bold]MISSION:[/bold] {goal}\n")

        try:
            result = queen.execute_mission(goal, verbose=True)

            if result["success"]:
                console.print(
                    "\n[bold green]✓ Mission completed successfully[/bold green]"
                )
                raise typer.Exit(0)
            else:
                console.print(
                    "\n[bold yellow]⚠ Mission completed with errors[/bold yellow]"
                )
                raise typer.Exit(1)

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Mission interrupted by user[/yellow]")
            raise typer.Exit(130)
        except Exception as e:
            console.print(f"\n[bold red]FATAL ERROR:[/bold red] {str(e)}")
            raise typer.Exit(1)


@app.command()
def list_capabilities(
    queen_id: str = typer.Option(
        "default_queen", "--queen-id", "-q", help="ID of the Queen whose capabilities to list"
    ),
):
    """List all available drones and tools for a specific Queen."""

    console.print(f"\n[bold cyan]Initializing Hive Mind for Queen '{queen_id}'...[/bold cyan]")
    queen, registry, queen_registry = initialize_hive(queen_id)

    capabilities = registry.get_capabilities_summary()

    console.print(f"\n[bold]CAPABILITIES for Queen '{queen.queen_id}':[/bold]")
    console.print("\n[bold]AVAILABLE DRONES:[/bold]")
    for drone_name, drone_info in capabilities["drones"].items():
        console.print(f"\n[green]• {drone_name}[/green]")
        console.print(f"  {drone_info['description']}")
        if drone_info.get("methods"):
            console.print("  [dim]Methods:[/dim]")
            for method in drone_info["methods"]:
                params = ", ".join([f"{p['name']}:{p['type']}" + ("?" if p.get("optional") else "") for p in method["parameters"]])
                console.print(f"    - {method.get('name', 'unknown')}({params})")

    console.print("\n[bold]AVAILABLE TOOLS:[/bold]")
    for tool_name, tool_info in capabilities["tools"].items():
        console.print(f"\n[green]• {tool_name}[/green]")
        if isinstance(tool_info, dict):
            console.print(f"  {tool_info.get('description', 'No description')}")

    console.print("\n[bold]Available Queens:[/bold]")
    for q_id, q_instance in queen_registry.get_all_queens().items():
        console.print(f"  - [cyan]{q_id}[/cyan] ({'Active' if q_id == queen.queen_id else 'Inactive'})")
    
    console.print()


@app.command()
def history(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of missions to show"),
    queen_id: str = typer.Option(
        "default_queen", "--queen-id", "-q", help="ID of the Queen whose mission history to view"
    ),
):
    """View mission history for a specific Queen."""

    console.print(f"\n[bold cyan]Initializing Hive Mind for Queen '{queen_id}'...[/bold cyan]")
    queen, _, _ = initialize_hive(queen_id) # Only need the queen object

    missions = queen.get_mission_history(limit)

    if not missions:
        console.print(f"\n[yellow]No mission history available for Queen '{queen.queen_id}'[/yellow]\n")
        return

    console.print(f"\n[bold]Last {len(missions)} Missions for Queen '{queen.queen_id}':[/bold]\n")

    for mission_entry in missions:
        status_color = "green" if mission_entry.get("status") == "completed" else "yellow"
        console.print(f"[{status_color}]Mission #{mission_entry.get('id')}[/{status_color}]")
        console.print(f"  Goal: {mission_entry.get('goal')}")
        console.print(f"  Status: {mission_entry.get('status')}")
        console.print(f"  Steps: {len(mission_entry.get('steps', []))}")
        console.print(f"  Time: {mission_entry.get('timestamp', 'Unknown')}")
        console.print()


if __name__ == "__main__":
    app()
