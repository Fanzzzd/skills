# Gate kinds

Pick one kind per gate. Each sets what the judge must look at and how the bar is phrased. Copy the chosen kind's rules into the gate file.

| The user wants | Kind |
|---|---|
| The repo polished, reliable, launch-ready | [Code](#code) |
| To match or beat a named product or repo | [Parity](#parity) |
| A flow that makes sense to the people who use it | [UX](#ux) |
| Faster, lighter, "to the limit" | [Performance](#performance) |
| A document, thesis or letter good enough to submit | [Prose](#prose) |
| A result that holds up | [Research](#research) |

## Code

- Default dimensions: ergonomics, reliability, speed, onboarding, polish, docs, shareability. Swap in the project's own where they fit better (API design for a library, accessibility for a site). Keep the set fixed across rounds so scores compare.
- The judge reads the code, runs the test suite and linters, and runs the product in the sandbox when a finding depends on behaviour. A fix that reads right can do nothing at runtime.
- Release hygiene is in scope: CI green on the frozen SHA, changelog entries for shipped fixes, no round labels in code comments.

## Parity

- Pin the reference: a repo at a commit, a product at a dated version. The judge studies the reference itself; a summary written by the fixer carries the fixer's blind spots.
- Turn "beat X" into a feature matrix before round 1: one row per capability the reference has, each with how to observe it in both. The bar is rows passed plus a severity threshold.
- Every score quotes both sides: reference `file:line` or screenshot beside ours. A dimension with no side-by-side evidence scores 1.
- Gaps that need outside evidence the agent cannot produce (real credentials, a provider key, a human acceptance record) are owner items. They keep the gate from PASS honestly; the verdict is OWNER, not CONTINUE.

## UX

- Black-box persona: the judge plays a named user of the product (role, goal, what they know), is barred from code, docs and git, and uses only the running product.
- Write 4 to 8 tasks the persona must complete and binary criteria per task ("finds why this plan was chosen without help"). The judge takes a screenshot of every screen it judges, at the widths the users use.
- The judge drives the product itself. Screenshots the fixer chose show only what the fixer chose.
- A wholesale new visual direction is an owner item: show the user two or three mockups and let them pick.

## Performance

- Fix the benchmark first: workload, metric, build flags, machine. Run it from a clean build of each SHA, on an isolated instance of the app.
- Measure the noise floor from two baseline runs. Run A/B/A/B interleaved. A metric is IMPROVED only when both candidate runs beat both baseline runs by more than the noise; REGRESSED the mirror case; otherwise unchanged.
- Check that the measurement does not perturb the system: a synchronous stats call on the hot path can turn hundreds of requests per second into a dozen.
- A candidate is ACCEPTED when the target metric IMPROVED and nothing user-facing REGRESSED, and becomes the new baseline; otherwise it is REJECTED and reverted. ACCEPTED is a round result, not the PASS verdict.
- A fixed target ("p95 under 120 ms") is a bar like any other: a candidate that meets it reaches PANEL, then PASS. "As fast as possible" or "to the limit" has no PASS. Its plateau is two REJECTED candidates in a row; it ends there, or on BUDGET.
- Keep baselines and the noise floor in `.judge/rounds.md`, so a judge that dies mid-baseline is replaced without starting over.

## Prose

- The judge compares against the source text for faithfulness: facts, citations, qualifiers and terms survive every round.
- Mechanical metrics (pattern hits, detector scores) are noisy. Measure their spread on an unchanged draft before treating any change as real.
- Style rules conflict with clarity. Write the precedence down (logical connectives are not style faults) before the second round, or fixes oscillate.
- For a dedicated de-AI workflow with detectors, call the Skill tool with "deai" if it is installed.

## Research

- The fixer never grades its own benchmark. The judge picks a public standard benchmark where one exists, or audits the custom one for train/test leakage, difficulty and whether a trivial baseline already passes.
- The bar names the baseline to beat and the margin, on held-out data.
- The judge reruns the headline number from the committed code. A number that can't be rerun is not evidence.
