TOOL_NORMALIZATION_MAP = {
    "editor": "filesystem",
    "text_editor": "filesystem",
    "file_writer": "filesystem",
    "node": "terminal",
    "python": "terminal",
    "bash": "terminal",
    "shell": "terminal",
    "cmd": "terminal",
    "command": "terminal",
    "script": "terminal",
    "code": "filesystem",
    "write": "filesystem",
    "create": "filesystem",
    "file": "filesystem"
}


def normalize_tool(tool_name: str) -> str:
    return TOOL_NORMALIZATION_MAP.get(tool_name.lower(), tool_name.lower())
