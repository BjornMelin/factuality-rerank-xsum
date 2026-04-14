---
title: "Factuality-Aware Reranking for Extreme Summarization"
author: "Bjorn Melin"
date: "April 2026"
aspectratio: 169
---

# Factuality-Aware Reranking for Extreme Summarization

- Bounded XSum study with fine-tuned BART, factuality-aware reranking, and explicit audit validation
- Final system improves factuality composite from `0.3324` to `0.4420`
- ROUGE-Lsum changes from `0.3569` to `0.3398`

\vfill

Bounded scope: `train=128`, `val_tune=64`, `val_full=128`, `test=128`, audit `=24`

## Problem and Setup

- XSum rewards compression, so fluent hallucinations are common.
- Overlap metrics alone do not tell us whether a summary is supported by the article.
- Goal: keep the public `facebook/bart-large-xsum` path as the baseline, then ask whether reranking can trade a small amount of ROUGE for better factuality.

![](../../../outputs/final/figures/pipeline_diagram.png){ width=70% }

## Method

- Fine-tune `facebook/bart-large-xsum` on the bounded train split.
- Generate beam candidates with sizes `4`, `8`, and `16`.
- Score each candidate with:
  - generation likelihood
  - SummaC-style support
  - FactCC-style consistency
  - entity / number / date support
- Select the operating point on validation search, then evaluate once on the test split.

## Main Result

| Metric | Baseline | Final |
| --- | ---: | ---: |
| ROUGE-Lsum | 0.3569 | 0.3398 |
| Factuality composite | 0.3324 | 0.4420 |
| Audit consistent rate | 0.0000 | 0.0417 |
| MiniCheck support rate | 0.3333 | 0.4583 |

- Bootstrap ROUGE delta CI: `[-0.0310, -0.0029]`
- Bootstrap factuality delta CI: `[0.0887, 0.1321]`
- Honest interpretation: factuality win, modest ROUGE cost

## Search and Refinement

![](../../../outputs/final/figures/pareto_frontier.png){ width=64% }

- Selected operating point: `custom_0097`, beam `16`
- Weights: `logprob=0.0`, `summac=0.75`, `factcc=1.0`, `entity=0.5`
- Refinement iteration: add entity support after error analysis
- Ablation: `0.4061 -> 0.4106` factuality composite

## Audit and Limits

![](../../../outputs/final/figures/error_taxonomy.png){ width=48% }

- 24-row stratified Codex / AI-assisted expert adjudication audit
- Outcome counts: reranker win `8`, baseline win `8`, tie/close `8`
- Dominant remaining failure: entity distortion (`12/24`)
- MiniCheck runs only on the audit subset, not the full test split
- This is a bounded study, not a benchmark-scale XSum claim

## Takeaways

- Simple reranking signals materially improve factuality on this bounded XSum run.
- Entity support is a useful small refinement, not a silver bullet.
- The strongest remaining gap is entity-level hallucination when all candidates drift the same way.
- Submission-ready deliverables now exist in-repo:
  - final report PDF
  - editable PPTX + slide PDF + speaker notes
  - packaged code and tracked artifacts
