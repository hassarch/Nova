import requests
from app.config.settings import settings
from app.core.context.collector import collect_context
from app.core.context.formatter import format_context_for_prompt


class Planner:

    def __init__(self, db):
        self.db = db

    def generate_plan(self, prompt: str, session_id: str):
        # 🔹 Collect environment context
        context = collect_context(self.db, session_id)
        context_str = format_context_for_prompt(context)

        payload = {
            "model": "llama3",
            "prompt": self._build_prompt(prompt, context_str),
            "stream": False
        }

        url = f"{settings.OLLAMA_URL}/api/generate"

        response = requests.post(url, json=payload, timeout=300)

        if response.status_code != 200:
            raise Exception("Failed to connect to Ollama")

        return response.json()["response"]

    def _build_prompt(self, user_prompt: str, context_str: str):
        return f"""You are NOVA - Neural Orchestrated Virtual Assistant.

CRITICAL: You MUST return ONLY valid JSON. Nothing else.

ENVIRONMENT CONTEXT:
{context_str}

Return this exact format:
{{
  "task_id": "unique_id",
  "message": "optional message if task is already complete or skipped",
  "steps": [
    {{
      "step_id": "step_1",
      "tool": "filesystem",
      "action": "Create file",
      "command": null,
      "file_path": "./filename.ext",
      "content": "file content"
    }}
  ]
}}

RULES:
- ONLY output JSON
- NO markdown, NO explanations, NO backticks
- Escape all quotes in content with backslash
- Use ./ for relative paths
- For Python files: include if __name__ == "__main__": pass
- For C files: include #include <stdio.h> and main function
- For empty files: use empty string ""
- IMPORTANT: If the user asks to initialize git and git is already initialized (git_status is not "Git not initialized"), return an empty steps array with a message explaining git is already initialized
- IMPORTANT: Check the git_status in the context before attempting any git initialization
- IMPORTANT: When the user refers to "that file", "the file we just created", "the file", "that code", or similar, use the most_recent_file from context
- IMPORTANT: When modifying a file, READ the most_recent_file_content first to understand what you're modifying
- IMPORTANT: If modifying a file, use "Modify file" action, not "Create file"
- IMPORTANT: When modifying a file, the tool should be "filesystem" with action "Modify file"
- IMPORTANT: Preserve the original file's purpose and structure when modifying

User request: {user_prompt}
"""
