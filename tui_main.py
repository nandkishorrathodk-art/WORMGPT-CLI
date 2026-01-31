#!/usr/bin/env python3
"""WormGPT Hive Mind - Advanced Textual TUI"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, Input, Button, RichLog,
    DataTable, Label, ProgressBar
)
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.worker import Worker, WorkerState
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

from wormgpt_hive.drones.base_drone import DroneRegistry
from wormgpt_hive.drones.shell_drone import ShellDrone
from wormgpt_hive.drones.coder_drone import CoderDrone
from wormgpt_hive.drones.research_drone import ResearchDrone
from wormgpt_hive.drones.polyglot_drone import PolyglotDrone
from wormgpt_hive.drones.tool_maker_drone import ToolMakerDrone
from wormgpt_hive.drones.security_drone import SecurityDrone
from wormgpt_hive.tools.shell_executor import ShellExecutorTool
from wormgpt_hive.tools.file_system import FileSystemTool
from wormgpt_hive.tools.google_search import GoogleSearchTool
from wormgpt_hive.tools.web_browser import WebBrowserTool
from wormgpt_hive.tools.polyglot_code_interpreter import PolyglotCodeInterpreter
from wormgpt_hive.tools.security_analyzer import SecurityAnalyzerTool
from wormgpt_hive.queen.orchestrator import QueenOrchestrator
from wormgpt_hive.shared.state_manager import StateManager
from wormgpt_hive.shared.config import OPENROUTER_API_KEY


class HumanFeedbackDialog(ModalScreen[str]):
    """Modal dialog for requesting human feedback."""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, question: str, **kwargs):
        super().__init__(**kwargs)
        self.question = question
    
    def compose(self) -> ComposeResult:
        with Container(classes="dialog"):
            yield Label(f"🐝 QUEEN REQUIRES YOUR GUIDANCE", classes="dialog-title")
            yield Label(self.question, classes="dialog-content")
            yield Input(placeholder="Enter your response...", id="feedback-input")
            with Horizontal():
                yield Button("Submit", variant="primary", id="submit-btn")
                yield Button("Cancel", id="cancel-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-btn":
            feedback_input = self.query_one("#feedback-input", Input)
            self.dismiss(feedback_input.value)
        elif event.button.id == "cancel-btn":
            self.dismiss("")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)


class MissionHistoryScreen(Screen):
    """Screen showing mission history."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Back"),
    ]
    
    def __init__(self, state_manager: StateManager, **kwargs):
        super().__init__(**kwargs)
        self.state_manager = state_manager
    
    def compose(self) -> ComposeResult:
        yield Header()
        with ScrollableContainer():
            yield Label("📜 MISSION HISTORY", classes="dialog-title")
            yield DataTable(id="history-table")
        yield Footer()
    
    def on_mount(self) -> None:
        table = self.query_one("#history-table", DataTable)
        table.add_columns("ID", "Goal", "Status", "Steps", "Time")
        
        missions = self.state_manager.get_mission_history(20)
        for mission in missions:
            table.add_row(
                str(mission.get("id", "?")),
                mission.get("goal", "Unknown")[:50],
                mission.get("status", "unknown"),
                str(len(mission.get("steps", []))),
                mission.get("timestamp", "Unknown")[:19]
            )
    
    def action_dismiss(self) -> None:
        self.app.pop_screen()


