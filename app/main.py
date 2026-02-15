import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import sys
import os
import difflib

from app.database.connection import SessionLocal
from app.agent.controller import AgentController

app = typer.Typer()
console = Console()


def show_diff_preview(file_path: str, new_content: str):
    """Show a diff preview for file modifications"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                old_content = f.read()
        else:
            old_content = ""
        
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{file_path}",
            tofile=f"{file_path}",
            lineterm=""
        )
        
        diff_lines = list(diff)
        if diff_lines:
            console.print("[bold blue]📝 Diff Preview:[/bold blue]")
            for line in diff_lines[:25]:  # Show first 25 lines
                line = line.rstrip()
                if line.startswith('+') and not line.startswith('+++'):
                    console.print(f"[green]{line}[/green]")
                elif line.startswith('-') and not line.startswith('---'):
                    console.print(f"[red]{line}[/red]")
                elif line.startswith('@@'):
                    console.print(f"[cyan]{line}[/cyan]")
                elif line.startswith('---') or line.startswith('+++'):
                    console.print(f"[dim]{line}[/dim]")
                else:
                    console.print(f"[dim]{line}[/dim]")
            
            if len(diff_lines) > 25:
                console.print(f"[dim]... and {len(diff_lines) - 25} more lines[/dim]")
            console.print()
    except Exception as e:
        console.print(f"[dim]Could not generate diff: {e}[/dim]")
        console.print()


@app.command()
def run(
    prompt: str,
    simulate: bool = typer.Option(False, "--simulate", is_flag=True, help="Run in simulation mode (no execution)"),
    plan_only: bool = typer.Option(False, "--plan-only", is_flag=True, help="Show plan only (skip policy evaluation)")
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
    plan_only_bool = "--plan-only" in sys.argv
    controller = AgentController(db, simulate=simulate_bool, plan_only=plan_only_bool)

    try:
        console.print(Text(
            "Planning..." if plan_only_bool else ("Simulating..." if simulate_bool else "Executing..."),
            style="yellow"
        ))
        console.print()

        result = controller.run(prompt)

        # ------------------------------
        # 📋 PLAN-ONLY MODE DISPLAY
        # ------------------------------
        if result and isinstance(result, dict) and result.get("plan_only"):

            table = Table(
                title="[bold cyan]Execution Plan[/bold cyan]",
                show_header=True,
                header_style="bold white",
                border_style="cyan",
                padding=(0, 1)
            )

            table.add_column("Step", style="cyan", width=6)
            table.add_column("Tool", style="green", width=12)
            table.add_column("Action", style="white", width=18)
            table.add_column("Target", style="blue", width=22)

            for i, step in enumerate(result["steps"], 1):
                tool = step.get("tool", "N/A").upper()
                action = step.get("action", "N/A")[:16]
                file_path = step.get("file_path", "")
                command = step.get("command", "")
                
                if tool == "FILESYSTEM":
                    target = file_path[:20] if file_path else "N/A"
                elif tool == "TERMINAL":
                    target = command[:20] if command else "N/A"
                else:
                    target = "N/A"

                table.add_row(
                    f"#{i}",
                    tool,
                    action,
                    target
                )

            console.print(table)
            console.print()

            # Show diff previews for modifications
            for step in result.get("steps", []):
                if step.get("tool") == "filesystem" and step.get("action", "").lower() == "modify file":
                    file_path = step.get("file_path", "")
                    content = step.get("content", "")
                    if file_path and content:
                        show_diff_preview(file_path, content)

            console.print(
                Panel(
                    Text(" Plan generated (no execution)", style="bold cyan"),
                    border_style="cyan",
                    padding=(1, 2)
                )
            )
            console.print()
            return

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

            table.add_column("Step", style="cyan", width=6)
            table.add_column("Tool", style="green", width=12)
            table.add_column("Action", style="white", width=18)
            table.add_column("Target", style="blue", width=22)
            table.add_column("Risk", style="white", width=10)
            table.add_column("Status", style="white", width=12)

            # Risk color mapping
            risk_colors = {
                "low": "green",
                "high": "yellow",
                "critical": "red"
            }

            # Metrics
            total_steps = len(result.get("steps", []))
            risk_counts = {"low": 0, "high": 0, "critical": 0}
            blocked_steps = 0
            file_operations = 0
            terminal_operations = 0
            files_affected = []

            for i, step in enumerate(result["steps"], 1):
                tool = step.get("tool", "N/A").upper()
                action = step.get("action", "N/A")[:16]
                risk = step.get("risk", "low").lower()
                file_path = step.get("file_path", "")
                command = step.get("command", "")
                allowed = step.get("allowed", True)
                
                # Count metrics
                if risk in risk_counts:
                    risk_counts[risk] += 1
                
                if tool == "FILESYSTEM":
                    file_operations += 1
                    if file_path:
                        files_affected.append(file_path)
                    target = file_path[:20] if file_path else "N/A"
                elif tool == "TERMINAL":
                    terminal_operations += 1
                    target = command[:20] if command else "N/A"
                else:
                    target = "N/A"

                # Determine status
                if not allowed:
                    status = "✗ Block"
                    blocked_steps += 1
                elif risk == "critical":
                    status = "✗ Block"
                    blocked_steps += 1
                elif risk == "high":
                    status = "⚠ Review"
                else:
                    status = "✓ Allow"

                # Color the risk level
                risk_color = risk_colors.get(risk, "white")
                risk_text = f"[{risk_color}]{risk.upper()}[/{risk_color}]"

                table.add_row(
                    f"#{i}",
                    tool,
                    action,
                    target,
                    risk_text,
                    status
                )

            console.print(table)
            console.print()

            # Show diff previews for modifications
            for step in result.get("steps", []):
                if step.get("tool") == "filesystem" and step.get("action", "").lower() == "modify file":
                    file_path = step.get("file_path", "")
                    content = step.get("content", "")
                    if file_path and content:
                        show_diff_preview(file_path, content)

            # Show policy block reasons if any
            blocked_items = [step for step in result.get("steps", []) 
                           if not step.get("allowed", True) or step.get("risk") == "critical"]
            if blocked_items:
                console.print("[bold red]⚠️  Policy Blocks:[/bold red]")
                for i, step in enumerate(blocked_items, 1):
                    reason = step.get("policy_reason", "Security policy violation")
                    action = step.get("action", "Unknown")
                    console.print(f"  {i}. {action}: {reason}")
                console.print()

            # Show affected files (deduplicated)
            if files_affected:
                unique_files = list(dict.fromkeys(files_affected))  # Remove duplicates while preserving order
                console.print("[bold blue]📁 Files to be affected:[/bold blue]")
                for file_path in unique_files:
                    console.print(f"  • {file_path}")
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
