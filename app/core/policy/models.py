from dataclasses import dataclass
from typing import Optional


@dataclass
class PolicyDecision:
    allowed: bool
    risk_level: str  # low | medium | high | critical
    reason: Optional[str] = None
