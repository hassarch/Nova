import difflib
import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from app.agent.controller import AgentController
from app.core.analytics.queries import get_failed_steps, get_recent_prompts, get_retry_stats, get_session_summary
from app.database.connection import SessionLocal
from app.database.models import Session as DBSession

console = Console()


def show_diff_preview(file_path: str, new_content: str):
    """Show a diff preview for file modifications"""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                old_content = f.read()
        else:
            old_content = ""

        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = difflib.unified_diff(old_lines, new_lines, fromfile=f"{file_path}", tofile=f"{file_path}", lineterm="")

        diff_lines = list(diff)
        if diff_lines:
            console.print("[bold blue]📝 Diff Preview:[/bold blue]")
            for line in diff_lines[:25]:  # Show first 25 lines
                line = line.rstrip()
                if line.startswith("+") and not line.startswith("+++"):
                    console.print(f"[green]{line}[/green]")
                elif line.startswith("-") and not line.startswith("---"):
                    console.print(f"[red]{line}[/red]")
                elif line.startswith("@@"):
                    console.print(f"[cyan]{line}[/cyan]")
                elif line.startswith("---") or line.startswith("+++"):
                    console.print(f"[dim]{line}[/dim]")
                else:
                    console.print(f"[dim]{line}[/dim]")

            if len(diff_lines) > 25:
                console.print(f"[dim]... and {len(diff_lines) - 25} more lines[/dim]")
            console.print()
    except Exception as e:
        console.print(f"[dim]Could not generate diff: {e}[/dim]")
        console.print()


@click.group()
def cli():
    """NOVA - AI Agent for task execution"""
    pass


