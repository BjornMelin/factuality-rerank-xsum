# PLAN.md - Hardened final implementation handoff for the XSum factuality-reranking project

This is the final merged implementation plan. It combines the stronger execution and repository discipline from the forked response with the stronger modernization, deliverable contract, and artifact design from the earlier handoff produced in this session.

This file is intended to be pasted into a new GPT-5.4 Pro coding session with the attached files from this bundle. That new session should build the repository, run the pipeline, package the outputs, and refresh the project docs based on what it actually implemented and what results it actually produced.

---

## 0. Read this first

This project is **not** a new summarizer architecture project.

It is a tightly scoped, analysis-heavy **decoding-time reranking study** on XSum:

- baseline generator: BART on XSum,
- candidate generation: beam search,
- candidate scoring: generator likelihood + entailment-style factuality + FactCC-style factuality,
- main contribution: ablations, trade-off analysis, manual hallucination audit, and one targeted refinement.

The build session must optimize for:

1. finishing the full required path,
2. producing clean artifacts,
3. preserving scientific honesty,
4. keeping every decision reportable in a 4-6 page paper.

---

## 1. Final merged verdict

### 1.1 What was kept from the earlier handoff

Retain from the earlier handoff:

- the stronger insistence on **artifact contracts** in `outputs/final/`,
- the stronger emphasis on **bootstrap confidence intervals** and report-ready outputs,
- the requirement that the implementation chat actually runs the pipeline and does not stop at scaffolding,
- the notebook artifact and final-writing handoff structure,
- the explicit fallback away from the archived original FactCC codebase toward a modern implementation path.

### 1.2 What was kept from the forked response

Retain from the forked response:

- the stronger **repo tree**,
- the stronger **runbook / prompt / packaging structure**,
- the clearer **artifact-first philosophy**,
- the explicit notion that the **candidate-level scored table is the central artifact**,
- the cleaner **execution phases / verification gates / failure rules**,
- the stronger **RESULTS_SUMMARY-first** handoff to the writing chat.

### 1.3 What changed after fresh review and current-state research

After reviewing current docs, model cards, package pages, repositories, and newer factuality papers, the final merged plan changes several things:

1. **FactCC path**
   - Required path: use a modern FactCC-style inference route, with the public Hugging Face checkpoint `manueldeprada/FactCC` as the first-choice implementation.
   - Optional advanced path: train a small FactCC-style classifier on synthetic corruptions only **after** the core pipeline is working.

2. **Metric shelf modernization**
   - Required: ROUGE, SummaC, FactCC-style, manual audit.
   - Optional modern subset metrics: MiniCheck and/or FENICE on a subset.
   - QAGS remains literature-relevant but implementation-optional and explicitly deprioritized.

3. **Environment strategy**
   - Default: one modern `uv`-managed project environment.
   - Fallback: a second lightweight metric environment only if SummaC or another factuality tool conflicts with the core stack.
   - PyTorch must be installed using the official selector, not guessed.

4. **Reproducibility**
   - Pin exact package versions in `pyproject.toml`.
   - Pin dataset and model revisions / commit hashes wherever feasible.
   - Save config snapshots and artifact manifests at every expensive stage.

---

## 2. The exact project statement to preserve

Use this exact research anchor unless real results force you to narrow the wording:

> We investigate factual hallucinations in abstractive summarization and test whether decoding-time reranking of beam-search candidates can reduce factual errors without materially hurting standard overlap metrics. Using XSum and a BART summarizer, we generate a small candidate set per article and rerank summaries with a mixture of (i) a FactCC-style factual-consistency classifier, (ii) an entailment-based consistency signal in the style of SummaC, and (iii) the summarizer log-likelihood. We evaluate the trade-off surface over beam sizes and score weights using ROUGE and automatic factuality metrics, then validate these gains with a manual hallucination audit.

Do not let the build session drift into:

- a correction or rewriting system,
- an LLM judge benchmark,
- a multi-summarizer benchmark zoo,
- a heavy retraining or RL project,
- a QAGS replication project.

---

## 3. Non-negotiable success criteria

## 3.1 Core experimental requirements

The build session must deliver:

- [ ] Baseline summarization on XSum using `facebook/bart-large-xsum`
- [ ] Beam candidate generation with cached outputs
- [ ] Candidate log-likelihood extraction from generation outputs
- [ ] Candidate-level SummaC scores
- [ ] Candidate-level FactCC-style scores
- [ ] Candidate-level merged score table
- [ ] Weight search over reranking signals
- [ ] Evaluation with ROUGE-1 / ROUGE-2 / ROUGE-L / ROUGE-Lsum
- [ ] At least one factuality metric beyond ROUGE in all main tables
- [ ] A Pareto-style trade-off analysis
- [ ] At least 3 meaningful reranking ablations
- [ ] A manual audit CSV with a concise hallucination taxonomy
- [ ] One targeted refinement tied to observed errors
- [ ] A packaged repo zip and final handoff docs

