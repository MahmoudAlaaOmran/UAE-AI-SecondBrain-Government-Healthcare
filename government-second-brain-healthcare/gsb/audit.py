"""Minimal tamper-evident audit chain: no patient text or secret prompts stored."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def canonical(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class AuditTrail:
    def __init__(self):
        self.entries: list[dict[str, Any]] = []

    def append(self, action: str, detail: dict[str, Any], timestamp: str | None = None) -> dict[str, Any]:
        previous_hash = self.entries[-1]["hash"] if self.entries else "GENESIS"
        payload = {
            "sequence": len(self.entries) + 1,
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            "action": action,
            "detail": detail,
            "previous_hash": previous_hash,
        }
        entry = {**payload, "hash": hashlib.sha256(canonical(payload)).hexdigest()}
        self.entries.append(entry)
        return entry

    def verify(self) -> bool:
        previous_hash = "GENESIS"
        for idx, entry in enumerate(self.entries):
            payload = {k: v for k, v in entry.items() if k != "hash"}
            if entry["sequence"] != idx + 1 or entry["previous_hash"] != previous_hash:
                return False
            if hashlib.sha256(canonical(payload)).hexdigest() != entry["hash"]:
                return False
            previous_hash = entry["hash"]
        return True

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(e, sort_keys=True, ensure_ascii=False) for e in self.entries) + "\n"
