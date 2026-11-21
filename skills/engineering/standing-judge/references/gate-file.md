# Gate file and round ledger templates

Write `.judge/gate.md` before Round 1. Delete a subsection only when the gate kind says it does not apply.

```markdown
# Gate: <project>, <one line: what it is>

Status: <confirmed | unconfirmed>
Primary kind: <code | parity | UX | performance | prose | research | adoption>
Modifiers: <none | parity-matrix | perf-budget | ux-checkpoint | release-hygiene>
Reference: <named product at dated version, repo URL pinned to commit SHA, or "none">
Adoption: <external user feedback or payment citation | "none" (launch-blockers-only until external signal) | "n/a" (internal tool / prose / research)>

## Evidence (copied from gate-kinds.md)

- <rule>
- <rule>

## Bar (binary, decides PASS)

- <criterion, e.g. no open finding of medium or higher>
- <criterion, e.g. every P0 passes on the frozen SHA>

Severity: high = <crash, data loss, security, blocks core flow>; medium = <wrong result or broken flow with workaround>; low = everything else with user impact.

## Bounded heuristics (optional; required for regex, shell-matching, or detector domains)

- Scope / fixed corpus: <what inputs count as in-bounds for medium findings>
- Out-of-bounds rule: <edge cases beyond this corpus log as low follow-ups, never medium blockers>

## Dimensions (0 to 10, trend only)

<dimension>: <what 10 means here, one line>

Precedence when rules conflict: <rule A> wins over <rule B>.

## Owner items (never findings)

- <decision or out-of-code gap>: <what closes it>

## Sandbox and resources

Never touch: <user running apps, real data dirs, other repos, pointer, external posts>.
Forbidden commands: <publish, force-push, brew services, rm outside own temp dir>.
Judge may run: <test, lint, build, isolated app instance>.
Exclusive locks (serial only): <none | display ID | browser profile | port | embedded DB>.
Disk floor: <10 GiB free before creating any clone>.
Max parallel heavy workers: <2>.
PASS path uses no public network and no timing assertion tighter than <N ms>.

## Budget and stop

Epoch budget: <6 rounds (default; pause and ask user before starting next epoch)>.
Plateau: 2 consecutive bar-unmet rounds with no net drop in open blocking findings, or blocking finding in a REWRITE target on the next round (open-ended perf: 2 consecutive REJECTED candidates).
Judge noise: <spread on unchanged SHA, or "not measured, bar is binary">.

## Ship path

<commit only | commit and push <branch> | release PR>. Verified fixes ship as they land.

## Judge models (user-approved)

Fixer model: <model>.
Approved judge models: <model A (family 1), model B (family 2)>. Never use an unlisted model without asking.
Rounds: <alternate A and B | model schedule>.
Panel lenses: <lens: model, ... (include >=1 model family different from fixer when available)>.
```

## Round ledger (`.judge/rounds.md`)

Keep `.judge/rounds.md` strictly compact (**max 8 lines per round**). Put full judge reports, sweep lists, and raw test output in `.judge/reports/r<N>-<role>.md` so the ledger stays readable across long sessions and compactions.

```markdown
## Round <N> | <SHA> | <model> | <YYYY-MM-DD>
- Verdict: <BUDGET | ADOPTION | PASS | PANEL | OWNER | PLATEAU | REWRITE | CONTINUE> [<flags>]
- Bar: <passed>/<total> | Open blockers: <H> high, <M> medium (delta <+/-N>)
- Scores: <dim score, ...>
- Fixed / Classes: <finding -> owning module or local fix; report link>
- Tests: <counts, flakes named>
- Panel (Phase 2 only): <lens: clean@SHA | open@SHA (reviewed paths, model)>
- Follow-ups (Phase 2 lows): <short list or none>
```
