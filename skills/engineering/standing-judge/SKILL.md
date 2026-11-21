---
name: standing-judge
description: Run a judge-gated iteration loop where a fresh read-only judge scores a frozen commit every round and rules whether development continues. Supports code, parity, UX, performance, prose, research, and adoption gates (or hybrid combinations). Use when the user asks for an agent as a gate or judge (评委, 裁判) that decides when to stop, asks to keep going until perfect or full marks (满分, 极限), to beat a named product, or asks whether a project is worth developing further. Do not use for a single-diff code review or one-off bug diagnosis.
---

# Standing judge

A **gate** loop with maker-checker separation. Each round, a **fresh read-only judge** evaluates a frozen commit SHA from a clean clone using its own evidence. You coordinate the loop: freeze the gate, verify findings, fix them (or dispatch fixer subagents), prove fixes, ship on the approved path, and issue one **verdict**.

> **Iron Law:** Every PASS, fix claim, and next round rests on fresh evidence from a frozen SHA. The judge stays read-only and stateless across rounds.

## Red flags (stop and follow the rule)

| Temptation | Apply |
|---|---|
| "User said unlimited budget, keep going" | Pause at the 6-round epoch cap (Section 1.5, `BUDGET`). |
| "Also tidy up these lows during PANEL" | Fix blocking findings only in Phase 2 (Section 2.4). |
| "Reuse the fixer's model for every judge" | Add a second model family for `PANEL` or stamp `single-family-judge` (Section 3). |
| "UX judge scored 10/10, visuals are done" | Pause after Round 1 for human visual sign-off (`gate-kinds.md`). |
| "Count this exotic regex/shell fuzz case as medium" | Enforce `Bounded heuristics` in `.judge/gate.md` (Section 1.2). |
| "Leave reports and clones in `/tmp`" | Persist reports in `.judge/reports/` and remove clones after each round (Section 2.2). |

## 1. Write and freeze the gate

Read the repo (README, docs, ADRs, `AGENTS.md`/`CLAUDE.md`) and conversation, write `.judge/gate.md` from [references/gate-file.md](references/gate-file.md), and add `.judge/` to `.git/info/exclude`.

1. **Primary kind and modifiers.** Pick a primary kind from [references/gate-kinds.md](references/gate-kinds.md) (`code`, `parity`, `UX`, `performance`, `prose`, `research`, `adoption`) plus any modifiers (`parity-matrix`, `perf-budget`, `ux-checkpoint`, `release-hygiene`), and copy their evidence rules into `.judge/gate.md`.
2. **Binary bar and bounded heuristics.** Define binary PASS criteria with a severity threshold ("no open finding of medium or higher", "every P0 passes"). Keep 0 to 10 scores beside them for trend tracking only. For open-ended heuristic domains (regexes, shell matchers, detectors), pin a fixed corpus or attack boundary in `Bounded heuristics`; out-of-corpus fuzzing logs as `low`.
3. **Owner items and adoption scope.** Record out-of-code gaps and owner decisions (credentials, notarization, public stars, sign-offs); exclude owner items from findings. On personal products with no recorded external user feedback or payment (`Adoption: none`), scope the gate to launch-blocking defects only (crash, data loss, security hole, broken install/first-run).
4. **Sandbox, resources, and ship path.** List forbidden targets and commands, exclusive resource locks (display, browser, ports, DB), disk floor (default 10 GiB free), max parallel heavy workers (default 2), and how far verified fixes ship without asking. For heavy, multi-platform, GUI, or `bd`-tracked repos, load [references/ops.md](references/ops.md).
5. **Epoch budget and judge models.** Set a round cap (default 6 rounds per epoch; even when the user says "unlimited", pause every 6 rounds with a convergence delta report and ask before opening the next epoch). Propose judge models from the harness, including a second model family when available, and select judges strictly from the approved list.

<HARD-GATE>
Show the user the bar, owner items, adoption status, epoch budget, ship path, and judge models in a short summary before Round 1. Start after confirmation (or standing autonomous authorization). In headless runs, set `Status: unconfirmed` and print `gate unconfirmed` right after the verdict on every report. Once confirmed, keep the bar and thresholds frozen; update `.judge/gate.md` only when the user settles an owner item or changes scope.
</HARD-GATE>

When the bar relies on a numeric score or noisy metric, run two judges on the same unchanged SHA once to measure noise; treat deltas inside that spread as unchanged.

## 2. Run a round

