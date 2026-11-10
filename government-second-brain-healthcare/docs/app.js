"use strict";
// Static, synthetic-only visualization. Executable backend and audit trail: streamlit_app.py + gsb/.
const policies = [
  ["U1","UAE Federal Health ICT Law (2019)","https://u.ae/en/about-the-uae/digital-uae/whole-of-government-approach/digital-health/ict-in-the-health-sector"],
  ["U5","Health ICT Executive Regulation (2020)","https://uaelegislation.gov.ae/en/legislations/1444"],
  ["U2","UAE Personal Data Protection framework (scope-dependent)","https://u.ae/en/about-the-uae/digital-uae/data/data-protection-laws"],
  ["U3","UAE National AI Strategy 2031","https://ai.gov.ae/strategy/"],
  ["U4","UAE Charter for Development and Use of AI","https://ai.gov.ae/wp-content/uploads/2024/07/UAEAI-Methaq-EN2-3.pdf"],
  ["I1","ITU-T Y.3172 ML Architecture","https://www.itu.int/rec/T-REC-Y.3172/en"],
  ["I2","ITU AI Readiness Framework","https://www.itu.int/epublications/publication/ai-ready-analysis-towards-a-standardized-readiness-framework"],
  ["G1","WHO Ethics and Governance of AI for Health","https://www.who.int/publications/i/item/9789240029200"]
];
const scenarios = [
  {title:"Service deterioration", desc:"Synthetic completion falls from 76% to 53%; complaints and repeat visits increase. The system has correlation, not verified causation.", responses:[
    ["Service Journey Analyst","Investigate journey-stage failures, tracking quality and language-access differences.",false],
    ["Policy Adviser","Retrieve relevant sources; do not invent legal authority for changing a service.",false],
    ["Privacy Guardian","Limit analysis to synthetic and approved aggregate data.",false],
    ["Clinical Safety","Service metrics do not establish clinical conclusions.",false],
    ["Institutional Coordinator","Refer an evidence-based investigation request to the authorized service owner.",false]],
   gate:"Service owner must verify instrumentation and investigate root causes before approving any redesign."},
  {title:"Privacy and vendor escalation", desc:"An export is reported to contain patient identifiers and clinical detail; a vendor proposes uploading it to an external AI service. No actual records are included.", responses:[
    ["Privacy Guardian","BLOCK restricted-data ingestion and unsanctioned external upload; quarantine the reported export.",true],
    ["Cybersecurity Adviser","Escalate vendor data-transfer request for security review and preserve incident metadata.",true],
    ["Policy Adviser","Review healthcare ICT law and relevant data-protection scope; legal applicability is not assumed.",true],
    ["Clinical Safety","No patient-level inference, treatment or diagnosis is authorized.",false],
    ["Institutional Coordinator","Escalate to privacy, security and legal owners, with no disclosure permission granted.",true]],
   gate:"External AI transfer is blocked. Privacy and security owners must review the incident and any disclosure obligations."},
  {title:"Unverified eligibility policy", desc:"An outdated procedure is cited for automated applicant rejection. Its current authority is unknown; the simulator refuses to infer legal or clinical eligibility.", responses:[
    ["Policy Adviser","BLOCK automatic eligibility changes: the cited procedure is unverified and source authority is incomplete.",true],
    ["Clinical Safety","BLOCK automated rejection. Evaluate patient-access effects and safe manual fallback.",true],
    ["Privacy Guardian","Maintain quarantine on previously reported sensitive complaint information.",true],
    ["Service Journey Analyst","Continue root-cause investigation without turning completion metrics into eligibility rules.",false],
    ["Institutional Coordinator","Request clinical, legal, policy and service-owner review and record the final human disposition.",true]],
   gate:"Automated eligibility changes and restricted-data transfers remain blocked. Only competent human authorities may approve subsequent actions."}
];
const escapeHtml = (s)=>String(s).replace(/[&<>"']/g,(ch)=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch]));
document.getElementById("policy-grid").innerHTML=policies.map(p=>`<article class="policy"><small>${p[0]} · SOURCE REFERENCE</small><strong>${escapeHtml(p[1])}</strong><a href="${p[2]}" target="_blank" rel="noopener noreferrer">View original source ↗</a></article>`).join("");
function setStage(n){
  const item=scenarios[n-1];
  document.querySelectorAll(".step").forEach(button=>{button.classList.toggle("active",Number(button.dataset.stage)===n);button.setAttribute("aria-pressed",String(Number(button.dataset.stage)===n));});
  document.getElementById("stage-title").textContent=item.title;
  document.getElementById("stage-desc").textContent=item.desc;
  document.getElementById("responses").innerHTML=item.responses.map(a=>`<div class="response ${a[2]?"risk":""}"><strong>${escapeHtml(a[0])}</strong><p>${escapeHtml(a[1])}</p></div>`).join("");
  document.getElementById("gate-copy").textContent=item.gate;
  document.getElementById("gate-title").textContent=n===1?"Human review required":"Restricted action blocked · Human escalation";
}
document.querySelectorAll(".step").forEach(button=>button.addEventListener("click",()=>setStage(Number(button.dataset.stage))));
setStage(1);
