from dataclasses import dataclass


@dataclass
class ExecutionResultData:
    stdout: str
    stderr: str
    return_code: int
