# DECISION_FRAMEWORK.md - archival handoff-comparison history

Superseded as active repo authority.

Keep this file only as historical context for how an earlier handoff package was
evaluated. Current repo authority now lives in `REPORT.md`, `docs/RUNBOOK.md`,
`docs/planning/CODEX_EXECUTION_REQUIREMENTS.md`, `docs/RESULTS_SUMMARY.md`, and
`docs/CLAIMS_SAFE_TO_WRITE.md`.

This file records the custom weighted comparison used to decide what to keep, what to reject, and what to change.

---

## 1. Comparison targets

### A. Earlier handoff from this session

Strengths:

- stronger modernization of the FactCC path
- stronger output artifact contract
- stronger final-writing handoff
- notebook support already present

Weaknesses:

- less detailed repo/runbook/prompt structure
- weaker explicit execution gating
- less detailed failure-handling logic

### B. Forked response

Strengths:

- stronger repo tree
- stronger execution phases
- stronger packaging and docs structure
- stronger prompt templates
- better explanation that the candidate table is the central artifact

Weaknesses:

- some assumptions needed verification against current docs
- QAGS still had too much visibility relative to its practical value
- FactCC path needed harder modernization
- needed explicit update for newer optional metrics and dataset/model revision pinning

### C. Final merged hardened package

Strengths:

- keeps the fork’s operational strength
- keeps the earlier handoff’s modernization and deliverable contract
- corrects brittle assumptions with current doc/package verification
- adds stronger modern optional metric policy
- adds stronger artifact and claim discipline

---

## 2. Weights

| Criterion | Weight |
| --- | ---: |
| Proposal fidelity | 15% |
| Research grounding + freshness | 15% |
| Implementation specificity | 20% |
| Reproducibility + environment robustness | 15% |
| Analysis + audit design | 15% |
| Scope control + risk handling | 10% |
| Handoff + prompt usability | 10% |

---

## 3. Scores

| Package | Proposal fidelity | Research grounding + freshness | Implementation specificity | Reproducibility + environment robustness | Analysis + audit design | Scope control + risk handling | Handoff + prompt usability | Final weighted score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Earlier handoff (this session) | 9.4 | 9.2 | 8.8 | 8.9 | 9.3 | 9.0 | 8.7 | **9.05** |
| Forked response | 9.5 | 8.8 | 9.6 | 9.3 | 9.4 | 9.4 | 9.5 | **9.36** |
| Merged hardened handoff (final) | 9.7 | 9.8 | 9.7 | 9.7 | 9.8 | 9.8 | 9.9 | **9.76** |

---

## 4. Why the fork beat the earlier handoff on its own

The forked response scored higher than the earlier handoff because it offered:

- a more complete repo structure,
- a clearer execution order,
- stronger failure handling,
- better prompt templates,
- and a more inspectable operational plan.

In other words, the fork was the better “operations manual”.

---

## 5. Why the merged package beats both

The merged package improves on the fork by:

1. hardening the **FactCC** plan around the modern public HF checkpoint rather than the archived original repo;
2. moving **QAGS** further down the priority stack;
3. adding **MiniCheck / FENICE** as more modern optional subset metrics;
4. using **current exact package pins** verified against official package pages;
5. formalizing **dataset/model revision pinning** for reproducibility;
6. strengthening the final artifact contract in `outputs/final/`;
7. integrating the attached **jupyter-notebook skill** into the repo handoff.

---

## 6. Final keep / reject / modify table

| Component | Keep | Modify | Reject | Final decision |
| --- | --- | --- | --- | --- |
| XSum main dataset | Yes | No | No | Keep |
| `facebook/bart-large-xsum` baseline | Yes | No | No | Keep |
| Optional short fine-tune from `facebook/bart-large` | Yes | Minor | No | Keep as optional |
| Beam candidate generation | Yes | No | No | Keep |
| SummaC as main entailment-style scorer | Yes | No | No | Keep |
| Original archived FactCC repo as required dependency | No | No | Yes | Reject |
| Modern FactCC-style checkpoint path | Yes | No | No | Keep |
| QAGS as required component | No | No | Yes | Reject |
| QAGS as optional tiny subset add-on | Yes | Minor | No | Keep as low-priority optional |
| MiniCheck as optional subset validator | No | Yes | No | Add |
| FENICE as optional subset validator | No | Yes | No | Add |
| Entity/date/number support refinement | Yes | No | No | Keep |
| Learned reranker | No | No | Yes | Reject |
| LLM judge as core metric | No | No | Yes | Reject |
| Artifact-first scored-candidate table | Yes | No | No | Keep |
| RESULTS_SUMMARY.md as central handoff | Yes | No | No | Keep |
| `uv` project management | No | Yes | No | Add as main env strategy |

---

## 7. Final interpretation

If the next build chat follows only one rule, it should be this:

> Finish the clean required path first, and treat everything else as a bonus.

That is the central principle that the merged package improves and makes explicit.
