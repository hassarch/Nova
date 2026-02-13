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
        return f"""You are NOVA - Neural Orchestrated Virtual Assistant.

CRITICAL: You MUST return ONLY valid JSON. Nothing else.

Return this exact format:
{{
  "task_id": "unique_id",
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

User request: {user_prompt}"""
