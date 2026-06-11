"""Append-only, hash-chained audit log. Tamper-evident, SQLite-backed.

Each row carries the hash of the previous row, so any edit to history breaks the chain.
In production this is a Postgres table with the same shape.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path

GENESIS = "0" * 64


class AuditLog:
    def __init__(self, path: str = "audit.db") -> None:
        self.path = path
        self._db = sqlite3.connect(path)
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS audit (
                   seq INTEGER PRIMARY KEY AUTOINCREMENT,
                   ts REAL NOT NULL,
                   request_id TEXT NOT NULL,
                   event TEXT NOT NULL,
                   data TEXT NOT NULL,
                   prev_hash TEXT NOT NULL,
                   row_hash TEXT NOT NULL
               )"""
        )
        self._db.commit()

    def _last_hash(self) -> str:
        row = self._db.execute(
            "SELECT row_hash FROM audit ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else GENESIS

    def append(self, request_id: str, event: str, data: dict) -> str:
        ts = time.time()
        prev = self._last_hash()
        body = json.dumps(data, sort_keys=True, default=str)
        digest = hashlib.sha256(
            f"{ts}|{request_id}|{event}|{body}|{prev}".encode()
        ).hexdigest()
        self._db.execute(
            "INSERT INTO audit (ts, request_id, event, data, prev_hash, row_hash) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (ts, request_id, event, body, prev, digest),
        )
        self._db.commit()
        return digest

    def verify_chain(self) -> bool:
        """Recompute every hash; returns False if any row was tampered with."""
        prev = GENESIS
        for ts, rid, event, data, stored_prev, stored_hash in self._db.execute(
            "SELECT ts, request_id, event, data, prev_hash, row_hash FROM audit ORDER BY seq"
        ):
            if stored_prev != prev:
                return False
            recomputed = hashlib.sha256(
                f"{ts}|{rid}|{event}|{data}|{prev}".encode()
            ).hexdigest()
            if recomputed != stored_hash:
                return False
            prev = stored_hash
        return True

    def close(self) -> None:
        self._db.close()


def fresh_log(path: str = "audit.db") -> AuditLog:
    Path(path).unlink(missing_ok=True)
    return AuditLog(path)
