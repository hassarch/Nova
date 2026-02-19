import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = os.getenv("DB_NAME")
    DB_USER: Optional[str] = os.getenv("DB_USER")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    OLLAMA_URL: Optional[str] = os.getenv("OLLAMA_URL")
    USE_SANDBOX: bool = os.getenv("USE_SANDBOX", "true").lower() == "true"

    def __init__(self):
        port_str = os.getenv("DB_PORT")
        if port_str:
            try:
                self.DB_PORT = int(port_str)
            except (ValueError, TypeError):
                self.DB_PORT = None


settings = Settings()
