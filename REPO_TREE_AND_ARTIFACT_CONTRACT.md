# REPO_TREE_AND_ARTIFACT_CONTRACT.md

This file is a compact summary of what the build chat must create.

---

## Required top-level files
- README.md
- PLAN.md
- REPORT.md
- DECISION_FRAMEWORK.md
- REFERENCES_FULL_URLS.md
- VERSIONS.md
- pyproject.toml
- uv.lock
- Makefile

## Required docs
- docs/RUNBOOK.md
- docs/RESULTS_SUMMARY.md
- docs/SUBMISSION_CHECKLIST.md
- docs/SLIDES_OUTLINE.md
- docs/CLAIMS_SAFE_TO_WRITE.md

## Required outputs
- outputs/final/main_metrics.csv
- outputs/final/ablation_metrics.csv
- outputs/final/pareto_points.csv
- outputs/final/bootstrap_cis.json
- outputs/final/manual_audit.csv
- outputs/final/manual_audit_summary.json
- outputs/final/figures/*
- outputs/final/tables/*
- outputs/final/system_card.md

## Required experiment stages
1. verify environment
2. verify dataset
3. run baseline
4. generate candidates
5. score candidates
6. rerank
7. evaluate
8. run manual audit
9. apply targeted refinement
10. package repo

## Final packaging requirement
The build chat must export a downloadable zip file containing:
- repo code
- configs
- docs
- final tables
- final figures
- audit files
- results summary
