from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

import numpy as np

if TYPE_CHECKING:
    import pandas as pd


class BootstrapResult(TypedDict):
    metric: str
    delta_mean: float
    ci_low: float
    ci_high: float
    iterations: float
    n: float


def bootstrap_difference(
    baseline: pd.DataFrame,
    contender: pd.DataFrame,
    *,
    metric_col: str,
    iterations: int = 2000,
    seed: int = 42,
) -> BootstrapResult:
    merged = baseline[["id", metric_col]].merge(
        contender[["id", metric_col]],
        on="id",
        suffixes=("_baseline", "_contender"),
    )
    merged["delta"] = merged[f"{metric_col}_contender"] - merged[f"{metric_col}_baseline"]
    deltas = merged["delta"].to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    samples: list[float] = []
    for _ in range(iterations):
        draw = rng.choice(deltas, size=len(deltas), replace=True)
        samples.append(float(draw.mean()))
    samples_array = np.array(samples, dtype=float)
    return {
        "metric": metric_col,
        "delta_mean": round(float(deltas.mean()), 6),
        "ci_low": round(float(np.quantile(samples_array, 0.025)), 6),
        "ci_high": round(float(np.quantile(samples_array, 0.975)), 6),
        "iterations": float(iterations),
        "n": float(len(deltas)),
    }
