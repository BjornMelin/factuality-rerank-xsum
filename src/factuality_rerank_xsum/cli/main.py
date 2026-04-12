from __future__ import annotations

import typer

from factuality_rerank_xsum import pipeline

app = typer.Typer(add_completion=False)


@app.command()
def env() -> None:
    pipeline.run_env_check()


@app.command()
def data() -> None:
    pipeline.run_prepare_dataset()


@app.command()
def train() -> None:
    pipeline.run_train_or_load_bart()


@app.command()
def generate() -> None:
    pipeline.run_generate_candidates()


@app.command()
def score() -> None:
    pipeline.run_score_candidates_summac()
    pipeline.run_score_candidates_factcc()
    pipeline.run_score_candidates_entity_support()
    pipeline.run_merge_candidate_scores()


@app.command()
def search() -> None:
    pipeline.run_search_weights()


@app.command()
def evaluate() -> None:
    pipeline.run_rerank_and_eval()
    pipeline.run_bootstrap_metrics()


@app.command()
def audit() -> None:
    pipeline.run_sample_manual_audit()
    pipeline.run_summarize_manual_audit()


@app.command()
def package() -> None:
    pipeline.run_make_tables_and_figures()
    pipeline.run_build_results_summary()
    pipeline.run_package_repo()