@cli.command()
@click.argument("prompt")
@click.option("--simulate", is_flag=True, help="Run in simulation mode (no execution)")
@click.option("--plan-only", is_flag=True, help="Show plan only (skip policy evaluation)")
def run(prompt, simulate, plan_only):
    """Execute a task with NOVA"""
    from sqlalchemy.exc import ProgrammingError

    console.print()
    console.print(
        Panel(Text(" NOVA", style="bold cyan") + "\n\n" + Text(prompt, style="dim white"), border_style="cyan", padding=(1, 2))
    )

    db = SessionLocal()
    controller = AgentController(db, simulate=simulate, plan_only=plan_only)

    try:
        console.print(Text("Planning..." if plan_only else ("Simulating..." if simulate else "Executing..."), style="yellow"))
        console.print()

        try:
            result = controller.run(prompt)
        except ProgrammingError:
            console.print()
            console.print(
                Panel(
                    Text(
                        "✗ Error: Database tables not initialized. Run migrations first:\n\nalembic upgrade head",
                        style="bold red",
                    ),
                    border_style="red",
                    padding=(1, 2),
                )
            )
            console.print()
            db.close()
            return

        # ------------------------------
        # 📋 PLAN-ONLY MODE DISPLAY
        # ------------------------------
        if result and isinstance(result, dict) and result.get("plan_only"):
            table = Table(
                title="[bold cyan]Execution Plan[/bold cyan]",
                show_header=True,
                header_style="bold white",
                border_style="cyan",
                padding=(0, 1),
            )

            table.add_column("Step", style="cyan", width=6)
            table.add_column("Tool", style="green", width=12)
            table.add_column("Action", style="white", width=18)
            table.add_column("Target", style="blue", width=22)
            table.add_column("Risk", style="white", width=10)
            table.add_column("Status", style="white", width=12)

            # Risk color mapping
            risk_colors = {"low": "green", "high": "yellow", "critical": "red"}

            for i, step in enumerate(result["steps"], 1):
                tool = step.get("tool", "N/A").upper()
                action = step.get("action", "N/A")[:16]
                risk = step.get("risk", "low").lower()
                allowed = step.get("allowed", True)
                file_path = step.get("file_path", "")
                command = step.get("command", "")

                if tool == "FILESYSTEM":
                    target = file_path[:20] if file_path else "N/A"
                elif tool == "TERMINAL":
                    target = command[:20] if command else "N/A"
                else:
                    target = "N/A"

                # Determine status
                if not allowed:
                    status = "✗ Block"
                elif risk == "critical":
                    status = "✗ Block"
                elif risk == "high":
                    status = "⚠ Review"
                else:
                    status = "✓ Allow"

                # Color the risk level
                risk_color = risk_colors.get(risk, "white")
                risk_text = f"[{risk_color}]{risk.upper()}[/{risk_color}]"

                table.add_row(f"#{i}", tool, action, target, risk_text, status)

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
                Panel(Text(" Plan generated (no execution)", style="bold cyan"), border_style="cyan", padding=(1, 2))
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
                padding=(0, 1),
            )

            table.add_column("Step", style="cyan", width=6)
            table.add_column("Tool", style="green", width=12)
            table.add_column("Action", style="white", width=18)
            table.add_column("Target", style="blue", width=22)
            table.add_column("Risk", style="white", width=10)
            table.add_column("Status", style="white", width=12)

            # Risk color mapping
            risk_colors = {"low": "green", "high": "yellow", "critical": "red"}

            # Metrics
            risk_counts = {"low": 0, "high": 0, "critical": 0}
            blocked_steps = 0
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
                    if file_path:
                        files_affected.append(file_path)
                    target = file_path[:20] if file_path else "N/A"
                elif tool == "TERMINAL":
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

                table.add_row(f"#{i}", tool, action, target, risk_text, status)

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
            blocked_items = [
                step for step in result.get("steps", []) if not step.get("allowed", True) or step.get("risk") == "critical"
            ]
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
                    Text(" Simulation completed (no changes made)", style="bold yellow"), border_style="yellow", padding=(1, 2)
                )
            )
            console.print()
            return

        # ------------------------------
        # 📊 NORMAL EXECUTION RESULTS
        # ------------------------------
        if result and isinstance(result, dict) and "steps" in result:
            # Display subtasks if available
            if result.get("subtasks"):
                console.print("[bold cyan]📋 Execution Plan:[/bold cyan]")
                for i, subtask in enumerate(result["subtasks"], 1):
                    console.print(f"  {i}. {subtask.get('objective', 'N/A')}")
                console.print()

            table = Table(
                title="[bold cyan]Execution Results[/bold cyan]",
                show_header=True,
                header_style="bold white",
                border_style="cyan",
                padding=(0, 1),
            )

            table.add_column("Step", style="cyan", width=8)
            table.add_column("Tool", style="green", width=15)
            table.add_column("Action", style="white", width=30)
            table.add_column("Status", style="green", width=12)

            for i, step in enumerate(result["steps"], 1):
                action = step.get("action", "N/A")[:28]

                table.add_row(f"#{i}", step.get("tool", "N/A").upper(), action, "✓ Done")

            console.print(table)
            console.print()

        console.print(Panel(Text(" Task completed successfully", style="bold green"), border_style="green", padding=(1, 2)))
        console.print()

    except Exception as e:
        console.print()
        console.print(Panel(Text(f"✗ Error: {e}", style="bold red"), border_style="red", padding=(1, 2)))
        console.print()

    finally:
        # Show metrics for this session
        try:
            from sqlalchemy.exc import ProgrammingError

            from app.database.models import Session as DBSession

            last_session = db.query(DBSession).order_by(DBSession.id.desc()).first()

            if last_session and not simulate and not plan_only:
                console.print(
                    Panel(
                        Text(
                            f"📊 Session Metrics\n"
                            f"Reads: {last_session.read_count} | "
                            f"Writes: {last_session.write_count} | "
                            f"Retries: {last_session.retry_count} | "
                            f"Risk Score: {last_session.risk_score}",
                            style="dim cyan",
                        ),
                        border_style="cyan",
                        padding=(0, 1),
                    )
                )
                console.print()
        except (Exception, ProgrammingError):
            pass

        db.close()


