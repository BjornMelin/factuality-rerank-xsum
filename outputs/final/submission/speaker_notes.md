# Speaker Notes

Estimated total time: about 6 minutes

## Slide 1: Reranking Improves Factuality on XSum (`0:30`)

This project asks a simple question: if I generate several summary candidates and then choose among them more carefully, can I make the final summary more factual? On this bounded XSum study, the answer was yes. I improved factuality meaningfully with reranking, while accepting a modest drop in ROUGE. The core pipeline was: fine-tune BART, generate beam candidates, score them with factuality signals, and then pick the best operating point.

## Slide 2: What This Project Is Actually Doing (`0:35`)

Before the results, here are the few terms that matter. XSum is a news summarization benchmark where the target is a single very short summary sentence. Beam search just means the model generates several plausible summaries instead of only one. Reranking means I score those candidates again after generation and choose the one that looks best under my scoring rule. ROUGE is a wording-overlap metric with the reference summary, so it is useful, but it does not directly tell us whether the summary is actually true. The point of this project was not to invent a new model family. It was to test whether better selection improves groundedness.

## Slide 3: Why Fluent XSum Summaries Can Still Be Wrong (`0:50`)

XSum is a hard factuality setting because it rewards aggressive compression. The summaries are short and often very fluent, but that fluency can hide unsupported facts, wrong entities, or incorrect relations. My baseline here is the public BART XSum model using normal beam-search decoding. So the question is not whether a different generator wins. The question is whether reranking can trade a small amount of ROUGE for meaningfully stronger factuality. I treated success as a higher factuality composite on the bounded test split while reporting the ROUGE cost explicitly.

## Slide 4: Generate Candidates, Score Them, Choose the Operating Point (`0:55`)

This slide shows the full method. Starting on the left, I materialize the bounded XSum split and fine-tune BART, while keeping the public baseline for comparison. Then I generate multiple beam candidate summaries for each article. The lower box is the factuality-scoring module that scores every candidate on support, consistency, and entity grounding. I then run weight search on the validation split to find a good operating point, and I evaluate that chosen setting once on test and in the audit. The important point is that the intervention happens after generation. I am not replacing the summarizer. I am choosing among its candidates more carefully.

## Slide 5: Reranking Improves Factuality, With a Modest ROUGE Trade-off (`1:20`)

Here is the main result. The baseline factuality composite was 0.331, and the reranked system increased that to 0.434. At the same time, ROUGE-Lsum went from 0.359 to 0.339, so the trade-off was about minus 0.02 ROUGE for plus 0.103 factuality. I want to be explicit that this was a deliberate operating-point choice, not an accident. On the frontier, I selected a point near the high-factuality knee rather than the highest-ROUGE corner. The bootstrap intervals were also directionally stable, which gave me more confidence that this was a real bounded improvement. A bounded MiniCheck check on the qualitative subset moved in the same direction, so the result is not resting on only one metric.

## Slide 6: Qualitative Analysis (`0:55`)

I also wanted to understand what still goes wrong. I did a 24-example stratified qualitative review with Codex and AI-assisted expert adjudication. The outcome split was balanced between reranker wins, baseline wins, and ties or close calls, but the dominant remaining error type was entity distortion. In other words, the system is still most vulnerable when a named entity is wrong, swapped, or unsupported. This also matches the refinement result in the report: adding entity support helped, but only modestly. So the conclusion is not that factuality is solved. The conclusion is that reranking helps overall, but entity grounding remains the main bottleneck.

## Slide 7: Takeaways (`0:45`)

I want to end on three points. First, a lightweight reranker materially improved factuality on this bounded XSum run. Second, the main limitation is still entity-level error, especially when all of the beam candidates drift toward the same wrong fact. Third, the most promising next step is to increase candidate diversity and add stronger entity-preservation constraints. So the short version of the project is: reranking helps, but entity grounding is still the hardest problem.

## Slide 8: Questions (`0:05`)

Thank you. I’m happy to take questions.