## 3.2 Rubric-driven requirements

The finished repo must support:

- [ ] proposal readiness,
- [ ] final paper writing,
- [ ] presentation creation,
- [ ] instructor-inspectable code and outputs,
- [ ] a methodology-heavy narrative with error analysis,
- [ ] at least one iteration informed by analysis.

## 3.3 Hard artifact contract for the writing chat

The build chat must leave behind these files, or clearly explain why one is missing and what alternative file replaces it:

```text
outputs/final/
├── main_metrics.csv
├── ablation_metrics.csv
├── pareto_points.csv
├── bootstrap_cis.json
├── manual_audit.csv
├── manual_audit_summary.json
├── examples_success.md
├── examples_failures.md
├── figures/
│   ├── pipeline_diagram.png
│   ├── pareto_frontier.png
│   ├── beam_tradeoff.png
│   ├── component_ablation.png
│   ├── error_taxonomy.png
│   └── metric_vs_human_scatter.png
├── tables/
│   ├── report_tables.md
│   ├── qualitative_examples.csv
│   └── audit_taxonomy_table.csv
└── system_card.md
```

Required repo docs:

```text
docs/
├── RUNBOOK.md
├── RESULTS_SUMMARY.md
├── SUBMISSION_CHECKLIST.md
├── SLIDES_OUTLINE.md
└── CLAIMS_SAFE_TO_WRITE.md
```

---

## 4. Final architecture decisions

## 4.1 Dataset

**Use XSum as the main dataset.**

Do not switch the main study to CNN/DailyMail. XSum is more abstractive and therefore a better factuality stress test.

Implementation rules:

- use the official public XSum dataset path through Hugging Face,
- do not redistribute raw data in the repo zip,
- cache only derived artifacts needed for reproducibility,
- save the exact dataset `revision` you used.

Expected fields:

- `document`
- `summary`
- `id`

Expected splits:

- train: 204,045
- validation: 11,332
- test: 11,334

## 4.2 Generator

**Primary baseline:** `facebook/bart-large-xsum`

**Optional secondary baseline:** a short clean fine-tune of `facebook/bart-large` on XSum via the official Hugging Face summarization stack.

Decision rule:

- if compute is tight, the public `bart-large-xsum` checkpoint is the main baseline,
- if compute allows and the run is clean, include the short fine-tune path as an additional row or a swap-in baseline,
- do not block the project on full fine-tuning.

## 4.3 Candidate generation

Use beam search and store multiple candidates per example.

Default grid:

- `num_beams`: 4, 8, 16
- `num_return_sequences = num_beams`
- `length_penalty`: 0.8, 1.0, 1.2
- `no_repeat_ngram_size = 3`
- `max_new_tokens = 64`
- `min_new_tokens = 10`

Required stored values:

- generated text,
- generated token ids,
- Hugging Face `sequences_scores`,
- per-token transition scores,
- average token log-probability,
- beam rank,
- summary length,
- full generation config snapshot.

## 4.4 Candidate-level likelihood extraction

This is mandatory.

Use:

- `return_dict_in_generate=True`
- `output_scores=True`
- `model.compute_transition_scores(outputs.sequences, outputs.scores, outputs.beam_indices, normalize_logits=False)`

Store:

- raw Hugging Face sequence score,
- sum of token transition scores,
- average token transition score,
- optional length-normalized forms.

Do not rely only on beam rank.

## 4.5 Required scoring signals

Required core signals:

1. generator log-likelihood
2. SummaC-style entailment consistency score
3. FactCC-style summary factuality score

Required targeted-refinement candidate:
4. entity/date/number support score

Optional analysis-only signals:

- BERTScore
- summary length
- extractiveness / coverage statistics
- MiniCheck subset score
- FENICE subset score

## 4.6 Primary factuality stack

### Required

- **SummaCConv** as the main entailment-style signal
- **FactCC-style** classifier as the second factuality signal

### Recommended optional add-on on a subset

Choose at most one modern extra metric after the required path is complete:

- **MiniCheck** for sentence-level evidence-grounded checking, or
- **FENICE** for a modern summarization-specific factuality metric

### Explicitly optional and deprioritized

- **QAGS**

QAGS may be mentioned in related work and, only if the environment is already working, run on a tiny subset. It is not a required dependency and must not block the core pipeline.

## 4.7 Reranker

Use a simple, interpretable fusion function, not a learned reranker.

Primary fused score:

```text
score = a * generator_score + b * summac_score + c * factcc_score + d * entity_support_score
```

Default policy:

