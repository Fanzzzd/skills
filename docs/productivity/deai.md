## What it does

`deai` revises Chinese or English prose (theses, reports, articles, cover letters) so it reads like an author who knows the subject wrote it. You get specific actors, stated evidence, and judgments that stop where the evidence stops. Facts, citations, hedges and terms are locked before any sentence changes. The agent records a ledger of every number, qualifier and citation in a paragraph before editing it, and checks the ledger afterwards.

The skill never adds material to look human. When a judge asks for evidence the sources don't have, the agent narrows the claim or marks the gap as `【待补】` for the author to fill. Lowering a detector score by synonym swaps or chatty phrasing counts as a failure.

## When to reach for it

Type `/deai`, or the agent reaches for it when you say the text sounds like AI, ask to lower an AI-detector score, or ask a judge to review a chapter.

| You have | Use |
|---|---|
| A paragraph to a chapter | The single pass: locate, scan, rewrite in four layers (argument, paragraph, sentence, format), self-check |
| A long formal document going to a reviewer | The judge loop: two independent judges per round, one fix agent per file, stop rules |

For a code or product gate that runs until a bar is met, use [standing-judge](./../engineering/standing-judge.md). That skill hands prose gates to this one.

## Prerequisites

- Python 3 for `prose_check.py`, the rule scanner. It covers Chinese only.
- For the detectors: a Python 3.12 venv with `torch` and `transformers`. The `aigc` script prints the two `uv` commands that create it at `~/.cache/deai/venv`, or point `AIGC_PY` at an existing one. The script runs offline by default, so the first run needs `AIGC_ONLINE=1` to download the weights from Hugging Face (it says so if you forget): about 0.8 GB for the two Chinese detectors and 2.2 GB for the two English ones.
- For the judge loop: the `claude` CLI, the `codex` CLI, or both. Two judges from different model families disagree in useful places.

## The detectors

The local detectors are a taste reference. They don't approximate CNKI, Turnitin or any submission checker, and a low local score doesn't predict a low official one. The agent reads the share of flagged paragraphs across the document, never one paragraph's score. Calibration against human-written theses from before ChatGPT put that share at 18% to 44%. Unrevised agent drafts land at 70% to 90%. The reference point is 10% or below, and the score should fall because the text gained concrete objects and real data.

## Common questions

**Why does the agent refuse to add a statistic the judge asked for?**
Inventing evidence to satisfy a reviewer is the failure this skill exists to prevent. The agent narrows the claim to what the sources support, or leaves a `【待补】` marker naming exactly what material is missing.

**The judges never stop reporting P1 issues. When does the loop end?**
P0 issues must reach zero. After that the loop stops when P1 counts and scores stop falling for two rounds. Judges are told to over-report, so P1 never reaches zero. A "fully passed" result depends on data completeness, which better prose can't raise. When the gap is missing material, the agent stops and asks the author for it.

**After several rounds the text reads like a pile of citations. What happened?**
Judges counted reasoning connectives ("because", "therefore") as AI patterns, and the fix agents deleted them. The skill now separates signposts (delete) from reasoning connectives (keep), and every few rounds it reads the whole chapter only for coherence.

**Does it work for English?**
The single pass, the judge loop and the fix prompt all take English drafts. The rule scanner is Chinese-only: on an English file it reports "skipped", which is not a pass. English drafts rely on the English detectors and the judges, and `--baseline` still checks English hedges and word count against the original. The judges' pattern codes are written for Chinese, so English reports mark patterns in plain words.

## It's working if

- Every number, citation marker and hedge in the original is still there, or the delivery note says where each one went.
- New `【待补】` markers name concrete material, not "more data".
- The detector share falls together with the text gaining named objects, dates and sources.
- No sentence opener is used more than twice in a document.