@cli.command()
@click.argument("session_identifier")
def resume(session_identifier):
    """Resume a failed workflow from the last incomplete subtask"""
    from sqlalchemy.exc import ProgrammingError

    console.print()
    console.print(Panel(Text(f" Resume Session {session_identifier}", style="bold cyan"), border_style="cyan", padding=(1, 2)))
    console.print()

    db = SessionLocal()
    controller = AgentController(db)

    try:
        console.print(Text("Resuming workflow...", style="yellow"))
        console.print()

        # Try to parse as integer first (database ID), then as session UUID
        try:
            db_session = None
            if session_identifier.isdigit():
                db_session = db.query(DBSession).filter_by(id=int(session_identifier)).first()
            else:
                db_session = db.query(DBSession).filter_by(session_id=session_identifier).first()
        except ProgrammingError:
            console.print(
                Panel(
                    Text("✗ Error: Database tables not initialized. Run migrations first.", style="bold red"),
                    border_style="red",
                    padding=(1, 2),
                )
            )
            console.print()
            db.close()
            return

        if not db_session:
            console.print(
                Panel(
                    Text(f"✗ Error: Session '{session_identifier}' not found", style="bold red"),
                    border_style="red",
                    padding=(1, 2),
                )
            )
            console.print()
            db.close()
            return

        result = controller.resume(db_session.id)

        if "error" in result:
            console.print(
                Panel(
                    Text(f"✗ Error: {result['error']}", style="bold red"),
                    border_style="red",
                    padding=(1, 2),
                )
            )
        else:
            console.print(
                Panel(
                    Text(f"✓ {result.get('message', 'Resume completed')}", style="bold green"),
                    border_style="green",
                    padding=(1, 2),
                )
            )

        console.print()

    except Exception as e:
        console.print()
        console.print(Panel(Text(f"✗ Error: {e}", style="bold red"), border_style="red", padding=(1, 2)))
        console.print()

    finally:
        db.close()


@cli.command()
def version():
    """Show NOVA version"""
    console.print(Text("NOVA v0.2.0", style="bold cyan"))


@cli.command()
@click.option("--limit", default=5, help="Number of sessions to show")
def session(limit):
    """View session history and metrics"""
    from sqlalchemy.exc import ProgrammingError

    console.print()
    console.print(Panel(Text(" Session History", style="bold cyan"), border_style="cyan", padding=(1, 2)))
    console.print()

    try:
        db = SessionLocal()
        try:
            sessions = db.query(DBSession).order_by(DBSession.id.desc()).limit(limit).all()
        except ProgrammingError:
            console.print("[dim]No sessions found[/dim]")
            db.close()
            return

        if not sessions:
            console.print("[dim]No sessions found[/dim]")
            db.close()
            return

        # Table view
        table = Table(
            title="[bold cyan]Recent Sessions[/bold cyan]",
            show_header=True,
            header_style="bold white",
            border_style="cyan",
            padding=(0, 1),
        )

        table.add_column("Session ID", style="cyan", width=36)
        table.add_column("Reads", style="green", width=8)
        table.add_column("Writes", style="green", width=8)
        table.add_column("Retries", style="yellow", width=8)
        table.add_column("Risk", style="white", width=8)
        table.add_column("Created", style="dim", width=20)

        for s in sessions:
            created = s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else "N/A"
            table.add_row(
                s.session_id[:36], str(s.read_count), str(s.write_count), str(s.retry_count), str(s.risk_score), created
            )

        console.print(table)
        console.print()

        # Show statistics
        avg_risk = sum(s.risk_score or 0 for s in sessions) / len(sessions) if sessions else 0
        total_ops = sum((s.read_count or 0) + (s.write_count or 0) for s in sessions)
        total_retries = sum(s.retry_count or 0 for s in sessions)

        stats_panel = Panel(
            Text(
                f"📊 Statistics (Last {len(sessions)} sessions)\n"
                f"Average Risk: {avg_risk:.1f} | "
                f"Total Operations: {total_ops} | "
                f"Total Retries: {total_retries}",
                style="dim white",
            ),
            border_style="cyan",
            padding=(0, 1),
        )
        console.print(stats_panel)
        console.print()

        db.close()

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print()


