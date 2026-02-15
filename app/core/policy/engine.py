from app.core.policy.models import PolicyDecision
from app.core.policy.rules import evaluate_command


class PolicyEngine:

    def evaluate(self, step: dict) -> PolicyDecision:

        command = step.get("command")

        result = evaluate_command(command)

        risk = result["risk"]
        reason = result["reason"]

        if risk == "critical":
            return PolicyDecision(
                allowed=False,
                risk_level="critical",
                reason=reason
            )

        if risk == "high":
            return PolicyDecision(
                allowed=True,
                risk_level="high",
                reason=reason
            )

        return PolicyDecision(
            allowed=True,
            risk_level="low",
            reason=None
        )
