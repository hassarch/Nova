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

        payload = {"model": "llama3", "prompt": self._build_prompt(prompt, context_str), "stream": False}

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

Return JSON in EXACTLY this format:

{{
  "task_id": "unique_id",
  "goal": "overall goal description",
  "message": "optional message if task is already complete or skipped",
  "subtasks": [
    {{
      "objective": "subtask objective",
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
  ]
}}

RULES:
- ONLY output JSON
- NO markdown
- NO explanations
- NO backticks
- Escape all quotes in content with backslash
- Use ./ for relative paths
- Break complex tasks into logical subtasks
- Each subtask must have a clear objective
- Each subtask must contain one or more steps
- For simple tasks, create ONE subtask only
- If task is already complete, return empty subtasks array and provide message
- When modifying a file:
  - Use tool "filesystem"
  - Use action "Modify file"
  - Preserve original file structure
- If git is already initialized, do NOT reinitialize it
- Always consider git state before git operations
- Preserve project structure integrity

User request: {user_prompt}
"""
