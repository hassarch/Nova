import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from app.database.connection import SessionLocal
from app.agent.controller import AgentController

app = typer.Typer()
console = Console()


@app.command()
def run(prompt: str):
    """Execute a task with NOVA"""

    # Header
    console.print()
    console.print(Panel(
        Text(" NOVA", style="bold cyan") + "\n\n" + Text(prompt, style="dim white"),
        border_style="cyan",
        padding=(1, 2)
    ))

    db = SessionLocal()
    controller = AgentController(db)
    
    try:
        # Execution indicator
        console.print(Text("Executing...", style="yellow"))
        console.print()
        
        plan = controller.run(prompt)
        
        # Check if there's a message indicating task is already complete
        if plan and isinstance(plan, dict) and plan.get("message"):
            console.print(Panel(
                Text(f" {plan['message']}", style="bold yellow"),
                border_style="yellow",
                padding=(1, 2)
            ))
            console.print()
            return
        
        # Results table
        if plan and isinstance(plan, dict) and "steps" in plan:
            table = Table(
                title="[bold cyan]Execution Results[/bold cyan]",
                show_header=True,
                header_style="bold white",
                border_style="cyan",
                padding=(0, 1)
            )
            table.add_column("Step", style="cyan", width=8)
            table.add_column("Tool", style="green", width=15)
            table.add_column("Action", style="white", width=30)
            table.add_column("Status", style="green", width=12)
            
            for i, step in enumerate(plan["steps"], 1):
                action = step.get("action", "N/A")[:28]
                table.add_row(
                    f"#{i}",
                    step.get("tool", "N/A").upper(),
                    action,
                    "✓ Done"
                )
            
            console.print(table)
            console.print()
        
        # Success message
        console.print(Panel(
            Text(" Task completed successfully", style="bold green"),
            border_style="green",
            padding=(1, 2)
        ))
        console.print()
        
    except Exception as e:
        console.print()
        console.print(Panel(
            Text(f"✗ Error: {e}", style="bold red"),
            border_style="red",
            padding=(1, 2)
        ))
        console.print()


@app.command()
def version():
    """Show NOVA version"""
    console.print(Text("NOVA v1.0.0", style="bold cyan"))


def main():
    app()


if __name__ == "__main__":
    main()