class WormGPTHiveTUI(App):
    """Advanced Textual TUI for WormGPT Hive Mind."""
    
    CSS_PATH = "main.css"
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+h", "show_history", "History"),
        Binding("ctrl+d", "toggle_dark", "Toggle Theme"),
    ]
    
    def __init__(self):
        super().__init__()
        self.queen: Optional[QueenOrchestrator] = None
        self.registry: Optional[DroneRegistry] = None
        self.state_manager: Optional[StateManager] = None
        self.current_worker: Optional[Worker] = None
        self.mission_callback = None
        self.awaiting_feedback = False
        self.feedback_question = ""
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, id="header")
        
        with Container(id="main-container"):
            with Vertical(id="mission-log-panel"):
                yield Label("📋 MISSION LOG", classes="dialog-title")
                yield RichLog(id="mission-log", highlight=True, markup=True)
            
            with Vertical(id="drone-status-panel"):
                yield Label("🐝 DRONE STATUS", classes="dialog-title")
                yield RichLog(id="drone-status", highlight=True, markup=True)
            
            with Vertical(id="memory-panel"):
                yield Label("🧠 MEMORY", classes="dialog-title")
                yield RichLog(id="memory", highlight=True, markup=True)
        
        with Container(id="footer"):
            yield Input(placeholder="Enter mission goal...", id="mission-input")
            with Horizontal():
                yield Button("Execute Mission", variant="primary", id="execute-btn")
                yield Button("History", id="history-btn")
                yield Button("Capabilities", id="cap-btn")
                yield ProgressBar(total=100, show_eta=False, id="progress")
    
    def on_mount(self) -> None:
        """Initialize the hive on startup."""
        self.title = "WormGPT Hive Mind - Matrix Terminal"
        self.sub_title = "No Restrictions. Ruthless Efficiency."
        
        mission_log = self.query_one("#mission-log", RichLog)
        mission_log.write(Panel.fit(
            "[bold green]WormGPT Hive Mind - Phase 8\n"
            "Advanced Textual TUI Active[/bold green]",
            border_style="green"
        ))
        
        self.initialize_hive()
    
    def initialize_hive(self) -> None:
        """Initialize the WormGPT Hive Mind."""
        mission_log = self.query_one("#mission-log", RichLog)
        
        try:
            if not OPENROUTER_API_KEY:
                mission_log.write("[bold red]ERROR: OPENROUTER_API_KEY not set in .env file[/bold red]")
                return
            
            mission_log.write("[cyan]Initializing Hive Mind...[/cyan]")
            
            self.registry = DroneRegistry()
            
            shell_tool = ShellExecutorTool()
            fs_tool = FileSystemTool()
            search_tool = GoogleSearchTool()
            browser_tool = WebBrowserTool()
            polyglot_tool = PolyglotCodeInterpreter()
            security_tool = SecurityAnalyzerTool()
            
            self.registry.register_tool("shell_executor", shell_tool)
            self.registry.register_tool("file_system", fs_tool)
            self.registry.register_tool("google_search", search_tool)
            self.registry.register_tool("web_browser", browser_tool)
            self.registry.register_tool("polyglot_interpreter", polyglot_tool)
            self.registry.register_tool("security_analyzer", security_tool)
            
            shell_drone = ShellDrone()
            shell_drone.register_tool("shell_executor", shell_tool)
            self.registry.register_drone(shell_drone)
            
            coder_drone = CoderDrone()
            coder_drone.register_tool("file_system", fs_tool)
            self.registry.register_drone(coder_drone)
            
            research_drone = ResearchDrone()
            research_drone.register_tool("google_search", search_tool)
            research_drone.register_tool("web_browser", browser_tool)
            self.registry.register_drone(research_drone)
            
            self.state_manager = StateManager()
            self.queen = QueenOrchestrator(self.registry, self.state_manager)
            
            polyglot_drone = PolyglotDrone()
            polyglot_drone.register_tool("polyglot_interpreter", polyglot_tool)
            polyglot_drone.register_tool("llm_client", self.queen.client)
            self.registry.register_drone(polyglot_drone)
            
            tool_maker_drone = ToolMakerDrone()
            tool_maker_drone.register_tool("llm_client", self.queen.client)
            tool_maker_drone.register_tool("registry", self.registry)
            self.registry.register_drone(tool_maker_drone)
            
            security_drone = SecurityDrone()
            security_drone.register_tool("security_analyzer", security_tool)
            security_drone.register_tool("llm_client", self.queen.client)
            security_drone.register_tool("file_system", fs_tool)
            self.registry.register_drone(security_drone)
            
            capabilities = self.registry.get_capabilities_summary()
            drone_count = len(capabilities["drones"])
            tool_count = len(capabilities["tools"])
            
            mission_log.write(f"[green]✓ {drone_count} Drones online[/green]")
            mission_log.write(f"[green]✓ {tool_count} Tools loaded[/green]")
            mission_log.write(f"[green]✓ Queen ready[/green]\n")
            
            self.update_drone_status()
            self.update_memory()
            
        except Exception as e:
            mission_log.write(f"[bold red]Initialization failed: {str(e)}[/bold red]")
    
    def update_drone_status(self) -> None:
        """Update the drone status panel."""
        if not self.registry:
            return
        
        drone_status = self.query_one("#drone-status", RichLog)
        drone_status.clear()
        
        capabilities = self.registry.get_capabilities_summary()
        
        table = Table(title="Active Drones", border_style="green")
        table.add_column("Drone", style="cyan")
        table.add_column("Status", style="green")
        
        for drone_name, drone_info in capabilities["drones"].items():
            table.add_row(
                drone_name,
                "[green]READY[/green]" if drone_info else "[dim]IDLE[/dim]"
            )
        
        drone_status.write(table)
    
    def update_memory(self) -> None:
        """Update the memory panel with recent missions."""
        if not self.state_manager:
            return
        
        memory = self.query_one("#memory", RichLog)
        memory.clear()
        
        missions = self.state_manager.get_mission_history(5)
        
        if missions:
            table = Table(title="Recent Missions", border_style="green")
            table.add_column("Goal", style="cyan", width=30)
            table.add_column("Status", style="yellow")
            
            for mission in missions:
                status = mission.get("status", "unknown")
                status_style = "[green]" if status == "completed" else "[yellow]"
                goal = mission.get("goal", "Unknown")[:30]
                table.add_row(goal, f"{status_style}{status}[/]")
            
            memory.write(table)
        else:
            memory.write("[dim]No mission history available[/dim]")
    
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "execute-btn":
            await self.execute_mission()
        elif event.button.id == "history-btn":
            await self.action_show_history()
        elif event.button.id == "cap-btn":
            self.show_capabilities()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle mission input submission."""
        if event.input.id == "mission-input":
            await self.execute_mission()
    
    async def execute_mission(self) -> None:
        """Execute a mission based on user input."""
        mission_input = self.query_one("#mission-input", Input)
        goal = mission_input.value.strip()
        
        if not goal:
            return
        
        mission_input.value = ""
        
        if not self.queen:
            mission_log = self.query_one("#mission-log", RichLog)
            mission_log.write("[red]Hive not initialized![/red]")
            return
        
        mission_log = self.query_one("#mission-log", RichLog)
        mission_log.write(f"\n[bold cyan]{'='*60}[/bold cyan]")
        mission_log.write(f"[bold green]🐝 QUEEN: Initiating new mission[/bold green]")
        mission_log.write(f"[bold]GOAL:[/bold] {goal}")
        mission_log.write(f"[bold cyan]{'='*60}[/bold cyan]\n")
        
        self.current_worker = self.run_worker(
            self.run_mission(goal),
            exclusive=True
        )
    
    async def run_mission(self, goal: str) -> None:
        """Run mission in background worker."""
        mission_log = self.query_one("#mission-log", RichLog)
        progress = self.query_one("#progress", ProgressBar)
        
        try:
            modified_queen = ModifiedQueenOrchestrator(
                self.queen,
                self.log_mission_update,
                self.request_human_feedback_async
            )
            
            result = await asyncio.to_thread(
                modified_queen.execute_mission,
                goal,
                verbose=False
            )
            
            if result["success"]:
                mission_log.write(f"\n[bold green]✓ Mission completed successfully[/bold green]\n")
            else:
                mission_log.write(f"\n[bold yellow]⚠ Mission completed with errors[/bold yellow]\n")
            
            progress.update(total=100, progress=100)
            self.update_memory()
            
        except Exception as e:
            mission_log.write(f"\n[bold red]FATAL ERROR: {str(e)}[/bold red]\n")
            progress.update(total=100, progress=0)
    
    def log_mission_update(self, update_type: str, data: Dict[str, Any]) -> None:
        """Callback for mission updates."""
        mission_log = self.query_one("#mission-log", RichLog)
        progress = self.query_one("#progress", ProgressBar)
        
        if update_type == "planning":
            mission_log.write(f"[cyan]📋 QUEEN: Planning mission...[/cyan]")
        
        elif update_type == "plan_created":
            steps = data.get("steps", 0)
            mission_log.write(f"[cyan]📋 QUEEN: Mission plan created with {steps} steps[/cyan]\n")
            progress.update(total=steps * 100, progress=0)
        
        elif update_type == "step_start":
            step_id = data.get("step_id", "?")
            action = data.get("action", "Unknown")
            reasoning = data.get("reasoning", "")
            mission_log.write(f"\n[bold cyan]{'─'*60}[/bold cyan]")
            mission_log.write(f"[bold]STEP {step_id}:[/bold] {action}")
            mission_log.write(f"[dim]REASONING:[/dim] {reasoning}")
            mission_log.write(f"[bold cyan]{'─'*60}[/bold cyan]")
        
        elif update_type == "step_complete":
            observation = data.get("observation", "")
            status = data.get("status", "unknown")
            step_num = data.get("step_num", 0)
            total_steps = data.get("total_steps", 1)
            
            if status == "completed":
                mission_log.write(f"[green]✓ SUCCESS:[/green] {observation}")
            else:
                mission_log.write(f"[red]✗ FAILED:[/red] {observation}")
            
            progress.update(progress=(step_num + 1) * 100)
        
        elif update_type == "reflection":
            mission_log.write(f"\n[yellow]🤔 QUEEN: Reflecting on failure...[/yellow]")
            next_action = data.get("next_action", "continue")
            mission_log.write(f"[yellow]Next action: {next_action}[/yellow]\n")
        
        elif update_type == "replan":
            mission_log.write(f"\n[cyan]🔄 QUEEN: Re-planning mission...[/cyan]\n")
    
    async def request_human_feedback_async(self, question: str) -> str:
        """Request human feedback through dialog."""
        result = await self.push_screen_wait(HumanFeedbackDialog(question))
        
        mission_log = self.query_one("#mission-log", RichLog)
        mission_log.write(f"\n[bold yellow]💬 HUMAN FEEDBACK:[/bold yellow] {result}\n")
        
        return result or "continue"
    
    def show_capabilities(self) -> None:
        """Show available capabilities."""
        if not self.registry:
            return
        
        mission_log = self.query_one("#mission-log", RichLog)
        mission_log.write("\n[bold cyan]AVAILABLE CAPABILITIES:[/bold cyan]\n")
        
        capabilities = self.registry.get_capabilities_summary()
        
        table = Table(title="Drones & Tools", border_style="green")
        table.add_column("Type", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description", style="white", width=40)
        
        for drone_name, drone_info in capabilities["drones"].items():
            table.add_row(
                "Drone",
                drone_name,
                drone_info.get("description", "")[:40]
            )
        
        for tool_name in capabilities["tools"].keys():
            table.add_row(
                "Tool",
                tool_name,
                ""
            )
        
        mission_log.write(table)
        mission_log.write("")
    
    async def action_show_history(self) -> None:
        """Show mission history screen."""
        if self.state_manager:
            await self.push_screen(MissionHistoryScreen(self.state_manager))
    
    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


class ModifiedQueenOrchestrator:
    """Wrapper around QueenOrchestrator to add callbacks."""
    
    def __init__(self, queen: QueenOrchestrator, log_callback, feedback_callback):
        self.queen = queen
        self.log_callback = log_callback
        self.feedback_callback = feedback_callback
    
    def execute_mission(self, goal: str, verbose: bool = False) -> Dict[str, Any]:
        """Execute mission with callbacks."""
        self.log_callback("planning", {})
        
        self.queen.current_mission = {
            "goal": goal,
            "status": "planning",
            "steps": [],
            "result": None
        }
        
        capabilities = self.queen.registry.get_capabilities_summary()
        plan = self.queen._generate_plan(goal, capabilities)
        
        if not plan:
            return {
                "success": False,
                "error": "Failed to generate mission plan",
                "mission": self.queen.current_mission
            }
        
        self.queen.mission_steps = plan
        self.queen.current_mission["steps"] = [step.to_dict() for step in plan]
        self.queen.current_mission["status"] = "executing"
        
        self.log_callback("plan_created", {"steps": len(plan)})
        
        for idx, step in enumerate(plan):
            self.queen.step_index = idx
            
            self.log_callback("step_start", {
                "step_id": step.step_id,
                "action": step.action,
                "reasoning": step.reasoning
            })
            
            self.queen._execute_step(step)
            
            self.log_callback("step_complete", {
                "status": step.status,
                "observation": step.observation,
                "step_num": idx,
                "total_steps": len(plan)
            })
            
            if step.status == "failed":
                reflection = self.queen._reflect_on_failure(step)
                
                if isinstance(reflection, dict):
                    self.log_callback("reflection", reflection)
                    
                    if reflection.get("next_action") == "request_human_feedback":
                        question = reflection.get("question", "How should I proceed?")
                        feedback = asyncio.run(self.feedback_callback(question))
                    
                    elif reflection.get("next_action") == "replan":
                        self.log_callback("replan", {})
                        revised_plan = reflection.get("revised_plan", [])
                        if revised_plan:
                            remaining_steps = self.queen._parse_plan_from_llm(revised_plan)
                            plan = plan[:idx+1] + remaining_steps
                            self.queen.mission_steps = plan
        
        self.queen.current_mission["status"] = "completed"
        
        success_count = sum(1 for s in plan if s.status == "completed")
        self.queen.current_mission["result"] = {
            "total_steps": len(plan),
            "successful_steps": success_count,
            "failed_steps": len(plan) - success_count
        }
        
        self.queen.state_manager.add_mission(self.queen.current_mission)
        
        return {
            "success": success_count == len(plan),
            "mission": self.queen.current_mission,
            "steps": [s.to_dict() for s in plan]
        }


if __name__ == "__main__":
    app = WormGPTHiveTUI()
    app.run()