- start with `a, b, c`,
- add `d` only after the first analysis pass or in the targeted refinement ablation.

Support:

- z-score normalization,
- min-max normalization,
- rank-based fusion,
- optional constrained weights summing to 1.

## 4.8 Weight search policy

Tune only on validation.
Never use test during iteration.

Stage the search:

1. coarse search on `dev_small`,
2. narrowed search on `val_tune`,
3. lock final settings,
4. evaluate once on test.

Select at least three operating points:

- **best balanced**
- **best factuality**
- **best ROUGE-preserving** under a small ROUGE tolerance

## 4.9 Manual audit taxonomy

Use this taxonomy:

1. Entity swap / wrong named entity / unsupported named entity
2. Number or date distortion
3. Negation / polarity / stance reversal
4. Unsupported relation / unsupported event composition / unsupported causal link
5. Source-unsupported but plausibly factual world knowledge addition
6. No clear factual issue

The fifth bucket is important because modern factuality work shows that some hallucinated content can still be true in the world while remaining unsupported by the source. Do not collapse that into the main hallucination buckets.

## 4.10 Default targeted refinement

Default refinement:

- **entity/date/number support score**

Fallback refinements if the audit points elsewhere:

- sentence-level entailment aggregation,
- stronger length normalization,
- candidate deduplication and tie-breaking,
- source-sentence coverage bias.

Do not escalate to RL, preference optimization, or end-to-end correction unless everything else is complete.

---

## 5. Decision framework that selected this final merged plan

Use this custom weighted decision framework to guide implementation decisions.

| Criterion | Weight | What “good” means |
| --- | ---: | --- |
| Proposal fidelity | 15% | Stays tightly aligned to the approved proposal |
| Research grounding + freshness | 15% | Uses current docs, model cards, package status, and modern factuality literature |
| Implementation specificity | 20% | Gives exact repo structure, commands, schemas, configs, and execution order |
| Reproducibility + environment robustness | 15% | Lockfiles, explicit versions, fallbacks, cache policy, test lock |
| Analysis + audit design | 15% | Strong manual audit, ablations, figures, and claim discipline |
| Scope control + risk handling | 10% | Prevents optional tools from blocking completion |
| Handoff + prompt usability | 10% | Makes the next chats easy to run correctly |

### Weighted scores from the comparison

- Earlier handoff from this session: **9.05 / 10**
- Forked response: **9.36 / 10**
- Final merged hardened handoff: **9.76 / 10**

Interpretation:

- the fork was stronger on execution detail,
- the earlier handoff was stronger on modernization and final artifact contract,
- the merged version is strongest because it keeps the fork’s operational discipline while tightening the factuality stack, environment strategy, and deliverable guarantees.

---

## 6. Environment and version strategy

## 6.1 Primary environment manager

Use **`uv`** for the main project environment.

Why:

- `uv` natively manages `pyproject.toml`,
- creates `.python-version`, `.venv`, and `uv.lock`,
- supports `uv run`, `uv sync`, and `uv lock`,
- is ideal for a clean, reproducible project repo.

## 6.2 Python version

Use **Python 3.11** unless the host only cleanly supports 3.12.

Reason:

- current core packages support Python 3.10+,
- 3.11 is a safe middle ground for PyTorch + HF tooling,
- 3.11 is less likely than 3.12 to surface edge-case dependency incompatibilities.

## 6.3 PyTorch installation policy

Do **not** guess the PyTorch install command.
Use the official PyTorch selector for the host platform and CUDA version.

Required behavior:

- save the exact command used in `docs/RUNBOOK.md`,
- record `torch.__version__`,
- record CUDA availability and device name,
- record whether fp16 or bf16 was used.

## 6.4 Current package pins to start from

Use these exact pins in the default `pyproject.toml` example unless the build chat finds a verified incompatibility on the host:

```toml
transformers==5.5.3
datasets==4.8.4
accelerate==1.13.0
evaluate==0.4.6
peft==0.18.1
sentencepiece==0.2.1
```

Additional recommended dependencies:

```toml
rouge_score>=0.1.2
bert-score>=0.3.13
nltk>=3.9
numpy>=1.26,<3
pandas>=2.2,<3
pyarrow>=17,<20
scikit-learn>=1.5,<2
scipy>=1.13,<2
matplotlib>=3.9,<4
pyyaml>=6.0,<7
jsonlines>=4.0.0,<5
typer>=0.12,<1
rich>=13,<14
spacy>=3.8,<4
```

Important:

- install PyTorch first via the official selector,
- then `uv sync`.

## 6.5 Single-env default, two-env fallback

### Default

Try to keep one `uv` project environment.

### Fallback

If `summac` or another factuality tool conflicts with the main stack, create:

- `.venv-core` for training / generation / evaluation,
- `.venv-metrics` for SummaC and optional legacy-like metrics.

