import shlex
import subprocess

from nova.execution.result import ExecutionResultData
from nova.execution.strategy import ExecutionStrategy


class NativeExecutor(ExecutionStrategy):
    def execute(self, command: str) -> ExecutionResultData:
        try:
            # Check if command contains shell operators
            shell_operators = ["&&", "||", "|", ">", "<", ";", "$", "`", "(", ")"]
            has_shell_operators = any(op in command for op in shell_operators)

            if has_shell_operators:
                # Use shell=True for commands with operators
                # Security: Commands are validated by policy engine before reaching here
                process = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)  # nosec B602
            else:
                # Use shlex.split for simple commands
                args = shlex.split(command)
                process = subprocess.run(args, capture_output=True, text=True, timeout=30)

            return ExecutionResultData(stdout=process.stdout, stderr=process.stderr, return_code=process.returncode)

        except subprocess.TimeoutExpired:
            return ExecutionResultData(stdout="", stderr="Execution timed out", return_code=1)
