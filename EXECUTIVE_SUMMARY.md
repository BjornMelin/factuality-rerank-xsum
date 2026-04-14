# Executive Summary

## One-sentence overview

This project studies whether **post-generation reranking** can make **XSum summarization** more factual by selecting better summaries from beam-search candidates, instead of changing the generator alone.

## Fast explanation

XSum is a difficult summarization benchmark because it rewards very short, fluent summaries, and that fluency can hide unsupported facts. The core question in this project was:

> Can reranking trade a small amount of ROUGE for meaningfully stronger factuality?

The final system answers **yes, within a bounded study**.

## What I built

The repo implements a full end-to-end research pipeline for:

1. Preparing a bounded XSum split
2. Fine-tuning `facebook/bart-large-xsum`
3. Generating multiple beam-search summary candidates
4. Scoring candidates with factuality-oriented signals
5. Searching for a good reranking operating point on validation
6. Evaluating the chosen configuration on test
7. Auditing failure modes and packaging the final report artifacts

The reranker combines:

- Support-style factuality scoring
- Consistency / entailment-style scoring
- Entity-support scoring

The final selected operating point was:

- Beam size: `16`
- Search winner: `custom_0097`
- Weights: factuality-heavy fusion with non-zero entity support

## Main result

On the bounded test split:

- **Baseline ROUGE-Lsum**: `0.3592`
- **Reranked ROUGE-Lsum**: `0.3393`
- **Baseline factuality composite**: `0.3310`
- **Reranked factuality composite**: `0.4337`

Interpretation:

- Factuality improved by about **+0.103**
- ROUGE-Lsum decreased by about **-0.020**
- Bootstrap intervals supported that this trade-off was directionally stable

This means the project found a **clear factuality gain**, but not for free: the system gives up some overlap score to become more grounded.

## Why the result matters

The project shows that a **small, interpretable post-generation selection layer** can improve factual quality without requiring a completely different summarization architecture. In other words, better candidate selection can help even when the base model is unchanged.

## What the audit showed

The final qualitative audit used a **24-example stratified Codex / AI-assisted expert adjudication sample**.

Key finding:

- The biggest remaining failure mode is **entity distortion**: wrong, swapped, or unsupported named entities

So the reranker improves overall factuality, but it does **not** solve the hardest grounding problem. The most promising next step is stronger entity preservation and more diverse candidate generation.

## Important project boundaries

This is a **bounded study**, not a benchmark-scale XSum claim.

- The final test split is `128` examples
- The qualitative audit is useful for error analysis, not human-annotation reliability claims
- The MiniCheck run is bounded subset validation, not a replacement for the main test metrics

## If I had 30 seconds to explain it

I fine-tuned a BART summarizer on XSum, generated multiple candidate summaries per article, and then reranked those candidates using factuality-focused scores instead of picking the default highest-likelihood summary. On a bounded test split, that raised a factuality composite score from `0.331` to `0.434`, while ROUGE-Lsum dropped from `0.359` to `0.339`. The main takeaway is that reranking helps factuality in a meaningful way, but entity grounding remains the hardest unsolved problem.

## Best files to open next

- [REPORT.md](./REPORT.md): canonical full project handoff
- [docs/RESULTS_SUMMARY.md](./docs/RESULTS_SUMMARY.md): concise artifact-backed metrics summary
- [outputs/final/submission/final_report.pdf](./outputs/final/submission/final_report.pdf): final written report
- [outputs/final/submission/final_slides.pptx](./outputs/final/submission/final_slides.pptx): final presentation deck
- [outputs/final/submission/speaker_notes.md](./outputs/final/submission/speaker_notes.md): presentation talking points
