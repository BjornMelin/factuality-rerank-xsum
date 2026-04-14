# Proposal Alignment

Updated: 2026-04-13

## Alignment summary

The repo now has the CLI-first study skeleton, bounded fine-tuning,
checkpoint-backed generation, refreshed scoring/search/evaluation outputs, a
provenance-explicit audit workflow, and packaged final outputs that agree with
artifact truth.

## Confirmed aligned today

- CLI-first stage surface exists end to end.
- Public `facebook/bart-large-xsum` baseline path exists and remains the explicit baseline comparator.
- Candidate reranking combines likelihood with model-backed factuality signals and an explicit entity-support refinement lane.
- Search, evaluation, reporting, packaging, and bounded MiniCheck subset validation are present.

## Misaligned today

- The audit is not human annotation and must continue to be described exactly as Codex / AI-assisted expert adjudication.
- The run remains bounded to 16/64/128 split sizes plus a 24-row audit subset; report wording must not inflate it into a full benchmark sweep.

## Required alignment work

1. Keep the artifact-truth guardrails in the main reporting/package path.
2. Preserve the fine-tuned BART lane and public baseline comparison story in docs.
3. Report the entity-support augmentation as the explicit iterative refinement.
4. Keep the audit provenance wording exact in slides/report/prompt surfaces.
5. Reuse the bounded MiniCheck subset lane only as optional supporting evidence.