1. **Freeze the candidate.** Commit all changes and record the SHA before launching any judge.
2. **Launch a fresh read-only judge** in the background using [references/judge-prompt.md](references/judge-prompt.md), alternating approved models between rounds. The judge clones the frozen SHA in `/tmp` (only when free disk meets the 10 GiB floor), saves its full report and any minimal reproduction script to `.judge/reports/r<N>-<role>.md`, and removes the `/tmp` clone immediately afterward. Crashed, timed-out, or safety-interrupted judges spend zero budget; re-run fresh on the same SHA.
3. **Verify before fixing.** Reproduce every finding before editing code. Drop false claims and owner items, and list false claims for the next judge.
4. **Fix at the right depth.**
   - **First occurrence in an area:** fix locally, most severe first, in one pass. On large repos (>3 modules or >3 min test runs), stay Coordinator and delegate edits to fresh worktree fixer subagents (see [references/ops.md](references/ops.md)).
   - **Recurring class (2nd round in the same area/rule) or `REWRITE`:** load [references/deep-fix.md](references/deep-fix.md) to generalize the class, trace lineage, deepen the owning module via `codebase-design`, and delete duplicate copies.
   - **Phase 2 (after bar passes):** fix blocking findings only. Record all `low` findings as follow-ups while leaving unrelated code and docs untouched.
   - **UX / visual gates after Round 1:** pause for human visual and direction sign-off before autonomous polish rounds (see [references/gate-kinds.md](references/gate-kinds.md)).
5. **Prove, ship, and log.** Run build, linter, unit tests, and affected end-to-end checks on the fresh build, reporting flake counts explicitly ("7 of 8"). Ship strictly along the approved ship path. Keep `.judge/rounds.md` append-only at **max 8 lines per round**, storing full evidence in `.judge/reports/`.
6. **Round completion check and report.** Confirm `.judge/reports/r<N>-*.md` exists, `/tmp` clone is removed, and `.judge/rounds.md` is appended. Report in under 10 lines: verdict (plus flags such as `gate unconfirmed` or `single-family-judge`), open blocker delta, score delta, fixes landed, test counts, and next step.

## 3. Issue the verdict

Walk this table top to bottom after every round and take the first matching verdict. Lead the report with it.

| Verdict | Condition | Action |
|---|---|---|
| **BUDGET** | The current epoch (default 6 rounds) or total time/round budget is spent. | Stop. Report convergence delta, distance to bar, and pending panel lenses; ask before opening another epoch. |
| **ADOPTION** | Personal product with `Adoption: none`, at least one judged round is verified on the current SHA, and zero launch-blocking defects remain. | Stop. Ship to real users; open a full gate only after external user feedback or first payment is recorded in `.judge/gate.md`. |
| **PASS** | Bar holds on the current SHA, and every panel lens has a valid clean result on it. | Stop. Report final table and follow-up list. |
| **PANEL** | Bar holds on the current SHA, and at least one panel lens lacks a valid clean result. | Run only the missing or invalidated lenses next round. |
| **OWNER** | Bar is unmet, and every remaining blocker is an owner item. | Stop. List each owner item and what closes it. |
| **PLATEAU** | Circuit breaker fired: (a) 2 consecutive bar-unmet rounds where open blocking findings do not drop and passed binary criteria do not rise, (b) a `REWRITE` target still has a blocking finding on the next round, or (c) 2 consecutive `REJECTED` candidates on an open-ended performance goal. | Stop. Report the stuck class, distance to bar, and what a different approach requires. |
| **REWRITE** | Same area or rule produced blocking findings 2 rounds in a row (first time for that area). | Load [references/deep-fix.md](references/deep-fix.md), consolidate the rule behind one owning module, prove it end-to-end, and tell the next judge to attack that module. |
| **CONTINUE** | Bar is unmet, and code can fix a remaining blocker. | Fix, ship, run next round. |

When two rules oscillate, record their precedence in `.judge/gate.md` before the next round.

### The panel (Phase 2 closeout)

One judge's 10 covers only its own rubric. Before `PASS`, run 3 to 4 parallel judges on the same SHA with independent lenses (for example: security, release and CI, newcomer onboarding, runtime/CLI). Include at least one **different approved model family** than the fixer when available; otherwise stamp `single-family-judge` on every report.

- **Fixed lens set:** Lock the lenses on the first `PANEL` round in `.judge/rounds.md`.
- **Concrete scope (`Reviewed:`):** Every lens ends with `Reviewed:` listing exact inspected files or tight directories (avoid repo-wide `**` wildcards). For black-box lenses, write `runtime-surface` plus the user-facing surfaces checked (UI, CLI, README).
- **Clean persistence:** A lens stays clean across a later SHA while `git diff --name-only <clean SHA>..<current SHA>` stays outside its `Reviewed:` paths (and for `runtime-surface`, leaves shipped runtime/UI/CLI/onboarding behavior untouched).
- **Targeted re-verification:** The first `PANEL` round sweeps freely within each lens. Any re-run of an invalidated lens uses the **Panel Re-verify** template in [references/judge-prompt.md](references/judge-prompt.md): verify the fix and check for regressions in touched files only, keeping speculative new fuzz axes out of closeout.

## Calibration and self-grading

- Score a dimension 10 when no code-fixable finding of real user impact remains. Holding a 9 requires naming the exact code change for 10. Two consecutive judges holding 9 with no nameable code fix completes that dimension.
- Exclude nits without user impact and owner items from findings.
- **A benchmark the fixer built is no gate.** When the work defines its own eval or benchmark, the judge runs a public standard benchmark where one exists, or audits the custom one for leakage and trivial baselines before counting any score.
