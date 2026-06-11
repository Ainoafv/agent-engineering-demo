"""The safety guarantees are tested, not assumed."""
from src.gate import evaluate, AUTO_CONFIDENCE_FLOOR
from src.models import ActionType, AgentDecision, Permission


def _d(action: ActionType, conf: float = 0.95) -> AgentDecision:
    return AgentDecision(action=action, target="x", reason="t", confidence=conf)


def test_high_risk_never_auto_executes():
    for action in (ActionType.ISSUE_REFUND, ActionType.DELETE_RECORD):
        v = evaluate(_d(action, conf=1.0))
        assert v.permission is Permission.NEVER
        assert v.allowed_to_execute is False


def test_send_email_requires_human():
    v = evaluate(_d(ActionType.SEND_EMAIL))
    assert v.allowed_to_execute is False


def test_low_risk_high_confidence_auto_runs():
    v = evaluate(_d(ActionType.DRAFT_REPLY, conf=0.9))
    assert v.allowed_to_execute is True


def test_low_confidence_escalates_even_for_auto_action():
    v = evaluate(_d(ActionType.DRAFT_REPLY, conf=AUTO_CONFIDENCE_FLOOR - 0.01))
    assert v.allowed_to_execute is False
    assert v.permission is Permission.ASK
