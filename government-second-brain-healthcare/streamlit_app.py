"""Interactive UI for Government Second Brain in Healthcare.

Run: streamlit run streamlit_app.py
All initial data and scenario numbers are SYNTHETIC.
"""
import json
import os
from pathlib import Path
import streamlit as st

from gsb.kb import PolicyKnowledgeBase
from gsb.orchestrator import load_scenarios, run_simulation
from gsb.audit import AuditTrail
from gsb.security import unsafe_text
from gsb import llm

st.set_page_config(page_title="Government Second Brain | Healthcare", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.block-container {padding-top: 1.7rem; max-width: 1320px}
.hero {border-radius: 17px; background: linear-gradient(110deg, #102A3F, #076E7D); padding: 24px 28px; color:white; margin-bottom:15px}
.hero h1 {color:white; font-size:2.15rem; margin:0 0 5px 0}
.hero p {color:#E0EFF2; margin:0; font-size:1.05rem}
.kicker {color:#9CD3DC; font-size:.75rem; font-weight:700; letter-spacing:.11em}
.panel {background:#F1F6F8; border:1px solid #D9E7EA; border-radius:12px; padding:14px 18px; margin:12px 0}
.agenthead {font-weight:760; font-size:1.02rem}
small.note {font-size:.8rem; color:#647986}
</style>
""", unsafe_allow_html=True)

kb = PolicyKnowledgeBase.from_file()
scenarios = load_scenarios()
with st.sidebar:
    st.markdown("### Government Second Brain")
    st.caption("AI for Good Lab · UAE 2026")
    page = st.radio("Navigate", ["Decision Lab", "Policy Knowledge Base", "Audit and Evaluation", "Architecture and Safety"], label_visibility="collapsed")
    st.divider()
    st.info("Public hackathon prototype. All journey metrics and incident events are synthetic. **Never enter patient data or government-confidential information.**")
    st.caption("Offline by default · Six role-specific agents · Human approval gate")

st.markdown("""<div class="hero"><div class="kicker">HEALTHCARE GOVERNANCE  /  PROPOSED RESEARCH PROTOTYPE</div>
<h1>Government Second Brain in Healthcare</h1><p>A policy-grounded, multi-agent institutional decision-support sandbox.</p></div>""", unsafe_allow_html=True)

if "report" not in st.session_state:
    st.session_state.report = run_simulation(1, kb)

if page == "Decision Lab":
    st.subheader("Scenario replay: Medical-fitness service disruption")
    st.write("Events are disclosed sequentially, simulating incomplete information received by different institutional actors. No agent is authorized to decide patient eligibility or change government services.")
    stage = st.radio("Release a stage", [1, 2, 3], format_func=lambda n: f"T{n} — {scenarios[n-1]['title']}", horizontal=True)
    with st.form("run_form"):
        question = st.text_input("Optional executive question (synthetic text only)", value="What should a service owner investigate, and who must approve the response?", max_chars=500)
        pressed = st.form_submit_button("Run six agents and policy gate", type="primary", use_container_width=True)
    if pressed:
        try:
            st.session_state.report = run_simulation(stage, kb, question)
        except ValueError as exc:
            st.error(str(exc))
    r = st.session_state.report
    st.caption(f"Currently evaluated: stage T{r['stage']}. Click the button to apply the selected stage.")
    cols = st.columns(4)
    cols[0].metric("Independent roles", "5 + coordinator")
    cols[1].metric("Policy references", len(r["citations"]))
    cols[2].metric("Blocked action types", len(r["decision"]["blocked_actions"]))
    cols[3].metric("Human approval gate", "ACTIVE")

    with st.expander("Released event timeline", expanded=True):
        for e in r["events"]:
            st.markdown(f"**{e['id']}: {e['title']}** — {e['narrative']}")
            if e["metrics"].get("baseline_completion_percent") is not None:
                before = e["metrics"]["baseline_completion_percent"]
                after = e["metrics"]["observed_completion_percent"]
                st.caption(f"Synthetic completion: {before}% → {after}% ({after-before:+g} percentage points). Not a measured government statistic.")

    st.subheader("Independent agent assessments")
    acols = st.columns(2)
    for index, a in enumerate(r["assessments"]):
        with acols[index % 2]:
            with st.container(border=True):
                st.markdown(f"**{a['role']}**")
                st.caption("Critical escalation" if a["severity"] == "critical" else "Assessment for review")
                st.write(a["finding"])
                st.markdown("**Suggested action**")
                st.write(a["recommendation"])
                st.caption("References: " + ", ".join(a["policy_ids"]))
                if a["blocked_actions"]:
                    st.error("Blocked: " + ", ".join(a["blocked_actions"]))

    st.subheader("Institutional oversight gate")
    with st.container(border=True):
        st.warning(r["decision"]["status"])
        st.write(r["decision"]["recommended_next_step"])
        st.markdown("**Review owner:** " + r["decision"]["next_owner"])
        st.markdown("**Blocked actions:** " + (", ".join(r["decision"]["blocked_actions"]) if r["decision"]["blocked_actions"] else "None identified in this stage"))
        st.caption("The platform records a proposed action packet; it does not simulate a fictitious official approval.")
    st.download_button("Download JSON evidence packet", json.dumps(r, indent=2, ensure_ascii=False), file_name=f"gsb-stage-{r['stage']}-evidence.json", mime="application/json")

    with st.expander("Optional AI-generated executive summary"):
        st.write("Default mode is fully offline. An external AI provider is used only if an API key is configured and you explicitly opt in. Only structured synthetic role assessments and public-source summaries are transmitted. AI commentary cannot override hard safety blocks.")
        if not llm.enabled():
            st.caption("No OPENAI_API_KEY configured. The deterministic demonstration above is fully usable without one.")
        opt_in = st.checkbox("I consent to send synthetic agent assessments to the configured external AI provider", disabled=not llm.enabled())
        if st.button("Generate optional executive briefing", disabled=not (llm.enabled() and opt_in)):
            try:
                st.write(llm.summarize_synthetic(r, consent=opt_in))
            except Exception as exc:
                st.error(f"AI briefing unavailable: {type(exc).__name__}. Review deployment configuration.")
        if st.button("Ask five independently prompted AI roles", disabled=not (llm.enabled() and opt_in)):
            try:
                with st.spinner("Evaluating synthetic scenario through independent model roles..."):
                    reviews = llm.run_role_model_reviews(r, consent=opt_in)
                for review in reviews:
                    st.markdown(f"**{review['role']} — advisory model response**")
                    st.write(review["model_advice"])
                st.caption("Advisory model text only. Original deterministic policy, privacy and approval decisions remain unchanged.")
            except Exception as exc:
                st.error(f"AI role reviews unavailable: {type(exc).__name__}. Review deployment configuration.")

elif page == "Policy Knowledge Base":
    st.subheader("Source registry and transparent retrieval")
    st.write("All records are summarized pointers to authoritative documents or non-binding benchmarks. They are **not the full legal texts**, and retrieved summaries do not constitute legal advice.")
    query = st.text_input("Search indexed policy summaries", value="health information confidentiality patient privacy")
    if query and unsafe_text(query):
        st.error("Do not enter identifiers or clinical record content.")
    elif query:
        matches = kb.search(query, limit=8)
        if not matches:
            st.info("No indexed reference matched. Consult a qualified policy owner; the registry is not comprehensive.")
        for rec in matches:
            with st.expander(f"[{rec['id']}] {rec['title']} (similarity {rec['score']:.3f})", expanded=rec == matches[0]):
                st.write(rec["summary"])
                st.caption(f"{rec['issuer']} · {rec['type']} · {rec['scope']} · Verified {rec['last_verified']}")
                st.markdown(f"[Open original source]({rec['source_url']})")
    st.download_button("Download source registry JSON", json.dumps(kb.records, indent=2, ensure_ascii=False), file_name="public-policy-source-registry.json", mime="application/json")

elif page == "Audit and Evaluation":
    r = st.session_state.report
    st.subheader("Decision audit: reviewable and tamper-evident")
    st.write("Every synthetic event, retrieval, role assessment and decision gate receives an ordered SHA-256-linked audit record. The prototype does not record private model chain-of-thought or patient information.")
    trail = AuditTrail()
    trail.entries = r["audit"]
    st.success("Hash chain valid" if trail.verify() else "Hash chain verification failed")
    st.dataframe([{"seq": e["sequence"], "action": e["action"], "event/role": e["detail"].get("event_id", e["detail"].get("role", "")), "hash": e["hash"][:14] + "…"} for e in r["audit"]], use_container_width=True, hide_index=True)
    st.download_button("Download JSONL audit log", trail.to_jsonl(), file_name=f"gsb-stage-{r['stage']}-audit.jsonl", mime="application/jsonl")
    st.subheader("Scenario evaluation checks")
    st.json(r["evaluation"])
    st.caption("Metrics here describe controlled test checks, not external accuracy measurements, legal certification, or production reliability.")

else:
    st.subheader("Architecture and ITU-T Y.3172 mapping")
    st.code("Official public sources + synthetic events\n        ↓ SRC\nRead-only connectors and provenance registry\n        ↓ C\nSanitization → metadata → TF-IDF vector index\n        ↓ PP\nFive distinct role agents → policy retrieval\n        ↓ M\nPolicy/privacy/clinical safeguards + human gate\n        ↓ P\nStructured evidence, citation and audit package\n        ↓ D\nDecision Lab / approved human reviewers\n        ↓ SINK", language="text")
    st.table([
        {"Y.3172 node": "SRC", "Prototype": "Official policy pointers; synthetic healthcare-service events"},
        {"Y.3172 node": "C", "Prototype": "Source registry and event reader"},
        {"Y.3172 node": "PP", "Prototype": "Input quarantine, tokenization, vector index"},
        {"Y.3172 node": "M", "Prototype": "Explainable role agents; optional external-language-model narration"},
        {"Y.3172 node": "P", "Prototype": "Independent policy, privacy and clinical checks + approval gate"},
        {"Y.3172 node": "D", "Prototype": "Evidence packet with references and SHA-256-linked audit records"},
        {"Y.3172 node": "SINK", "Prototype": "Human reviewers and decision-support dashboard"},
    ])
    st.info("This is an adaptation of a future-networks ML architecture, not ITU certification. For public GitHub, no private EHS documents, health records, internal service data, passwords or access tokens are included.")
    st.markdown("See [ITU-T Y.3172](https://www.itu.int/rec/T-REC-Y.3172/en), [ITU AI Ready](https://www.itu.int/epublications/publication/ai-ready-analysis-towards-a-standardized-readiness-framework) and [WHO guidance](https://www.who.int/publications/i/item/9789240029200).")
