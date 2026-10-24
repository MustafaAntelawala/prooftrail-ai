# Prior-art review (initial)

**Review date:** 2026-10-24
**Status:** Preliminary; not an exhaustive literature, code, patent, or product search.

## Closely related work found

| Project / paper | Relevant overlap | Intended distinction to test |
|---|---|---|
| [EviGuard](https://www.mdpi.com/2076-3417/16/18/8925) | Claim-level evidence grounding, provenance, deterministic verification, adversarial evaluation | Narrow benchmark of controlled Windows/SOC telemetry mutations and per-mutation failure reporting |
| [ClaimArena-LLM](https://www.mdpi.com/2504-4990/8/10/327) | Adversarial false causal claims, synthetic cases, deterministic scoring | Focus on corruption of event telemetry itself, rather than multi-agent debate propagation |
| [Timesketch](https://github.com/google/timesketch) | Forensic timeline investigation | Automated robustness evaluation of correlation verifiers |
| [Causa](https://github.com/npmiaman/causa) | Causal graphs and counterfactual incident analysis | Benchmarking failure modes under controlled log corruption |
| [SIFT Kernel](https://github.com/Sathvik-1007/sift-kernel) | Evidence-grounded forensic reasoning and formal testing | Small, transparent, reproducible mutation benchmark for event correlation |
| [LLM Hallucination Detector](https://github.com/SYasJ/llm-hallucination-detector) | Claim-level source support/contradiction checking and JSON export | Security-event relationship claims and telemetry corruption |

## Novelty statement

No claim of global novelty is made. The proposed contribution is a *specific combination to validate*: a public, deterministic, mutation-labelled benchmark for security-event correlation that records ground truth, applies controlled telemetry corruption, and reports false acceptance/rejection by mutation type.

Before making a novelty claim, compare the exact feature combination and benchmark protocol against the linked work, search GitHub and scholarly indexes for alternate terminology, and document any additional matches.

## Open questions

- Do existing tools already provide equivalent mutation operators and ground-truth labels for Windows/SOC event correlation?
- Is there a public benchmark with the same corruption taxonomy and per-mutation metrics?
- Which mutation types expose a meaningful weakness in current baseline correlation methods?
- Can results be independently reproduced from a clean checkout?
