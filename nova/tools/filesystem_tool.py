import os

from nova.execution.result import ExecutionResultData


class FileSystemTool:
    def execute(self, step: dict, metrics=None) -> ExecutionResultData:
        file_path = step.get("file_path")
        content = step.get("content")
        action = (step.get("action") or "").lower()
        action = step.get("action", "").lower()

        try:
            if not file_path:
                return ExecutionResultData(stdout="", stderr="Missing file_path for filesystem tool", return_code=1)

            base_dir = os.getcwd()
            full_path = os.path.abspath(os.path.join(base_dir, file_path))

            if not full_path.startswith(base_dir):
                return ExecutionResultData(stdout="", stderr="Path traversal attempt detected", return_code=1)

            # READ
            if "read" in action:
                if metrics:
                    metrics.track_read()

                if not os.path.exists(full_path):
                    return ExecutionResultData(stdout="", stderr="File not found", return_code=1)

                with open(full_path, "r") as f:
                    data = f.read()

                return ExecutionResultData(stdout=data, stderr="", return_code=0)

            #  WRITE (default action)
            if metrics:
                metrics.track_write()

            # Handle delete operation
            if "delete" in action:
                if os.path.isfile(full_path):
                    os.remove(full_path)
                    return ExecutionResultData(stdout=f"File deleted: {file_path}", stderr="", return_code=0)
                else:
                    return ExecutionResultData(stdout="", stderr=f"File not found: {file_path}", return_code=1)

            # Create or write file
            with open(full_path, "w") as f:
                if content:
                    f.write(content)

            return ExecutionResultData(stdout=f"File written: {file_path}", stderr="", return_code=0)

        except Exception as e:
            return ExecutionResultData(stdout="", stderr=str(e), return_code=1)
