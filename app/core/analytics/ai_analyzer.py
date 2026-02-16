import requests

from app.config.settings import settings
from app.core.analytics.queries import get_session_summary


class AIAnalyzer:
    def __init__(self, db):
        self.db = db

    def analyze(self):
        summary = get_session_summary(self.db)

        prompt = self._build_prompt(summary)

        payload = {"model": "llama3", "prompt": prompt, "stream": False}

        response = requests.post(f"{settings.OLLAMA_URL}/api/generate", json=payload, timeout=120)

        if response.status_code != 200:
            raise Exception("Failed to connect to Ollama")

        return response.json()["response"]

    def _build_prompt(self, summary: dict):
        return f"""
You are an AI system performance analyst.

Analyze the following NOVA system metrics:

{summary}

Provide:
1. System health assessment
2. Failure risk analysis
3. Retry efficiency analysis
4. Suggested improvements
5. Observed anomalies

Respond in clean structured text.
"""
