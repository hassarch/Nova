from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class NodeStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionNode(BaseModel):
    """
    Represents a single executable step in the workflow graph.
    """

    id: str
    command: str

    # dependency nodes
    depends_on: List[str] = []

    # runtime settings
    retry_limit: int = 2
    timeout: int = 120

    # runtime state
    status: str = "pending"

    # execution outputs
    stdout: Optional[str] = None
    stderr: Optional[str] = None
