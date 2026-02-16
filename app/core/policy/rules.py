import re
from typing import Dict

# Risk scoring rules
HIGH_RISK_COMMANDS = [
    r"\brm\b",
    r"\bchmod\b",
    r"\bchown\b",
    r"\bdocker\b",
]

CRITICAL_PATTERNS = [
    r"\bsudo\b",
    r"\brm\s+-rf\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bmkfs\b",
    r"\bdd\b",
    r":\(\)\{:\|:&\};:",  # fork bomb
]


def evaluate_command(command: str) -> Dict:
    if not command:
        return {"risk": "low", "reason": None}

    # Critical block
    for pattern in CRITICAL_PATTERNS:
        if re.search(pattern, command):
            return {"risk": "critical", "reason": f"Matched critical pattern: {pattern}"}

    # High risk (allowed but flagged)
    for pattern in HIGH_RISK_COMMANDS:
        if re.search(pattern, command):
            return {"risk": "high", "reason": f"High-risk command detected: {pattern}"}

    return {"risk": "low", "reason": None}
