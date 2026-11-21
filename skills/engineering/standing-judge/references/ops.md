# Operational guardrails for heavy loops

Load this reference for large repos, multi-language builds (Rust, Swift, Kotlin, Docker), embedded databases, or GUI/browser UX gates.

## 1. Coordinator vs Fixer split

Long sessions that both orchestrate judges and edit large codebases compact repeatedly and drop gate rules. When a round touches more than 3 modules or its test suite takes more than 3 minutes:

- **Main session stays Coordinator:** owns `.judge/gate.md`, `.judge/rounds.md`, SHA freezing, judge dispatch, resource locks, merging, and verdicts.
- **Fixes run in disposable subagents:** dispatch one fresh subagent per independent fix class in an isolated git worktree (`branch` or `share`). Cap each subagent's final hand-back report at 15 lines (details in `.judge/reports/`).
- **Never share a mutable checkout across parallel judges.** Parallel sub-judges must never run `pnpm install` / `cargo build` / `npm ci` inside a shared workspace directory; either give each judge its own clone or pre-build one read-only artifact directory and forbid package installs inside sub-judges.

## 2. Machine resource hygiene

- **Disk floor (10 GiB default):** Run `df -g /` before cloning or starting heavy suites. Below the floor, stop and clean stale `/tmp/*judge*` directories or build caches before continuing.
- **Clone cleanup:** Every round clone lives under `/tmp/<project>-judge-r<N>-<role>`. Once `.judge/reports/r<N>-<role>.md` is written and verified, remove that `/tmp` clone immediately. Never accumulate clones across rounds.
- **Heavy concurrency cap (default 2):** Run at most 2 heavy test/build pipelines simultaneously (embedded Postgres, browser suites, native toolchains, full monorepo checks). Serialize extra heavy jobs with a lockfile or queue script rather than spiking machine load and triggering false timeouts.

## 3. Exclusive resource locks

Declare shared machine resources in `.judge/gate.md` under `Exclusive locks`:

- **Virtual displays / real GUI windows / browser profiles / fixed localhost ports:** Strictly one judge or test runner at a time. Never let two UX or onboarding judges compete for the same display or browser session.
- **Process cleanup:** Track PIDs of daemons, dev servers, browsers, and test DBs spawned during a round; verify they exit when the round finishes so orphan processes do not leak memory across rounds.

## 4. Crash, reboot, and API-interrupt recovery

- **Persistent state lives in `.judge/`:** Reports go to `.judge/reports/`, ledger to `.judge/rounds.md`. Treat `/tmp` as volatile scratch only.
- **Judge interruption:** If a judge dies from API rate limits, network drops, machine reboot, or a false-positive safety refusal, do not count that attempt against budget and do not infer `CLEAN`. Record `aborted` in `.judge/reports/` and re-run a fresh judge on the same frozen SHA (for false-positive safety refusals on local defensive tests, state explicit local authorization and use benign synthetic fixtures).
- **Session resume:** After a crash or reboot, read `.judge/gate.md`, `.judge/rounds.md`, and `ls .judge/reports/` first to resume from the exact last completed artifact without repeating finished rounds.
