You are revising one document, in Chinese or English. Write the revised text back to the same file. Report in the document's language.

File: {CURRENT}
Judge reports: {REPORTS}
Rules: {SKILL}/SKILL.md, {RULES}/patterns.md (the AI-pattern codes the judges use), {RULES}/techniques.md, {RULES}/lessons.md. Also any project writing plan or term-lock table the user named: {PROJECT_RULES}

Sources of truth (verify every number, quote and claim you touch, by grep):
{SOURCES}
Quotes must be verbatim. A paraphrase tagged with a source or interviewee code must be something that source said; otherwise label it as the author's inference. Other files in the project are context only: do not edit them, list the changes they need.

Do:
1. Record the starting length: for Chinese, the char count from `python3 {SCRIPTS}/prose_check.py {CURRENT}`; for English, `wc -w {CURRENT}`.
2. Before editing a paragraph, note its facts ledger: numbers, hedges (可能、如果、未必、仅、部分、约、尚未; may, might, if, some, about, not yet), direction of each judgment, entities, conditions, citation markers. Compare after editing.
3. Fix every P0 and P1 in both reports, plus each report's "下一轮最该改的5处". Verify each finding against the sources before acting. When a claim lacks support, narrow it to what the source says or delete it. Never add new facts, numbers, quotes or dates to satisfy a judge. If a judge is wrong, leave the text and say why.
4. Reduce the paragraph-level pattern hits the judges mark: vary paragraph openings, remove signposts, summary or aphorism endings, symmetric constructions and stacked lists; tie general statements to concrete objects. Do not replace them with colloquial phrasing, and do not introduce a new repeated construction (any opener used more than twice is a new template).
5. Keep headings, required template sentences, tables (fix wrong cells), citation markers, term-lock names and problem/recommendation numbering. No em dashes, no list lines or bold in body prose.
6. Length: final length, in the same unit as step 1, within ±3% of the starting count. Prefer deleting overreaching or repeated sentences over adding.
7. Chinese: run and pass `python3 {SCRIPTS}/prose_check.py {CURRENT}`; if a pre-edit copy exists, also run it with `--baseline <copy>` and check every hedge drop. English: prose_check reports the rule scan as skipped, but `--baseline <copy>` still checks English hedges and word count; run it. Both: run the detector, `{SCRIPTS}/aigc {CURRENT}` (Chinese target: mpu flagged paragraphs ≤10%; English: desklib paragraph mean ≤0.5; a taste reference, not a goal).

Report concisely: P0/P1 handled (one line each), items rejected and why, cross-file changes needed, start and final char count, prose_check result, detector result.
