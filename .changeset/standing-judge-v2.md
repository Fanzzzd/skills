---
"fanzzzd-skills": minor
---

Overhaul `standing-judge` based on 12 real multi-round sessions and progressive-disclosure skill patterns:

- **Working `PLATEAU` and epoch budgets:** Across 12 repos, the old plateau rule fired 0 times and "unlimited budget" runs stretched to 20 to 30 rounds (`shipping-board`, `fastpipe`, `eradb`). `PLATEAU` now fires after 2 consecutive bar-unmet rounds with no net drop in open blockers or a blocking finding right after a `REWRITE`, and all loops pause every 6-round epoch to report delta.
- **Two-mode Panel and bounded heuristics:** `shipping-board` (R23 to R30) and `dot-skill` (R7 to R10) looped when tiny heuristic/doc edits voided broad `Reviewed:` globs and `whole build`. Panel lenses now require narrow `Reviewed:` paths, Phase 2 bans `low` edits, heuristic domains declare a fixed corpus in `Bounded heuristics`, and panel re-runs perform targeted re-verification instead of opening new fuzz axes.
- **Cross-family judging and UX Round-1 checkpoint:** Same-family judges scored 10/10 while another model family found P0 gaps (`lailai`), and UX judges scored 10/10 on layouts with immediate human-visible defects (`shipment-doc-platform`, `touch-grass-space`, `cupertino-datetime-picker`). Panel now requires a second model family when available (or marks `single-family-judge`), and UX gates pause after Round 1 for human visual sign-off.
- **Progressive disclosure and ops guardrails:** Moved deep-fix (`references/deep-fix.md`) and heavy-loop ops (`references/ops.md`, Coordinator/Fixer split, 10 GiB disk floor, exclusive display/browser locks, `/tmp` clone cleanup, persistent `.judge/reports/`, compact 8-line `.judge/rounds.md` ledger) out of `SKILL.md` so core rules survive long-session compactions.
- **Aligned `Adoption` gate and hybrid kinds:** Wired `Adoption: none` launch-blockers-only scope directly into `judge-prompt.md` and supported composable `Primary kind + Modifiers` (7 of 12 real projects used hybrid kinds).