This is a fallback, not the starting assumption.

## 6.6 Reproducibility rules

- save `uv.lock`,
- export `pip freeze`,
- save package versions in `VERSIONS.md`,
- pin dataset and model `revision` / commit ids where possible,
- save all config YAMLs copied into the output package,
- never overwrite final selected configs silently.

---

## 7. Repository that the build session must create

Use this repo structure or something very close to it:

```text
factuality-rerank-xsum/
├── README.md
├── PLAN.md
├── REPORT.md
├── DECISION_FRAMEWORK.md
├── REFERENCES_FULL_URLS.md
├── VERSIONS.md
├── .python-version
├── pyproject.toml
├── uv.lock
├── Makefile
├── .gitignore
├── LICENSE
├── configs/
│   ├── data/
│   │   └── xsum.yaml
│   ├── model/
│   │   ├── bart_xsum_public.yaml
│   │   ├── bart_xsum_finetune.yaml
│   │   └── factcc_hf.yaml
│   ├── generate/
│   │   ├── beams_4.yaml
│   │   ├── beams_8.yaml
│   │   └── beams_16.yaml
│   ├── score/
│   │   ├── summac.yaml
│   │   ├── factcc.yaml
│   │   ├── entity_support.yaml
│   │   ├── minicheck_optional.yaml
│   │   └── fenice_optional.yaml
│   ├── rerank/
│   │   ├── weight_grid.yaml
│   │   └── final_selection.yaml
│   └── audit/
│       └── annotation_schema.yaml
├── scripts/
│   ├── 00_env_check.py
│   ├── 01_prepare_xsum.py
│   ├── 02_train_or_load_bart.py
│   ├── 03_generate_candidates.py
│   ├── 04_score_candidates_summac.py
│   ├── 05_score_candidates_factcc.py
│   ├── 06_score_candidates_entity_support.py
│   ├── 07_score_candidates_minicheck_optional.py
│   ├── 08_merge_candidate_scores.py
│   ├── 09_search_weights.py
│   ├── 10_rerank_and_eval.py
│   ├── 11_bootstrap_metrics.py
│   ├── 12_sample_manual_audit.py
│   ├── 13_summarize_manual_audit.py
│   ├── 14_make_tables_and_figures.py
│   ├── 15_build_results_summary.py
│   └── 16_package_repo.py
├── src/
│   └── factuality_rerank_xsum/
│       ├── __init__.py
│       ├── cli/
│       ├── data/
│       ├── generation/
│       ├── scorers/
│       ├── rerank/
│       ├── eval/
│       ├── audit/
│       ├── viz/
│       └── utils/
├── notebooks/
│   ├── 01_sanity_checks.ipynb
│   ├── 02_candidate_analysis.ipynb
│   ├── 03_final_figures.ipynb
│   └── 04_manual_audit_review.ipynb
├── docs/
│   ├── RUNBOOK.md
│   ├── RESULTS_SUMMARY.md
│   ├── SUBMISSION_CHECKLIST.md
│   ├── SLIDES_OUTLINE.md
│   └── CLAIMS_SAFE_TO_WRITE.md
├── data/
│   ├── cache/
│   ├── processed/
│   └── audit/
├── artifacts/
│   ├── models/
│   ├── generations/
│   ├── scores/
│   ├── search/
│   ├── eval/
│   ├── audit/
│   ├── figures/
│   ├── tables/
│   └── package/
└── outputs/
    └── final/
```

---

## 8. Data policy and subset design

## 8.1 Raw data policy

- do not commit raw XSum data,
- do not redistribute raw XSum data in the final zip,
- keep only IDs, cached processed forms, and generated outputs.

## 8.2 Deterministic subsets

Create and save deterministic ID lists:

- `dev_smoke`: 64 examples
- `dev_small`: 500 examples
- `val_tune`: 3,000 examples
- `val_full`: full validation
- `test_final`: full test

Persist files:

```text
data/processed/splits/
├── dev_smoke_ids.txt
├── dev_small_ids.txt
├── val_tune_ids.txt
├── val_full_ids.txt
└── test_final_ids.txt
```

## 8.3 Test-set lock

The build session must not iteratively tune on test.
Use test once after final selection is locked.

---

## 9. Baseline generator plan

## 9.1 Required baseline

Start with `facebook/bart-large-xsum`.

## 9.2 Optional second baseline

If compute allows, run a short clean fine-tune of `facebook/bart-large` on XSum with `Seq2SeqTrainer`.

## 9.3 Recommended training defaults for the optional fine-tune

