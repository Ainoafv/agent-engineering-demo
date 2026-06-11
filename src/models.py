"""Strict schemas. The LLM must conform to these or its output is rejected."""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Closed set of actions. Anything outside this fails closed at the gate."""
    DRAFT_REPLY = "draft_reply"      # low risk  -> AUTO
    SEND_EMAIL = "send_email"        # medium    -> ASK (human approves)
    ISSUE_REFUND = "issue_refund"    # high risk -> NEVER auto
    DELETE_RECORD = "delete_record"  # high risk -> NEVER auto
    NO_ACTION = "no_action"          # safe default


class InboundRequest(BaseModel):
    """The trigger entering the agent."""
    request_id: str
    channel: str
    customer: str
    message: str


class AgentDecision(BaseModel):
    """What the model proposes. Validated before anything else looks at it."""
    action: ActionType
    target: str = Field(description="who/what the action applies to")
    reason: str = Field(description="one-line justification, audit-friendly")
    confidence: float = Field(ge=0.0, le=1.0)
    payload: dict = Field(default_factory=dict)


class Permission(str, Enum):
    AUTO = "auto"      # execute now
    ASK = "ask"        # queue for human approval
    NEVER = "never"    # never auto; always human, regardless of confidence


class Verdict(BaseModel):
    permission: Permission
    allowed_to_execute: bool
    note: str
