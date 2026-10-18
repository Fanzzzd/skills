# Gate file template

Write this to `.judge/gate.md` before round 1. Fill every `<...>`. Delete a section only when the gate kind says it does not apply.

```markdown
# Gate: <project>, <one line on what it is>

Kind: <code | parity | UX | performance | prose | research>
Reference: <named product, repo URL pinned to a commit, or "none">

## Bar (binary, decides PASS)

- <criterion, e.g. no open finding of medium or higher>
- <criterion, e.g. every P0 in the list below passes on the frozen SHA>
- <criterion>

Severity: high = <data loss, crash, security, blocks a core task>; medium = <wrong result or broken flow with a workaround>; low = everything else with user impact.

## Dimensions (0 to 10, tracks progress)

<dimension>: <what 10 means here, one line>
<dimension>: <...>

Precedence when two rules conflict: <rule A> wins over <rule B>.

## Owner items (never scored against)

- <decision or out-of-code gap>: <what it would take>

## Sandbox

Judge and fixer never: <touch the user's running app, real data dirs, other repos, the pointer, push, post>.
Judge may run: <test, lint, build commands; the app only as <isolated instance, demo profile>>.
PASS path uses no public network and no timing assertion tighter than <N ms>.
Max parallel test workers while judges run: <N>.

## Budget and stop

Budget: <N rounds | N hours>.
Plateau: two rounds with no dimension moving and no new medium-or-higher finding.
Judge noise: <spread measured on an unchanged candidate, or "not measured, bar is binary">.

## Ship path

<commit, changeset, push, release PR, install>. Verified fixes ship as they land.
```

`.judge/rounds.md` gets one block per round:

```markdown
## Round <N>, <SHA>, judge <model>

Scores: <dimension score, ...>
Criteria: <passed>/<total>
Fixed: <one clause per finding>
Tests: <suite pass counts, flakes named>
Verdict: <CONTINUE | PASS | OWNER | PLATEAU | BUDGET | REWRITE>
```
