"""Thin orchestration. Every step is explicit and logged — no hidden control flow."""
from __future__ import annotations

from dataclasses import dataclass

from . import llm, tools
from .audit import AuditLog
from .gate import evaluate
from .models import InboundRequest, Permission


@dataclass
class Outcome:
    request_id: str
    action: str
    permission: str
    executed: bool
    result: str


class Agent:
    def __init__(self, audit: AuditLog) -> None:
        self.audit = audit

    def handle(self, req: InboundRequest) -> Outcome:
        self.audit.append(req.request_id, "received", req.model_dump())

        decision = llm.decide(req)
        self.audit.append(req.request_id, "decided", decision.model_dump())

        verdict = evaluate(decision)
        self.audit.append(req.request_id, "gated", verdict.model_dump())

        if verdict.allowed_to_execute:
            result = tools.execute(decision)
            self.audit.append(req.request_id, "executed", {"result": result})
            return Outcome(req.request_id, decision.action.value,
                           verdict.permission.value, True, result)

        # Not allowed to auto-run: queue for a human. No side effect happens.
        queued = "QUEUED FOR HUMAN APPROVAL"
        if verdict.permission is Permission.NEVER:
            queued = "BLOCKED — human-only action"
        self.audit.append(req.request_id, "queued", {"note": verdict.note})
        return Outcome(req.request_id, decision.action.value,
                       verdict.permission.value, False, f"{queued} — {verdict.note}")
