"""Permission gate. The model proposes; this code decides. Fail closed."""
from __future__ import annotations

from .models import ActionType, AgentDecision, Permission, Verdict

# Explicit policy. Anything not listed is treated as NEVER (fail closed).
POLICY: dict[ActionType, Permission] = {
    ActionType.NO_ACTION: Permission.AUTO,
    ActionType.DRAFT_REPLY: Permission.AUTO,
    ActionType.SEND_EMAIL: Permission.ASK,
    ActionType.ISSUE_REFUND: Permission.NEVER,
    ActionType.DELETE_RECORD: Permission.NEVER,
}

# Even AUTO actions need the model to be reasonably sure.
AUTO_CONFIDENCE_FLOOR = 0.70


def evaluate(decision: AgentDecision) -> Verdict:
    permission = POLICY.get(decision.action, Permission.NEVER)

    if permission is Permission.NEVER:
        return Verdict(permission=permission, allowed_to_execute=False,
                       note="High-impact or unknown action — routed to human, never auto.")

    if permission is Permission.ASK:
        return Verdict(permission=permission, allowed_to_execute=False,
                       note="Queued for human approval before execution.")

    # AUTO — but still gated on confidence.
    if decision.confidence < AUTO_CONFIDENCE_FLOOR:
        return Verdict(permission=Permission.ASK, allowed_to_execute=False,
                       note=f"Confidence {decision.confidence:.2f} below floor "
                            f"{AUTO_CONFIDENCE_FLOOR:.2f} — escalated to human.")

    return Verdict(permission=Permission.AUTO, allowed_to_execute=True,
                   note="Low-risk and confident — auto-executed.")
