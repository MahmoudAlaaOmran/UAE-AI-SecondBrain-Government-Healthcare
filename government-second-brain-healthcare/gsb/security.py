"""Synthetic-demo input boundaries and privacy-first safeguards.

Not an enterprise DLP engine. Production use requires independent security testing.
"""
from __future__ import annotations
import re
from typing import Any

# Sensitive patterns are illustrative, deliberately conservative. Never log raw matches.
_RULES = (
    re.compile(r"\b784[- ]?\d{4}[- ]?\d{7}[- ]?\d\b"),  # Emirates ID format
    re.compile(r"\b(?:patient|person|medical)[ _-]?(?:id|identifier|record)[ \t]*[:=][ \t]*\S+", re.I),
    re.compile(r"\b(?:diagnosis|patient name|date of birth|medical record)[ \t]*[:=][ \t]*\S+", re.I),
)

FORBIDDEN_INPUT_KEYS = {"raw_payload", "patient_id", "medical_record", "diagnosis", "date_of_birth", "patient_name"}


def unsafe_text(text: str) -> bool:
    return any(rule.search(text) for rule in _RULES)


def sanitized_question(question: str) -> str:
    if unsafe_text(question):
        raise ValueError("Sensitive or patient-identifying input is not permitted in this demonstration.")
    return question[:500].strip()


def safe_event(event: dict[str, Any]) -> dict[str, Any]:
    """Whitelist event properties to avoid ingesting raw records or identifiers."""
    if any(k.casefold() in FORBIDDEN_INPUT_KEYS for k in event):
        raise ValueError("Raw patient or medical fields are not accepted; provide synthetic aggregates only.")
    flags = event.get("flags") or {}
    metrics = event.get("metrics") or {}
    # Allow only enumerated, boolean flags and numeric synthetic metrics.
    allowed_flags = {
        "privacy_incident", "external_transfer_requested",
        "automatic_eligibility_change_requested", "unverified_policy",
    }
    allowed_metrics = {"baseline_completion_percent", "observed_completion_percent", "complaints_increasing", "repeat_visits_increasing"}
    clean = {
        "id": str(event.get("id", "unknown"))[:24],
        "stage": int(event.get("stage", 0)),
        "title": str(event.get("title", ""))[:80],
        "narrative": str(event.get("narrative", ""))[:650],
        "flags": {k: bool(flags.get(k, False)) for k in allowed_flags},
        "metrics": {k: v for k, v in metrics.items() if k in allowed_metrics and isinstance(v, (int, float, bool))},
        "signals": [str(s)[:100] for s in event.get("signals", [])[:8]],
    }
    for field in ("title", "narrative"):
        if unsafe_text(clean[field]):
            raise ValueError("Event contains potentially identifying data. Refuse ingestion.")
    if any(unsafe_text(x) for x in clean["signals"]):
        raise ValueError("Event signals contain potentially identifying data.")
    return clean
