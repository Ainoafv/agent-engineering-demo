"""LLM provider behind one interface. Mock by default; OpenAI when configured.

The agent code never cares which is active — same contract, same validated output.
"""
from __future__ import annotations

import json
import os

from .models import AgentDecision, ActionType, InboundRequest

SYSTEM_PROMPT = (
    "You are a support triage agent. Read the inbound request and choose exactly "
    "one action from this set: draft_reply, send_email, issue_refund, delete_record, "
    "no_action. Return STRICT JSON with keys: action, target, reason, confidence "
    "(0..1), payload (object). Never invent actions outside the set."
)


def _mock_decision(req: InboundRequest) -> AgentDecision:
    """Deterministic, keyword-driven — so a walkthrough is reproducible."""
    text = req.message.lower()
    if "refund" in text or "money back" in text:
        return AgentDecision(
            action=ActionType.ISSUE_REFUND, target=req.customer,
            reason="Customer explicitly requests a refund.",
            confidence=0.91, payload={"amount_hint": "from order history"},
        )
    if "delete" in text or "gdpr" in text or "erase" in text:
        return AgentDecision(
            action=ActionType.DELETE_RECORD, target=req.customer,
            reason="Data erasure request — high impact.", confidence=0.88,
        )
    if "thanks" in text or "great" in text:
        return AgentDecision(
            action=ActionType.NO_ACTION, target=req.customer,
            reason="Positive message, no action needed.", confidence=0.72,
        )
    if "quote" in text or "pricing" in text or "send me" in text:
        return AgentDecision(
            action=ActionType.SEND_EMAIL, target=req.customer,
            reason="Customer asks for info to be sent.", confidence=0.83,
            payload={"subject": "Your requested details"},
        )
    return AgentDecision(
        action=ActionType.DRAFT_REPLY, target=req.customer,
        reason="General question — draft a reply for review.", confidence=0.79,
    )


def _openai_decision(req: InboundRequest) -> AgentDecision:
    from openai import OpenAI

    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    resp = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.model_dump_json()},
        ],
    )
    raw = resp.choices[0].message.content or "{}"
    # Validation is the safety net: malformed model output never reaches the gate.
    return AgentDecision.model_validate(json.loads(raw))


def decide(req: InboundRequest) -> AgentDecision:
    mode = os.getenv("LLM_MODE", "mock").lower()
    if mode == "openai":
        return _openai_decision(req)
    return _mock_decision(req)
