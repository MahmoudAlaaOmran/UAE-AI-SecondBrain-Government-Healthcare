"""Explicitly opted-in AI-generated narrative; deterministic guardrails remain authoritative.

For synthetic examples only. Never submit real patient/government data or uploaded files.
"""
from __future__ import annotations
import json
import os
from typing import Any


def enabled() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def summarize_synthetic(result: dict[str, Any], *, consent: bool = False) -> str:
    if not consent:
        raise PermissionError("External API usage requires explicit consent for this run.")
    if not enabled():
        raise RuntimeError("OPENAI_API_KEY not configured.")
    from openai import OpenAI
    client = OpenAI()
    # Strictly controlled fields only: never transmit event narrative, user question, or documents.
    payload = {
        "stage": result["stage"],
        "roles": [{"role": a["role"], "finding": a["finding"], "recommendation": a["recommendation"], "policy_ids": a["policy_ids"]} for a in result["assessments"]],
        "decision": result["decision"],
    }
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        instructions=("Produce a concise 150-word executive briefing for a SYNTHETIC healthcare-service simulation. "
                      "Use only supplied assessments; cite source IDs, never fabricate regulatory text or approvals. "
                      "Do not propose patient eligibility decisions, clinical actions, external data transfer or any autonomous high-stakes action. "
                      "All actions require human review. This is not legal or clinical advice."),
        input=json.dumps(payload, ensure_ascii=False),
        max_output_tokens=350,
    )
    return response.output_text

ROLE_QUESTIONS = {
    "Service Journey Analyst": "Identify alternative operational hypotheses and missing evidence, without claiming causation.",
    "Policy and Legal Adviser": "Identify possible relevant policy scope and unresolved authority, without stating a binding legal opinion.",
    "Privacy and Data Governance Guardian": "Identify privacy safeguards and required escalation; never authorize transfer.",
    "Clinical Safety Reviewer": "Identify patient access risks and human clinical governance needs; no diagnosis or eligibility decision.",
    "Cybersecurity and Assurance Adviser": "Identify protective security controls and reporting needs, without claiming a confirmed breach.",
}


def run_role_model_reviews(result: dict[str, Any], *, consent: bool = False) -> list[dict[str, str]]:
    """Optional distinct model calls for independently scoped synthetic role advice.

    No user question, event narrative, personal data or confidential documents are sent.
    Outputs are displayed as *untrusted advisory commentary* and never alter the gate.
    """
    if not consent:
        raise PermissionError("External AI calls require explicit opt-in.")
    if not enabled():
        raise RuntimeError("OPENAI_API_KEY not configured.")
    from openai import OpenAI
    client = OpenAI()
    reviews = []
    for assessment in result["assessments"]:
        role = assessment["role"]
        if role not in ROLE_QUESTIONS:
            continue
        refs = [p for p in result["citations"] if p["id"] in assessment["policy_ids"]]
        allowlisted = {
            "role": role,
            "role_question": ROLE_QUESTIONS[role],
            "simulation_stage": result["stage"],
            "known_synthetic_events": [e["id"] for e in result["events"]],
            "role_findings": assessment["finding"],
            "rule_based_recommendation": assessment["recommendation"],
            "blocked_actions": assessment["blocked_actions"],
            "official_source_pointers": [{"id": p["id"], "title": p["title"], "summary": p["summary"]} for p in refs],
        }
        answer = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            instructions=("You are a simulation agent reviewing public-policy summaries and synthetic government healthcare incidents. "
                          "Provide up to 110 words of additional role-specific observations, plausible alternatives, and uncertainties. "
                          "Use only supplied facts, cite policy IDs when relevant and state that summarized sources need verification. "
                          "Do not alter blocked actions, authorize policy or clinical decisions, infer patient information, or invent legal mandates. "
                          "Do not give a chain of thought; give only a brief, auditable conclusion."),
            input=json.dumps(allowlisted, ensure_ascii=False),
            max_output_tokens=250,
        )
        reviews.append({"role": role, "model_advice": answer.output_text})
    return reviews
