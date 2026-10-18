## What it does

`standing-judge` runs a gate over your project. Each round a fresh, read-only judge subagent clones a frozen commit, gathers its own evidence, scores the work and lists findings. The main agent checks each finding, fixes it, proves the fix with tests, ships it, and calls the next judge. After every round the agent issues a verdict: continue, or stop with a reason.

The judge never fixes and never remembers. A judge that edits grades its own work, and a judge that remembers its last verdict defends it. A new judge each round, told only the last scores and what changed, finds what the previous one missed.

## When to reach for it

Type `/standing-judge`, or the agent reaches for it when you ask for an agent as a gate, judge or reviewer that decides when to stop, or when you ask it to keep going "until it's perfect", "until full marks", "to the limit", or "until it beats X".

| You want | Gate kind |
|---|---|
| A repo that is reliable, documented and ready to share | Code |
| To match or beat a named product | Parity |
| A flow that makes sense to the people who use it | UX (black-box persona) |
| Faster, to the limit | Performance (interleaved A/B with a noise floor) |
| A document good enough to submit | Prose |
| A result that holds up | Research (judge picks the benchmark) |

For a single review of one diff, use a code review skill instead. This skill is for loops that run until a bar is met.

## The verdict

Every round ends on exactly one verdict, and the report leads with it:

- **PANEL**: the bar just passed, so the agent closes the last checks before PASS: one more judge round on the last fix, and a panel of judges with other lenses.
- **PASS**: every binary criterion passes, the last fix was judged, and a panel of judges with other lenses found nothing at or above the bar's severity.
- **OWNER**: only gaps that need your decision or outside evidence remain (stars, notarization, real credentials, a human sign-off).
- **PLATEAU**: two rounds without movement. More rounds of the same approach won't get there. An open-ended goal like "as fast as possible" ends here, at the limit.
- **BUDGET**: the round or time budget is spent.
- **REWRITE**: one area keeps regressing, so the agent rewrites it to a stated rule instead of patching it again.
- **CONTINUE**: fixable findings remain.

This is the answer to "should we keep developing this?" A gate that only ever says "continue" or "perfect" is not doing its job.

## The gate file

Before round 1 the agent writes `.judge/gate.md` (excluded from git): the bar, the dimensions, your owner decisions, what the loop may never touch on your machine, a budget, the stop rules, and how far a fix may ship without asking. It shows you the bar, owner items, budget and ship path before round 1. After that the bar is frozen. Thresholds don't move to let the work pass. Each round is logged in `.judge/rounds.md`, so a judge that dies or a new session picks up where the loop left off.

## Common questions

**Why did it stop before everything was 10?**
Read the verdict. OWNER and PLATEAU are real answers: the remaining gap needs you, or needs a different approach. Loops run without a plateau rule went 24 to 39 rounds without converging.

**The judge said something wrong. Does the agent fix it anyway?**
No. The agent reproduces each finding first. Judges make confident wrong claims, and the agent fixes what is really there and tells the next judge.

**It reached all 10s. Is it done?**
Not until a panel round passes. One judge's 10 only covers the dimensions it was given. In one run, a project at all 10s from a single judge scored 3 out of 10 on open-source readiness from the first panel judge given that lens.

**Will it touch my running app or real data?**
The gate file lists what both roles may never touch, and the fixer's test runs obey it too. Fill that section in honestly. An end-to-end suite that quits your app is a sandbox violation, not a test.

**Can I use a different model as the judge?**
Yes, and the skill alternates the judge's model between rounds when the harness offers more than one. One model shares one set of blind spots.

**Does it cost a lot?**
Each round is one or more full subagent runs. Set the budget in the gate file. A gate with 190 scripted criteria and four red teams per round was stopped by its owner for token cost after five rounds.

## It's working if

- Every report starts with a verdict word, not a vibe.
- Scores and criteria are tied to a commit SHA you can check out.
- Findings come with how the judge observed them: a command it ran, a screen it drove, a line it quoted from the reference.
- The loop stops on its own, and the stop names what is left and who can close it.
