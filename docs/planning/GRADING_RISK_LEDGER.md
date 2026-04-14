# Grading Risk Ledger

Updated: 2026-04-13

## Current status

| Rubric dimension | Status | Confirmed repo truth | Evidence | Next action | Claim impact |
| --- | --- | --- | --- | --- | --- |
| Proposal fidelity | Low risk | `train` performs a bounded two-epoch BART fine-tuning run and writes checkpoint manifests. | `src/factuality_rerank_xsum/training/stage.py`, `artifacts/models/training_manifest.json` | Keep the bounded-run scope explicit in the report. | Can claim the proposal’s fine-tuning commitment is completed at bounded scale. |
| Artifact truth | Low risk | Artifact-truth validation now passes across data, generation, evaluation, audit, and final outputs. | `src/factuality_rerank_xsum/runtime/artifact_truth.py`, `artifacts/validation/artifact_truth_report.json` | Preserve the validator as the trust gate for future reruns. | Report/package surfaces are now safe to treat as current. |
| Generation provenance | Low risk | Active candidate tables are refreshed HF outputs from the exported fine-tuned checkpoint and no longer carry offline-only columns. | `artifacts/generations/generation_summary.json`, `src/factuality_rerank_xsum/generation/offline.py` | Describe the public BART path as the baseline comparator, not the active generator. | HF generation claims are now defensible. |
| Audit credibility | Medium risk | The final audit is a 24-row stratified Codex / AI-assisted expert adjudication sample with explicit provenance, not a human-annotator study. | `artifacts/audit/manual_audit_completed.csv`, `data/audit/manual_audit_template.csv` | Keep provenance wording exact in slides/report. | Can claim bounded expert adjudication; cannot claim human-label reliability. |
| Iterative refinement | Low risk | The entity-support augmentation is now the explicit refinement lane and modestly improves factuality composite in the ablation table. | `outputs/final/ablation_metrics.csv`, `configs/rerank/final_selection.yaml` | Narrate the refinement as incremental, not transformative. | Supports an honest “v1 vs refined” discussion. |
| Independent evaluator | Low risk | MiniCheck completed on the 24-row audit subset through the repo CLI and wrote subset diagnostics. | `artifacts/scores/minicheck/stage_summary.json`, `src/factuality_rerank_xsum/scoring/stage.py` | Keep it framed as subset validation rather than a main metric replacement. | Supports a bounded independent-evaluator claim. |
| Packaging and handoff | Low risk | Package and final-output surfaces now fail on stale truth mismatches and the final zip was rebuilt after the refresh. | `artifacts/package/artifact_manifest.json`, `artifacts/package/factuality-rerank-xsum.zip` | Keep running `package` as the final truth gate. | Final handoff zip is report-ready within the bounded scope. |
| Technical communication | Low risk | The final paper, editable slide deck, slide PDF, and speaker notes are now tracked in the repo and aligned to the bounded-run claims. | `docs/final-report/`, `outputs/final/submission/`, `docs/SUBMISSION_CHECKLIST.md` | Re-run QA if any metric or wording changes. | Communication artifacts now satisfy the course deliverable shape. |

## Exit criteria

- All P0 rows move to low risk or explicitly bounded deferral.
- Final report surfaces only describe refreshed, validated artifacts.
