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
from wormgpt_hive.tools.shell_executor import ShellExecutorTool
from wormgpt_hive.tools.file_system import FileSystemTool
from wormgpt_hive.tools.google_search import GoogleSearchTool
from wormgpt_hive.tools.web_browser import WebBrowserTool
from wormgpt_hive.tools.polyglot_code_interpreter import PolyglotCodeInterpreter
from wormgpt_hive.tools.tor_proxy import TorProxyTool
from wormgpt_hive.queen.orchestrator import QueenOrchestrator
from wormgpt_hive.shared.state_manager import StateManager
from wormgpt_hive.shared.config import OPENROUTER_API_KEY, TOR_PROXY_HOST, TOR_PROXY_PORT

app = typer.Typer()
console = Console()


def initialize_hive() -> tuple[QueenOrchestrator, DroneRegistry]:
    """Initialize the WormGPT Hive Mind with drones and tools."""
    
    if not OPENROUTER_API_KEY:
        console.print("[bold red]ERROR:[/bold red] OPENROUTER_API_KEY not set in .env file")
        raise typer.Exit(1)
    
    registry = DroneRegistry()
    
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
    
    state_manager = StateManager()
    
    queen = QueenOrchestrator(registry, state_manager)
    
    polyglot_drone = PolyglotDrone()
    polyglot_drone.register_tool("polyglot_interpreter", polyglot_tool)
    polyglot_drone.register_tool("llm_client", queen.client)
    registry.register_drone(polyglot_drone)
    
    tool_maker_drone = ToolMakerDrone()
    tool_maker_drone.register_tool("llm_client", queen.client)
    tool_maker_drone.register_tool("registry", registry)
    registry.register_drone(tool_maker_drone)
    
    opsec_drone = OPSECDrone()
    opsec_drone.register_tool("tor_proxy", tor_tool)
    opsec_drone.register_tool("shell_executor", shell_tool)
    registry.register_drone(opsec_drone)
    
    return queen, registry


def print_banner():
    """Print the WormGPT Hive Mind banner."""
    banner = """
╦ ╦╔═╗╦═╗╔╦╗╔═╗╔═╗╔╦╗  ╦ ╦╦╦  ╦╔═╗  ╔╦╗╦╔╗╔╔╦╗
║║║║ ║╠╦╝║║║║ ╦╠═╝ ║   ╠═╣║╚╗╔╝║╣   ║║║║║║ ║║
╚╩╝╚═╝╩╚═╩ ╩╚═╝╩   ╩   ╩ ╩╩ ╚╝ ╚═╝  ╩ ╩╩╝╚╝═╩╝
    
    Advanced AI Agent Framework - Phase 5
    No Restrictions. Ruthless Efficiency.
    """
    console.print(Panel(banner, style="bold green", border_style="green"))


@app.command()
def mission(
    goal: Optional[str] = typer.Argument(None, help="Mission goal to execute"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode")
):
    """Execute a mission with the WormGPT Hive Mind."""
    
    print_banner()
    
    console.print("\n[bold cyan]Initializing Hive Mind...[/bold cyan]")
    queen, registry = initialize_hive()
    
    capabilities = registry.get_capabilities_summary()
    drone_count = len(capabilities["drones"])
    tool_count = len(capabilities["tools"])
    
    console.print(f"[green]✓[/green] {drone_count} Drones online")
    console.print(f"[green]✓[/green] {tool_count} Tools loaded")
    console.print(f"[green]✓[/green] Queen ready\n")
    
    if interactive or not goal:
        console.print("[bold yellow]INTERACTIVE MODE[/bold yellow]")
        console.print("Enter mission goals (type 'exit' to quit, 'history' to view past missions)\n")
        
        while True:
            goal = Prompt.ask("[bold cyan]Mission Goal[/bold cyan]")
            
            if goal.lower() == "exit":
                console.print("\n[bold green]Shutting down Hive Mind. Goodbye.[/bold green]")
                break
            
            if goal.lower() == "history":
                history = queen.get_mission_history(5)
                if history:
                    console.print("\n[bold]Recent Missions:[/bold]")
                    for mission in history:
                        status_color = "green" if mission.get("status") == "completed" else "yellow"
                        console.print(f"  [{status_color}]•[/{status_color}] {mission.get('goal')}")
                else:
                    console.print("\n[yellow]No mission history available[/yellow]")
                console.print()
                continue
            
            if not goal.strip():
                continue
            
            try:
                result = queen.execute_mission(goal, verbose=True)
                
                if result["success"]:
                    console.print("\n[bold green]✓ Mission completed successfully[/bold green]\n")
                else:
                    console.print("\n[bold yellow]⚠ Mission completed with errors[/bold yellow]\n")
            
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
                console.print("\n[bold green]✓ Mission completed successfully[/bold green]")
                raise typer.Exit(0)
            else:
                console.print("\n[bold yellow]⚠ Mission completed with errors[/bold yellow]")
                raise typer.Exit(1)
        
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Mission interrupted by user[/yellow]")
            raise typer.Exit(130)
        except Exception as e:
            console.print(f"\n[bold red]FATAL ERROR:[/bold red] {str(e)}")
            raise typer.Exit(1)


@app.command()
def list_capabilities():
    """List all available drones and tools."""
    
    console.print("\n[bold cyan]Initializing Hive Mind...[/bold cyan]")
    _, registry = initialize_hive()
    
    capabilities = registry.get_capabilities_summary()
    
    console.print("\n[bold]AVAILABLE DRONES:[/bold]")
    for drone_name, drone_info in capabilities["drones"].items():
        console.print(f"\n[green]• {drone_name}[/green]")
        console.print(f"  {drone_info['description']}")
        if drone_info.get("methods"):
            console.print("  [dim]Methods:[/dim]")
            for method in drone_info["methods"]:
                console.print(f"    - {method.get('name', 'unknown')}")
    
    console.print("\n[bold]AVAILABLE TOOLS:[/bold]")
    for tool_name, tool_info in capabilities["tools"].items():
        console.print(f"\n[green]• {tool_name}[/green]")
        if isinstance(tool_info, dict):
            console.print(f"  {tool_info.get('description', 'No description')}")
    
    console.print()


@app.command()
def history(limit: int = typer.Option(10, "--limit", "-n", help="Number of missions to show")):
    """View mission history."""
    
    state_manager = StateManager()
    missions = state_manager.get_mission_history(limit)
    
    if not missions:
        console.print("\n[yellow]No mission history available[/yellow]\n")
        return
    
    console.print(f"\n[bold]Last {len(missions)} Missions:[/bold]\n")
    
    for mission in missions:
        status_color = "green" if mission.get("status") == "completed" else "yellow"
        console.print(f"[{status_color}]Mission #{mission.get('id')}[/{status_color}]")
        console.print(f"  Goal: {mission.get('goal')}")
        console.print(f"  Status: {mission.get('status')}")
        console.print(f"  Steps: {len(mission.get('steps', []))}")
        console.print(f"  Time: {mission.get('timestamp', 'Unknown')}")
        console.print()


if __name__ == "__main__":
    app()
