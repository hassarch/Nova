from abc import ABC, abstractmethod

from nova.execution.result import ExecutionResultData


class ExecutionStrategy(ABC):
    @abstractmethod
    def execute(self, command: str) -> ExecutionResultData:
        pass
