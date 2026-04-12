"""Project-wide constants shared across pipeline stages."""

from __future__ import annotations

BASELINE_SYSTEM = "baseline_best_likelihood"
BEST_BALANCED = "best_balanced"
BEST_FACTUALITY = "best_factuality"
BEST_SIMPLE = "best_simple"

BEAM_SIZES = [4, 8, 16]
PIPELINE_SPLITS = ["dev_smoke", "dev_small", "val_tune", "val_full", "test_final"]
SCORING_STAGES = ["summac", "factcc", "entity_support"]
