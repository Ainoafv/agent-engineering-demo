# Agent Engineering Demo — production patterns in ~300 lines

A tiny, runnable agent that shows the patterns I bring to production agentic systems:

```
inbound request
  -> fetch context
  -> LLM decides (strict JSON, Pydantic-validated)
  -> permission gate (AUTO / ASK / NEVER) — fail closed
  -> execute side effect  OR  queue for human approval
  -> append-only audit log (hash-chained, tamper-evident)
```

This is **not** the client's product. It's a clean, debuggable skeleton that demonstrates
how I keep LLM agents safe: the model *proposes*, code *decides*, every action is logged,
and anything not explicitly allowed never runs.

## Run it (no API key needed)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_demo.py            # mock LLM, deterministic — perfect for a walkthrough
```

With a real model:

```bash
export OPENAI_API_KEY=sk-...
export LLM_MODE=openai
python run_demo.py
```

## What to look at

| File | Pattern it demonstrates |
|------|-------------------------|
| `src/models.py` | Strict schemas — the LLM must return valid JSON or we reject it |
| `src/llm.py` | Provider swap (mock / OpenAI) behind one interface; structured output |
| `src/gate.py` | Permission ladder, **fail-closed**: unknown action = denied |
| `src/audit.py` | Append-only, hash-chained audit log (tamper-evident) |
| `src/agent.py` | Thin orchestration — no magic, fully traceable |
| `tests/test_gate.py` | The safety guarantees are tested, not assumed |

## Why it matters for your agents

The whole point of production agents is **not trusting the model with side effects**.
High-risk actions (refunds, deletes, sends) route to a human; low-risk drafts auto-execute;
unknown actions fail closed. Same discipline I run in regulated clinical AI today.
