from app.execution.native_executor import NativeExecutor
from app.execution.result import ExecutionResultData
import os


class ToolDispatcher:

    def __init__(self):
        self.executor = NativeExecutor()

    def dispatch(self, step: dict):
        """Execute a single step from the plan"""
        
        print(f"\n▶ Executing step {step['step_id']} using {step['tool']}")

        if step["tool"] == "terminal" and step["command"]:
            result = self.executor.execute(step["command"])
            print(f"✓ Command executed")
            return result
        
        elif step["tool"] == "filesystem":
            file_path = step.get("file_path")
            content = step.get("content")
            
            if file_path and content:
                try:
                    # Create directories if they don't exist
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Write the file
                    with open(file_path, 'w') as f:
                        f.write(content)
                    
                    print(f"✓ File created at {file_path}")
                    
                    return ExecutionResultData(
                        stdout=f"File created successfully at {file_path}",
                        stderr="",
                        return_code=0
                    )
                except Exception as e:
                    return ExecutionResultData(
                        stdout="",
                        stderr=str(e),
                        return_code=1
                    )
        
        return None
