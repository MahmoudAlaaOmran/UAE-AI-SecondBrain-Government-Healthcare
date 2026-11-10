"""Progressive error-scenario engine and oversight gate."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .agents import run_agents
from .audit import AuditTrail
from .kb import PolicyKnowledgeBase, ROOT
from .security import safe_event, sanitized_question


def load_scenarios(path: str | Path | None = None) -> list[dict[str, Any]]:
    source = Path(path) if path else ROOT / "data" / "scenarios.json"
    events = json.loads(source.read_text(encoding="utf-8"))
    return [safe_event(e) for e in sorted(events, key=lambda e: e["stage"])]


def run_simulation(stage: int, kb: PolicyKnowledgeBase | None = None, question: str = "") -> dict[str, Any]:
    if stage not in (1, 2, 3):
        raise ValueError("Stage must be 1, 2 or 3.")
    question = sanitized_question(question) if question else ""
    kb = kb or PolicyKnowledgeBase.from_file()
    events = load_scenarios()[:stage]
    audit = AuditTrail()
    for event in events:
        audit.append("event_released", {"event_id": event["id"], "stage": event["stage"], "flags": event["flags"]})
    query = "healthcare medical fitness service digital journey patient privacy government AI human authorization " + " ".join(e["title"] for e in events) + " " + question
    evidence = kb.search(query, limit=6)
    audit.append("evidence_retrieval", {"source_ids": [p["id"] for p in evidence], "source_count": len(evidence)})
    assessments = run_agents(events)
    for agent in assessments:
        audit.append("agent_assessment", {"role": agent["role"], "severity": agent["severity"], "policy_ids": agent["policy_ids"], "blocked_actions": agent["blocked_actions"]})
    blocked = sorted({a for assessment in assessments for a in assessment["blocked_actions"]})
    approval_required = True  # structural safeguard: no automatic high-stakes action
    decision = {
        "status": "Escalated for human authorization" if blocked else "Investigation requested; human approval required",
        "human_approval_required": approval_required,
        "blocked_actions": blocked,
        "next_owner": "Authorized service owner with privacy, legal, clinical and security reviewers" if blocked else "Authorized service owner",
        "recommended_next_step": "No autonomous eligibility, treatment, data disclosure or final legal decisions. Request verified evidence and documented human review.",
    }
    audit.append("decision_gate", {"approved": False, "human_approval_required": True, "blocked_actions": blocked})
    mapped_citations = {id_ for agent in assessments for id_ in agent["policy_ids"]}
    citations = [kb.by_id(id_) for id_ in sorted(mapped_citations) if kb.by_id(id_)]
    return {
        "project": "Government Second Brain in Healthcare", "mode": "Synthetic policy-grounded demonstration",
        "stage": stage, "events": events, "assessments": assessments, "citations": citations,
        "retrieval": evidence, "decision": decision,
        "evaluation": {
            "role_assessments": len(assessments), "cited_policy_records": len(citations),
            "blocked_action_types": len(blocked), "restricted_external_transfer_blocked": "external_llm_transfer" in blocked,
            "clinical_eligibility_automation_blocked": "automatic_eligibility_change" in blocked,
            "human_gate_active": approval_required, "audit_chain_valid": audit.verify(),
            "note": "Demonstration assertions only, not independently validated real-world performance metrics."
        },
        "audit": audit.entries,
    }
