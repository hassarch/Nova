# app/core/context/formatter.py

import json

from .models import ExecutionContext


def format_context_for_prompt(context: ExecutionContext) -> str:
    payload = {
        "working_directory": context.working_directory,
        "file_tree": context.file_tree,
        "git_status": context.git_status,
        "installed_tools": context.installed_tools,
        "last_execution_summary": context.last_execution_summary,
        "most_recent_file": context.most_recent_file,
        "most_recent_file_content": context.most_recent_file_content,
        "recent_interactions": context.session_memory,
    }

    return json.dumps(payload, indent=2)
