import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import sys

from app.database.connection import SessionLocal
from app.agent.controller import AgentController

app = typer.Typer()
console = Console()


@app.command()
def run(
    prompt: str,
    simulate: bool = typer.Option(False, "--simulate", is_flag=True, help="Run in simulation mode (no execution)")
):
    """Execute a task with NOVA"""

    console.print()
    console.print(
        Panel(
            Text(" NOVA", style="bold cyan") +
            "\n\n" +
            Text(prompt, style="dim white"),
            border_style="cyan",
            padding=(1, 2)
        )
    )

    db = SessionLocal()
    # Workaround: check sys.argv directly for --simulate flag
    simulate_bool = "--simulate" in sys.argv
    controller = AgentController(db, simulate=simulate_bool)

    try:
        console.print(Text(
            "Simulating..." if simulate_bool else "Executing...",
            style="yellow"
        ))
        console.print()

        result = controller.run(prompt)

        # ------------------------------
        # 🧪 SIMULATION MODE DISPLAY
        # ------------------------------
        if result and isinstance(result, dict) and result.get("simulation"):

            table = Table(
                title="[bold yellow]Simulation Preview[/bold yellow]",
                show_header=True,
                header_style="bold white",
                border_style="yellow",
                padding=(0, 1)
            )

            table.add_column("Step", style="cyan", width=8)
            table.add_column("Tool", style="green", width=15)
            table.add_column("Action", style="white", width=30)
            table.add_column("Risk", style="red", width=12)

            for i, step in enumerate(result["steps"], 1):
                table.add_row(
                    f"#{i}",
                    step.get("tool", "N/A").upper(),
                    step.get("action", "N/A")[:28],
                    step.get("risk", "low").upper()
                )

            console.print(table)
            console.print()

            console.print(
                Panel(
                    Text(" Simulation completed (no changes made)", style="bold yellow"),
                    border_style="yellow",
                    padding=(1, 2)
                )
            )
            console.print()
            return

        # ------------------------------
        # 📊 NORMAL EXECUTION RESULTS
        # ------------------------------
        if result and isinstance(result, dict) and "steps" in result:

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

            for i, step in enumerate(result["steps"], 1):
                action = step.get("action", "N/A")[:28]

                table.add_row(
                    f"#{i}",
                    step.get("tool", "N/A").upper(),
                    action,
                    "✓ Done"
                )

            console.print(table)
            console.print()

        console.print(
            Panel(
                Text(" Task completed successfully", style="bold green"),
                border_style="green",
                padding=(1, 2)
            )
        )
        console.print()

    except Exception as e:
        console.print()
        console.print(
            Panel(
                Text(f"✗ Error: {e}", style="bold red"),
                border_style="red",
                padding=(1, 2)
            )
        )
        console.print()

    finally:
        db.close()


@app.command()
def version():
    """Show NOVA version"""
    console.print(Text("NOVA v1.0.0", style="bold cyan"))


def main():
    app()


if __name__ == "__main__":
    main()
