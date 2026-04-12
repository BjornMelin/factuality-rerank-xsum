# PROMPT_02_ANALYZE_RESULTS_AND_WRITE_REPORT.md

Paste this prompt into the **second new GPT-5.4 Pro session** after attaching:
- the built repo zip from Chat 1
- `PLAN.md`
- `REPORT.md`
- `DECISION_FRAMEWORK.md`
- `REFERENCES_FULL_URLS.md`

```text
You are an expert NLP researcher and research writer. You are given a completed repository and its artifacts for an XSum factuality-reranking project.

Read all attached files first, following the attachment-ingestion protocol if available.

Your job:
1. Inspect the repo structure and verify which artifacts actually exist.
2. Read `docs/RESULTS_SUMMARY.md` carefully.
3. Read the main metrics, ablation tables, figures, and manual-audit outputs.
4. Identify the final baseline, the final selected reranker, and the main analysis results.
5. Write the final 4-6 page research-style report in clear, submission-ready prose.
6. Write a short presentation outline.
7. Keep every claim aligned with actual artifacts only.

The report must include:
- Abstract
- Introduction
- Related Work
- Methods
- Experiments
- Results and Discussion
- Limitations
- Conclusion
- References

Rules:
- Do not invent missing experiments.
- Do not overclaim exact reproduction of legacy metrics if the repo used a modern checkpoint path.
- Prefer methodology, ablations, and audit findings over benchmark hype.
- Use the figures and tables that already exist.
- If metrics disagree with manual audit, discuss that honestly.

Also produce:
- a short slide outline,
- a concise executive summary for oral presentation,
- a list of safe claims and unsafe claims for submission review.
```
