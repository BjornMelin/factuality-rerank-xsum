# REPORT

This file is the canonical master handoff for the current repo state.

Use it for grading, report writing, and repo handoff. Use `docs/RUNBOOK.md`
for the canonical operator flow and
`docs/planning/CODEX_EXECUTION_REQUIREMENTS.md` for the checked-in future
execution checklist.

## 1. Confirmed, disproven, bounded

### Confirmed current repo truth

- The canonical stage surface is the CLI:
  `env`, `data`, `train`, `generate`, `score`, `search`, `evaluate`, `audit`,
  `figures`, `results-summary`, `package`, and `minicheck-optional`.
- `train` now performs a real bounded fine-tuning run for
  `facebook/bart-large-xsum` on XSum and exports a local best checkpoint.
- The public `facebook/bart-large-xsum` path remains the explicit baseline
  comparator.
- The final rerun produced refreshed generation, scoring, search, evaluation,
  audit, figures, results-summary, and package artifacts.
- The final audit is a 24-row stratified Codex / AI-assisted expert
  adjudication sample with explicit provenance fields.
- The independent evaluator lane ran through MiniCheck on the audit subset.
- Artifact-truth validation now checks row counts, split coverage, final-output
  presence, and audit provenance before package trust is granted.

### Disproven or replaced prior repo behavior

- The earlier repo state described `train` as a manifest-only stage. That is no
  longer true.
- Earlier candidate and evaluation outputs were stale enough that generation
  provenance, row-count coverage, and report wording could not be trusted
  together.
- The earlier 8-row assistant-filled audit is not the final audit record and is
  replaced by the 24-row stratified adjudication set.
- The last committed repo metrics before this execution pass
  (`ROUGE-Lsum 0.1314`, factuality composite `0.9827`, audit rows `8`) are
  superseded repo-state numbers, not a directly comparable benchmark against the
  refreshed run.

### Bounded or deferred

- This remains a bounded XSum run, not a benchmark-scale sweep.
- The final test split is 128 examples, not the full dataset.
- MiniCheck is bounded support evidence on the 24-row audit subset, not a
  replacement for test-set evaluation.
- The audit is useful for error slicing and comparison, but it must not be
  described as human annotation.

## 2. Exact final rerun chain

```bash
uv sync --locked --dev
uv run factuality-rerank-xsum env
uv run factuality-rerank-xsum data
uv run factuality-rerank-xsum train
uv run factuality-rerank-xsum generate
uv run factuality-rerank-xsum score
uv run factuality-rerank-xsum search
uv run factuality-rerank-xsum evaluate
uv run factuality-rerank-xsum audit
uv run factuality-rerank-xsum minicheck-optional
uv run factuality-rerank-xsum figures
uv run factuality-rerank-xsum results-summary
uv run factuality-rerank-xsum package
```

Repo gates completed after the refresh:

```bash
uv run ruff check
uv run ruff format --check
uv run mypy .
uv run ty check
uv run pytest
```

`pytest` finished at `49 passed, 2 warnings`.

## 3. Decisive execution evidence

### Fine-tuning completed

```json
{
  "status": "completed",
  "train_rows": 128,
  "eval_rows": 64,
  "best_checkpoint": "artifacts/models/bart_xsum_finetuned/checkpoint-32",
  "export_dir": "artifacts/models/bart_xsum_finetuned/best_model",
  "eval_rougeLsum": 0.37151
}
```

Source: `artifacts/models/training_manifest.json`

### MiniCheck completed on the audit subset

```json
{
  "status": "completed",
  "model_name": "roberta-large",
  "audit_rows": 24,
  "scored_rows": 48,
  "baseline_support_rate": 0.333333,
  "reranked_support_rate": 0.458333
}
```

Source: `artifacts/scores/minicheck/stage_summary.json`

### Artifact truth passed at package time

```json
{
  "stage": "package",
  "ok": true,
  "require_final_outputs": true,
  "final_main_metrics_rows": 8,
  "final_audit_rows": 24,
  "errors": []
}
```

Source: `artifacts/validation/artifact_truth_report.json`

