ProofTrail AI
A reproducible benchmark for testing security-event correlation when
evidence is incomplete, inconsistent, or corrupted.
Project status: The current version is a rule-based prototype with
a Streamlit dashboard and a synthetic benchmark. Local LLM review
using Ollama and Qwen3:4B is a proposed next step; it is not yet
implemented in the current codebase.

Why this project?
Security teams correlate events from endpoints, identity systems,
firewalls, and other telemetry sources. Logs can be missing, timestamps
can be uncertain, host identifiers can conflict, and an event occurring
after another event does not automatically prove causation.

ProofTrail AI explores this question: Can a system justify a
security-event correlation claim using only the evidence available---and
abstain when evidence is insufficient?

It is a research prototype, not a replacement for a SIEM, EDR, or
analyst.
Current features
- Nine synthetic benchmark scenarios.
- Rule-based claim verification with supported, contradicted, and
  unknown verdicts.
- Controlled mutations: host changes, timestamp skew, missing source
  events, duplicate/conflicting IDs, reversed time, and unsupported
  causal claims.
- Evaluation metrics including accuracy/agreement with expected
  labels, supported precision/recall, false-acceptance and
  false-rejection counts, and a confusion matrix.
- Streamlit dashboard with summary metrics, verdict distribution,
  mutation summaries, filters, case details, and JSON report download.
- Canonical JSON reporting with reproducibility metadata and SHA-256
  hashing.
- Pytest suite. The last recorded local run passed 26 tests; rerun the
  suite to verify your current checkout.
Architecture
Synthetic scenarios
       |
       v
prooftrail/verifier.py  -> verdict, reason, evidence event IDs
       |
       v
prooftrail/evaluate.py  -> metrics and confusion matrix
       |
       v
prooftrail/cli.py       -> canonical JSON report
       |
       v
app.py                  -> Streamlit dashboard and report download
Key files: - prooftrail/models.py --- event, claim, and scenario data
models. - prooftrail/mutations.py --- benchmark scenario construction
and mutations. - prooftrail/verifier.py --- deterministic, rule-based
verification. - prooftrail/evaluate.py --- benchmark metrics. -
prooftrail/cli.py --- report generation. - app.py --- dashboard. -
tests/ --- automated tests. - docs/benchmark-spec.md --- benchmark
rules and limitations.
Run locally on Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Run tests:
python -m pytest -q
Generate a report (create results first if needed):
New-Item -ItemType Directory -Force results
python -m prooftrail.cli --output results\baseline.json
Launch the dashboard:
python -m streamlit run app.py
Planned open-source AI integration
The next planned capability is an optional local LLM review using:
- Ollama to serve a model locally.
- qwen3:4b as an initial model to evaluate on a computer with 16 GB
  RAM.
- A proposed dashboard panel that shows the deterministic verifier's
  verdict beside an AI-generated assessment.
Proposed workflow
Scenario + claim + supplied evidence
          |                         |
          v                         v
Rule-based verifier          Local LLM reviewer
          |                         |
          v                         v
Deterministic verdict        Structured AI assessment
          \                         /
           \                       /
            v                     v
             Comparison and review panel
The LLM should receive only the scenario fields needed for review. Its
response is advisory, not ground truth. The rule-based verifier remains
the baseline and should work when Ollama is unavailable.
Prepare a local model (optional)
Install Ollama from its official Windows download
page, then run:
ollama --version
ollama run qwen3:4b
The first run downloads the model. Speed and memory usage depend on
CPU/GPU and quantization. These commands test the model locally; they
do not integrate it into the ProofTrail dashboard. Verify the exact
model artifact and license before redistribution.
Planned safeguards
- Keep AI review optional; the benchmark must work without Ollama.
- Label AI output separately from expected benchmark labels.
- Ask the model to cite supplied event IDs and state when evidence is
  insufficient.
- Do not allow the model to invent logs, users, timestamps, or causal
  relationships.
- Validate responses against a schema; handle timeouts and malformed
  responses.
- Record model/version/settings for reproducibility.
- Evaluate disagreements, unsupported claims, false
  acceptance/rejection, and abstention behavior on the same scenarios.
- Do not send real or sensitive security logs to an external service.
  Local inference reduces data sharing, but local access controls
  still matter.
Benchmark interpretation and limitations
- The current benchmark uses nine synthetic scenarios; it does not
  establish real-world SOC accuracy.
- Expected verdicts are labels defined by the benchmark
  scenario/specification. Their rationale should be independently
  reviewed.
- A 100% match on these cases means agreement on a small test
  set---not production readiness.
- supported means the defined checks pass; it does not prove event
  authenticity or causation.
- unknown is an intentional outcome when evidence is insufficient or
  ambiguous.
- The current verifier is deterministic and rule-based. The planned
  LLM integration is not implemented by this README update.
Roadmap
1. Independently review expected labels and document the rationale for
   every scenario.
2. Add an optional Ollama client module with timeouts, error handling,
   and structured output.
3. Add an AI Review panel to Streamlit without changing existing
   benchmark behavior.
4. Compare rule-based and LLM results on identical scenarios.
5. Add more scenarios and, when appropriate, carefully sanitized
   real-format logs.
6. Report limitations and evaluation methodology clearly.
Responsible use
Do not commit credentials, private logs, customer information, or other
sensitive data. This project is for research, testing, and education. Do
not use its verdicts as the sole basis for incident response or other
high-impact security decisions.