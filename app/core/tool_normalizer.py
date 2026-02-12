TOOL_NORMALIZATION_MAP = {
    "editor": "filesystem",
    "text_editor": "filesystem",
    "file_writer": "filesystem"
}


def normalize_tool(tool_name: str) -> str:
    return TOOL_NORMALIZATION_MAP.get(tool_name, tool_name)
