"""Bounded sequence-to-sequence fine-tuning for the XSum generator."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import numpy as np
import torch
from datasets import Dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    PreTrainedTokenizerBase,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from factuality_rerank_xsum.data.fixtures import ids_for_split, load_dataset_table
from factuality_rerank_xsum.eval.metrics import aggregate_rouge
from factuality_rerank_xsum.runtime.manifests import repo_relative_display_path
from factuality_rerank_xsum.utils.hf import model_sha
from factuality_rerank_xsum.utils.io import read_yaml, write_json
from factuality_rerank_xsum.utils.paths import artifact_path, config_path, project_root
from factuality_rerank_xsum.utils.transformers_runtime import select_torch_device

if TYPE_CHECKING:
    from collections.abc import Callable

    import pandas as pd


def _resolve_project_path(value: str) -> Path:
    path = project_root() / value if not value.startswith("/") else Path(value)
    return path.resolve()


def _training_config() -> dict[str, Any]:
    return read_yaml(config_path("model", "bart_xsum_finetune.yaml"))


def _public_generator_config() -> dict[str, Any]:
    return read_yaml(config_path("model", "bart_xsum_public.yaml"))


def _split_frame(split: str) -> pd.DataFrame:
    frame = load_dataset_table()
    ids = ids_for_split(split)
    selected = frame[frame["id"].astype(str).isin(ids)].copy()
    if selected.empty:
        msg = f"Training split {split} resolved to zero rows."
        raise ValueError(msg)
    return selected.sort_values("id").reset_index(drop=True)


def _hf_dataset(frame: pd.DataFrame) -> Dataset:
    return Dataset.from_pandas(
        frame[["id", "document", "summary"]].reset_index(drop=True),
        preserve_index=False,
    )


def _tokenize_dataset(
    dataset: Dataset,
    *,
    tokenizer: Any,
    max_source_length: int,
    max_target_length: int,
) -> Dataset:
    def _encode(batch: dict[str, list[str]]) -> dict[str, Any]:
        encoded = tokenizer(
            batch["document"],
            max_length=max_source_length,
            truncation=True,
        )
        labels = tokenizer(
            text_target=batch["summary"],
            max_length=max_target_length,
            truncation=True,
        )
        encoded["labels"] = labels["input_ids"]
        return dict(encoded)

    return dataset.map(
        _encode,
        batched=True,
        remove_columns=list(dataset.column_names),
        desc="tokenize_seq2seq_training",
    )


def _compute_metrics(tokenizer: Any) -> Callable[[Any], dict[str, float]]:
    def _inner(eval_prediction: Any) -> dict[str, float]:
        predictions, labels = eval_prediction
        if isinstance(predictions, tuple):
            predictions = predictions[0]
        labels_array = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_predictions = tokenizer.batch_decode(predictions, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labels_array, skip_special_tokens=True)
        rouge = aggregate_rouge(decoded_predictions, decoded_labels)
        summary_lengths = [
            len(tokenizer(prediction, add_special_tokens=False)["input_ids"])
            for prediction in decoded_predictions
        ]
        rouge["summary_len_tokens"] = round(
            float(np.mean(summary_lengths)) if summary_lengths else 0.0,
            6,
        )
        return rouge

    return _inner


def _precision_args(config: dict[str, Any], device: torch.device) -> dict[str, bool]:
    precision = str(config.get("precision", "auto"))
    if precision == "bf16":
        return {"bf16": True, "fp16": False}
    if precision == "fp16":
        return {"bf16": False, "fp16": True}
    if precision == "cpu":
        return {"bf16": False, "fp16": False}
    if device.type == "cuda" and torch.cuda.is_bf16_supported():
        return {"bf16": True, "fp16": False}
    return {"bf16": False, "fp16": device.type == "cuda"}


def _training_args(config: dict[str, Any], *, output_dir: Path) -> Seq2SeqTrainingArguments:
    device = select_torch_device(str(config.get("device", "auto")))
    precision_args = _precision_args(config, device)
    bf16 = precision_args["bf16"]
    fp16 = precision_args["fp16"]
    return Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        per_device_train_batch_size=int(config["per_device_train_batch_size"]),
        per_device_eval_batch_size=int(config["per_device_eval_batch_size"]),
        gradient_accumulation_steps=int(config["gradient_accumulation_steps"]),
        learning_rate=float(config["learning_rate"]),
        weight_decay=float(config["weight_decay"]),
        num_train_epochs=float(config["num_train_epochs"]),
        warmup_steps=int(config["warmup_steps"]),
        logging_steps=int(config["logging_steps"]),
        save_total_limit=int(config["save_total_limit"]),
        save_strategy=str(config["save_strategy"]),
        eval_strategy=str(config["eval_strategy"]),
        predict_with_generate=True,
        generation_max_length=int(config["generation_max_length"]),
        generation_num_beams=int(config["generation_num_beams"]),
        load_best_model_at_end=True,
        metric_for_best_model="rougeLsum",
        greater_is_better=True,
        seed=int(config["seed"]),
        data_seed=int(config["seed"]),
        report_to="none",
        remove_unused_columns=True,
        dataloader_num_workers=0,
        use_cpu=device.type == "cpu",
        optim=str(config.get("optim", "adamw_torch")),
        bf16=bf16,
        fp16=fp16,
    )


def run_real_finetune() -> dict[str, Any]:
    """Run a bounded BART fine-tuning pass and export the best checkpoint."""

    config = _training_config()
    if not bool(config.get("enabled", False)):
        msg = "configs/model/bart_xsum_finetune.yaml is disabled."
        raise ValueError(msg)

    public_config = _public_generator_config()
    base_model_name = str(config["base_model_name_or_path"])
    base_revision = str(config.get("base_revision") or "")
    train_split = str(config["train_split"])
    eval_split = str(config["eval_split"])
    output_dir = _resolve_project_path(str(config["output_dir"]))
    export_dir = _resolve_project_path(str(config["export_dir"]))
    output_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = cast(
        "PreTrainedTokenizerBase",
        AutoTokenizer.from_pretrained(
            base_model_name,
            revision=base_revision or None,
            use_fast=True,
        ),
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        base_model_name,
        revision=base_revision or None,
    )
    model.train()
    model.config.use_cache = False

    train_frame = _split_frame(train_split)
    eval_frame = _split_frame(eval_split)
    train_dataset = _tokenize_dataset(
        _hf_dataset(train_frame),
        tokenizer=tokenizer,
        max_source_length=int(config["max_source_length"]),
        max_target_length=int(config["max_target_length"]),
    )
    eval_dataset = _tokenize_dataset(
        _hf_dataset(eval_frame),
        tokenizer=tokenizer,
        max_source_length=int(config["max_source_length"]),
        max_target_length=int(config["max_target_length"]),
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=_training_args(config, output_dir=output_dir),
        train_dataset=cast("Any", train_dataset),
        eval_dataset=cast("Any", eval_dataset),
        processing_class=tokenizer,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model),
        compute_metrics=_compute_metrics(tokenizer),
    )
    train_result = trainer.train()
    eval_metrics = trainer.evaluate(metric_key_prefix="eval")
    trainer.save_model(str(export_dir))
    tokenizer.save_pretrained(str(export_dir))

    best_checkpoint = trainer.state.best_model_checkpoint or str(export_dir)
    payload = {
        "status": "completed",
        "active_generator_label": "bart_xsum_finetuned",
        "baseline_generator_label": "bart_xsum_public",
        "public_baseline_model": public_config["model_name_or_path"],
        "public_baseline_revision": public_config.get("revision"),
        "base_model_name_or_path": base_model_name,
        "base_model_revision_requested": base_revision or None,
        "base_model_revision_resolved": model_sha(base_model_name, base_revision or None),
        "train_split": train_split,
        "eval_split": eval_split,
        "train_rows": len(train_frame),
        "eval_rows": len(eval_frame),
        "seed": int(config["seed"]),
        "output_dir": str(output_dir.relative_to(project_root())),
        "export_dir": str(export_dir.relative_to(project_root())),
        "best_checkpoint": repo_relative_display_path(Path(best_checkpoint).resolve()),
        "train_metrics": {key: float(value) for key, value in train_result.metrics.items()},
        "eval_metrics": {
            key: float(value)
            for key, value in eval_metrics.items()
            if isinstance(value, (int, float))
        },
        "hyperparameters": {
            key: config[key]
            for key in [
                "max_source_length",
                "max_target_length",
                "generation_max_length",
                "generation_num_beams",
                "per_device_train_batch_size",
                "per_device_eval_batch_size",
                "gradient_accumulation_steps",
                "learning_rate",
                "weight_decay",
                "num_train_epochs",
                "warmup_steps",
                "logging_steps",
                "save_total_limit",
                "save_strategy",
                "eval_strategy",
                "optim",
                "precision",
            ]
        },
    }
    write_json(artifact_path("models", "training_manifest.json"), payload)
    write_json(
        artifact_path("models", "baseline_info.json"),
        {
            "requested_baseline": public_config["model_name_or_path"],
            "baseline_revision_requested": public_config.get("revision"),
            "baseline_revision_resolved": model_sha(
                str(public_config["model_name_or_path"]),
                str(public_config.get("revision") or "") or None,
            ),
            "requested_factcc_checkpoint": None,
            "requested_nli_checkpoint": None,
            "finetune_enabled": True,
            "active_generator_label": payload["active_generator_label"],
            "export_dir": payload["export_dir"],
            "best_checkpoint": payload["best_checkpoint"],
            "train_rows": payload["train_rows"],
            "eval_rows": payload["eval_rows"],
            "train_metrics": payload["train_metrics"],
            "eval_metrics": payload["eval_metrics"],
            "reason": (
                "Train stage executed a bounded Hugging Face seq2seq fine-tuning run and "
                "exported the best local checkpoint for downstream generation."
            ),
        },
    )
    return payload