@cli.command()
def sessions():
    """Show session summary"""

    db = SessionLocal()
    summary = get_session_summary(db)

    table = Table(title="[bold cyan]Session Summary[/bold cyan]")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Sessions", str(summary["sessions"]))
    table.add_row("Total Steps", str(summary["steps"]))
    table.add_row("Execution Results", str(summary["results"]))
    table.add_row("Total Retries", str(summary["retries"]))

    console.print(table)
    db.close()


@cli.command()
@click.option("--limit", default=5, help="Number of prompts to show")
def history(limit):
    """Show recent prompts"""

    db = SessionLocal()
    prompts = get_recent_prompts(db, limit)

    table = Table(title="[bold cyan]Recent Prompts[/bold cyan]")
    table.add_column("ID", style="cyan")
    table.add_column("Content", style="white")

    for p in prompts:
        table.add_row(str(p.id), p.content[:60])

    console.print(table)
    db.close()


@cli.command()
def failures():
    """Show failed execution steps"""

    db = SessionLocal()
    failed = get_failed_steps(db)

    table = Table(title="[bold red]Failed Steps[/bold red]")
    table.add_column("Step ID", style="cyan")
    table.add_column("Return Code", style="red")
    table.add_column("Error", style="white")

    for f in failed:
        table.add_row(str(f.step_id), str(f.return_code), (f.stderr or "")[:60])

    console.print(table)
    db.close()


@cli.command()
def retries():
    """Show retry attempts"""

    db = SessionLocal()
    retry_list = get_retry_stats(db)

    table = Table(title="[bold yellow]Retry Attempts[/bold yellow]")
    table.add_column("Step ID", style="cyan")
    table.add_column("Retry #", style="yellow")

    for r in retry_list:
        table.add_row(str(r.step_id), str(r.retry_number))

    console.print(table)
    db.close()


@cli.command()
def metrics():
    """Show simple system metrics"""

    db = SessionLocal()
    summary = get_session_summary(db)

    success_rate = 0
    if summary["steps"] > 0:
        success_rate = (summary["results"] / summary["steps"]) * 100

    panel = Panel(
        f"[bold cyan]NOVA Metrics[/bold cyan]\n\n"
        f"Sessions: {summary['sessions']}\n"
        f"Steps: {summary['steps']}\n"
        f"Results: {summary['results']}\n"
        f"Retries: {summary['retries']}\n"
        f"Approx Success Rate: {success_rate:.2f}%",
        border_style="cyan",
    )

    console.print(panel)
    db.close()


@cli.command()
def analyze():
    """Analyze entire project using AI analyzer layer"""

    console.print()
    console.print(Panel(Text(" AI Project Analysis", style="bold cyan"), border_style="cyan", padding=(1, 2)))
    console.print()

    try:
        from app.core.analytics.ai_analyzer import AIAnalyzer

        db = SessionLocal()
        analyzer = AIAnalyzer(db)

        console.print(Text("Analyzing project metrics...", style="yellow"))
        console.print()

        analysis = analyzer.analyze()

        console.print(Panel(Text(analysis, style="white"), border_style="cyan", padding=(1, 2)))
        console.print()

        db.close()

    except Exception as e:
        console.print()
        console.print(Panel(Text(f"✗ Analysis Error: {e}", style="bold red"), border_style="red", padding=(1, 2)))
        console.print()


def main():
    cli()


if __name__ == "__main__":
    main()
