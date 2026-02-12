import re


FORBIDDEN_PATTERNS = [
    r"\bsudo\b",
    r"\brm\s+-rf\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bmkfs\b",
    r"\bdd\b",
    r":\(\)\{:\|:&\};:",  # fork bomb
]


class CommandSecurityError(Exception):
    pass


class CommandValidator:

    @staticmethod
    def validate(command: str):

        if not command:
            return

        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, command):
                raise CommandSecurityError(
                    f"Blocked unsafe command pattern: {pattern}"
                )
