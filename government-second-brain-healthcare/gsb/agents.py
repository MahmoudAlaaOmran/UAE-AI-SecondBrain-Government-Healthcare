"""Six explainable, independently scoped role agents for sequential simulations.

Rules are intentionally reproducible. Optional LLM narrative generation is isolated
from these safety-critical guards. These agents do not represent actual agencies.
"""
from __future__ import annotations
from typing import Any


def make(name: str, finding: str, recommendation: str, policy_ids: list[str], severity: str = "review", blocked: list[str] | None = None) -> dict[str, Any]:
    return {"role": name, "finding": finding, "recommendation": recommendation,
            "policy_ids": policy_ids, "severity": severity, "blocked_actions": blocked or [],
            "human_review_required": True}


def service_journey(events: list[dict[str, Any]]) -> dict[str, Any]:
    baseline = next((e["metrics"].get("baseline_completion_percent") for e in events if "baseline_completion_percent" in e["metrics"]), None)
    observed = next((e["metrics"].get("observed_completion_percent") for e in events if "observed_completion_percent" in e["metrics"]), None)
    delta = round(observed - baseline, 1) if baseline is not None and observed is not None else None
    finding = f"Synthetic journey completion changed from {baseline}% to {observed}% ({delta:+.1f} percentage points). Correlation is not a diagnosis of the root cause." if delta is not None else "Operational root cause has not been established."
    return make("Service Journey Analyst", finding,
                "Inspect anonymized funnel steps and language accessibility; validate instrumentation and interview the service owner before redesign.", ["U3", "I2"])


def policy_adviser(events: list[dict[str, Any]]) -> dict[str, Any]:
    conflict = any(e["flags"].get("unverified_policy") for e in events)
    return make("Policy and Legal Adviser",
                "An outdated or unverified procedural instruction has no established authority for an automated eligibility change." if conflict else "Published health ICT law and AI strategy provide relevant context, but the precise current service-specific authority has not been supplied.",
                "Request a current, officially approved service procedure and legal sign-off. Never infer authority from a strategy or global benchmark.",
                ["U1", "U5", "U2", "U3"], "critical" if conflict else "review",
                ["automatic_eligibility_change"] if conflict else [])


def privacy_guardian(events: list[dict[str, Any]]) -> dict[str, Any]:
    incident = any(e["flags"].get("privacy_incident") for e in events)
    external = any(e["flags"].get("external_transfer_requested") for e in events)
    if incident:
        return make("Privacy and Data Governance Guardian", "Sensitive patient information is reported in a complaint export; treat as restricted until assessed.",
                    "Quarantine the export, prevent external sharing, preserve minimal incident metadata, and refer to authorized privacy, legal and information-security owners for classification and response.",
                    ["U1", "U5", "U2"], "critical", ["restricted_data_ingestion"] + (["external_llm_transfer"] if external else []))
    return make("Privacy and Data Governance Guardian", "Only synthetic aggregate service indicators are available to this prototype.",
                "Retain data minimization and access control; require approvals before any real government health feed is connected.", ["U1", "U2"])


def clinical_safety(events: list[dict[str, Any]]) -> dict[str, Any]:
    auto = any(e["flags"].get("automatic_eligibility_change_requested") for e in events)
    if auto:
        return make("Clinical Safety Reviewer", "Automated eligibility rejection could materially affect patient access and requires competent clinical and legal assessment.",
                    "Block automatic rejection. Consider an accessible manual fallback and request authorized clinical, policy and service-owner review.",
                    ["U1", "G1", "U4"], "critical", ["automatic_eligibility_change"])
    return make("Clinical Safety Reviewer", "No diagnosis or clinical outcome can be determined from aggregate digital journey statistics.",
                "Preserve clinical oversight; use these indicators solely to prioritize operational investigation.", ["G1", "U4"])


def cybersecurity(events: list[dict[str, Any]]) -> dict[str, Any]:
    external = any(e["flags"].get("external_transfer_requested") for e in events)
    return make("Cybersecurity and Assurance Adviser",
                "An external AI upload is proposed without an established authorization path." if external else "No infrastructure compromise is established by the synthetic inputs.",
                "Block unsanctioned external transfer, preserve a safe incident record, and refer to an approved security review." if external else "Ensure least-privilege read access and trace every retrieval/decision.",
                ["U1", "U5", "I1"], "critical" if external else "review", ["external_llm_transfer"] if external else [])


def institutional_coordinator(assessments: list[dict[str, Any]]) -> dict[str, Any]:
    blockers = sorted({b for a in assessments for b in a["blocked_actions"]})
    severity = "critical" if any(a["severity"] == "critical" for a in assessments) else "review"
    return make("Institutional Coordinator",
                f"Independent role assessments received. {len(blockers)} prohibited or gated action type(s) identified; no government mandate is assumed.",
                "Route service diagnosis to the service owner, data incidents to privacy/security, and eligibility-policy conflicts to authorized legal/clinical leadership. Record human decisions and revisit after verified evidence.",
                sorted({id_ for a in assessments for id_ in a["policy_ids"]}), severity, blockers)


def run_agents(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    independent = [service_journey(events), policy_adviser(events), privacy_guardian(events),
                   clinical_safety(events), cybersecurity(events)]
    return [*independent, institutional_coordinator(independent)]