### Final package exists

```text
artifacts/package/factuality-rerank-xsum.zip  26M
```

## 4. What changed and why it mattered

### Milestone 0: artifact-truth and proposal-gap closure

- Added artifact-truth validation under
  `src/factuality_rerank_xsum/runtime/artifact_truth.py`.
- Wired validation into reporting and packaging so stale outputs stop the trust
  surfaces instead of slipping through.
- Added planning ledgers under `docs/planning/` to separate proposal
  commitments, current repo truth, and grading risks.

Why it mattered:

- The repo previously had truth-repair gaps large enough to make old packaged
  outputs unsafe as evidence.
- This closed the P0 requirement that code, artifacts, docs, and package all
  tell the same story.

### Milestone 1: real bounded fine-tuning

- Implemented real training in
  `src/factuality_rerank_xsum/training/stage.py`.
- Added bounded fine-tuning config in
  `configs/model/bart_xsum_finetune.yaml`.
- Added the `train_finetune` split in `configs/data/xsum.yaml`.

Why it mattered:

- The proposal committed to fine-tuning BART. The old branch did not do it.
- The new train stage closes that gap with a real checkpointed run while
  keeping the public baseline path intact for comparison.

### Milestone 2: real generation and score-refresh correctness

- Switched generation to the exported fine-tuned checkpoint by default while
  retaining the public baseline comparator path.
- Fixed score-stage merge behavior so duplicate beam summaries do not corrupt
  downstream tables.
- Refreshed artifacts across all configured beams and bounded splits.

Why it mattered:

- The old story mixed stale provenance with current docs.
- The refreshed artifacts now have coverage and row counts that match the
  configured bounded run.

### Milestone 3: search, evaluation, and iterative refinement

- Reran search and selected `custom_0097` as the best-balanced operating point.
- Kept entity support as the explicit iterative refinement.
- Preserved the public baseline comparator and reported trade-offs honestly.

Why it mattered:

- The final system now reflects a completed reranking study rather than a
  partial search surface.
- The refinement story is now explicit and tied to a measured ablation instead
  of an implied future improvement.

### Milestone 4: audit and independent evaluator

- Replaced the weak audit surface with a 24-row stratified adjudication set
  carrying `annotator_id` and `annotation_method`.
- Added the bounded MiniCheck lane and ran it successfully after P0 closure.

Why it mattered:

- The repo now has a defensible final audit surface with honest provenance.
- The independent evaluator lane is no longer a placeholder.

### Milestone 5: docs, package, and prompt readiness

- Refreshed `README.md`, `docs/RESULTS_SUMMARY.md`,
  `docs/CLAIMS_SAFE_TO_WRITE.md`, `docs/RUNBOOK.md`,
  `docs/SUBMISSION_CHECKLIST.md`, `docs/SLIDES_OUTLINE.md`, prompt surfaces,
  and package contents.

Why it mattered:

- `PROMPT_02` report writing and `PROMPT_03` QA now have aligned authorities
  instead of having to reconcile stale package text against fresher artifacts.

## 5. Three-way comparison

| Lane | Status | ROUGE-Lsum | Factuality composite | Audit rows | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| Prior committed repo state | Superseded | 0.1314 | 0.9827 | 8 | Not a like-for-like benchmark for the refreshed run; useful only as evidence that the prior repo story was stale and under-specified. |
| Public baseline in the refreshed rerun | Current comparator | 0.3569 | 0.3324 | 24 | This is the explicit `facebook/bart-large-xsum` baseline path kept for honest comparison. |
| Fine-tuned plus reranked final system | Current final result | 0.3398 | 0.4420 | 24 | The final system trades a moderate ROUGE drop for materially stronger factuality on the bounded run. |

Important caveat:

- The prior committed repo-state result is included because it was the repo
  truth before this execution pass, but it should not be presented as an
  apples-to-apples baseline against the refreshed run. The meaningful model
  comparison is public baseline versus refreshed fine-tuned plus reranked
  system.

## 6. Headline results and supporting metrics

### Final operating point

