"""NOVA Environment diagnostics and health checks"""
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nova.config.loader import load_config

console = Console()


def check_python() -> tuple[bool, str]:
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, "Python 3.9+ required"


def check_git() -> tuple[bool, str]:
    """Check if Git is installed"""
    try:
        result = subprocess.run(["git", "--version"], check=True, capture_output=True, text=True, timeout=5)
        version = result.stdout.strip()
        return True, version
    except Exception:
        return False, "Git not found"


def check_ollama() -> tuple[bool, str]:
    """Check if Ollama is running"""
    try:
        subprocess.run(["ollama", "list"], check=True, capture_output=True, timeout=5)
        return True, "Ollama running"
    except Exception:
        return False, "Ollama not running or not installed"


def check_model() -> tuple[bool, str]:
    """Check if configured model is available"""
    try:
        config = load_config()
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if config.model in result.stdout:
            return True, f"Model '{config.model}' available"
        return False, f"Model '{config.model}' not found"
    except Exception:
        return False, "Unable to verify model"


def check_config() -> tuple[bool, str]:
    """Check if config is valid"""
    try:
        load_config()
        config_file = Path.home() / ".nova" / "config.yaml"
        if config_file.exists():
            return True, f"Config loaded from {config_file}"
        return True, "Using default config"
    except Exception:
        return False, "Config invalid"


def check_database() -> tuple[bool, str]:
    """Check if database is accessible"""
    try:
        from nova.database.connection import engine

        engine.connect().__enter__().__exit__(None, None, None)
        return True, "Database connected"
    except Exception as e:
        return False, f"Database error: {str(e)[:50]}"


def run_doctor() -> bool:
    """Run all environment checks and display results"""
    console.print()
    console.print(
        Panel(
            Text("NOVA Environment Check", style="bold cyan"),
            border_style="cyan",
            padding=(0, 2),
        )
    )
    console.print()

    table = Table(show_header=True, header_style="bold white", border_style="cyan")
    table.add_column("Check", style="cyan", width=15)
    table.add_column("Status", width=50)

    checks = {
        "Python": check_python(),
        "Git": check_git(),
        "Ollama": check_ollama(),
        "Model": check_model(),
        "Config": check_config(),
        "Database": check_database(),
    }

    all_good = True

    for name, (status, message) in checks.items():
        if status:
            table.add_row(name, f"[green]✔ {message}[/green]")
        else:
            table.add_row(name, f"[red]✘ {message}[/red]")
            all_good = False

    console.print(table)
    console.print()

    if all_good:
        console.print(
            Panel(
                Text("✅ All checks passed", style="bold green"),
                border_style="green",
                padding=(0, 2),
            )
        )
    else:
        console.print(
            Panel(
                Text("⚠️  Some checks failed", style="bold yellow"),
                border_style="yellow",
                padding=(0, 2),
            )
        )

    console.print()
    return all_good
