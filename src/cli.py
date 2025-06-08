"""Command line interface for multi-agent framework"""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional

from .config.config_manager import ConfigManager

app = typer.Typer(help="Multi-Agent Framework CLI")
console = Console()

@app.command()
def init(
    name: str = typer.Argument(..., help="Project name"),
    framework: str = typer.Option("crewai", help="Framework to use (crewai, langgraph, autogen)")
):
    """Initialize a new multi-agent project"""
    console.print(f"[blue]Initializing new project:[/blue] {name}")
    console.print(f"[blue]Using framework:[/blue] {framework}")
    
    # Create project structure
    project_path = Path(name)
    project_path.mkdir(exist_ok=True)
    
    console.print("[green]Project initialized successfully![/green]")

@app.command()
def list_agents():
    """List all available agents"""
    try:
        config = ConfigManager()
        
        table = Table(title="Available Agents")
        table.add_column("Name", style="cyan")
        table.add_column("Role", style="magenta")
        table.add_column("Tools", style="green")
        
        for name, agent_def in config.agents.items():
            tools_str = ", ".join(agent_def.tools)
            table.add_row(name, agent_def.role, tools_str)
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error loading agents: {e}[/red]")

@app.command()
def run_workflow(
    workflow_name: str = typer.Argument(..., help="Workflow to execute"),
    task: str = typer.Option(..., help="Task description"),
    verbose: bool = typer.Option(False, help="Enable verbose output")
):
    """Run a multi-agent workflow"""
    console.print(f"[blue]Running workflow:[/blue] {workflow_name}")
    console.print(f"[blue]Task:[/blue] {task}")
    
    if workflow_name == "research":
        console.print("[green]Workflow completed![/green]")
        console.print("[blue]Results:[/blue] Simulated research results for demo")

@app.command()
def test(
    test_type: str = typer.Option("unit", help="Test type (unit, integration, behavioral)")
):
    """Run tests"""
    import subprocess
    
    console.print(f"[blue]Running {test_type} tests...[/blue]")
    
    cmd = ["pytest", f"tests/{test_type}", "-v"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        console.print("[green]All tests passed![/green]")
    else:
        console.print("[red]Some tests failed![/red]")
        console.print(result.stdout)
        console.print(result.stderr)

if __name__ == "__main__":
    app()
