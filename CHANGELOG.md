# fanzzzd-skills

## 0.2.0

### Minor Changes

- [`f1ced4e`](https://github.com/Fanzzzd/skills/commit/f1ced4e18edfd0e1b62202bc728ec36d15ea795b) Thanks [@Fanzzzd](https://github.com/Fanzzzd)! - Remove `deai` from the plugin. It moved to its own repository, where it ships with a new `deai-setup` skill: a stale detector venv (a link into one thesis project) and missing weights showed that installing the detectors needed its own skill, including installs on other hosts.

- [`a31987d`](https://github.com/Fanzzzd/skills/commit/a31987d45082906a5191305bd4dadf6789075e86) Thanks [@Fanzzzd](https://github.com/Fanzzzd)! - Overhaul `standing-judge` based on 12 real multi-round sessions and progressive-disclosure skill patterns:

  - **Working `PLATEAU` and epoch budgets:** Across 12 repos, the old plateau rule fired 0 times and "unlimited budget" runs stretched to 20 to 30 rounds (`shipping-board`, `fastpipe`, `eradb`). `PLATEAU` now fires after 2 consecutive bar-unmet rounds where open blockers do not drop and passed binary criteria do not rise, or after a blocking finding right after a `REWRITE`, and all loops pause every 6-round epoch to report delta.
  - **Two-mode Panel and bounded heuristics:** `shipping-board` (R23 to R30) and `dot-skill` (R7 to R10) looped when tiny heuristic/doc edits voided broad `Reviewed:` globs and `whole build`. Panel lenses now require narrow `Reviewed:` paths, Phase 2 restricts edits to blocking findings, heuristic domains declare a fixed corpus in `Bounded heuristics`, and panel re-runs perform targeted re-verification instead of opening new fuzz axes.
  - **Cross-family judging, UX Round-1 checkpoint, and unverified leads:** Same-family judges scored 10/10 while another model family found P0 gaps (`lailai`), UX judges scored 10/10 on layouts with immediate human-visible defects (`shipment-doc-platform`, `touch-grass-space`, `cupertino-datetime-picker`), and judges fabricated findings when lacking a non-blocking slot for leads. Panel now requires a second model family when available (or stamps `single-family-judge`), UX gates pause after Round 1 for human visual sign-off, and judge prompts include an `UNVERIFIED LEADS` section plus repro preservation before `/tmp` clone cleanup.
  - **Progressive disclosure, ops guardrails, and optional `bd` backend:** Moved deep-fix (`references/deep-fix.md`) and heavy-loop ops (`references/ops.md`, Coordinator/Fixer split, 10 GiB disk floor, exclusive display/browser locks, `/tmp` clone cleanup, persistent `.judge/reports/`, compact 8-line `.judge/rounds.md` ledger, and optional `bd`/Beads tracking for `.beads/` repos) out of `SKILL.md` so core rules survive long-session compactions.
  - **Verified `ADOPTION` gate and hybrid kinds:** Wired `Adoption: none` launch-blockers-only scope directly into `judge-prompt.md`, required at least one verified judged round on the current SHA before `ADOPTION` stops, and supported composable `Primary kind + Modifiers` (7 of 12 real projects used hybrid kinds).

## 0.1.0

### Minor Changes

- First public release with two skills. `standing-judge` is a gate loop where a fresh read-only judge scores the work every round and issues a verdict (BUDGET, PASS, PANEL, OWNER, PLATEAU, REWRITE, CONTINUE). It covers six gate kinds: code, parity, UX, performance, prose and research.
- `deai` revises Chinese or English prose that reads like an AI wrote it, without losing facts, citations, hedges or terms. It ships a rule scanner, local AIGC detectors routed by language, and a two-judge revision loop.
