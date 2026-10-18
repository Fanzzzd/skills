---
name: standing-judge
description: Run a gate loop where a fresh read-only judge subagent scores the work every round and rules whether development continues. You fix every verified finding, prove it, ship it, and call the next judge, until the bar passes, a plateau or budget stops the loop, or only owner decisions remain. Covers code quality, parity with a reference product, black-box UX, performance A/B, prose, and research benchmarks. Use when the user wants an agent or subagent as a gate, judge, reviewer, 评委 or 裁判 that decides when to stop; asks to keep improving until full marks, perfect, 满分, 极限, or better than a named product; or asks whether a project is good enough to keep developing.
---

# Standing judge

A **gate** loop with two roles. The **judge** is a fresh subagent each round: read-only, strict, calibrated. It gathers its own evidence, scores, and finds. You are the **fixer**: you verify each finding, fix it, prove the fix, ship it, and call the next judge. After every round you issue a **verdict** that says whether the loop continues.

The judge is fresh each round on purpose. A judge that remembers its last verdict defends it; a fresh one, told only the last scores and what changed, re-reads the work and finds what the last one missed. The judge never fixes: a judge grading its own fixes stops finding problems in them.

## 1. Write the gate file

Before round 1, write `.judge/gate.md` from [references/gate-file.md](references/gate-file.md) and add `.judge/` to `.git/info/exclude`. Read the conversation, the repo (README, docs, ADRs, `CLAUDE.md`) and memory before asking the user anything. The gate file holds:

- **Kind.** Pick the gate kind from [references/gate-kinds.md](references/gate-kinds.md) (code, parity, UX, performance, prose, research) and copy its evidence rules. The kind decides what the judge must look at; a judge reading only code misses what only a running product shows.
- **Bar.** Binary criteria with a severity threshold decide PASS: "no finding of medium or higher", "every P0 passes", "all seven persona tasks complete". Scores 0 to 10 per dimension track progress beside them. A loop whose only bar is "every dimension 10" drifts and oscillates.
- **Owner items.** Choices the owner made, and gaps no code can close (stars, notarization, credentials, a human sign-off). The judge never scores against them.
- **Sandbox.** What neither role may touch: the user's running apps, real data, other repos, the pointer, public networks in the PASS path. List the forbidden commands on this machine. The fixer's test runs obey it too.
- **Budget and stop rules.** A cap in rounds or wall clock, and a plateau rule (default: two rounds with no dimension moving and no new medium-or-higher finding).
- **Ship path.** How a fix reaches users. Verified fixes ship on it as they land; the gate never holds a release hostage.

Freeze the bar, the rubric and the thresholds. A threshold that moves to let the work pass is no longer a gate. Change the gate file only when the user settles a new owner item or changes the bar, and say so in the next report.

When the bar is a score from the judge itself, measure the judge's noise once: run two judges on the same unchanged candidate. A change smaller than that spread is noise and earns neither credit nor a fix.

## 2. Run a round

1. **Freeze the candidate.** Commit, note the SHA. The judge scores that SHA from a clean clone in its own temp directory, never your working tree.
2. **Launch the judge** in the background with [references/judge-prompt.md](references/judge-prompt.md), filled in. Alternate the judge's model between rounds when the harness offers more than one. While it runs, write the test you were missing or check CI.
3. **Verify every finding** before fixing it. Judges make confident wrong claims. Reproduce the finding; when it is wrong, fix what is really there and tell the next judge. A finding that re-raises an owner item is dropped.
4. **Fix every verified finding**, most severe first, in one pass. Reproduce first, then fix: a fix aimed at a guess lands beside the bug.
5. **Prove it.** Build, unit tests, linter, then the end-to-end path the change touches. Confirm the suite runs the build you just made. Run a flaky suite several times and report the count ("7 of 8, the failure the known timing flake"). A fix no test can reach gets a test, or is reported as reasoned from code.
6. **Ship** on the ship path: changeset if the repo uses them, commit with the test results, push.
7. **Record the round** in `.judge/rounds.md`: SHA, judge model, scores, findings fixed, test counts, verdict. The file is the loop's memory, so a dead judge or a new session resumes from it.
8. **Report** in a few lines: the verdict, the score delta, what was fixed, the test counts, what the next judge checks.

Every judge prompt names the fixes to verify and the side effects each could cause ("can a hand-over landing during the await re-arm what it cleared"). You know where your fix is fragile; tell the judge. Every few rounds, or when scores stall, ask for a full sweep of the whole project instead.

## 3. Issue the verdict

After each round pick exactly one, and lead the report with it:

| Verdict | When | Next |
|---|---|---|
| **CONTINUE** | Verified findings remain that code can fix. | Fix, ship, next round. |
| **PASS** | Every binary criterion passes on the frozen SHA, and the pre-pass checks below hold. | Stop. Report the final table. |
| **OWNER** | Every remaining gap is an owner item. | Stop. List each item and what it would take. |
| **PLATEAU** | The plateau rule fired. | Stop. Report the distance to the bar and the gaps a different approach would need. |
| **BUDGET** | The budget is spent. | Stop. Report the distance to the bar. |
| **REWRITE** | One area regressed two or three rounds running, each fix opening the next hole. | Write the rule the area should follow in two or three sentences, rewrite the area to it, write the end-to-end test of the real scenario, then CONTINUE. |

When fixes oscillate (one rule's fix trips another), the rubric conflicts with itself. State the precedence in the gate file and the judge prompt before the next round.

### Before PASS

- **The last fix was judged.** A loop that stops on a fix nobody has looked at is reporting a guess. Run one more round, or tell the user plainly that the final change is reasoned, not observed.
- **A panel has looked.** One judge's 10 covers only the dimensions it was given. Run one panel round: three to five judges in parallel, each with a lens the fixer did not pick (release and CI, accessibility, newcomer onboarding, security), on a different model where possible. Fold its findings into CONTINUE.

## Calibration

The judge must be calibrated, or the loop never ends:

- A dimension with no code-fixable finding of real user impact scores 10.
- A judge holding a dimension at 9 names the specific change that makes it 10.
- Nits without user impact are not findings.
- For limits outside the code (an OS floor, a platform rule), the judge names the floor and scores what code can still do.

If two judges in a row hold a 9 with no nameable change, that dimension is done.

## Self-grading is no gate

A bar the fixer wrote and a benchmark the fixer built grade the fixer's own guess. When the work defines its own test (a research result, a custom eval), the judge picks a public standard benchmark where one exists, or audits the custom one for leakage and difficulty before any score counts.
