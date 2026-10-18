---
name: standing-judge
description: Gate loop where a fresh read-only judge subagent scores the work every round and rules whether development continues. Covers code, parity with a named product, black-box UX, performance, prose and research gates. Use when the user wants an agent as a gate or judge (评委, 裁判) that decides when to stop, asks to keep going until perfect or full marks (满分, 极限), to beat a named product, or asks whether a project is worth developing further.
---

# Standing judge

A **gate** loop with two roles. The **judge** is a fresh subagent each round: read-only, strict, calibrated. It gathers its own evidence, scores, and finds. You are the **fixer**: you verify each finding, fix it, prove the fix, ship it, and call the next judge. After every round you issue a **verdict** that says whether the loop continues.

The judge is fresh each round on purpose. A judge that remembers its last verdict defends it; a fresh one, told only the last scores and what changed, re-reads the work and finds what the last one missed. The judge never fixes: a judge grading its own fixes stops finding problems in them.

## 1. Write the gate file

Before round 1, write `.judge/gate.md` from [references/gate-file.md](references/gate-file.md) and add `.judge/` to `.git/info/exclude`. Read the conversation, the repo (README, docs, ADRs, `CLAUDE.md`) and memory before asking the user anything. The gate file holds:

- **Kind.** Pick the gate kind from [references/gate-kinds.md](references/gate-kinds.md) (code, parity, UX, performance, prose, research) and copy its evidence rules. The kind decides what the judge must look at; a judge reading only code misses what only a running product shows.
- **Bar.** Binary criteria with a severity threshold decide PASS: "no finding of medium or higher", "every P0 passes", "all seven persona tasks complete". Scores 0 to 10 per dimension track progress beside them. A loop whose only bar is "every dimension 10" drifts and oscillates.
- **Owner items.** Choices the owner made, and gaps no code can close (stars, notarization, credentials, a human sign-off). An owner item is never a finding; it counts against the bar only when a criterion names it ("every P0 passes" where one P0 needs real credentials).
- **Sandbox.** What neither role may touch: the user's running apps, real data, other repos, the pointer, public networks in the PASS path. List the forbidden commands on this machine. The fixer's test runs obey it too.
- **Budget and stop rules.** A hard cap in rounds or wall clock, and the plateau rule. The default plateau is two rounds in a row with the bar unmet, no dimension moving, and no new finding at or above the bar's severity; the performance kind defines its own.
- **Ship path.** How far a fix travels without asking: commit only, or commit and push, or a release PR. Verified fixes ship on it as they land; the gate never holds a release hostage.

Show the user the bar, owner items, budget and ship path in a few lines. Step 1 is done when the user confirms them, or has told you to proceed on your judgment. When the harness can't ask (a headless run), proceed with `Status: unconfirmed` in the gate file, and put "gate unconfirmed" right after the verdict in every report until the user confirms.

Then freeze the bar, the rubric and the thresholds. A threshold that moves to let the work pass is no longer a gate. Change the gate file only when the user settles a new owner item or changes the bar, and say so in the next report.

When the bar is a score from the judge itself, measure the judge's noise once: run two judges on the same unchanged candidate. A change smaller than that spread is noise and earns neither credit nor a fix.

## 2. Run a round

1. **Freeze the candidate.** Commit, note the SHA. The judge scores that SHA from a clean clone in its own temp directory, never your working tree.
2. **Launch the judge** in the background with [references/judge-prompt.md](references/judge-prompt.md), filled in. Alternate the judge's model between rounds when the harness offers more than one. While it runs, write the test you were missing or check CI.
3. **Verify every finding** before fixing it. Judges make confident wrong claims. Reproduce the finding; when it is wrong, fix what is really there and tell the next judge. A finding that re-raises an owner item is dropped.
4. **Fix** most severe first, in one pass. While the bar is unmet, fix every verified finding. Once the bar has passed, fix only findings at or above its severity; the rest go to the follow-up list in `.judge/rounds.md` for after the loop. Reproduce first, then fix: a fix aimed at a guess lands beside the bug.
5. **Prove it.** Build, unit tests, linter, then the end-to-end path the change touches. Confirm the suite runs the build you just made. Run a flaky suite several times and report the count ("7 of 8, the failure the known timing flake"). A fix no test can reach gets a test, or is reported as reasoned from code.
6. **Ship** on the gate file's ship path, and only as far as it goes: a changeset if the repo uses them, a commit with the test results, then a push or release only if the ship path includes it.
7. **Record the round** in `.judge/rounds.md`: SHA, judge model, scores, findings fixed, test counts, verdict. The file is the loop's memory, so a dead judge or a new session resumes from it.
8. **Report** in a few lines: the verdict, the score delta, what was fixed, the test counts, what the next judge checks.

