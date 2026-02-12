import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "phi3",
        "prompt": "Say hello like a DevOps AI agent.",
        "stream": False
    }
)

print(response.json()["response"])
