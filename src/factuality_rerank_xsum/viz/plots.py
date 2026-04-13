from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd
    from matplotlib.figure import Figure


def _save(fig: Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def make_pipeline_diagram(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 2.5))
    ax.axis("off")
    steps = [
        "Fixture / XSum load",
        "Candidate generation",
        "SummaC-style scoring",
        "FactCC-style scoring",
        "Entity support",
        "Weight search",
        "Audit + packaging",
    ]
    for idx, label in enumerate(steps):
        x = 0.08 + idx * 0.14
        ax.text(
            x,
            0.5,
            label,
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.35", "edgecolor": "black", "facecolor": "white"},
            transform=ax.transAxes,
        )
        if idx < len(steps) - 1:
            ax.annotate(
                "",
                xy=(x + 0.07, 0.5),
                xytext=(x + 0.11, 0.5),
                arrowprops={"arrowstyle": "->"},
                xycoords=ax.transAxes,
                textcoords=ax.transAxes,
            )
    _save(fig, path)


def plot_pareto(points: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(points["rougeLsum"], points["factuality_composite"])
    ax.set_xlabel("ROUGE-Lsum")
    ax.set_ylabel("Factuality composite")
    ax.set_title("Pareto frontier")
    if {"system", "rougeLsum", "factuality_composite"} <= set(points.columns):
        for _, row in points.iterrows():
            ax.annotate(
                str(row["system"]),
                (row["rougeLsum"], row["factuality_composite"]),
                fontsize=8,
            )
    _save(fig, path)


def plot_beam_tradeoff(metrics: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    beam_frame = metrics.sort_values("beam_size")
    ax.plot(beam_frame["beam_size"], beam_frame["rougeLsum"], marker="o", label="ROUGE-Lsum")
    ax.plot(
        beam_frame["beam_size"],
        beam_frame["factuality_composite"],
        marker="s",
        label="Factuality composite",
    )
    ax.set_xlabel("Beam size")
    ax.set_ylabel("Score")
    ax.set_title("Beam-size trade-off")
    ax.legend()
    _save(fig, path)


def plot_component_ablation(ablation: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    ordered = ablation.sort_values("factuality_composite", ascending=False)
    ax.bar(ordered["system"], ordered["factuality_composite"])
    ax.set_xlabel("System")
    ax.set_ylabel("Factuality composite")
    ax.set_title("Component ablation")
    ax.tick_params(axis="x", rotation=45)
    _save(fig, path)


def plot_error_taxonomy(audit_summary: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(audit_summary["primary_error_type"], audit_summary["count"])
    ax.set_xlabel("Audit label")
    ax.set_ylabel("Count")
    ax.set_title("Manual audit taxonomy")
    ax.tick_params(axis="x", rotation=45)
    _save(fig, path)


def plot_metric_vs_human_scatter(audit_frame: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    human = audit_frame["reranked_consistent"].astype(int)
    auto = audit_frame["reranked_factcc_style_score"]
    ax.scatter(auto, human)
    ax.set_xlabel("FactCC-style score")
    ax.set_ylabel("Human consistency label")
    ax.set_title("Metric vs human agreement")
    _save(fig, path)
