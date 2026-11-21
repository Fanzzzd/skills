---
name: standing-judge
description: Run a judge-gated iteration loop where a fresh read-only judge scores a frozen commit every round and rules whether development continues. Supports code, parity, UX, performance, prose, research, and adoption gates (or hybrid combinations). Use when the user asks for an agent as a gate or judge (评委, 裁判) that decides when to stop, asks to keep going until perfect or full marks (满分, 极限), to beat a named product, or asks whether a project is worth developing further. Do not use for a single-diff code review or one-off bug diagnosis.
---

# Standing judge

A **gate** loop with strict maker-checker separation. Each round, a **fresh read-only judge** evaluates a frozen commit SHA from a clean clone using its own evidence. You coordinate the loop: freeze the gate, verify each finding, fix it (or dispatch fixer subagents), prove the fix, ship on the approved path, and issue one **verdict**.

> **Iron Law:** No PASS, fix claim, or next round without fresh evidence on a frozen SHA. A judge never edits and never remembers prior rounds.

## Hard gates and red flags

Stop and correct course if any of these rationalizations appear:

| Rationalization | Required rule |
|---|---|
| "User said unlimited budget, keep looping" | Cap every run at **6 rounds per epoch**; pause at epoch end with delta and ask before opening the next epoch. |
| "I'll also clean up these lows during PANEL" | Phase 2 fixes **blocking findings only**; extra edits void clean panel lenses and trigger re-run loops. |
| "The current model is already approved for judging" | Same-family judges share blind spots; require a second approved model family for PANEL, or stamp `single-family-judge` on every report. |
| "UX judge scored 10/10, so visuals are ready" | LLM UX judges catch state bugs, not aesthetics or motion feel; get human visual sign-off after Round 1 before autonomous loops. |
| "This exotic regex/shell edge case is medium" | Check `Bounded heuristics` in `.judge/gate.md`; out-of-corpus fuzzing is `low`, never a blocker. |
| "Write judge reports and clones to `/tmp`" | Persist reports in `.judge/reports/`; delete `/tmp` clones after each round; refuse new clones below 10 GiB free disk. |

## 1. Write and freeze the gate

Before Round 1, read the repo (README, docs, ADRs, `AGENTS.md`/`CLAUDE.md`) and conversation, then write `.judge/gate.md` from [references/gate-file.md](references/gate-file.md) and add `.judge/` to `.git/info/exclude`.

1. **Primary kind and modifiers.** Pick a primary kind from [references/gate-kinds.md](references/gate-kinds.md) (`code`, `parity`, `UX`, `performance`, `prose`, `research`, `adoption`) plus any modifiers (for example `code + parity-matrix` or `UX + perf-budget`), and copy their evidence rules into `.judge/gate.md`.
2. **Binary bar and bounded heuristics.** Define binary PASS criteria with a severity threshold ("no open finding of medium or higher", "every P0 passes"). Keep 0 to 10 dimension scores beside them for trend tracking only. For open-ended heuristic domains (regexes, shell matchers, detectors), pin a fixed corpus or attack boundary in `Bounded heuristics`.
3. **Owner items and adoption scope.** List out-of-code gaps and owner decisions (credentials, notarization, public stars, sign-offs); owner items are never findings. On personal products with no recorded external user feedback or payment (`Adoption: none`), Round 1 checks launch-blocking defects only (crash, data loss, security hole, broken install/first-run).
4. **Sandbox, resources, and ship path.** List forbidden targets and commands, exclusive resource locks (display, browser, ports, DB), disk floor (default 10 GiB), max parallel heavy workers (default 2), and how far verified fixes ship without asking. For heavy, multi-platform, or GUI repos, load [references/ops.md](references/ops.md).
5. **Epoch budget and judge models.** Set a round cap (default 6 rounds per epoch, even when the user says "unlimited"). Propose approved judge models from the harness, including a second model family when available; never invoke an unapproved model without asking.

<HARD-GATE>
Show the user the bar, owner items, adoption status, epoch budget, ship path, and judge models in a short summary before Round 1. Start only after confirmation (or standing autonomous authorization). In headless runs, set `Status: unconfirmed` and print `gate unconfirmed` right after the verdict on every report. Once confirmed, freeze the bar and thresholds; edit `.judge/gate.md` only when the user settles an owner item or changes scope.
</HARD-GATE>

When the bar relies on a numeric judge score or noisy metric, run two judges on the same unchanged SHA once to measure noise; deltas within that spread earn neither credit nor fixes.

## 2. Run a round

