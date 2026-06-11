# Loom script — Adrienne / ELLMO AI (target 5 min, async instead of a call)

> Interactive version (try it yourself, no install): https://ainoafv.github.io/agent-engineering-demo/
> Repo (Python engine + tests): https://github.com/Ainoafv/agent-engineering-demo


Record screen + voice. Two windows: editor (left) + terminal (right). Keep it calm, no rush.

---

## 0:00 — Hook (15s)
"Hi Adrienne, Ainoa here. Instead of a call, I built you a tiny runnable agent that
shows exactly how I keep LLM agents safe in production. Same patterns I run in
regulated clinical AI today. Let me walk you through it — about 5 minutes."

## 0:15 — The shape (30s)
Show README diagram. Read it out:
"Inbound request → fetch context → the LLM *proposes* an action as strict JSON →
a permission gate *decides* → we either execute, or queue for a human → and every
step lands in an append-only audit log. The model never touches a side effect directly."

## 0:45 — Run it first (45s)
Terminal: `python run_demo.py`
Point at the output:
- "Pricing request → send_email → gate says ASK → queued for a human."
- "Refund and GDPR-delete → NEVER → blocked, human-only, no matter how confident the model is."
- "A thanks and a simple question → low risk → auto-executed."
- "And the audit chain verifies — tamper-evident."
"Zero API key for this run — it's in mock mode so it's reproducible. Flip LLM_MODE=openai
and the exact same code runs against a real model."

## 1:30 — models.py (40s)
"Everything starts with strict schemas. The action set is closed — five actions, nothing
else. If the model returns anything off-schema, Pydantic rejects it before it reaches my
logic. That's the first safety layer."

## 2:10 — llm.py (40s)
"One interface, two backends — mock and OpenAI. The agent never knows which is live.
With OpenAI I use JSON-mode structured output, then validate it. Swapping models or
providers is a one-line change, not a refactor."

## 2:50 — gate.py (60s) — the important part
"This is where I'd earn my keep. The model proposes; this code decides. A policy table maps
each action to AUTO, ASK, or NEVER. Refunds and deletes are NEVER auto — always a human.
And it's fail-closed: anything not in the table defaults to NEVER. Even AUTO actions have a
confidence floor — if the model isn't sure, it escalates instead of guessing."

## 3:50 — audit.py + tests (50s)
"Audit log is append-only and hash-chained — each row hashes the one before it, so editing
history breaks the chain. `verify_chain()` proves it. And the safety rules aren't a promise —
they're tested." Run `pytest -q`, show 4 passed.

## 4:40 — Close + the ask (30s)
"That's the skeleton. For ELLMO I'd shape the actions, tools, and policy around your real
workflow — internal tooling or customer-facing, greenfield Postgres or extending yours.
I work async-first with same-day replies and end-of-day written updates. Happy to do a live
session once my event wraps, but I wanted you to have something concrete now. Looking
forward to it — thanks!"

---

### Tips
- Mention the SERGAS / clinical angle once (credibility), don't dwell.
- Don't read code line by line — point at the *idea* per file.
- Re-run `python run_demo.py` at the end if you want a clean final frame.
- Upload to Loom, paste the link in Upwork chat (Loom links are allowed; WhatsApp is not).
