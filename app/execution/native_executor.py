import subprocess
from app.execution.strategy import ExecutionStrategy
from app.execution.result import ExecutionResultData


class NativeExecutor(ExecutionStrategy):

    def execute(self, command: str) -> ExecutionResultData:

        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            return ExecutionResultData(
                stdout=process.stdout,
                stderr=process.stderr,
                return_code=process.returncode
            )

        except subprocess.TimeoutExpired:
            return ExecutionResultData(
                stdout="",
                stderr="Execution timed out",
                return_code=1
            )