1. **Freeze the candidate.** Commit and record the SHA. Never judge a dirty working tree.
2. **Launch a fresh read-only judge** in the background using [references/judge-prompt.md](references/judge-prompt.md). Alternate approved models between rounds. Judge writes its full report to `.judge/reports/r<N>-<role>.md` from a clean clone in `/tmp`, then deletes the clone (or coordinator cleans it once the report lands). Crashed, timed-out, or safety-interrupted judges do not consume budget; re-run on the same SHA.
3. **Verify before fixing.** Reproduce every finding before touching code. Drop findings that are false or re-raise owner items, and report false claims to the next judge.
4. **Fix at the right depth.**
   - **First occurrence in an area:** fix locally, most severe first, in one pass. On large repos (>3 modules or >3 min test runs), act as Coordinator and delegate implementation to a fresh worktree fixer subagent (see [references/ops.md](references/ops.md)).
   - **Recurring class (2nd round in the same area/rule) or `REWRITE` verdict:** load [references/deep-fix.md](references/deep-fix.md) to generalize the class, trace lineage, deepen the owning module with the `codebase-design` skill, and replace duplicate copies.
   - **Phase 2 (after bar passes):** fix ONLY findings at or above the bar's severity. Record all `low` findings as follow-ups without editing code or unrelated docs.
   - **UX / visual gates after Round 1:** pause for human visual/direction sign-off before running autonomous polish rounds (see [references/gate-kinds.md](references/gate-kinds.md)).
5. **Prove, ship, and log.** Run build, linter, unit tests, and the affected end-to-end path on the new build. Report flake counts explicitly ("7 of 8"). Ship only as far as the gate file's ship path allows. Append a compact entry (**max 8 lines**) to `.judge/rounds.md` and keep verbose notes in `.judge/reports/`.
6. **Report** in under 10 lines: verdict (plus flags like `gate unconfirmed` or `single-family-judge`), open blocker delta, score delta, root fixes landed, test counts, and next step.

## 3. Issue the verdict

Walk this table top to bottom after every round and take the first matching verdict. Lead the report with it.

| Verdict | Condition | Action |
|---|---|---|
| **BUDGET** | The current epoch (default 6 rounds) or total time/round budget is spent. | Stop. Report convergence delta, distance to bar, and pending panel lenses; ask before opening another epoch. |
| **ADOPTION** | Personal product with `Adoption: none`, Round 1 is complete, and zero launch-blocking defects remain. | Stop. Ship to real users; open a full gate only after external user feedback or first payment is recorded in `.judge/gate.md`. |
| **PASS** | Bar holds on the current SHA, and every panel lens has a valid clean result on it. | Stop. Report final table and follow-up list. |
| **PANEL** | Bar holds on the current SHA, and at least one panel lens lacks a valid clean result. | Run only the missing or invalidated lenses next round. |
| **OWNER** | Bar is unmet, and every remaining blocker is an owner item. | Stop. List each owner item and what closes it. |
| **PLATEAU** | Circuit breaker fired: (a) 2 consecutive bar-unmet rounds with no net drop in open blocking findings, (b) a `REWRITE` target still has a blocking finding on the next round, or (c) 2 consecutive `REJECTED` candidates on an open-ended performance goal. | Stop. Report the stuck class, distance to bar, and what a different approach requires. |
| **REWRITE** | Same area or rule produced blocking findings 2 rounds in a row (first time for that area). | Load [references/deep-fix.md](references/deep-fix.md), consolidate the rule behind one owning module, prove it end-to-end, and tell the next judge to attack that module. |
| **CONTINUE** | Bar is unmet, and code can fix a remaining blocker. | Fix, ship, run next round. |

When two rules oscillate, write their precedence into `.judge/gate.md` before the next round.

### The panel (Phase 2 closeout)

One judge's 10 covers only its own rubric. Before `PASS`, run 3 to 4 parallel judges on the same SHA with independent lenses the fixer did not optimize for (for example: security, release and CI, newcomer onboarding, runtime/CLI). Include at least one **different approved model family** than the fixer when available; otherwise stamp `single-family-judge` on every report.

- **Fixed lens set:** Lock the lenses on the first `PANEL` round in `.judge/rounds.md`.
- **Concrete scope (`Reviewed:`):** Every lens ends with `Reviewed:` naming the exact files or tight directories it actually inspected (never lazy `**` repo-wide globs). Use `runtime-surface` instead of `whole build` for black-box lenses, and list which user-facing surfaces it covers (UI, CLI, README).
- **Clean persistence:** A lens stays clean across a later SHA if `git diff --name-only <clean SHA>..<current SHA>` does not intersect its `Reviewed:` paths (and for `runtime-surface`, does not alter shipped runtime/UI/CLI/onboarding behavior).
- **Targeted re-verification:** The first `PANEL` round sweeps freely within each lens. Any subsequent re-run of an invalidated lens uses the **Panel Re-verify** prompt in [references/judge-prompt.md](references/judge-prompt.md): verify the reported fix and check for regressions in touched files only. Do not open new speculative fuzz axes during Phase 2 closeout.

## Calibration and self-grading

- A dimension with no code-fixable finding of real user impact scores 10. Holding a 9 requires naming the exact code change for 10.
- Nits without user impact and owner items are never findings. Two consecutive judges holding 9 with no nameable code fix means that dimension is done.
- **A benchmark the fixer built is no gate.** When a project defines its own eval or benchmark, the judge uses a public standard benchmark where one exists, or audits the custom one for leakage and trivial baselines before any score counts.
