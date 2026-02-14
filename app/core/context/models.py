from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ExecutionContext:
    working_directory: str
    file_tree: List[str]
    git_status: str
    installed_tools: List[str]
    last_execution_summary: str
    session_memory: List[Dict[str, Any]]
    most_recent_file: str = "None"
    most_recent_file_content: str = ""