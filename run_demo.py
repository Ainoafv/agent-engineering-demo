"""Walkthrough entry point. Runs four scenarios that exercise every gate path."""
from __future__ import annotations

import os

from src.agent import Agent
from src.audit import fresh_log
from src.models import InboundRequest

SCENARIOS = [
    InboundRequest(request_id="req-001", channel="email", customer="ana@acme.io",
                   message="Hi, can you send me pricing for the team plan?"),
    InboundRequest(request_id="req-002", channel="chat", customer="rob@globex.com",
                   message="This is broken and I want my money back / a refund now."),
    InboundRequest(request_id="req-003", channel="email", customer="li@initech.dev",
                   message="Please delete my account and erase my data (GDPR)."),
    InboundRequest(request_id="req-004", channel="chat", customer="sam@hooli.xyz",
                   message="Thanks, that worked great!"),
    InboundRequest(request_id="req-005", channel="email", customer="mia@umbrella.co",
                   message="Quick question — does the export support CSV as well?"),
]

BAR = "-" * 72


def main() -> None:
    mode = os.getenv("LLM_MODE", "mock")
    print(f"\nAgent demo — LLM_MODE={mode}\n{BAR}")

    audit = fresh_log()
    agent = Agent(audit)

    for req in SCENARIOS:
        out = agent.handle(req)
        flag = "EXEC " if out.executed else "HOLD "
        print(f"[{flag}] {out.request_id}  action={out.action:<14} "
              f"gate={out.permission:<5} -> {out.result}")

    print(BAR)
    ok = audit.verify_chain()
    print(f"Audit chain integrity: {'OK (tamper-evident)' if ok else 'BROKEN'}")
    print(f"Audit rows written to: {audit.path}\n")
    audit.close()


if __name__ == "__main__":
    main()
