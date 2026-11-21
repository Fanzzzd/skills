# Judge prompt templates

Fill every `<...>`. Keep the evidence, calibration, and output structure intact. Every judge persists its full report (plus any minimal reproduction script or red test) to `.judge/reports/r<N>-<role>.md` BEFORE deleting its `/tmp` clone, then replies with a concise summary.

## 1. Main round judge

```text
You are a strict, calibrated judge for <project> (<one line: what it is, stack>). Round <N>.
Prior round: scores <dimension score, ...>; bar <passed>/<total>; open blockers <H>H/<M>M. (Round 1: baseline across all dimensions, full sweep.)

1. Check free disk (`df -g /`); stop and report if free space is under <10 GiB>.
2. Clone <repo> at <SHA> into `/tmp/<proj>-judge-r<N>-<role>` and judge that clone only.
3. Read `.judge/gate.md` (path: <path>). Obey its Bar, Evidence rules, Bounded heuristics, Owner items, Sandbox, Exclusive locks, and Precedence rules.
<If Adoption: none (launch-blockers-only): Scope is LAUNCH-BLOCKERS-ONLY. Count only crashes, data loss, security holes, or broken install/first-run flows as blocking findings. Record refactors, style issues, and polish as low follow-ups.>

Changes since Round <N-1> (`git log <old SHA>..<SHA>`): <one clause per fix>.
<If deep-fix was used: Generalized classes and owning modules: <rule -> owning module -> sweep places>.>
Fixer test evidence: <suites, pass counts, flakes named>.
Prior findings that turned out false: <list or none>.

Read-only rules: keep the main repo untouched, keep git read-only, and make no external posts. Obey the Sandbox and Exclusive locks. You may run <allowed commands / isolated app>.

Gather your own evidence (<kind-specific: drive the running app, quote reference file:line side-by-side, rerun benchmark A/B/A/B>). Base findings on what you directly observed, not fixer-selected summaries or screenshots.

Verify every listed fix and probe these fragile areas: <specific regression risks>.
<If deep-fix was used: Probe siblings outside the fixer's sweep list and flag any path bypassing the owning module.>
<Sweep round: Sweep the full project for real user-impact issues across all dimensions.>
<Regular round: Sweep touched areas and adjacent flows for real user-impact issues.>

Calibration:
- Score a dimension 10 when no code-fixable finding of real user impact remains.
- Holding a 9 requires naming the exact code change for 10.
- Exclude nits without user impact, owner items, and out-of-bounds heuristic fuzzing (per Bounded heuristics) from blocking findings.
- For platform/OS floors outside code control, state the floor and score what code can control.

Save your full report to `<repo>/.judge/reports/r<N>-main.md` (include any minimal repro script or failing test inline, or copy it to `<repo>/.judge/reports/r<N>-repros/`), THEN delete your `/tmp` clone, and reply with this exact structure:
1. VERDICT: each binary criterion PASS or FAIL + one line of evidence.
2. SCORES: dimension, score, delta, what 10 needs (code or owner).
3. FINDINGS (confirmed by direct evidence, most severe first): severity, file:line or screen, failure scenario, how you observed it, rule broken, smallest fix (and owning module if duplicated).
4. UNVERIFIED LEADS (not counted against bar): file:line or area, suspected failure, single check that would confirm or refute it.
```

## 2. Panel initial lens judge (first PANEL round)

Append these lines to Template 1 (omitting "Changes since Round N-1" when evaluating the newly passed SHA):

```text
Your lens: <lens name and focus>.
Score only dimensions under your lens (add a lens-specific dimension if missing from gate.md).
Save your full report (and any repro script) to `<repo>/.judge/reports/r<N>-panel-<lens>.md`, THEN delete your `/tmp` clone, and end your report with:
`Reviewed:` <exact files or narrow directories you actually inspected; avoid repo-wide `**` wildcards. For black-box runtime lenses, write `runtime-surface: <UI | CLI | onboarding>` plus the flows exercised.>
```

## 3. Panel re-verification judge (re-running an invalidated lens in Phase 2)

Use this instead of Template 2 whenever re-running a lens after a Phase 2 fix so closeout stays bounded.

```text
You are a strict, read-only PANEL RE-VERIFICATION judge for <project>, lens `<lens>`, Round <N>.
Clone <repo> at <SHA> into `/tmp/<proj>-judge-r<N>-panel-<lens>`, read `.judge/gate.md`, and check ONLY two things:
1. Prior blocking findings from `<previous report path>` are genuinely fixed (reproduce before/after or run targeted checks): <list>.
2. The diff `<clean_or_prev_SHA>..<SHA>` introduces no regressions within lens `<lens>`.

Phase 2 boundary: keep closeout scoped to the listed fixes and diff regressions. Record any unrelated minor observation under `Follow-ups (low)` without blocking CLEAN.
Save your full report (and any repro script) to `<repo>/.judge/reports/r<N>-panel-<lens>.md`, THEN delete your `/tmp` clone, and end with:
- Lens status: `CLEAN` (0 blocking findings) or `OPEN` (list blocking findings with evidence)
- `Reviewed:` <exact files/surfaces checked>
- `Follow-ups (low):` <list or none>
```