Every judge prompt names the fixes to verify and the side effects each could cause ("can a hand-over landing during the await re-arm what it cleared"). You know where your fix is fragile; tell the judge. Every few rounds, or when scores stall, ask for a full sweep of the whole project instead.

## 3. Issue the verdict

The loop has two phases. While the bar is unmet, rounds fix everything they verify. Once the bar passes, the loop is closing: it fixes only what blocks the bar, and a panel confirms the final SHA. The stop rules bind in both phases.

After each round, walk the table from the top and take the first verdict whose condition holds. Lead the report with it.

| Verdict | When | Next |
|---|---|---|
| **BUDGET** | The budget is spent. | Stop. Report the distance to the bar, and whether a panel was still pending. |
| **PASS** | The bar holds on the current SHA, and every panel lens has a clean result that holds on it (see below). | Stop. Report the final table and the follow-up list. |
| **PANEL** | The bar holds on the current SHA, and some panel lens has no clean result that holds on it. | Run those lenses next round (see below). |
| **OWNER** | The bar is unmet, and everything blocking it is an owner item. | Stop. List each item and what it would take. |
| **PLATEAU** | The plateau rule fired. | Stop. Report the distance to the bar and what a different approach would need. |
| **REWRITE** | One area regressed two or three rounds running, each fix opening the next hole. | Write the rule the area should follow in two or three sentences, rewrite the area to it, write the end-to-end test of the real scenario, then run the next round. |
| **CONTINUE** | The bar is unmet, and code can fix something blocking it: a finding, or a failing criterion. | Fix, ship, next round. |

A goal with no fixed number ("as fast as possible", "to the limit") is a target the bar never meets, so it never reaches PANEL or PASS. It ends on PLATEAU, which for it means two REJECTED candidates in a row (see the performance kind in gate-kinds), or on BUDGET or OWNER. An ACCEPTED candidate is progress, not a stop.

When fixes oscillate (one rule's fix trips another), the rubric conflicts with itself. State the precedence in the gate file and the judge prompt before the next round.

### The panel

One judge's 10 covers only the dimensions it was given. The panel is three to five judges in parallel on the same SHA, each with a lens the fixer did not pick (release and CI, accessibility, newcomer onboarding, security), on a different model where possible. Panel findings count against the bar at their own severity.

A lens is **clean** on a SHA when it found nothing at or above the bar's severity there. A clean result holds on a later SHA when the diff since touches nothing that lens reviewed; a fix to the area a lens reviewed voids its clean result. So after a panel finding is fixed, the next round runs the lens that found it plus every lens whose area the fix touched, and the rest stay clean. The first PANEL round runs every lens.

## Calibration

The judge must be calibrated, or the loop never ends:

- A dimension with no code-fixable finding of real user impact scores 10.
- A judge holding a dimension at 9 names the specific change that makes it 10.
- Nits without user impact are not findings.
- For limits outside the code (an OS floor, a platform rule), the judge names the floor and scores what code can still do.

If two judges in a row hold a 9 with no nameable change, that dimension is done.

## A benchmark the fixer built is no gate

A benchmark or eval the fixer wrote grades the fixer's own guess. When the work defines its own test (a research result, a custom eval), the judge picks a public standard benchmark where one exists, or audits the custom one for leakage and difficulty before any score counts.
