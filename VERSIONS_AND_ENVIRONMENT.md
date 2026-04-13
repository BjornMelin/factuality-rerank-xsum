# VERSIONS_AND_ENVIRONMENT

This file is the environment-policy companion to `VERSIONS.md`.

Use it to understand how a GPT-5.4 Pro session should reason about the repo’s runtime setup,
especially when working from a live checkout or an uploaded repo zip.

## 1. What is authoritative

For exact current-state runtime truth, prefer:

1. `uv.lock`
2. `VERSIONS.md`
3. `artifacts/env/env_report.json`
4. `artifacts/data/dataset_manifest.json`
5. `artifacts/models/baseline_info.json`

This file is policy and interpretation guidance. It is not the exact package snapshot.

## 2. Python and environment manager

Current validated local snapshot:

- Python `3.12.13`
- `uv 0.11.2`

Project metadata:

- `requires-python = ">=3.11"`

Guidance:

- use `uv` for dependency resolution, locking, and command execution
- treat the current branch as one canonical project environment unless a task explicitly proves
  otherwise
- do not invent a second environment just because older planning docs once mentioned it

## 3. Base install contract

The canonical install command is:

```bash
uv sync --locked --dev
```

For live-repo sessions, this is the default starting point.

For uploaded-zip sessions:

- treat `uv.lock` and `VERSIONS.md` as the evidence of intended package state
- do not assume the environment was recreated unless the session is explicitly doing that work

## 4. Torch and hardware policy

Torch is host-sensitive. The rule is:

- install PyTorch using the official selector for the target machine
- do not guess a hardware-specific wheel URL
- record torch version and accelerator availability in the env stage

For this branch, the current validated snapshot in `VERSIONS.md` records:

- `torch 2.11.0`

But a future rerun should still verify the exact host posture instead of blindly reusing that value.

## 5. Current runtime package line

The repo is built around this current package line:

- `transformers>=5.5.3,<6`
- `datasets>=4.8.4,<5`
- `accelerate>=1.13,<2`
- `huggingface-hub>=1,<2`
- `sentencepiece>=0.2.1,<1`
- `torch>=2.6,<3`
- `typer>=0.12,<1`

These are implementation-line constraints, not the exact installed snapshot.

For the exact installed versions used by the current bounded run, use `VERSIONS.md`.

## 6. Online runtime posture

The current branch is designed for:

- public PyPI package resolution
- public Hugging Face dataset and model assets
- HF CLI presence and auth reporting in the env stage

The current env report records:

- runtime mode `online_hf_ready`
- HF CLI available
- authenticated user present
- DNS reachability for `huggingface.co` and `pypi.org`

This means a future session should assume online-first execution unless the task explicitly requires
or proves a fallback path.

## 7. Relationship between policy and tracked outputs

Use these files together:

- `VERSIONS.md` for the exact snapshot
- `docs/RESULTS_SUMMARY.md` for executed-run interpretation
- `docs/CLAIMS_SAFE_TO_WRITE.md` for claim ceilings
- manifests for requested/resolved dataset and model revisions

Do not make package or runtime claims from this file alone if the tracked snapshot says otherwise.

## 8. Reproducibility rules

Any future session that changes runtime-affecting behavior should:

- keep `uv.lock` checked in
- record runtime readiness in `artifacts/env/env_report.json`
- record dataset/model revisions in tracked manifests
- refresh `docs/RESULTS_SUMMARY.md` if execution truth changes
- keep prompts and docs aligned with the resulting runtime story

## 9. Guidance for zip-based external sessions

When a GPT-5.4 Pro session receives only a repo zip and selected Markdown files:

- treat `VERSIONS.md` plus the manifests as the evidence bundle
- avoid assuming local package installation actually happened in that session
- distinguish clearly between current tracked runtime truth and recommended commands for a future
  rerun
