# Gate kinds and modifiers

Pick one **Primary kind** and any needed **Modifiers**. Copy the selected rules into `.judge/gate.md`'s `Evidence` section so every judge reads them directly.

| The user wants | Primary kind |
|---|---|
| A reliable, launch-ready repo or library | [Code](#code) |
| To match or beat a named product or repo | [Parity](#parity) |
| A user flow and interface that make sense | [UX](#ux) |
| Faster, lighter, or "to the limit" | [Performance](#performance) |
| A document, thesis, or letter ready to submit | [Prose](#prose) |
| A benchmarked research result that holds up | [Research](#research) |
| To test whether a product has real-world pull | [Adoption](#adoption) |

Common hybrid modifiers: `parity-matrix`, `perf-budget`, `ux-checkpoint`, `release-hygiene`.

## Code

- Default dimensions: ergonomics, reliability, speed, onboarding, polish, docs, shareability (swap project-specific ones before Round 1 and freeze them).
- Judge reads code, runs tests and linters, and exercises the built product in the sandbox whenever a finding depends on runtime behavior.
- Release hygiene is in scope: CI green on the frozen SHA, changelog entries for shipped fixes, no round labels in code comments or test titles.
- If the repo includes heuristic matchers (shell approval, regex filters, static scanners), declare a `Bounded heuristics` corpus in `.judge/gate.md` before Round 1.

## Parity

- Pin the reference to an exact commit SHA or dated product version. The judge inspects the reference directly; never feed a fixer-written summary as the sole source.
- Build a feature matrix before Round 1: one row per capability with how to observe both sides. Bar = rows passed plus severity threshold.
- Every finding quotes both sides (`file:line` or screenshot). Unbacked parity claims score 1 on that dimension.
- Gaps requiring real external credentials, paid tenants, or human acceptance are `Owner items` and end on `OWNER`, not `CONTINUE`.

## UX

- Black-box persona: judge plays a named user (role, goal, prior knowledge), stays out of source code/docs/git, and drives the running product itself.
- Write 4 to 8 concrete persona tasks with binary pass criteria. Judge captures its own screenshots at target viewport widths; fixer-selected screenshots do not count.
- **Round 1 human visual checkpoint:** LLM judges catch state-machine and flow bugs reliably, but miss visual taste, layout balance, and motion feel. After Round 1 fixes layout or visual changes, pause and send 2 to 3 real screenshots (or a local preview link) to the user for visual/direction sign-off before running autonomous polish rounds.
- A wholesale visual redesign is always an owner item: show 2 to 3 mockups and let the user pick.

## Performance

- Fix the benchmark before Round 1: exact workload, metric, build flags, and machine conditions. Run from a clean build on an isolated instance with no competing heavy jobs.
- Measure the noise floor from two identical baseline runs. Run candidate comparisons interleaved (`A/B/A/B`). A metric is `IMPROVED` only when both candidate runs beat both baseline runs by more than the noise floor; `REGRESSED` in the mirror case; otherwise unchanged.
- Verify measurement instrumentation does not perturb the hot path.
- `ACCEPTED` (target improved, no user-facing regression) updates the baseline and continues; `REJECTED` reverts. A fixed target ("p95 < 120 ms") moves to `PANEL` then `PASS`; an open-ended goal ("to the limit") never hits `PASS` and stops on `PLATEAU` (2 consecutive `REJECTED` candidates) or `BUDGET`.
- Record baselines and noise floor in `.judge/rounds.md` so crashed runs resume without re-baselining.

## Prose

- Compare every draft against source facts for faithfulness: numbers, citations, qualifiers, and domain terms must survive every round.
- Measure spread of automated detectors or pattern scripts on an unchanged draft before treating score deltas as real.
- State rule precedence before Round 2 (for example: factual precision and clarity win over compactness or style rules) so edits do not oscillate.
- For dedicated de-AI detector workflows, call the Skill tool with `deai` if installed.

## Research

- The fixer never grades its own benchmark. Judge selects a public standard benchmark where one exists, or audits the custom benchmark for train/test leakage, difficulty, and trivial baselines before any score counts.
- Bar names the baseline to beat, the margin, and held-out evaluation data.
- Judge reruns the headline metric from the committed code. Numbers that cannot be rerun are not evidence.

## Adoption

- Use when the user asks whether a personal product deserves further investment.
- Evidence comes strictly from outside the repo: non-author installs, active sessions, filed external issues, verbatim outside user feedback, or real payments. Self-dogfooding, synthetic personas, and internal tests do not count.
- Bar criteria require observable external signals (for example: 3 external users completing the core flow unassisted, or first paid customer).
- Missing external usage is an owner item, never a code finding. Judge verifies cited external proof and reports only launch-blocking defects; rounds end on `ADOPTION` or `OWNER`, never `CONTINUE`.
