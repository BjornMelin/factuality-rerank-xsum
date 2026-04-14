from __future__ import annotations

import warnings
from textwrap import fill
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd
    from matplotlib.figure import Figure


PRIMARY = "#0F4C81"
SECONDARY = "#D97706"
ACCENT = "#C44900"
MUTED = "#9CA3AF"
GRID = "#D1D5DB"
SUCCESS = "#2B8A3E"

SYSTEM_LABELS = {
    "logprob_only_beam_4": "Likelihood only\n(beam 4)",
    "logprob_only_beam_8": "Likelihood only\n(beam 8)",
    "logprob_only_beam_16": "Likelihood only\n(beam 16)",
    "summac_only": "SummaC only",
    "factcc_only": "FactCC only",
    "logprob_plus_summac": "Likelihood +\nSummaC",
    "logprob_plus_factcc": "Likelihood +\nFactCC",
    "summac_plus_factcc": "SummaC +\nFactCC",
    "logprob_plus_summac_plus_factcc": "Likelihood + SummaC\n+ FactCC",
    "logprob_plus_summac_plus_factcc_plus_entity_support": (
        "Likelihood + SummaC\n+ FactCC + entity"
    ),
}


def _save(fig: Figure, path: Path, *, use_tight_layout: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if use_tight_layout:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="This figure includes Axes that are not compatible with tight_layout",
                category=UserWarning,
            )
            fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight", pad_inches=0.16, facecolor="white")
    plt.close(fig)


def _style_axis(ax: plt.Axes, *, grid_axis: str = "y") -> None:
    ax.set_facecolor("white")
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _wrap(text: str, width: int = 18) -> str:
    return fill(text.replace("_", " "), width=width, break_long_words=False)


def _draw_box(
    ax: plt.Axes,
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    facecolor: str,
) -> tuple[float, float, float, float]:
    rect = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.4,
        edgecolor=PRIMARY,
        facecolor=facecolor,
    )
    ax.add_patch(rect)
    ax.text(
        x + width / 2,
        y + height / 2,
        label,
        ha="center",
        va="center",
        fontsize=10.5,
        color="#111827",
        fontweight="semibold",
    )
    return x, y, width, height


def _arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    connectionstyle: str = "arc3",
) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=14,
        linewidth=1.5,
        color=PRIMARY,
        connectionstyle=connectionstyle,
        shrinkA=6,
        shrinkB=6,
    )
    ax.add_patch(arrow)


def make_pipeline_diagram(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 3.35))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0.04, 0.82)

    load_box = _draw_box(
        ax,
        x=0.04,
        y=0.58,
        width=0.17,
        height=0.17,
        label="XSum split\nmaterialization",
        facecolor="#E8F1FB",
    )
    generator_box = _draw_box(
        ax,
        x=0.285,
        y=0.58,
        width=0.20,
        height=0.17,
        label="Fine-tuned BART\n+ public baseline",
        facecolor="#E8F1FB",
    )
    candidate_box = _draw_box(
        ax,
        x=0.515,
        y=0.58,
        width=0.15,
        height=0.17,
        label="Beam candidate\nsummaries",
        facecolor="#E8F1FB",
    )
    search_box = _draw_box(
        ax,
        x=0.705,
        y=0.58,
        width=0.13,
        height=0.17,
        label="Weight\nsearch",
        facecolor="#FBECD9",
    )
    final_box = _draw_box(
        ax,
        x=0.85,
        y=0.58,
        width=0.12,
        height=0.17,
        label="Evaluation,\naudit,\nreport",
        facecolor="#E8F6EC",
    )
    group_box = FancyBboxPatch(
        (0.49, 0.14),
        0.26,
        0.14,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.2,
        edgecolor=PRIMARY,
        facecolor="#F9FAFB",
    )
    ax.add_patch(group_box)
    ax.text(
        0.59,
        0.255,
        "Factuality scoring",
        ha="center",
        va="center",
        fontsize=10.5,
        fontweight="bold",
        color="#111827",
    )
    _draw_box(
        ax,
        x=0.505,
        y=0.175,
        width=0.055,
        height=0.055,
        label="SummaC",
        facecolor="#F3F4F6",
    )
    _draw_box(
        ax,
        x=0.57,
        y=0.175,
        width=0.055,
        height=0.055,
        label="FactCC",
        facecolor="#F3F4F6",
    )
    _draw_box(
        ax,
        x=0.635,
        y=0.175,
        width=0.07,
        height=0.055,
        label="Entity\nsupport",
        facecolor="#F3F4F6",
    )

    _arrow(ax, (load_box[0] + load_box[2], 0.665), (generator_box[0], 0.665))
    _arrow(ax, (generator_box[0] + generator_box[2], 0.665), (candidate_box[0], 0.665))
    _arrow(ax, (candidate_box[0] + candidate_box[2], 0.665), (search_box[0], 0.665))
    _arrow(ax, (search_box[0] + search_box[2], 0.665), (final_box[0], 0.665))
    _arrow(
        ax,
        (candidate_box[0] + candidate_box[2] / 2, candidate_box[1]),
        (0.62, 0.285),
        connectionstyle="arc3,rad=0.0",
    )
    _arrow(
        ax,
        (0.74, 0.23),
        (search_box[0] + 0.03, search_box[1]),
        connectionstyle="arc3,rad=0.0",
    )
    _save(fig, path, use_tight_layout=False)