```yaml
seed: 42
model_name_or_path: facebook/bart-large
dataset_name: EdinburghNLP/xsum
text_column: document
summary_column: summary
max_source_length: 1024
max_target_length: 64
val_max_target_length: 64
per_device_train_batch_size: 1
per_device_eval_batch_size: 2
gradient_accumulation_steps: 16
learning_rate: 3e-5
weight_decay: 0.01
num_train_epochs: 1
warmup_ratio: 0.03
label_smoothing_factor: 0.1
predict_with_generate: true
generation_max_new_tokens: 64
generation_num_beams: 5
save_total_limit: 2
fp16: true
```

## 9.4 Baseline evaluation policy

Evaluate the baseline on:

- `dev_small`
- `val_tune`
- `val_full`
- `test_final` only after locking final settings

Persist:

- raw predictions,
- decoded predictions,
- per-example lengths,
- ROUGE metrics JSON,
- runtime metadata.

---

## 10. Candidate generation implementation details

## 10.1 Candidate schema

Store candidate rows in both parquet and JSONL if possible.

Required fields:

```json
{
  "id": "string",
  "split": "validation",
  "document": "string",
  "reference": "string",
  "candidate_id": 0,
  "beam_rank": 0,
  "summary": "string",
  "summary_token_ids": [0,1,2],
  "summary_len_tokens": 27,
  "sequence_score_hf": -0.123,
  "token_logprob_sum": -12.34,
  "token_logprob_avg": -1.234,
  "num_beams": 8,
  "length_penalty": 1.0,
  "no_repeat_ngram_size": 3,
  "max_new_tokens": 64,
  "min_new_tokens": 10,
  "candidate_hash": "..."
}
```

## 10.2 Candidate deduplication

Within each example:

- trim leading/trailing whitespace,
- normalize internal whitespace,
- exact-string deduplicate,
- preserve the best original beam rank,
- record `num_unique_candidates`.

## 10.3 Integrity report

For every generation run, save:

```text
artifacts/generations/<run_name>/integrity_report.json
```

Checks:

- all requested example IDs appear exactly once,
- each example has at least one candidate,
- candidate text is non-empty,
- candidate scores have no NaNs,
- duplicates are documented.

---

## 11. Scorers

## 11.1 SummaC

Implement `SummaCConv` as the main entailment-style scorer.

Required behavior:

- batched scoring,
- deterministic cache key,
- per-candidate scores written to parquet / CSV.

## 11.2 FactCC-style scorer

### Required implementation path

Use `manueldeprada/FactCC` as the first-choice inference path.

### Optional advanced implementation path

Only after the full pipeline is working, optionally train a small FactCC-style classifier on synthetic corruptions.

If the build chat chooses the training path, it must still keep the inference checkpoint path available as a reproducible fallback.

## 11.3 Entity/date/number support scorer

Implement a lightweight rule-based feature using:

- spaCy NER,
- regex for dates and numeric patterns,
- normalized string matching against the source article.

Required sub-scores:

- entity precision in source
- number precision in source
- date precision in source
- combined support score

This scorer can be used:

- as a targeted refinement feature,
- as an analysis slice,
- as a metric-disagreement diagnosis tool.

## 11.4 Optional modern subset metric: MiniCheck

Only after the required stack is done, MiniCheck may be run on a subset because:

- it is an actively maintained grounding-based checker,
- it has a simple install path from GitHub,
- it is sentence-level and therefore useful for audit validation.

Do not make it the only factuality metric.
Do not let it delay the main path.

## 11.5 Optional modern subset metric: FENICE

FENICE is an acceptable optional subset metric because it is a modern summarization-specific factuality metric and has a public repository.

Use it only if:

- the required stack is already working,
- its install path is stable on the host,
- and there is time left after the core experiments.

## 11.6 QAGS

Keep QAGS outside the required path.

Policy:

- mention in related work,
- optionally run on 50-100 examples only if the environment is already stable,
- document clearly if it is skipped.

---

## 12. Score fusion and weight search

## 12.1 Fusion modes to implement

At minimum implement these modes:

1. `logprob_only`
2. `summac_only`
3. `factcc_only`
4. `logprob + summac`
5. `logprob + factcc`
6. `summac + factcc`
7. `logprob + summac + factcc`
8. `logprob + summac + factcc + entity_support`

Optional:

- `logprob + MiniCheck` on a subset,
- `logprob + FENICE` on a subset.

## 12.2 Normalization options

Support at least:

- global z-score,
- global min-max,
- rank fusion.

Default selection:

- start with global z-score.

## 12.3 Search strategy

Stage 1: `dev_small`

- coarse grid over weights,
- coarse sweep over beam sizes.

Stage 2: `val_tune`

- narrowed search around the best region.

Stage 3: `val_full`

- run only the shortlisted operating points.

## 12.4 Selection criteria

Select at least three final operating points:

