# CLAIMS_SAFE_TO_WRITE

## Supported by executed artifacts

- The repo implements the requested reranking study structure and artifact contract.
- The repo now defaults to public PyPI installs and public Hugging Face runtime assets.
- The rerank pipeline uses model-backed factuality scoring while preserving the legacy score-column contract required by downstream analysis.
- Entity/date/number support remains a complementary signal alongside the model-backed scorers.

## Too strong for the executed run

- Do not claim benchmark-level XSum gains.
- Do not claim more than the executed dataset and generator modes recorded in the manifests.
- Do not claim human-annotator reliability beyond a single-pass assistant audit.
