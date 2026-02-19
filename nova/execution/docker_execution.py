import subprocess

from nova.execution.result import ExecutionResultData
from nova.execution.strategy import ExecutionStrategy


class DockerExecutor(ExecutionStrategy):
    def execute(self, command: str) -> ExecutionResultData:
        docker_command = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--memory",
            "256m",
            "--cpus",
            "0.5",
            "-v",
            f"{self._get_current_dir()}:/workspace",
            "-w",
            "/workspace",
            "python:3.11-slim",
            "bash",
            "-c",
            command,
        ]

        try:
            process = subprocess.run(docker_command, capture_output=True, text=True, timeout=60)

            return ExecutionResultData(stdout=process.stdout, stderr=process.stderr, return_code=process.returncode)

        except subprocess.TimeoutExpired:
            return ExecutionResultData(stdout="", stderr="Docker execution timed out", return_code=1)

    def _get_current_dir(self):
        import os

        return os.getcwd()
