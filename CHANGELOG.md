# fanzzzd-skills

## 0.1.0

### Minor Changes

- First public release with two skills. `standing-judge` is a gate loop where a fresh read-only judge scores the work every round and issues a verdict (BUDGET, PASS, PANEL, OWNER, PLATEAU, REWRITE, CONTINUE). It covers six gate kinds: code, parity, UX, performance, prose and research.
- `deai` revises Chinese or English prose that reads like an AI wrote it, without losing facts, citations, hedges or terms. It ships a rule scanner, local AIGC detectors routed by language, and a two-judge revision loop.
