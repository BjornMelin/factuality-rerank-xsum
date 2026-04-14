# CLAIMS_SAFE_TO_WRITE

## Supported by executed artifacts

- The repo implements the requested reranking study structure and artifact contract.
- The repo now defaults to public PyPI installs and public Hugging Face runtime assets.
- The executed generator lane performs a bounded BART fine-tuning run and then generates from the exported local checkpoint while keeping the public `facebook/bart-large-xsum` path as the baseline comparator.
- The rerank pipeline uses model-backed factuality scoring while preserving the legacy score-column contract required by downstream analysis.
- Entity/date/number support is the explicit validated refinement lane in the current ablation set.
- The final audit is a 24-row stratified Codex / AI-assisted expert adjudication sample with explicit provenance fields.
- A bounded MiniCheck subset evaluation ran on the audit sample and is available under `artifacts/scores/minicheck/`.

## Too strong for the executed run

- Do not claim benchmark-level XSum gains.
- Do not claim more than the executed dataset and generator modes recorded in the manifests.
- Do not claim human-annotator reliability or inter-annotator agreement from the current Codex / AI-assisted audit.
- Do not present the MiniCheck subset numbers as full test-set metrics.