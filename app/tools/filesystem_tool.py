import os
from app.execution.result import ExecutionResultData


class FileSystemTool:

    def execute(self, step: dict) -> ExecutionResultData:

        file_path = step.get("file_path")
        content = step.get("content")

        try:
            if not file_path:
                return ExecutionResultData(
                    stdout="",
                    stderr="Missing file_path for filesystem tool",
                    return_code=1
                )

            # Ensure path is inside current working directory
            base_dir = os.getcwd()
            full_path = os.path.abspath(os.path.join(base_dir, file_path))

            if not full_path.startswith(base_dir):
                return ExecutionResultData(
                    stdout="",
                    stderr="Path traversal attempt detected",
                    return_code=1
                )

            # Create or write file
            with open(full_path, "w") as f:
                if content:
                    f.write(content)

            return ExecutionResultData(
                stdout=f"File created: {file_path}",
                stderr="",
                return_code=0
            )

        except Exception as e:
            return ExecutionResultData(
                stdout="",
                stderr=str(e),
                return_code=1
            )