- **best balanced**: highest factuality under a small ROUGE-Lsum drop tolerance
- **best factuality**: highest factuality regardless of ROUGE
- **best simple**: the best single additional scorer over logprob-only

Save:

```text
artifacts/search/
├── grid_results.csv
├── best_balanced.yaml
├── best_factuality.yaml
├── best_simple.yaml
└── pareto_points.csv
```

---

## 13. Evaluation policy

## 13.1 Required automatic metrics

Required:

- ROUGE-1
- ROUGE-2
- ROUGE-L
- ROUGE-Lsum
- SummaC aggregate
- FactCC-style aggregate

Recommended:

- BERTScore for context only
- entity support aggregate for refinement analysis

Optional subset metrics:

- MiniCheck
- FENICE
- QAGS

## 13.2 ROUGE implementation details

Use Evaluate’s ROUGE metric with:

- `use_stemmer=True`

For ROUGE-Lsum:

- sentence tokenize,
- join sentences with newline before metric computation.

## 13.3 Confidence intervals

Compute bootstrap confidence intervals for the main comparisons on validation and test if feasible.

Minimum:

- `bootstrap_cis.json` for the main selected system vs baseline on ROUGE-Lsum and one factuality metric.

## 13.4 Per-example comparison table

Create one joined table with:

- baseline summary,
- reranked summary,
- reference,
- all metrics,
- audit flags,
- candidate selection trace.

This table will drive:

- qualitative examples,
- manual audit sampling,
- metric disagreement analysis.

---

## 14. Manual audit protocol

## 14.1 Why the audit is mandatory

Automatic factuality metrics vary in performance across datasets and summarizer families. The project makes claims about hallucinations, not just about proxy metrics. Therefore the audit is mandatory.

## 14.2 Sampling strategy

Sample from validation using stratified buckets:

1. baseline weak -> reranker strong by metrics
2. baseline strong -> reranker weak by metrics
3. both strong
4. both weak
5. large ROUGE / factuality disagreement
6. strong entity-support penalties
7. strong metric disagreement between SummaC and FactCC

Target:

- 80 to 120 examples total

Recommended:

- 15-20 examples per key bucket

## 14.3 Annotation template

Save:

```text
data/audit/manual_audit_template.csv
```

Required columns:

```csv
id,split,document,reference,baseline_summary,reranked_summary,selected_system,baseline_consistent,reranked_consistent,primary_error_type,secondary_error_type,world_knowledge_addition,notes
```

## 14.4 Audit outputs

Save:

```text
artifacts/audit/
├── manual_audit_completed.csv
├── manual_audit_summary.json
├── audit_disagreement_cases.csv
└── audit_examples_for_paper.csv
```

If a second independent pass is possible:

- compute Cohen’s kappa or intra-annotator consistency,
- document it in `RESULTS_SUMMARY.md`.

## 14.5 Targeted refinement decision

Use the audit, not guesswork, to decide whether the entity/date/number support feature becomes part of the final selected reranker.

Required statement in `docs/RESULTS_SUMMARY.md`:
> The dominant remaining failures were X and Y, which motivated refinement Z.

---

## 15. Figures and tables that must be produced

## 15.1 Figures

Required figures:

1. pipeline diagram
2. Pareto frontier
3. beam-size trade-off plot
4. component ablation chart
5. metric-disagreement plot
6. manual-audit taxonomy chart

Optional:
7. score correlation heatmap
8. candidate diversity histogram

## 15.2 Tables

Required tables:

1. main validation results
2. main test results
3. ablation results
4. beam-size comparison
5. manual audit summary
6. qualitative examples

## 15.3 File formats

Save figures as:

- PNG
- PDF if easy

Save tables as:

- CSV
- Markdown for the paper-writing chat

---

## 16. Notebook plan and jupyter-notebook skill usage

Use the attached notebook skill to scaffold clean, reproducible notebooks.

Required notebook roles:

- `01_sanity_checks.ipynb` - dataset loading, baseline sanity, candidate schema checks
- `02_candidate_analysis.ipynb` - candidate diversity, score distributions, reranker slices
- `03_final_figures.ipynb` - regenerate the paper figures from saved artifacts
- `04_manual_audit_review.ipynb` - audit summaries and qualitative selection

Use the helper script pattern from the attached skill to scaffold new notebooks if needed.
Do not let notebooks become the only execution path.
Scripts remain the primary path; notebooks are for analysis and presentation.

---

## 17. Command surface and Makefile targets

Required `Makefile` targets:

