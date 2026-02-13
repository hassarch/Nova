from app.execution.native_executor import NativeExecutor
from app.execution.docker_execution import DockerExecutor


class ToolDispatcher:

    def __init__(self, use_sandbox: bool = True):

        if use_sandbox:
            print("🐳 Using Docker Sandbox Executor")
            self.executor = DockerExecutor()
        else:
            print("⚡ Using Native Executor")
            self.executor = NativeExecutor()

    def dispatch(self, step: dict):

        if step["tool"] == "terminal" and step["command"]:
            return self.executor.execute(step["command"])

        return None
