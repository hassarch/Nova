class FailureType:
    DEPENDENCY_MISSING = "dependency_missing"
    FILE_NOT_FOUND = "file_not_found"
    PORT_IN_USE = "port_in_use"
    GIT_CONFLICT = "git_conflict"
    PERMISSION_DENIED = "permission_denied"
    COMMAND_NOT_FOUND = "command_not_found"
    SYNTAX_ERROR = "syntax_error"
    UNKNOWN = "unknown"


class FailureClassifier:

    @staticmethod
    def classify(stderr: str) -> str:

        if not stderr:
            return FailureType.UNKNOWN

        stderr_lower = stderr.lower()

        if "modulenotfounderror" in stderr_lower:
            return FailureType.DEPENDENCY_MISSING

        if "no such file or directory" in stderr_lower:
            return FailureType.FILE_NOT_FOUND

        if "address already in use" in stderr_lower:
            return FailureType.PORT_IN_USE

        if "permission denied" in stderr_lower:
            return FailureType.PERMISSION_DENIED

        if "not a git repository" in stderr_lower:
            return FailureType.GIT_CONFLICT

        if "command not found" in stderr_lower:
            return FailureType.COMMAND_NOT_FOUND

        if "syntaxerror" in stderr_lower:
            return FailureType.SYNTAX_ERROR

        return FailureType.UNKNOWN
