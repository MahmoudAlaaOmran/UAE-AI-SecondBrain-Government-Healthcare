# Government Second Brain in Healthcare

**ITU AI for Good Lab Hackathon — UAE 2026** · Healthcare and public services

A runnable, policy-grounded **proof of concept** for institutional healthcare intelligence and responsible multi-agent decision support. It demonstrates how specialized government-role agents can analyze service failures, refer to an indexed source registry, block high-risk actions and prepare a traceable human-review packet.

**Status:** Independent research/hackathon prototype, **not** a deployed system, certified health product, legal decision tool, or official government service. Every scenario number is synthetic. No private EHS/other government documents or patient data are included.

## Demonstration capabilities

- **Six coordinated institutional roles:** Service Journey Analyst, Policy and Legal Adviser, Privacy and Data Governance Guardian, Clinical Safety Reviewer, Cybersecurity and Assurance Adviser, Institutional Coordinator.
- **Three sequenced error scenarios:** service completion decline; restricted complaint data and proposed vendor external AI upload; outdated policy and proposed automatic rejection.
- **Policy source registry:** eight reviewed pointers to publicly available UAE and international documents, with source links and scope notes.
- **Vector retrieval:** small explainable in-memory TF-IDF index over the curated registry (not a distributed vector database).
- **Human approval:** no automatic patient eligibility, clinical, legal or restricted-data actions.
- **Traceable results:** role-by-role structured outputs, source IDs and SHA-256 hash-chained event logs.
- **Two viewing options:** Streamlit interactive app and static GitHub Pages scenario preview.
- **Optional LLM role analysis:** with explicit opt-in and a separately configured API key, five distinct healthcare-government roles can provide source-grounded advisory review. The core safety decisions remain deterministic and the AI receives only allowlisted synthetic assessments and public-source summaries.

## Start locally

Requires Python 3.11+.

```bash
# From this repository's root directory
python -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run streamlit_app.py
```

A browser opens at `http://localhost:8501`. Select **Decision Lab**, release T1, T2, and T3, then inspect **Policy Knowledge Base** and **Audit and Evaluation**.

No credentials or network access are needed for the deterministic simulation (beyond installation). The optional external AI reviews and executive narrative are **off** unless deliberately configured and consented to.

### Run without Streamlit

The simulation engine itself uses only Python's standard library:

```bash
python -m gsb --stage 3 --output decision-evidence.json --audit demo-audit.jsonl
python -m unittest discover -s tests -v
```

The generated JSON is a reproducible decision evidence packet for the synthetic scenario. The JSONL log contains no patient data. Generated outputs are ignored when placed under `outputs/`.

## Publish the source to GitHub

1. Create a **new empty GitHub repository**, for example `government-second-brain-healthcare`. Do not initialize it with a README because one already exists.
2. Unzip the provided archive and open a terminal inside the `government-second-brain-healthcare` folder.
3. Replace `YOUR_USERNAME` in these commands:

```bash
git init
git branch -M main
git add .
git commit -m "Initial Government Second Brain healthcare prototype"
git remote add origin https://github.com/YOUR_USERNAME/government-second-brain-healthcare.git
git push -u origin main
```

Alternatively, use GitHub Desktop to publish the extracted folder. **Do not upload only the ZIP file** and expect GitHub to run or extract it.

## Host the demo

### Option A — GitHub Pages (static preview; free)

GitHub can directly host the `docs/` static scenario demo:

1. Repository → **Settings** → **Pages**.
2. Under *Build and deployment*, select **Deploy from a branch**.
3. Select branch `main`, folder `/docs`, and **Save**.
4. The published page will be at `https://YOUR_USERNAME.github.io/government-second-brain-healthcare/` (once Pages builds).

The GitHub Pages version demonstrates the interface and **simulated** staged agent responses. It is entirely client-side and does not execute the Python knowledge-search engine or persist audits.

### Option B — Streamlit Community Cloud (full Python demonstration)