```make
env:
 uv sync

smoke:
 uv run python scripts/00_env_check.py

data:
 uv run python scripts/01_prepare_xsum.py

train:
 uv run python scripts/02_train_or_load_bart.py

generate:
 uv run python scripts/03_generate_candidates.py

score:
 uv run python scripts/04_score_candidates_summac.py && \
 uv run python scripts/05_score_candidates_factcc.py && \
 uv run python scripts/06_score_candidates_entity_support.py

search:
 uv run python scripts/09_search_weights.py

eval:
 uv run python scripts/10_rerank_and_eval.py && \
 uv run python scripts/11_bootstrap_metrics.py

audit:
 uv run python scripts/12_sample_manual_audit.py && \
 uv run python scripts/13_summarize_manual_audit.py

figures:
 uv run python scripts/14_make_tables_and_figures.py

results-summary:
 uv run python scripts/15_build_results_summary.py

package:
 uv run python scripts/16_package_repo.py
```

Fallback if a second metric environment is needed:

- document the alternative commands in `docs/RUNBOOK.md`.

---

## 18. Execution phases

## Phase 0 - Fresh verification

Before writing code:

- verify package versions,
- verify model cards,
- verify repo status for FactCC / SummaC / MiniCheck / FENICE,
- verify XSum dataset path and split sizes.

## Phase 1 - Repo bootstrap

- create repo skeleton,
- write `pyproject.toml`,
- install PyTorch via official selector,
- `uv sync`,
- create `README.md`,
- create `docs/RUNBOOK.md`,
- save `VERSIONS.md`.

## Phase 2 - Smoke test

- load XSum
- load BART
- generate on 10-20 examples
- verify ROUGE
- verify candidate parquet schema
- verify at least one factuality scorer import

## Phase 3 - Baseline

- evaluate `facebook/bart-large-xsum` on `dev_small`
- evaluate on `val_tune`
- optionally run short fine-tune
- lock the main generator

## Phase 4 - Candidate generation

- generate beams on `dev_small`
- save and inspect candidate tables
- expand to `val_tune`
- shortlist decode configs
- run selected configs on `val_full`

## Phase 5 - Scoring

- SummaC scores
- FactCC-style scores
- entity/date/number support
- optional MiniCheck / FENICE subset scores
- merge candidate tables

## Phase 6 - Weight search and reranking

- coarse grid on `dev_small`
- narrowed search on `val_tune`
- run shortlisted operating points on `val_full`
- select final configs

## Phase 7 - Manual audit and refinement

- build audit sample
- annotate
- summarize taxonomy
- choose targeted refinement
- rerun the refinement ablation

## Phase 8 - Final evaluation

- evaluate locked systems on `test_final`
- compute bootstrap CIs
- create paper tables and figures
- write `RESULTS_SUMMARY.md`

## Phase 9 - Packaging

- clean repo
- export artifact manifest
- zip final repo
- refresh `PLAN.md`
- leave a truthful final summary for the writing chat

---

## 19. Verification gates

Do not move past a phase until its gate passes.

### Gate A - Environment

- [ ] PyTorch installed with official selector command
- [ ] `uv sync` succeeds
- [ ] versions logged
- [ ] tokenizer and model imports succeed
- [ ] NLTK sentence tokenizer works
- [ ] spaCy model installed if entity scorer is enabled

### Gate B - Data

- [ ] XSum loads
- [ ] fields are `document`, `summary`, `id`
- [ ] split sizes match expectations
- [ ] deterministic subset IDs saved

### Gate C - Baseline

- [ ] baseline generation runs on `dev_small`
- [ ] ROUGE outputs exist
- [ ] prediction schema is valid

### Gate D - Candidate generation

- [ ] multiple candidates are saved
- [ ] deduplication works
- [ ] sequence scores and transition scores exist
- [ ] integrity report saved

### Gate E - Scoring

- [ ] SummaC scores exist
- [ ] FactCC-style scores exist or documented fallback exists
- [ ] merged candidate score table exists

### Gate F - Reranking

- [ ] search results table exists
- [ ] at least one reranker operating point is reportable
- [ ] baseline anchor row exists

### Gate G - Audit

- [ ] audit sample exists
- [ ] annotation schema exists
- [ ] audit summary table exists

### Gate H - Final package

- [ ] final tables exist
- [ ] final figures exist
- [ ] RESULTS_SUMMARY exists
- [ ] zip export exists

---

## 20. Minimal ablation matrix

At minimum run:

1. baseline best-likelihood output
2. beam=4 logprob only
3. beam=8 logprob only
4. beam=16 logprob only
5. beam=8 SummaC only
6. beam=8 FactCC only
7. beam=8 logprob + SummaC
8. beam=8 logprob + FactCC
9. beam=8 SummaC + FactCC
10. beam=8 logprob + SummaC + FactCC
11. best combined + entity support refinement

Optional extra:
12. best combined + MiniCheck subset evaluation
13. best combined + FENICE subset evaluation

---

## 21. Failure-handling rules

## 21.1 If FactCC checkpoint path is brittle

Fallback order:

