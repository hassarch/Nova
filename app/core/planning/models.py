from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Step:
    step_id: str
    tool: str
    action: str
    command: str | None
    file_path: str | None
    content: str | None


@dataclass
class Subtask:
    objective: str
    steps: List[Dict[str, Any]]


@dataclass
class GoalPlan:
    goal: str
    subtasks: List[Subtask]
