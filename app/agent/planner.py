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
        print(f"Connecting to: {url}")
        
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
      "tool": "terminal",
      "action": "description",
      "command": "command_here",
      "file_path": null,
      "content": null
    }}
  ]
}}

User request:
{user_prompt}
"""
