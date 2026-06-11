"""Tool registry — the only place real side effects can happen.

Mocked here (prints), but in production these are the functions that actually
send email, call Stripe, touch the DB. The gate decides IF they run; this decides HOW.
"""
from __future__ import annotations

from .models import ActionType, AgentDecision


def _send_email(d: AgentDecision) -> str:
    return f"email sent to {d.target} (subject: {d.payload.get('subject', 'reply')})"


def _draft_reply(d: AgentDecision) -> str:
    return f"draft saved for {d.target} — pending nothing, low risk"


def _no_action(d: AgentDecision) -> str:
    return "no-op recorded"


REGISTRY = {
    ActionType.SEND_EMAIL: _send_email,
    ActionType.DRAFT_REPLY: _draft_reply,
    ActionType.NO_ACTION: _no_action,
}


def execute(decision: AgentDecision) -> str:
    handler = REGISTRY.get(decision.action)
    if handler is None:
        # Defense in depth: even if the gate let something through, no handler = no effect.
        raise RuntimeError(f"No executor for {decision.action} — refusing side effect.")
    return handler(decision)
