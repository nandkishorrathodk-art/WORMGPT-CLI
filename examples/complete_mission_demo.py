#!/usr/bin/env python3
"""
Complete Mission Demo - End-to-End Workflow

This comprehensive demo showcases the full WormGPT Hive Mind workflow:
1. Queen plans a complex multi-step mission
2. Multiple drones collaborate to achieve the goal
3. Demonstrates reflection, error handling, and state persistence

Mission Goal: Research the latest Python 3.12 features, create a summary file,
and write a simple Python script demonstrating one of the features.

Prerequisites:
- OpenRouter API key configured in .env
- Internet connection for web research
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wormgpt_hive.drones.base_drone import DroneRegistry
from wormgpt_hive.queen.orchestrator import QueenOrchestrator
from wormgpt_hive.shared.state_manager import StateManager
from wormgpt_hive.shared.dynamic_loader import DynamicLoader
from wormgpt_hive.shared.config import FIREWORKS_API_KEY
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


def check_prerequisites():
    console = Console()
    
    if not FIREWORKS_API_KEY or FIREWORKS_API_KEY == "your_openrouter_api_key_here":
        console.print(Panel(
            "[bold red]ERROR: OpenRouter API key not configured[/bold red]\n\n"
            "Please set your API key in the .env file:\n"
            "  FIREWORKS_API_KEY=\"sk-or-v1-YOUR_KEY_HERE\"",
            border_style="red"
        ))
        return False
    
    return True


def main():
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]WormGPT Hive Mind - Complete Mission Demo[/bold cyan]\n"
        "[dim]End-to-End Workflow with Queen Orchestration[/dim]",
        border_style="cyan"
    ))
    
    if not check_prerequisites():
        return
    
    console.print("\n[bold]Initializing Hive Mind...[/bold]")
    
    registry = DroneRegistry()
    state_manager = StateManager(state_file="agent_state_demo.json")
    
    loader = DynamicLoader()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading drones and tools...", total=None)
        loader.discover_and_register_all(registry)
        progress.update(task, completed=True)
    
    registered_drones = registry.get_all_drones()
    console.print(f"[green]✓[/green] Loaded {len(registered_drones)} drones")
    
    for drone_name in registered_drones:
        console.print(f"  • {drone_name}")
    
    console.print(f"\n[bold]Mission Goal:[/bold]")
    goal = (
        "Research the latest Python 3.12 features from the web, "
        "create a summary file called 'python312_summary.txt', "
        "and write a simple Python script called 'demo_feature.py' "
        "that demonstrates one of the new features."
    )
    console.print(Panel(goal, border_style="yellow"))
    
    queen = QueenOrchestrator(registry, state_manager)
    
    console.print("\n[bold cyan]🐝 Queen is planning the mission...[/bold cyan]\n")
    
    result = queen.execute_mission(goal, verbose=True)
    
    console.print("\n" + "=" * 70)
    
    if result["success"]:
        console.print(Panel(
            "[bold green]✓ Mission Successful![/bold green]\n\n"
            f"Result: {result.get('data', 'Mission completed')}",
            border_style="green"
        ))
        
        mission_data = result.get("mission", {})
        steps = mission_data.get("steps", [])
        
        console.print(f"\n[bold]Mission Statistics:[/bold]")
        console.print(f"  Total steps: {len(steps)}")
        completed = sum(1 for s in steps if s.get("status") == "completed")
        failed = sum(1 for s in steps if s.get("status") == "failed")
        console.print(f"  Completed: {completed}")
        console.print(f"  Failed: {failed}")
        
        output_dir = Path(__file__).parent.parent
        summary_file = output_dir / "python312_summary.txt"
        demo_file = output_dir / "demo_feature.py"
        
        console.print(f"\n[bold]Generated Files:[/bold]")
        if summary_file.exists():
            console.print(f"  [green]✓[/green] {summary_file}")
            console.print(f"    Size: {summary_file.stat().st_size} bytes")
        else:
            console.print(f"  [yellow]?[/yellow] {summary_file} [dim](not found)[/dim]")
        
        if demo_file.exists():
            console.print(f"  [green]✓[/green] {demo_file}")
            console.print(f"    Size: {demo_file.stat().st_size} bytes")
        else:
            console.print(f"  [yellow]?[/yellow] {demo_file} [dim](not found)[/dim]")
        
        state_file = Path("agent_state_demo.json")
        if state_file.exists():
            console.print(f"\n[bold]Persistent State:[/bold]")
            console.print(f"  [green]✓[/green] Mission saved to {state_file}")
            console.print(f"  [dim]The Queen will remember this mission in future sessions[/dim]")
        
    else:
        console.print(Panel(
            f"[bold red]✗ Mission Failed[/bold red]\n\n"
            f"Error: {result.get('error', 'Unknown error')}\n"
            f"Details: {result.get('details', 'No details available')}",
            border_style="red"
        ))
        
        console.print("\n[bold yellow]Troubleshooting:[/bold yellow]")
        console.print("  • Check your internet connection")
        console.print("  • Verify OpenRouter API key is valid")
        console.print("  • Ensure sufficient API credits")
        console.print("  • Review mission steps in verbose output above")
    
    console.print("\n" + "=" * 70)
    console.print("[dim]Demo complete. Check the files and agent_state_demo.json[/dim]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[yellow]Demo interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console = Console()
        console.print(f"\n[bold red]Unexpected Error:[/bold red] {str(e)}")
        
        import traceback
        console.print("\n[dim]Traceback:[/dim]")
        traceback.print_exc()
        
        sys.exit(1)
