import shlex
import subprocess

from nova.execution.result import ExecutionResultData
from nova.execution.strategy import ExecutionStrategy


class NativeExecutor(ExecutionStrategy):
    def execute(self, command: str) -> ExecutionResultData:
        try:
            # Use shlex.split to safely parse command without shell=True
            args = shlex.split(command)
            process = subprocess.run(args, capture_output=True, text=True, timeout=30)

            return ExecutionResultData(stdout=process.stdout, stderr=process.stderr, return_code=process.returncode)

        except subprocess.TimeoutExpired:
            return ExecutionResultData(stdout="", stderr="Execution timed out", return_code=1)
