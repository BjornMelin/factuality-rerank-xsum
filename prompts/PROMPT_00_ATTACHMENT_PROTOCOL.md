# PROMPT_00_ATTACHMENT_PROTOCOL.md

Paste this prompt into a new GPT-5.4 Pro session **before** asking it to implement or write anything, when you are attaching the handoff files.

```text
You are receiving a multi-file project handoff. Before you do any implementation or writing, perform this attachment-ingestion protocol exactly.

1. Inventory every attached file by filename.
2. Read `PLAN.md` first and treat it as the primary source of truth.
3. Read `REPORT.md` second for design rationale and scope protection.
4. Read `DECISION_FRAMEWORK.md` third for the scored comparison and final keep/reject decisions.
5. Read `REFERENCES_FULL_URLS.md` fourth and use it as the default source list for literature, docs, model cards, and repositories.
6. Read any notebook, example config, Makefile, or pyproject files after the core markdown files.
7. Summarize back to me:
   - the project goal,
   - the required deliverables,
   - the required path vs optional path,
   - the repo or writing task you are about to perform,
   - the key risks and fallbacks.
8. Only after that summary should you begin implementation or report writing.

Rules:
- Do not ignore attachments.
- Do not infer missing results that are not present in the files.
- If files disagree, follow `PLAN.md` first, then `REPORT.md`, then `DECISION_FRAMEWORK.md`.
- Be explicit about what is required, what is optional, and what you verified from attached files.
```
