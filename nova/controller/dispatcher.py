from typing import Union

from nova.execution.docker_execution import DockerExecutor
from nova.execution.native_executor import NativeExecutor
from nova.tools.filesystem_tool import FileSystemTool


class ToolDispatcher:
    def __init__(self, use_sandbox: bool = False):
        self.executor: Union[DockerExecutor, NativeExecutor]
        if use_sandbox:
            self.executor = DockerExecutor()
        else:
            self.executor = NativeExecutor()

        self.filesystem_tool = FileSystemTool()

    def dispatch(self, step, metrics=None):
        if step["tool"] == "terminal" and step["command"]:
            return self.executor.execute(step["command"])

        if step["tool"] == "filesystem":
            return self.filesystem_tool.execute(step, metrics)

        return None
