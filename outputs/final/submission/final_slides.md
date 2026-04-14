# Final Presentation Outline

## Slide 1: Reranking Improves Factuality on XSum

- Open with the result, then immediately bound the claim.
- Preview the method in one sentence: fine-tuned BART, beam candidates, and factuality-aware reranking.

## Slide 2: What This Project Is Actually Doing

- Define the key terms before the problem slide: XSum, beam search, reranking, and ROUGE.
- Frame the core idea clearly: generate multiple candidates, then use factuality-aware selection after generation.

## Slide 3: Why Fluent XSum Summaries Can Still Be Wrong

- XSum rewards compressed summaries that can still hallucinate.
- Baseline stays the public BART XSum path; the gain should come from selection, not a swapped generator.
- Objective: improve factual support while reporting the ROUGE trade-off honestly.

## Slide 4: Generate Candidates, Score Them, Choose the Operating Point

- Generate beam candidates, score them with support / consistency / entity-grounding signals, and search weights on validation.
- Emphasize that the contribution is improved candidate selection, not a new generator architecture.

## Slide 5: Reranking Improves Factuality, With a Modest ROUGE Trade-off

- Factuality composite improves from `0.331` to `0.434`.
- ROUGE-Lsum drops from `0.359` to `0.339`.
- The selected operating point sits near the high-factuality knee of the validation frontier.

## Slide 6: Qualitative Analysis

- 24-example stratified qualitative review with `Codex / AI-assisted expert adjudication`.
- Dominant remaining failure mode: entity distortion.
- Claims stay bounded; this is not a benchmark-scale XSum claim.

## Slide 7: Takeaways

- Reranking helps.
- Entity grounding remains the main gap.
- Best next step: stronger entity preservation plus more diverse candidates.

## Slide 8: Questions

- Minimal closing slide for Q&A.
