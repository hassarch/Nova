from app.core.recovery.failure_classifier import FailureType


class StrategyEngine:

    def get_strategy(self, failure_type: str, original_step: dict):

        if failure_type == FailureType.DEPENDENCY_MISSING:
            return self._install_missing_dependency(original_step)

        if failure_type == FailureType.PORT_IN_USE:
            return self._change_port(original_step)

        if failure_type == FailureType.FILE_NOT_FOUND:
            return self._create_missing_file(original_step)

        # Unknown failures fallback to LLM retry
        return None

    def _install_missing_dependency(self, original_step):
        return {
            "tool": "terminal",
            "action": "Install dependency",
            "command": "pip install -r requirements.txt",
            "file_path": None,
            "content": None
        }

    def _change_port(self, original_step):
        return {
            "tool": original_step.get("tool"),
            "action": "Retry with different port",
            "command": original_step.get("command", "").replace("8000", "8001"),
            "file_path": None,
            "content": None
        }

    def _create_missing_file(self, original_step):
        return {
            "tool": "filesystem",
            "action": "Create missing file",
            "command": None,
            "file_path": original_step.get("file_path"),
            "content": ""
        }
