from __future__ import annotations

from functools import lru_cache
from typing import Any

import torch
from transformers import AutoModelForSeq2SeqLM, AutoModelForSequenceClassification, AutoTokenizer


def select_torch_device(preference: str = "auto") -> torch.device:
    normalized = preference.lower()
    if normalized == "cpu":
        return torch.device("cpu")
    if normalized == "cuda":
        if not torch.cuda.is_available():
            msg = "CUDA device requested but torch.cuda.is_available() is false."
            raise RuntimeError(msg)
        return torch.device("cuda")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def move_batch_to_device(
    batch: dict[str, torch.Tensor], device: torch.device
) -> dict[str, torch.Tensor]:
    return {key: value.to(device) for key, value in batch.items()}


@lru_cache(maxsize=4)
def load_seq2seq_runtime(
    model_name_or_path: str,
    revision: str | None,
    device_preference: str,
) -> tuple[Any, Any, torch.device]:
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, revision=revision, use_fast=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name_or_path, revision=revision)
    device = select_torch_device(device_preference)
    model.to(device)
    model.eval()
    return tokenizer, model, device


@lru_cache(maxsize=8)
def load_sequence_classifier_runtime(
    model_name_or_path: str,
    revision: str | None,
    device_preference: str,
) -> tuple[Any, Any, torch.device]:
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, revision=revision, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name_or_path, revision=revision
    )
    device = select_torch_device(device_preference)
    model.to(device)
    model.eval()
    return tokenizer, model, device
