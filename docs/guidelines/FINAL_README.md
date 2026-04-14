# Final Project Guidelines

Superseded as the preferred long-form course guide.

Use `docs/guidelines/FINAL_PROJECT_GUIDELINES.md` as the canonical long-form
course reference. Keep this file only as a compatibility mirror for older
links.

## Introduction

Beyond programming assignments, you do a final project: significant NLP implementation and/or application. Expect:

- Group up to 3; solo OK; collaboration encouraged.
- Larger teams → more total work expected.
- Topic = anything in class scope; need not match lecture.
- Turn in: research-style write-up, short presentation, code.

## Grading

Heavier than one assignment: planning, research, plus pipeline (data, experiments, plots). **Start early; ask questions.**

Milestones:

- \[1%\] **Project Proposal**  
- \[0%\] **Milestone (optional)**  
- \[99%\] **Write-Up and Final Presentation**

With 2 or 3 members, each person should work with **at least one separate model** in experiments. Else possible point loss.

### Our Expectations of You

Graduate course: **you** seek help when stuck. Support exists if you ask.  
Don’t wait for feedback on deliverables to move. Formal path: Milestone section.

### Rubric Dimensions

Each dimension counts. Weak in one → much lower grade. Bullets show common failure modes; projects differ -- use judgment.

**Overall themes (10%):**

- Clear problem statement.  
- Novelty of approach.  
- Who else worked on this? What did they do? What do you do differently?  
- Read and understood cited papers? Right ones?

**Crisp objective (20%):**

- "How will I know success?" → usually an evaluation metric.  
- Tied to problem statement -- why this objective?  
- Clear baseline (e.g. classification: always predict majority class).  
- Same objective others use? If not, why?

**Methodology and analysis (50%):**

- Techniques fit the problem?  
- First attempts → what learned → how improved later iterations?  
- Weird data patterns? Model vs data? Interesting losses?  
- Patterns match papers? What did they do?

**Technical communication (20%):**

- Primarily: succinct, interesting talk; paper well organized.  
- Table stakes: spell check; proofread.

**Volume of work** (folded into other parts):

- Not only others’ GitHub + clean Kaggle data.  
- Not only assignment notebooks on new data with canned analysis.  
- Teams of 3: each person should show ~solo-project-level effort.

**Scoring each dimension:**

- Missing: 0%  
- Severe Issues: 1% - 69%  
- Needs more work/thought: 70% - 82%  
- Satisfactory: 83% - 88%  
- Strong: 89% - 94%  
- Near-publishable: 95% - 100%

Expect **Strong** on most parts for most students.

## Project Scope and Ideas

Very open-ended; **must be NLP** at core: text, speech, or other language. Need not be novel like full research; should be **non-trivial or non-obvious** with data and/or algorithm.

Examples:

- Apply known NLP method(s) to **new dataset**  
- **New** method + **known** dataset  
- Implement paper method + **new domain** or dataset  
- Descriptive NLP for practical or linguistic patterns

**Scope:** ambitious 2-3 person project ≈ **conference paper** depth + experiments.

**Ideas:** final projects from [previous](http://example-comment-quality.pdf) [semesters](http://example-grammar.pdf), Stanford [cs224n](https://web.stanford.edu/class/cs224n/index.html) ([2000-2017](http://nlp.stanford.edu/courses/cs224n/)), or DL [cs224d](http://cs224d.stanford.edu/) ([2015](http://cs224d.stanford.edu/reports_2015.html), [2016](http://cs224d.stanford.edu/reports_2016.html), [2017](https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1174/reports.html), [2018](https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1184/reports.html), [2019](https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1194/project.html), [2020](https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1204/project.html), [2021](https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1214/project.html), [2022](https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1224/project.html)). Starters:

- Abstractive summarization of news articles  
- Restaurant menu extraction from user reviews  
- Question-answering with neural attention or memory models  
- Image captioning (language generation)  
- Gender / power dynamics in movie dialogues  
- Interpreting “black box” / neural language models

NLP conferences: [ACL](https://www.aclweb.org/anthology/events/acl-2022/) and [EMNLP](https://www.aclweb.org/anthology/events/emnlp-2022/) are top two; recent proceedings = idea mine.

## Project Proposal

**Most important deliverable**; invest time. Concrete idea early → stronger project + course outcome.

One proposal per group; instructors give **detailed feedback**. **200-300 words**; **quality >> length.**

Address:

- What will you do?  
- Why important / hard?  
- Dataset(s)?  
- Algorithms? Good code exists or build your own? (OK if thin here.)  
- **≥4** paper references.

Four refs = research papers or similar technical pubs; **not** textbooks/docs alone (cite those extra; they don’t count toward four).

Resources: [ACL Anthology](http://aclanthology.org), [ACM DL](http://dl.acm.org/) ([SigKDD](http://www.kdd.org/), [WSDM](http://www.wsdm-conference.org/)), [NIPS](https://papers.nips.cc/), [ICML](http://proceedings.mlr.press/v97/), [Scholar](https://scholar.google.com/), [arXiv](https://arxiv.org/). Recent: [NAACL](https://aclanthology.org/events/naacl-2022/), [ACL](https://aclanthology.org/events/acl-2022/), [EMNLP](https://aclanthology.org/events/emnlp-2022/).

Between Week 2 and Week 4: OH sections on literature search + reading NLP papers; guided paper each week; schedule + list posted weekly.

**Submit:** Google Doc, comment access for anyone with link; [form](https://forms.gle/2TA6hfRRpbt2UHLE7). Inline comments. **No Word.**

## Authors' Contributions (teams 2-3)

**Required** end section listing who did what. Each member **≥ one model**. Missing section → **-1 point**; skipping per-person model work → possible deduction.

## Milestone (optional)

Want formal mid-stage feedback? Email **milestone/interim** report **one week before** OH; we review (email or OH).

Submit: **3-5 page** partial report + implementation. Include:

- Data obtained, loaded, explored (EDA).  
- Baseline results (random, majority class, BoW, etc.).

Rough draft of final; full results/conclusion optional; big changes before final OK.

Sections: **Abstract**, **Intro**, **Background**, **Methods**, **Results/discussion** (baseline+), **Next Steps** (remove for final; swap in conclusions + final analysis).

LaTeX easiest: ACL [zip](http://2023.aclweb.org/downloads/acl2023.zip), [Overleaf](https://www.overleaf.com/latex/templates/acl-2023-proceedings-template/qjdgcrdwcnwp), [Word template](http://2023.aclweb.org/downloads/acl2023.docx). Or Word/Docs if PDF export works.

**GitHub** link in submission.

PDF to [mids-nlp-instructors@googlegroups.com](mailto:mids-nlp-instructors@googlegroups.com) or follow section instructor.

## Presentations

~**6 min** live in last week. Schedule + format announced later.

## Final Submission

Research-style report: **4-6 pages**, between ACL [short and long](https://2023.aclweb.org/calls/main_conference/#paper-types-and-formats).

Sections: **Abstract**, **Intro**, **Background**, **Methods**, **Results/discussion** (plots; compare to baseline + literature), **Conclusion**.

**Privacy:** opt out of public release in form.

Submit PDF + code to course GitHub (solo) or team repo, then complete the current course submission form distributed by the instructors. **Do not** change content after deadline or **late penalty**.

Rubric feedback may take **up to ~1 month** after deadline; term grades may post before that feedback.
