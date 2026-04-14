"""Typer CLI entrypoints for the canonical pipeline stages."""

from __future__ import annotations

import typer

from factuality_rerank_xsum.audit.stage import run_sample_manual_audit, run_summarize_manual_audit
from factuality_rerank_xsum.data.stage import run_prepare_dataset
from factuality_rerank_xsum.evaluation.stage import run_bootstrap_metrics, run_rerank_and_eval
from factuality_rerank_xsum.generation.stage import run_generate_candidates
from factuality_rerank_xsum.packaging.repo_bundle import run_package_repo
from factuality_rerank_xsum.reporting.docs import run_build_results_summary
from factuality_rerank_xsum.reporting.final_outputs import run_make_tables_and_figures
from factuality_rerank_xsum.runtime.stage import run_env_check, run_train_or_load_bart
from factuality_rerank_xsum.scoring.stage import (
    run_merge_candidate_scores,
    run_optional_minicheck_placeholder,
    run_score_candidates_entity_support,
    run_score_candidates_factcc,
    run_score_candidates_summac,
)
from factuality_rerank_xsum.search.stage import run_search_weights

app = typer.Typer(add_completion=False)


@app.command()
def env() -> None:
    """Write environment and runtime readiness artifacts."""

    run_env_check()


@app.command()
def data() -> None:
    """Prepare the dataset artifacts used by downstream stages."""

    run_prepare_dataset()


@app.command()
def train() -> None:
    """Run bounded fine-tuning and write checkpoint metadata."""

    run_train_or_load_bart()


@app.command()
def generate() -> None:
    """Generate candidate summaries for every configured split."""

    run_generate_candidates()


@app.command()
def score() -> None:
    """Run all required scoring stages and merge their outputs."""

    run_score_candidates_summac()
    run_score_candidates_factcc()
    run_score_candidates_entity_support()
    run_merge_candidate_scores()


@app.command("minicheck-optional")
def minicheck_optional() -> None:
    """Run the bounded optional MiniCheck evaluator or record a deferral."""

    run_optional_minicheck_placeholder()


@app.command()
def search() -> None:
    """Search rerank weights on the validation split."""

    run_search_weights()


@app.command()
def evaluate() -> None:
    """Apply rerank systems and compute evaluation metrics."""

    run_rerank_and_eval()
    run_bootstrap_metrics()


@app.command()
def audit() -> None:
    """Produce manual-audit samples and aggregate their summary."""

    run_sample_manual_audit()
    run_summarize_manual_audit()


@app.command()
def figures() -> None:
    """Build report-ready tables, figures, and qualitative examples."""

    run_make_tables_and_figures()


@app.command("results-summary")
def results_summary() -> None:
    """Regenerate README and report-facing documentation."""

    run_build_results_summary()


@app.command()
def package() -> None:
    """Build final outputs and package the repository handoff zip."""

    run_make_tables_and_figures()
    run_build_results_summary()
    run_package_repo()