1. Push the repository to GitHub.
2. In Streamlit Community Cloud, choose **Create app** → repository → branch `main` → entrypoint `streamlit_app.py`.
3. Deploy. No secrets needed for offline simulation. Keep any optional provider API key in your host's encrypted secrets configuration; never commit it.

**Note:** A GitHub repository hosts source code; GitHub Pages alone cannot execute the Python server. The full interactive backend requires an appropriate Python application host.

## Project structure

```text
government-second-brain-healthcare/
├── streamlit_app.py             # Full interactive application
├── gsb/
│   ├── __main__.py              # CLI runner
│   ├── agents.py                # Independent institutional agent roles
│   ├── orchestrator.py          # Progressive scenario and decision gate
│   ├── kb.py                    # Vectorized (TF-IDF) source retrieval
│   ├── security.py              # Input minimization and rejection
│   ├── audit.py                 # Hash-linked decision log
│   └── llm.py                   # Optional explicit opt-in AI narrative
├── data/
│   ├── policies.json            # Public reference registry and summaries
│   └── scenarios.json           # Synthetic sequential events
├── docs/
│   ├── index.html               # GitHub Pages static demo
│   ├── styles.css
│   ├── app.js
│   ├── ARCHITECTURE.md
│   ├── DEMO_SCRIPT.md
│   └── SECURITY.md
├── tests/test_solution.py
├── .github/workflows/ci.yml
├── .streamlit/config.toml
├── requirements.txt
└── .env.example
```

## Knowledge base and source rights

`data/policies.json` holds short original summaries, citation identifiers, source URLs, scope classifications and verification date (2026-11-10), **not** full legislation text. Follow the official source to confirm the applicable current text. In particular, applicability of the general UAE Personal Data Protection Law to government and sector-specific health processing must not be presumed. Official original Arabic texts may control interpretation.

The prototype maps ITU-T Y.3172 logical ML nodes SRC/C/PP/M/P/D/SINK by analogy; the Recommendation concerns future networks. The project is not ITU-certified, legally validated, or independently security-tested.

Key sources include:

- [UAE ICT in health sector legislation and policy](https://u.ae/en/about-the-uae/digital-uae/whole-of-government-approach/digital-health/ict-in-the-health-sector)
- [UAE health ICT executive regulation](https://uaelegislation.gov.ae/en/legislations/1444)
- [UAE data protection laws](https://u.ae/en/about-the-uae/digital-uae/data/data-protection-laws)
- [UAE National AI Strategy 2031](https://ai.gov.ae/strategy/)
- [UAE AI Charter (2024)](https://ai.gov.ae/wp-content/uploads/2024/07/UAEAI-Methaq-EN2-3.pdf)
- [ITU-T Y.3172](https://www.itu.int/rec/T-REC-Y.3172/en)
- [ITU AI Readiness framework report](https://www.itu.int/epublications/publication/ai-ready-analysis-towards-a-standardized-readiness-framework)
- [WHO AI health ethics and governance guidance](https://www.who.int/publications/i/item/9789240029200)

## Tests and intended evaluation

Run `python -m unittest discover -s tests -v` and inspect `.github/workflows/ci.yml`. Automated checks cover event progression, vector retrieval, human approval gating, blocked external disclosure and eligibility changes, input rejection and tamper detection.

**Not yet validated:** actual multilingual retrieval accuracy, legislative citation completeness, real patient privacy compliance, live operational integration, scalability, model safety, production security or clinical performance. See [Security limitations](docs/SECURITY.md) and the [demo script](docs/DEMO_SCRIPT.md).

## Code rights and external sources

No open-source license has been selected for the prototype code. **The submitting owner should choose whether/how to license the code before publication**, consistent with the hackathon rules and institutional intellectual-property policies. Publishing on GitHub does not itself grant third parties a reuse license. Linked third-party materials retain their separate copyright and terms; complete texts have not been redistributed.
