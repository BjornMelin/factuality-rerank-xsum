# SUBMISSION_CHECKLIST

- [x] `REPORT.md` is the canonical current-state handoff.
- [x] `docs/RUNBOOK.md` is the canonical operator flow.
- [x] `docs/planning/CODEX_EXECUTION_REQUIREMENTS.md` exists as the checked-in execution checklist.
- [x] Repo includes code, configs, docs, and prompts.
- [x] Base install contract uses `uv sync --locked --dev`.
- [x] Final outputs include metrics CSVs, figures, and manual audit files.
- [x] README and RESULTS_SUMMARY reflect the executed run truthfully.
- [x] Dataset stage executed in `online_hub` mode.
- [x] Generator stage executed in `huggingface_generation` mode.
- [x] Audit wording explicitly says Codex / AI-assisted expert adjudication, not human annotation.
- [x] Optional MiniCheck subset evidence exists or is explicitly deferred.
- [x] `artifacts/validation/artifact_truth_report.json` passes for the packaged run.
- [x] The package copy at `artifacts/package/factuality-rerank-xsum.zip` matches the current docs and outputs.
- [x] Proposal commitments and rubric risks are tracked in `docs/planning/`.
- [x] Bounded-run caveats and claim ceilings remain explicit in the final report surfaces.