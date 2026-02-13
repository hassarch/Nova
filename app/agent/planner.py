import requests
from app.config.settings import settings


class Planner:

    def generate_plan(self, prompt: str):
        payload = {
            "model": "llama3",
            "prompt": self._build_prompt(prompt),
            "stream": False
        }

        url = f"{settings.OLLAMA_URL}/api/generate"
        
        response = requests.post(url, json=payload, timeout=300)

        if response.status_code != 200:
            raise Exception("Failed to connect to Ollama")

        return response.json()["response"]

    def _build_prompt(self, user_prompt: str):
        return f"""
You are NOVA - Neural Orchestrated Virtual Assistant.

You MUST return ONLY valid JSON.
Do NOT include markdown.
Do NOT include explanation.
Do NOT wrap in backticks.

Return strictly this format:

{{
  "task_id": "unique_string",
  "steps": [
    {{
      "step_id": "step_1",
      "tool": "filesystem",
      "action": "Create a new file",
      "command": null,
      "file_path": "./filename.ext",
      "content": "file content here"
    }}
  ]
}}

IMPORTANT RULES:
- Use relative paths starting with "./" for file_path (e.g., "./hello.py", "./src/main.java")
- For file creation, ALWAYS include content field with appropriate boilerplate or code
- For empty files, use empty string "" as content
- For Python files, include basic structure like: if __name__ == "__main__": pass
- For C files, include: #include <stdio.h>\nint main() {{\n    return 0;\n}}
- For text files, include meaningful content or empty string
- For terminal commands, use tool "terminal" with command field populated
- For file creation, use tool "filesystem" with file_path and content fields populated

User request:
{user_prompt}
"""
