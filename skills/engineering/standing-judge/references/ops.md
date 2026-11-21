# Operational guardrails for heavy loops

Load this reference for large repos, multi-language builds (Rust, Swift, Kotlin, Docker), embedded databases, GUI/browser UX gates, or repos initialized with `bd` (Beads).

## 1. Coordinator vs Fixer split

Long sessions that both orchestrate judges and edit large codebases compact repeatedly and lose gate state. When a round touches more than 3 modules or its test suite takes more than 3 minutes:

- **Main session stays Coordinator:** owns `.judge/gate.md`, `.judge/rounds.md`, SHA freezing, judge dispatch, resource locks, merging, and verdicts.
- **Fixes run in disposable subagents:** dispatch one fresh subagent per independent fix class in an isolated git worktree (`branch` or `share`). Cap each subagent's hand-back report at 15 lines (details in `.judge/reports/`).
- **Isolated checkouts for parallel judges:** give each parallel sub-judge its own clone, or pre-build one read-only artifact tree and keep package installs (`pnpm install`, `npm ci`, `cargo build`) out of shared directories.

## 2. Machine resource hygiene

- **Disk floor (10 GiB default):** Run `df -g /` before cloning or starting heavy suites. Below the floor, stop and clean stale `/tmp/*judge*` directories or build caches first.
- **Clone cleanup with repro preservation:** Every round clone lives under `/tmp/<project>-judge-r<N>-<role>`. Save the report and any minimal repro script to `.judge/reports/` FIRST, then remove the `/tmp` clone immediately.
- **Heavy concurrency cap (default 2):** Run at most 2 heavy test/build pipelines simultaneously (embedded Postgres, browser suites, native toolchains, full monorepo checks). Serialize extra heavy jobs with a lockfile or queue script to prevent load spikes and false timeouts.

## 3. Exclusive resource locks

Declare shared machine resources in `.judge/gate.md` under `Exclusive locks`:

- **Virtual displays, GUI windows, browser profiles, and fixed localhost ports:** Run strictly one judge or test runner at a time per exclusive resource.
- **Process cleanup:** Track PIDs of daemons, dev servers, browsers, and test DBs spawned during a round; confirm they exit before starting the next round so orphan processes do not leak memory.

## 4. Crash, reboot, and API-interrupt recovery

- **Persistent state lives in `.judge/`:** Store reports in `.judge/reports/` and the compact ledger in `.judge/rounds.md`. Treat `/tmp` as volatile scratch only.
- **Judge interruption:** If a judge dies from API rate limits, network drops, machine reboot, or a false-positive safety refusal, count zero budget against that attempt and do not infer `CLEAN`. Record `aborted` in `.judge/reports/` and re-run a fresh judge on the same frozen SHA (for false-positive safety refusals on local defensive tests, state explicit local authorization and use benign synthetic fixtures).
- **Session resume:** After a crash or reboot, read `.judge/gate.md`, `.judge/rounds.md`, and `ls .judge/reports/` first to resume from the exact last completed artifact.

## 5. Optional `bd` (Beads) backend

Enable only when `.beads/` already exists in the repo (or the user explicitly asks to track the loop in `bd`). Keep the read-only judge isolated from `bd`; the **Coordinator** performs all `bd` operations:

- **Finding ledger and recurrence:** Create one bead per verified blocking finding (`bd create ... --label severity:medium --label area:<module> --label round:<N>`). Close with the fix SHA; reopen via `bd reopen` if the next judge reproduces it. Compute `REWRITE` and `PLATEAU` triggers mechanically with `bd count` and `bd list --status open --label area:<module>` instead of scanning long prose logs.
- **Serialized merges:** Use `bd merge-slot acquire` / `bd merge-slot release` so parallel fixer worktrees merge in order without conflict races.
- **Dead-worker recovery:** Have long-running fixer subagents refresh their lease with `bd heartbeat`; run `bd reclaim` after crashes or timeouts to return orphaned `in_progress` fixes to ready.
- **Async gates:** Use `bd gate create` for `human` checkpoints (Round 1 UX visual sign-off, owner decisions), `gh:run` CI waits, and `bead` dependencies blocking the next judge round.
