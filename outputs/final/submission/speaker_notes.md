# Speaker Notes

## Slide 1: Title

- Open with the project goal: reduce factual hallucinations in extreme summarization without pretending the overlap metrics disappear.
- State the headline trade-off immediately: factuality composite rises from `0.3324` to `0.4420`, while ROUGE-Lsum falls from `0.3569` to `0.3398`.
- Emphasize that this is a bounded XSum study, not a full benchmark claim.

## Slide 2: Problem and Setup

- Explain why XSum is a hard factuality task: the target summaries are short and highly compressed, so models often invent unsupported details.
- The project keeps the public `facebook/bart-large-xsum` checkpoint as the explicit baseline comparator.
- Frame the central question clearly: can a lightweight reranking layer trade a small amount of ROUGE for better factual consistency?

## Slide 3: Method and Main Result

- The method is deliberately simple and analysis-focused.
- Fine-tune BART on the bounded train split, generate beam candidates, and rerank with four signals: likelihood, SummaC-style support, FactCC-style consistency, and entity support.
- Mention that the point was not to invent a new model family, but to ask whether better candidate selection improves factuality.
- Walk through the table from top to bottom.
- The important story is not “everything improved”; it is “factuality improved materially with a modest ROUGE cost.”
- Mention the bootstrap intervals to show that the factuality lift is stable while the ROUGE change remains slightly negative on this bounded run.

## Slide 4: Search and Refinement

- Explain that the final operating point was chosen on validation search, not on the test set.
- The selected config is `custom_0097`, beam `16`, with factuality-heavy weights and zero likelihood weight in the final fusion.
- The explicit refinement iteration was entity support, motivated by the error analysis, and it gave a small positive ablation.

## Slide 5: Qualitative Analysis and Limits

- Give the provenance once: the 24-example qualitative analysis uses `Codex / AI-assisted expert adjudication`.
- Use the sample to explain that remaining failures are dominated by entity distortion, not by a single global metric issue.
- Close by reinforcing the scope limit: this is a bounded study, not a benchmark-scale XSum paper.

## Slide 6: Takeaways

- End on the main claim: factuality improves materially, but the ROUGE trade-off remains real.
- Emphasize that entity support helped, but the next improvements likely require better candidate diversity or stronger entity constraints.
- Keep the ending forward-looking and research-oriented rather than talking about repo packaging.
