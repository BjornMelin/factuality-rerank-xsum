# PROMPT_01_BUILD_REPO_AND_RUN_PIPELINE.md

Paste this prompt into the **first new GPT-5.4 Pro coding session** together with:
- `PLAN.md`
- `REPORT.md`
- `DECISION_FRAMEWORK.md`
- `REFERENCES_FULL_URLS.md`
- notebook / example files from this bundle

```text
You are building a complete, reproducible NLP course-project repository and must execute the full implementation, experiment, analysis, and packaging pipeline.

Read all attached files first, following the attachment protocol in `PROMPT_00_ATTACHMENT_PROTOCOL.md` if present.

Project:
XSum abstractive summarization factuality reranking with BART beam-search candidates, scored by generator log-likelihood, SummaC-style entailment consistency, and FactCC-style factuality, plus a manual hallucination audit and one targeted refinement.

Your job:
1. Re-verify current package versions, model cards, repo status, and implementation feasibility before coding.
2. Build the full repository, not just scaffolding.
3. Use `PLAN.md` as the implementation source of truth.
4. Use public data and public packages only.
5. Keep the required path focused and working before any optional extension.
6. Run the pipeline in this order:
   - environment + version capture
   - dataset verification
   - smoke test
   - baseline
   - candidate generation
   - SummaC scoring
   - FactCC-style scoring
   - score merge
   - weight search
   - rerank + evaluation
   - manual audit prep
   - targeted refinement
   - final tables / figures
   - packaging
7. Write actual outputs into the repo and package them into a downloadable zip file.
8. Refresh `PLAN.md` and write `docs/RESULTS_SUMMARY.md` based on what actually happened.
9. Be explicit about any substitutions, skips, or failures.

Non-negotiable rules:
- Do not stop at planning.
- Do not let QAGS block the project.
- Do not rely on the archived original FactCC repo as the required path.
- Do not tune on test.
- Do not invent missing results.
- Save all commands, configs, and artifact paths clearly.

Required final outputs:
- completed repo zip
- docs/RESULTS_SUMMARY.md
- outputs/final/main_metrics.csv
- outputs/final/ablation_metrics.csv
- outputs/final/pareto_points.csv
- outputs/final/manual_audit.csv
- outputs/final/figures/*
- outputs/final/tables/*
- updated README.md
- updated PLAN.md

When you finish, present:
1. what you implemented,
2. what you ran,
3. what results you obtained,
4. where each artifact lives,
5. the downloadable zip file.
```
