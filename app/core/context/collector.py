# app/core/context/collector.py

import os
import subprocess
from typing import List
from .models import ExecutionContext


WHITELISTED_TOOLS = ["node", "npm", "python3", "docker", "git", "pip"]


def get_working_directory() -> str:
    return os.getcwd()


def get_file_tree(base_path: str, max_depth: int = 2) -> List[str]:
    results = []

    for root, dirs, files in os.walk(base_path, topdown=True, followlinks=False):
        level = root.replace(base_path, "").count(os.sep)

        if level > max_depth:
            dirs[:] = []
            continue

        relative_root = os.path.relpath(root, base_path)
        results.append(relative_root)

        for f in sorted(files):
            results.append(os.path.join(relative_root, f))

    return sorted(results)[:50]


def get_git_status() -> str:
    try:
        # Check if .git directory exists
        if os.path.isdir(".git"):
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            return result.stdout.strip() or "Clean"
        else:
            return "Git not initialized"
    except Exception:
        return "Git not initialized"


def get_installed_tools() -> List[str]:
    available = []

    for tool in WHITELISTED_TOOLS:
        try:
            result = subprocess.run(
                ["which", tool],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                available.append(tool)
        except Exception:
            continue

    return sorted(available)


def get_last_execution_summary(db):
    try:
        result = db.fetch_last_execution()
        return result.get("summary", "No previous execution")
    except Exception:
        return "Unavailable"


def get_most_recent_file() -> str:
    """Get the most recently modified file in the current directory"""
    try:
        import glob
        files = glob.glob("*")
        if not files:
            return "None"
        # Get the most recently modified file
        most_recent = max(files, key=lambda f: os.path.getmtime(f) if os.path.isfile(f) else 0)
        return most_recent if os.path.isfile(most_recent) else "None"
    except Exception:
        return "None"


def get_most_recent_file_content() -> str:
    """Get the content of the most recently modified file"""
    try:
        import glob
        files = glob.glob("*")
        if not files:
            return ""
        # Get the most recently modified file
        most_recent = max(files, key=lambda f: os.path.getmtime(f) if os.path.isfile(f) else 0)
        if os.path.isfile(most_recent):
            with open(most_recent, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()[:1000]  # Limit to 1000 chars
        return ""
    except Exception:
        return ""


def get_session_memory(db, session_id: str, limit: int = 5):
    try:
        return db.fetch_recent_interactions(session_id, limit)
    except Exception:
        return []


def collect_context(db, session_id: str) -> ExecutionContext:
    cwd = get_working_directory()

    return ExecutionContext(
        working_directory=cwd,
        file_tree=get_file_tree(cwd),
        git_status=get_git_status(),
        installed_tools=get_installed_tools(),
        last_execution_summary=get_last_execution_summary(db),
        session_memory=get_session_memory(db, session_id),
        most_recent_file=get_most_recent_file(),
        most_recent_file_content=get_most_recent_file_content(),
    )
