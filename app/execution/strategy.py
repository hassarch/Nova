from abc import ABC, abstractmethod

from app.execution.result import ExecutionResultData


class ExecutionStrategy(ABC):
    @abstractmethod
    def execute(self, command: str) -> ExecutionResultData:
        pass