def plot_pareto(points: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ordered = points.sort_values("rougeLsum")
    ax.plot(
        ordered["rougeLsum"],
        ordered["factuality_composite"],
        color=MUTED,
        linewidth=1.1,
        alpha=0.7,
        zorder=1,
    )
    ax.scatter(
        points["rougeLsum"],
        points["factuality_composite"],
        s=52,
        color=PRIMARY,
        alpha=0.85,
        zorder=2,
    )
    ax.set_xlabel("ROUGE-Lsum")
    ax.set_ylabel("Factuality composite")
    ax.set_title("Validation search frontier")
    _style_axis(ax, grid_axis="both")
    ax.margins(x=0.06, y=0.08)
    if {"system", "rougeLsum", "factuality_composite"} <= set(points.columns):
        highlighted = {
            "custom_0097": ("Selected final", (-30, 12), ACCENT),
            points.loc[points["rougeLsum"].idxmax(), "system"]: (
                "Highest ROUGE",
                (10, -6),
                SECONDARY,
            ),
            "custom_0086": ("High-factuality knee", (0, 12), SUCCESS),
        }
        seen: set[str] = set()
        for system, (label, offset, color) in highlighted.items():
            if system in seen:
                continue
            match = points.loc[points["system"] == system]
            if match.empty:
                continue
            seen.add(system)
            row = match.iloc[0]
            ax.scatter(
                [row["rougeLsum"]],
                [row["factuality_composite"]],
                s=88,
                color=color,
                edgecolors="white",
                linewidths=0.8,
                zorder=3,
            )
            ax.annotate(
                label,
                (row["rougeLsum"], row["factuality_composite"]),
                xytext=offset,
                textcoords="offset points",
                fontsize=9.5,
                fontweight="semibold",
                color="#111827",
                bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": color},
                arrowprops={"arrowstyle": "-", "color": color, "linewidth": 1.0},
            )
    _save(fig, path)


def plot_beam_tradeoff(metrics: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    beam_frame = metrics.sort_values("beam_size")
    ax.plot(
        beam_frame["beam_size"],
        beam_frame["rougeLsum"],
        marker="o",
        linewidth=2.0,
        markersize=7.5,
        color=PRIMARY,
        label="ROUGE-Lsum",
    )
    ax.plot(
        beam_frame["beam_size"],
        beam_frame["factuality_composite"],
        marker="s",
        linewidth=2.0,
        markersize=7.2,
        color=SECONDARY,
        label="Factuality composite",
    )
    ax.set_xlabel("Beam size")
    ax.set_ylabel("Score")
    ax.set_title("Beam-size trade-off")
    ax.set_xticks(beam_frame["beam_size"])
    _style_axis(ax, grid_axis="y")
    ax.legend(loc="center right", frameon=True)
    for _, row in beam_frame.iterrows():
        ax.annotate(
            f"{row['rougeLsum']:.3f}",
            (row["beam_size"], row["rougeLsum"]),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color=PRIMARY,
        )
        ax.annotate(
            f"{row['factuality_composite']:.3f}",
            (row["beam_size"], row["factuality_composite"]),
            xytext=(0, -16),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color=SECONDARY,
        )
    _save(fig, path)


def plot_component_ablation(ablation: pd.DataFrame, path: Path) -> None:
    fig, (ax_fact, ax_rouge) = plt.subplots(
        ncols=2,
        sharey=True,
        figsize=(10.6, 5.8),
        gridspec_kw={"width_ratios": [2.8, 1.3], "wspace": 0.03},
    )
    ordered = ablation.sort_values("factuality_composite", ascending=False)
    labels = [
        SYSTEM_LABELS.get(str(system), _wrap(str(system), 18)) for system in ordered["system"]
    ]
    y_positions = list(range(len(ordered)))
    ax_fact.barh(
        y_positions,
        ordered["factuality_composite"],
        color=PRIMARY,
        alpha=0.88,
    )
    ax_fact.set_yticks(y_positions, labels=labels)
    ax_fact.invert_yaxis()
    ax_fact.set_xlabel("Factuality composite")
    ax_fact.set_title("Component ablation")
    _style_axis(ax_fact, grid_axis="x")
    for ypos, value in zip(y_positions, ordered["factuality_composite"], strict=True):
        ax_fact.text(
            value + 0.004,
            ypos,
            f"{value:.3f}",
            va="center",
            fontsize=8.8,
            color="#111827",
        )
    ax_rouge.scatter(
        ordered["rougeLsum"],
        y_positions,
        color=SECONDARY,
        marker="D",
        s=54,
        zorder=3,
    )
    ax_rouge.set_xlabel("ROUGE-Lsum")
    ax_rouge.set_title("Quality view", fontsize=12)
    _style_axis(ax_rouge, grid_axis="x")
    ax_rouge.tick_params(axis="y", left=False, labelleft=False)
    ax_rouge.spines["left"].set_visible(False)
    ax_rouge.set_xlim(
        ordered["rougeLsum"].min() - 0.0025,
        ordered["rougeLsum"].max() + 0.0025,
    )
    baseline = 0.3569
    ax_rouge.axvline(baseline, color=MUTED, linestyle="--", linewidth=1.0)
    ax_rouge.text(
        baseline,
        len(y_positions) - 0.35,
        "baseline",
        color="#4B5563",
        fontsize=8.5,
        ha="center",
        va="bottom",
    )
    _save(fig, path)


def plot_error_taxonomy(audit_summary: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ordered = audit_summary.sort_values("count", ascending=True)
    labels = [_wrap(str(label), 28) for label in ordered["primary_error_type"]]
    bars = ax.barh(labels, ordered["count"], color=PRIMARY, alpha=0.88)
    ax.set_xlabel("Count")
    ax.set_ylabel("Count")
    ax.set_title("Manual audit taxonomy")
    _style_axis(ax, grid_axis="x")
    ax.set_ylabel("")
    for bar, count in zip(bars, ordered["count"], strict=True):
        ax.text(
            bar.get_width() + 0.15,
            bar.get_y() + bar.get_height() / 2,
            str(int(count)),
            va="center",
            fontsize=9.5,
            color="#111827",
        )
    _save(fig, path)


def plot_metric_vs_human_scatter(audit_frame: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    ranked = audit_frame.sort_values("reranked_factcc_style_score").reset_index(drop=True).copy()
    ranked["rank"] = ranked.index + 1
    colors = [SUCCESS if value else PRIMARY for value in ranked["reranked_consistent"]]
    ax.plot(
        ranked["rank"],
        ranked["reranked_factcc_style_score"],
        color=MUTED,
        linewidth=1.0,
        alpha=0.6,
        zorder=1,
    )
    ax.scatter(
        ranked["rank"],
        ranked["reranked_factcc_style_score"],
        c=colors,
        s=70,
        alpha=0.9,
        edgecolors="white",
        linewidths=0.8,
        zorder=2,
    )
    ax.set_xlabel("Audit examples ordered by FactCC-style score")
    ax.set_ylabel("FactCC-style score")
    ax.set_title("FactCC-style score vs qualitative label")
    ax.set_xlim(0.5, len(ranked) + 0.5)
    ax.set_ylim(-0.02, 1.04)
    ax.set_xticks([])
    _style_axis(ax, grid_axis="y")
    ax.axhline(0.5, color=MUTED, linestyle="--", linewidth=1.0)
    ax.text(0.8, 0.515, "0.5 reference", color="#4B5563", fontsize=8.5, va="bottom")
    consistent = ranked.loc[ranked["reranked_consistent"]]
    if not consistent.empty:
        row = consistent.iloc[0]
        ax.annotate(
            "Only consistent example",
            (row["rank"], row["reranked_factcc_style_score"]),
            xytext=(-125, -28),
            textcoords="offset points",
            fontsize=9.5,
            fontweight="semibold",
            color="#111827",
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": SUCCESS},
            arrowprops={"arrowstyle": "-", "color": SUCCESS, "linewidth": 1.0},
        )
    inconsistent_count = int((~ranked["reranked_consistent"]).sum())
    ax.text(
        len(ranked) * 0.58,
        0.09,
        f"{inconsistent_count} inconsistent / {len(consistent)} consistent",
        fontsize=9.5,
        color="#4B5563",
        bbox={"boxstyle": "round,pad=0.22", "facecolor": "white", "edgecolor": GRID},
    )
    _save(fig, path)
