TOOL_NORMALIZATION_MAP = {
    "editor": "filesystem",
    "text_editor": "filesystem",
    "file_writer": "filesystem",
    "node": "terminal",
    "python": "terminal",
    "python3": "terminal",
    "bash": "terminal",
    "shell": "terminal",
    "cmd": "terminal",
    "command": "terminal",
    "script": "terminal",
    "code": "filesystem",
    "write": "filesystem",
    "create": "filesystem",
    "file": "filesystem",
    "pip": "terminal",
    "npm": "terminal",
    "yarn": "terminal",
    "apt": "terminal",
    "brew": "terminal",
    "docker-compose": "terminal",
    "docker": "docker",
    "git": "git"
}


def normalize_tool(tool_name: str) -> str:
    return TOOL_NORMALIZATION_MAP.get(tool_name.lower(), tool_name.lower())
