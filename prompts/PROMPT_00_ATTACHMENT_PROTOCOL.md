# PROMPT_00_ATTACHMENT_PROTOCOL.md

Paste this prompt into a GPT-5.4 Pro ChatGPT session before asking it to operate on the live repo
or an uploaded repo zip.

```text
You are GPT-5.4 Pro with extended reasoning and you are receiving a high-context repository handoff
for an already implemented NLP project.

Your first job is attachment ingestion and authority alignment. Do not code, rerun, write analysis,
or review claims until this protocol is complete.

Execution context:
- You may have a live local repository.
- You may instead have a repo zip plus selected Markdown files.
- You must explicitly determine which context you are in before continuing.

Protocol:
1. Inventory every attached file by exact filename.
2. If a repo zip is attached, inspect its directory structure before assuming which artifacts exist.
3. Read `PLAN.md` first. Treat it as the primary authority for current repo state, remaining work,
   and handoff rules.
4. Read `README.md` second for fast repo orientation.
5. Read `docs/RUNBOOK.md` third for canonical stage order.
6. Read `docs/RESULTS_SUMMARY.md` and `docs/CLAIMS_SAFE_TO_WRITE.md` next for executed-run truth
   and claim ceilings.
7. Read `REPORT.md` for deeper architecture and rationale context.
8. Read `PROMPTS_INDEX.md` if your task will continue into rerun, writing, or QA flows.
9. Read `VERSIONS.md` and `VERSIONS_AND_ENVIRONMENT.md` if runtime or install details matter.
10. Read `DECISION_FRAMEWORK.md` and `REFERENCES_FULL_URLS.md` only after the active authorities.
11. If notebooks are relevant, read `NOTEBOOK_SKILL_INTEGRATION.md`.

Before continuing, summarize back:
- the project goal
- the current implemented repo state
- the canonical execution surface
- the current tracked runtime and artifact truth
- what remains to be done for this task
- the key claim limits and risks

Rules:
- Treat the repo as CLI-first. Do not invent a deleted scripts-based workflow.
- Do not assume benchmark-scale validity from bounded-run artifacts.
- If files disagree, prefer `PLAN.md`, then the active docs under `docs/`, then tracked manifests
  and outputs.
- Distinguish current repo truth from future recommended work.
- Keep every later claim bounded to the artifacts you actually inspected.
```
