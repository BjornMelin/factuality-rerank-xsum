---
marp: true
title: "Factuality-Aware Reranking for Extreme Summarization"
author: "Bjorn Melin"
date: "April 2026"
aspectratio: 169
paginate: true
---

## Problem and Setup

- XSum rewards compression, so fluent hallucinations are common.
- Overlap metrics alone do not tell us whether a summary is supported by the article.
- Keep the public `facebook/bart-large-xsum` path as the baseline.
- Headline trade-off: factuality composite `0.3324 -> 0.4420`, ROUGE-Lsum `0.3569 -> 0.3398`
- Bounded scope: `train=128`, `val_tune=64`, `val_full=128`, `test=128`, qualitative subset `=24`

---

## Method and Pipeline

- Fine-tune `facebook/bart-large-xsum` on the bounded train split.
- Generate beam candidates with sizes `4`, `8`, and `16`.
- Rerank with likelihood, SummaC-style support, FactCC-style consistency, and entity support.
- Select the operating point on validation search, then evaluate once on the test split.

---

## Pipeline Diagram

<div align="center">
  <img src="../../../outputs/final/figures/pipeline_diagram.png" width="76%">
</div>

---

## Search and Refinement

![](../../../outputs/final/figures/pareto_frontier.png){ width=68% }

- Selected operating point: `custom_0097`, beam `16`
- Factuality-heavy weights: `logprob=0.0`, `summac=0.75`, `factcc=1.0`, `entity=0.5`
- Main result: factuality composite `0.3324 -> 0.4420`
- Bootstrap result: factuality CI stays positive while ROUGE CI stays slightly negative

---

## Qualitative Analysis and Limits

![](../../../outputs/final/figures/error_taxonomy.png){ width=60% }

- 24-example stratified qualitative analysis with `Codex / AI-assisted expert adjudication`
- Dominant remaining failure: entity distortion (`12/24`)
- This is a bounded study, not a benchmark-scale XSum claim

---

## Takeaways

- Simple reranking signals materially improve factuality on this bounded XSum run.
- Entity support is a useful small refinement, not a silver bullet.
- The strongest remaining gap is entity-level hallucination when all candidates drift the same way.
- The next strongest improvements would likely come from better candidate diversity, stronger entity constraints, and broader external evaluation.
