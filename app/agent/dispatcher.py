from app.execution.native_executor import NativeExecutor
from app.execution.docker_execution import DockerExecutor
from app.tools.filesystem_tool import FileSystemTool


class ToolDispatcher:

    def __init__(self, use_sandbox: bool = False):

        if use_sandbox:
            self.executor = DockerExecutor()
        else:
            self.executor = NativeExecutor()

        self.filesystem_tool = FileSystemTool()

    def dispatch(self, step: dict):

        if step["tool"] == "terminal" and step["command"]:
            return self.executor.execute(step["command"])

        if step["tool"] == "filesystem":
            return self.filesystem_tool.execute(step)

        return None
