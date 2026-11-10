# Security, legal and responsible-AI limitations

**Public-prototype rules**

1. No patient records, medical histories, Emirates IDs, confidential government service exports, employee personal data or internal procedures are authorized inputs.
2. Input whitelisting and illustrative regex-based detection provide only basic safeguards. These are not a substitute for tested DLP, PII detection, encryption or privacy governance.
3. The external model mode is OFF by default. It requires an environment secret and per-session explicit consent, and it sends only the allowlisted structured assessment packet. No incident files or raw user narrative are transmitted.
4. The policy registry includes short **original summaries and source links**. It is not a legally authoritative copy. Applicability, exceptions and conflicting texts require counsel. UAE PDPL may contain exclusions for government and health data, so do not assume universal direct applicability.
5. No role agent has the legal authority of a government regulator, clinician, EHS official or institutional policy owner.
6. The human approval gate is a simulated gate only; it does not connect to a real authorization workflow.
7. The audit chain can detect local tampering *within an exported sequence*. It is not equivalent to a remotely anchored, immutable, enterprise-grade audit store.
8. TF-IDF is a basic vector retrieval method for English text and tokenized Arabic. It does not establish Arabic/English semantic equivalence or legal citation accuracy.
9. Audit exports should not be treated as secure organizational recordkeeping. Production requires RBAC, approved storage, encryption, retention and logging safeguards.

## Model risk boundaries

No diagnosis, prescription, treatment recommendation, patient eligibility determination, individualized benefit decisions, unauthorized information disclosure or legal conclusion is ever automatically executed.

## Reporting vulnerabilities

Please do not open public issues containing private data. Report vulnerabilities through a private and approved channel after the repository owner configures security contact information.