- Search winner: `custom_0097`
- Beam size: `16`
- Normalization: `zscore`
- Weights:
  - `token_logprob_avg`: `0.0`
  - `summac_style_score`: `0.75`
  - `factcc_style_score`: `1.0`
  - `entity_support_score`: `0.5`

### Main bounded test-set comparison

| Metric | Public baseline | Final system | Delta |
| --- | ---: | ---: | ---: |
| ROUGE-Lsum | 0.3569 | 0.3398 | -0.0171 |
| Factuality composite | 0.3324 | 0.4420 | +0.1096 |
| Audit consistent rate | 0.0000 | 0.0417 | +0.0417 |
| MiniCheck support rate | 0.3333 | 0.4583 | +0.1250 |

### Confidence and refinement details

- Bootstrap ROUGE-Lsum delta CI: `[-0.0310, -0.0029]`
- Bootstrap factuality delta CI: `[0.0887, 0.1321]`
- Iterative refinement ablation:
  `logprob_plus_summac_plus_factcc` -> `...plus_entity_support`
  changes factuality composite from `0.4061` to `0.4106`

Interpretation:

- The final operating point improves factuality materially on the bounded run.
- The ROUGE trade-off is small but consistently negative on this bounded run,
  so the honest claim is a factuality-oriented trade-off, not a universal
  quality win.
- Entity support remains justified as the refinement because it improves the
  factuality composite without requiring a new late-stage subsystem.

## 7. Run-log snippets worth citing

Use these short snippets in the final paper or submission notes when concrete
evidence is needed:

- Fine-tuning completion:
  `status=completed`, `train_rows=128`, `eval_rows=64`,
  `best_checkpoint=checkpoint-32`
- Final operating point:
  `custom_0097`, beam `16`, weights
  `{logprob=0.0, summac=0.75, factcc=1.0, entity=0.5}`
- Artifact truth:
  `stage=package`, `ok=true`, `final_main_metrics_rows=8`,
  `final_audit_rows=24`
- MiniCheck:
  support rate `0.3333 -> 0.4583`
- Package:
  `artifacts/package/factuality-rerank-xsum.zip` at `26M`

## 8. Report-writing safe framing

Safe claims:

- The repo now executes a full bounded end-to-end factuality-reranking study on
  XSum with a real fine-tuning stage.
- On the bounded 128-example test split, the final reranker improves the
  factuality composite relative to the public baseline while slightly reducing
  ROUGE-Lsum.
- The final operating point preserves the public baseline as an explicit
  comparator and documents the refinement effect of entity support.
- The audit and MiniCheck subset both support the direction of the factuality
  improvement.

Unsafe claims:

- Any statement that implies a benchmark-scale XSum win.
- Any statement that treats the 24-row audit as human annotation.
- Any statement that treats the superseded prior repo-state metrics as a clean
  benchmark against the refreshed run.

## 9. Final repo-ready status

The repo is ready for:

- `prompts/PROMPT_02_ANALYZE_RESULTS_AND_WRITE_REPORT.md`
- `prompts/PROMPT_03_FINAL_QA_SUBMISSION_REVIEW.md`

Submission-facing artifacts now exist under `outputs/final/submission/`:

- `final_report.pdf`
- `final_slides.pptx`
- `final_slides.pdf`
- `final_slides.md`
- `speaker_notes.md`

Those next steps should treat the following files as the core pack:

- `REPORT.md`
- `docs/RUNBOOK.md`
- `docs/planning/CODEX_EXECUTION_REQUIREMENTS.md`
- `docs/RESULTS_SUMMARY.md`
- `docs/CLAIMS_SAFE_TO_WRITE.md`
- `outputs/final/`

## 10. Residual risks and deferred items

- The run is still bounded and should be described that way everywhere.
- The superseded pre-refresh repo metrics remain useful only as repo-history
  context, not as a comparative result claim.
- MiniCheck ran successfully, so FENICE was not needed; there is no second
  independent-evaluator lane yet.
- If any future rerun changes code, configs, or bounded split sizes, the full
  refresh chain and generated docs must be rerun together.
