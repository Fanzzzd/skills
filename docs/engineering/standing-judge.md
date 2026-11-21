## What it does

`standing-judge` runs a maker-checker gate over your project. Each round, a fresh read-only judge clones a frozen commit, gathers its own evidence, scores the work, and lists findings. You (or delegated fixer subagents) verify each finding, fix it, prove the fix with tests, ship on the approved path, and issue one verdict: continue, or stop with a concrete reason.

The judge never edits and never remembers prior rounds. A judge that edits grades its own code, and a judge that remembers its last verdict defends it. A fresh judge each round finds what the previous one missed, while hard circuit breakers prevent infinite polish loops.

## When to reach for it

Type `/standing-judge`, or let the agent invoke it when you want a judge that decides when to stop, when you ask to keep going "until full marks" or "to the limit", when matching a named product, or when checking whether a project is worth developing further.

| You want | Primary kind |
|---|---|
| A reliable, launch-ready repo or library | Code |
| To match or beat a named product or repo | Parity |
| A user flow and interface that make sense | UX (black-box persona + Round 1 visual check) |
| Faster, lighter, or "to the limit" | Performance (interleaved A/B with noise floor) |
| A document, thesis, or letter ready to submit | Prose |
| A benchmarked research result that holds up | Research (judge picks or audits benchmark) |
| To check whether a product has real-world pull | Adoption (external users or revenue) |

Gates can combine a primary kind with modifiers (such as `code + parity-matrix` or `UX + perf-budget`). For a single review of one diff, use a code review skill instead.

## The verdict

Every round ends on exactly one verdict, and the report leads with it. The loop runs in two phases: Phase 1 clears blockers; Phase 2 locks out low-severity edits and confirms the final SHA through a cross-model panel.

- **BUDGET**: the current epoch (default 6 rounds) or total budget is spent. Even when asked for "unlimited" runs, the loop pauses at each epoch boundary with a convergence delta report and asks before continuing.
- **ADOPTION**: at least one judged round is verified on the current SHA for a personal product with `Adoption: none`, and zero launch-blocking defects remain. Ship to real users and record external feedback or payment in `.judge/gate.md` before opening a full gate.
- **PASS**: the bar holds on the current SHA, and every panel lens has a valid clean result on it.
- **PANEL**: the bar holds on the current SHA, and one or more panel lenses still need verification.
- **OWNER**: every remaining blocker is an owner item (credentials, signing, product decision, external proof).
- **PLATEAU**: the circuit breaker fired. Two consecutive bar-unmet rounds showed neither a drop in open blocking findings nor a rise in passed binary criteria, a `REWRITE` target still had a blocking finding on the next round, or an open-ended performance goal produced two rejected candidates in a row.
- **REWRITE**: the same area or rule produced blocking findings two rounds in a row (first time only). The fixer consolidates the rule behind one owning module and lets the next judge attack it.
- **CONTINUE**: code can fix a remaining blocker.

## The gate file and ledger

Before Round 1, the agent writes `.judge/gate.md` (excluded from git): the primary kind and modifiers, binary bar, bounded heuristics (so regex or shell matchers do not loop forever on exotic fuzzing), owner items, adoption status, sandbox and exclusive resource locks, epoch budget, ship path, and approved judge models. It shows you the summary before starting (headless runs mark every report `gate unconfirmed`).

Round history stays split in two: `.judge/rounds.md` holds a compact ledger (max 8 lines per round) so any resumed session reads the whole arc in seconds, while full judge reports live in `.judge/reports/` instead of volatile `/tmp`.

## Common questions

**Why does it pause every 6 rounds even if I say "unlimited budget"?**
Unbounded runs without checkpoints drift in scope and burn compute long after diminishing returns set in. Epoch pauses give you a convergence delta ("blockers went 9 -> 3 -> 2") so you decide whether another 6 rounds are worth running.

**Why did it stop after Round 1 on my personal product?**
Without external users or revenue, later rounds polish guesses instead of product-market fit. Once real external user feedback or first payment is recorded in `.judge/gate.md`, a full multi-round gate unlocks.

**Why does Phase 2 forbid fixing low findings?**
Fixing a `low` finding or tweaking unrelated docs during `PANEL` voids already-clean lenses and forces full panel re-runs. Phase 2 fixes only blocking findings, and re-run lenses perform targeted re-verification instead of opening new fuzz axes.

**Why does the panel want a different model family?**
Same-family judges share blind spots and frequently over-score their own family's drafts. Including a second approved model family in `PANEL` catches issues single-family self-judging misses. If only one family is approved, reports mark `single-family-judge`.

**Why does a UX gate pause after Round 1 for my review?**
LLM UX judges are strong at catching broken flows and state bugs, but weak at visual hierarchy, aesthetics, and motion feel. Confirming screenshots after Round 1 stops autonomous loops from polishing an unattractive layout to a 10/10 score.

**Will parallel judges fill my disk or fight over displays?**
The gate file sets a 10 GiB disk floor, caps heavy parallel workers at 2, requires exclusive locks for displays/browsers/ports, and deletes each `/tmp` clone as soon as its report is saved in `.judge/reports/`.

## It's working if

- Every report leads with one verdict word and an open-blocker delta, not a vibe.
- Scores and criteria tie to a frozen commit SHA verified from a clean clone.
- Findings cite direct evidence: a command run, a screen driven, or a reference line quoted side-by-side.
- The loop stops cleanly on `PASS`, `ADOPTION`, `OWNER`, `PLATEAU`, or an epoch `BUDGET` without burning 20+ idle rounds.