1. `manueldeprada/FactCC` via Transformers inference
2. optional small custom FactCC-style classifier only if time permits
3. SummaC + audit as the main factuality story, with FactCC clearly documented as unavailable

## 21.2 If SummaC conflicts with the main environment

- create `.venv-metrics`,
- run SummaC scoring out-of-process,
- merge score files later,
- document the split environment in `RUNBOOK.md`.

## 21.3 If QAGS is brittle

Skip it.
Do not let it affect the required path.

## 21.4 If MiniCheck or FENICE is brittle

Skip them.
They are bonus-only.

## 21.5 If beam=16 is too expensive

Use 4, 8, 12.

## 21.6 If full validation scoring is too heavy

Run:

- baseline on full validation,
- search on `val_tune`,
- final selected systems on full validation and test.

## 21.7 If candidate diversity is too low

Try one of:

- slightly different length penalties,
- increase beams,
- enable early deduplication and analyze unique-candidate counts.

---

## 22. README requirements

The repo `README.md` must include:

- project summary,
- setup steps,
- PyTorch install note,
- `uv` usage,
- quick path vs full path,
- main commands,
- artifact map,
- expected outputs,
- troubleshooting for SummaC / FactCC / optional metrics.

---

## 23. Required docs outputs

### `docs/RUNBOOK.md`

Must include:

- exact order of operations,
- host assumptions,
- hardware notes,
- environment fallback path,
- artifact locations,
- troubleshooting,
- memory-saving settings.

### `docs/RESULTS_SUMMARY.md`

This is the most important handoff file for the writing chat.
It must include:

- actual chosen baseline,
- actual chosen reranker,
- exact metrics,
- exact commands,
- exact artifact paths,
- key findings,
- limitations,
- safe claims.

### `docs/SUBMISSION_CHECKLIST.md`

Must map repo artifacts to the course rubric and deliverables.

### `docs/SLIDES_OUTLINE.md`

Must provide the 6-minute narrative:

1. motivation
2. method
3. candidate reranking
4. main results
5. audit and refinement
6. conclusion

### `docs/CLAIMS_SAFE_TO_WRITE.md`

Must list:

- claims supported by actual outputs,
- claims that are too strong and should not be written,
- caveats and limitations.

---

## 24. Prompt protocol for the next chats

### Chat 1 - build and run the repo

Attach:

- this `PLAN.md`
- `REPORT.md`
- `DECISION_FRAMEWORK.md`
- `REFERENCES_FULL_URLS.md`
- prompt file [PROMPT_01_BUILD_REPO_AND_RUN_PIPELINE.md](../prompts/PROMPT_01_BUILD_REPO_AND_RUN_PIPELINE.md)
- optional notebook file(s)

What Chat 1 must do:

- inspect all attachments,
- verify package and repo freshness,
- implement the full codebase,
- run the pipeline,
- populate outputs,
- package the repo zip,
- refresh all docs based on actual implementation.

### Chat 2 - analyze the built repo and write the paper

Attach:

- the built repo zip from Chat 1
- this `PLAN.md`
- `REPORT.md`
- `DECISION_FRAMEWORK.md`
- prompt file [PROMPT_02_ANALYZE_RESULTS_AND_WRITE_REPORT.md](../prompts/PROMPT_02_ANALYZE_RESULTS_AND_WRITE_REPORT.md)

What Chat 2 must do:

- inspect actual outputs,
- extract a truthful narrative,
- write the final paper,
- write the slide outline,
- avoid inventing any result not present in artifacts.

### Chat 3 - final QA / submission polish

Attach:

- the final report from Chat 2
- the repo zip
- prompt file [PROMPT_03_FINAL_QA_SUBMISSION_REVIEW.md](../prompts/PROMPT_03_FINAL_QA_SUBMISSION_REVIEW.md)

What Chat 3 must do:

- perform a rubric-by-rubric final review,
- verify citations, tables, figure references, and claims,
- generate a final submission checklist and any last corrections.

---

## 25. What the build chat must not forget

- [ ] Use `return_dict_in_generate=True` and `output_scores=True`
- [ ] Save transition scores with `compute_transition_scores`
- [ ] For ROUGE-Lsum, newline-separate sentences
- [ ] Pin dataset revision / snapshot
- [ ] Save config copies used for each run
- [ ] Save the exact selected weights
- [ ] Keep the baseline row in every main table
- [ ] Do not tune on test
- [ ] Generate manual audit sheets early
- [ ] Refresh `RESULTS_SUMMARY.md` at the end

---

## 26. Final instruction to the next build chat

Build the repository to completion.
Be conservative in claims and aggressive in execution.
Do not let optional components block the required path.
If something fails, document it clearly and fall back to the strongest simpler alternative while preserving the project’s scientific core.
