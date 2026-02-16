import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    OLLAMA_URL = os.getenv("OLLAMA_URL")
    USE_SANDBOX = os.getenv("USE_SANDBOX", "true").lower() == "true"


settings = Settings()
