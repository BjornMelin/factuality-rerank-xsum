from __future__ import annotations

import numpy as np
import pandas as pd


def normalize_series(values: pd.Series, mode: str) -> pd.Series:
    if mode == "zscore":
        std = float(values.std(ddof=0))
        if std == 0:
            return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
        return (values - float(values.mean())) / std
    if mode == "minmax":
        minimum = float(values.min())
        maximum = float(values.max())
        if minimum == maximum:
            return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
        return (values - minimum) / (maximum - minimum)
    if mode == "rank":
        ranks = values.rank(method="average", ascending=False)
        return 1 - ((ranks - 1) / max(len(values) - 1, 1))
    msg = f"Unsupported normalization mode: {mode}"
    raise ValueError(msg)


def fuse_scores(frame: pd.DataFrame, weights: dict[str, float], normalization: str) -> pd.DataFrame:
    fused = frame.copy()
    weighted_parts: list[pd.Series] = []
    for column, weight in weights.items():
        if weight == 0:
            continue
        normalized = normalize_series(fused[column].astype(float), normalization)
        fused[f"{column}_{normalization}"] = normalized
        weighted_parts.append(normalized * weight)
    if not weighted_parts:
        fused["fused_score"] = 0.0
    else:
        fused["fused_score"] = sum(weighted_parts)
    return fused


def select_top_candidate(frame: pd.DataFrame) -> pd.DataFrame:
    ordered = frame.sort_values(["id", "fused_score", "beam_rank"], ascending=[True, False, True])
    return ordered.groupby("id", as_index=False).head(1).reset_index(drop=True)


def pareto_frontier(frame: pd.DataFrame, x_col: str, y_col: str) -> pd.DataFrame:
    frontier_rows: list[pd.Series] = []
    points = frame.sort_values([x_col, y_col], ascending=[False, False]).reset_index(drop=True)
    best_y = float("-inf")
    for _, row in points.iterrows():
        current_y = float(row[y_col])
        if current_y >= best_y:
            frontier_rows.append(row)
            best_y = current_y
    if not frontier_rows:
        return frame.head(0).copy()
    return pd.DataFrame(frontier_rows).drop_duplicates(subset=[x_col, y_col])


def weight_grid(step: float = 0.25) -> list[dict[str, float]]:
    values = [round(value, 2) for value in np.arange(0.0, 1.0 + step, step)]
    configs: list[dict[str, float]] = []
    for logprob in values:
        for summac in values:
            for factcc in values:
                for entity in values:
                    if logprob == 0 and summac == 0 and factcc == 0 and entity == 0:
                        continue
                    configs.append(
                        {
                            "token_logprob_avg": logprob,
                            "summac_style_score": summac,
                            "factcc_style_score": factcc,
                            "entity_support_score": entity,
                        }
                    )
    return configs


def named_weight_configs() -> dict[str, dict[str, float]]:
    return {
        "logprob_only": {
            "token_logprob_avg": 1.0,
            "summac_style_score": 0.0,
            "factcc_style_score": 0.0,
            "entity_support_score": 0.0,
        },
        "summac_only": {
            "token_logprob_avg": 0.0,
            "summac_style_score": 1.0,
            "factcc_style_score": 0.0,
            "entity_support_score": 0.0,
        },
        "factcc_only": {
            "token_logprob_avg": 0.0,
            "summac_style_score": 0.0,
            "factcc_style_score": 1.0,
            "entity_support_score": 0.0,
        },
        "logprob_plus_summac": {
            "token_logprob_avg": 0.5,
            "summac_style_score": 0.5,
            "factcc_style_score": 0.0,
            "entity_support_score": 0.0,
        },
        "logprob_plus_factcc": {
            "token_logprob_avg": 0.5,
            "summac_style_score": 0.0,
            "factcc_style_score": 0.5,
            "entity_support_score": 0.0,
        },
        "summac_plus_factcc": {
            "token_logprob_avg": 0.0,
            "summac_style_score": 0.5,
            "factcc_style_score": 0.5,
            "entity_support_score": 0.0,
        },
        "logprob_plus_summac_plus_factcc": {
            "token_logprob_avg": 0.34,
            "summac_style_score": 0.33,
            "factcc_style_score": 0.33,
            "entity_support_score": 0.0,
        },
        "logprob_plus_summac_plus_factcc_plus_entity_support": {
            "token_logprob_avg": 0.25,
            "summac_style_score": 0.25,
            "factcc_style_score": 0.25,
            "entity_support_score": 0.25,
        },
    }


def config_name_from_weights(weights: dict[str, float]) -> str:
    inverse = {tuple(value.items()): key for key, value in named_weight_configs().items()}
    return inverse.get(tuple(weights.items()), "custom")
