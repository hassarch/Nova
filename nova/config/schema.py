"""NOVA Configuration Schema"""
from typing import List

from pydantic import BaseModel, Field


class NovaConfig(BaseModel):
    """NOVA configuration model with sensible defaults"""

    model: str = Field(default="llama3", description="LLM model to use")
    strict_git: bool = Field(default=True, description="Enforce git safety checks")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    sandbox_mode: bool = Field(default=False, description="Run commands in Docker sandbox")
    default_simulation: bool = Field(default=False, description="Default to simulation mode")
    max_execution_time: int = Field(default=60, description="Max execution time in seconds")
    protected_branches: List[str] = Field(default=["main", "master"], description="Branches protected from modifications")
    log_level: str = Field(default="info", description="Logging level (debug, info, warning, error)")

    class Config:
        """Pydantic config"""

        extra = "allow"  # Allow extra fields for future extensibility
