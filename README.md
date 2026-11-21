# Skills

[![Check](https://github.com/Fanzzzd/skills/actions/workflows/check.yml/badge.svg)](https://github.com/Fanzzzd/skills/actions/workflows/check.yml)

Agent skills I run on my own projects every week. They work in Claude Code, Codex, and any agent that reads `SKILL.md`.

There is one so far, a gate. Coding agents stop when they think they're done, and "keep going until it's perfect" turns into a loop that never ends or a loop that ends on a guess. `standing-judge` puts a fresh, read-only judge between the agent and "done". Each round the judge scores a frozen commit and lists findings. The agent verifies and fixes them, proves the fixes, and issues a verdict on whether development continues.

`deai`, the de-AI prose skill that used to ship here, moved to its own repository on 2026-11-18, together with a `deai-setup` skill that installs its detectors.

## Install

Pick one route per agent. Installing the plugin and the skills.sh copy together gives you every skill twice.

<details open>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin install fanzzzd-skills --marketplace Fanzzzd/skills
```

Needs Claude Code 2.1.292 or later; on older versions run `claude plugin marketplace add Fanzzzd/skills` first, then `claude plugin install fanzzzd-skills@fanzzzd`. Third-party marketplaces don't auto-update by default: turn it on in `/plugin`, **Marketplaces**, `fanzzzd`, **Enable auto-update**, or update by hand with `claude plugin update fanzzzd-skills@fanzzzd`.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add Fanzzzd/skills
codex plugin add fanzzzd-skills@fanzzzd
```

To update, run `codex plugin marketplace upgrade fanzzzd`.

</details>

<details>
<summary><strong>Any other agent, or editable files</strong></summary>

```bash
npx skills@latest add Fanzzzd/skills
```

This copies the files into your project, so you can edit them. To update, run `npx skills@latest update`.

</details>

## Skills

### Engineering

- **[standing-judge](./skills/engineering/standing-judge/SKILL.md)**: Run a gate loop where a fresh read-only judge scores the work every round and rules whether development continues, until the bar passes, a plateau or epoch budget stops it, or only owner decisions remain. [Docs](./docs/engineering/standing-judge.md).

## How `standing-judge` works

```
gate file ──> freeze SHA ──> fresh judge (clean clone, own evidence)
                 ^                         │
                 │                    scores + findings
                 │                         v
          ship + log round <── prove <── verify each finding, fix
                                           │
                                      verdict:
  BUDGET | ADOPTION | PASS | PANEL | OWNER | PLATEAU | REWRITE | CONTINUE
```

- **The bar is binary and frozen.** "No finding of medium or higher" or "every P0 passes" decides PASS. Scores from 0 to 10 track trend beside it. Thresholds never move to let the work pass.
- **Working circuit breakers.** Runs cap at 6-round epochs even when asked for unlimited budgets, `PLATEAU` stops after two rounds with no net drop in open blockers (or a failed rewrite), and personal products with no external users stop at `ADOPTION` after clearing launch blockers.
- **Composable gate kinds.** Pick a primary kind (code, parity, UX, performance, prose, research, adoption) plus modifiers (`parity-matrix`, `perf-budget`, `ux-checkpoint`, `release-hygiene`). UX gates pause after Round 1 for human visual sign-off.
- **Two-mode cross-family panel.** Before `PASS`, parallel lenses check blind spots on a second approved model family when available. Phase 2 fixes blocking findings only, and invalidated lenses run targeted re-verification instead of opening new fuzz axes.

Every rule comes from a loop that went wrong in a real session: a 30-round regex whack-a-mole panel loop, a 0-user personal app polished for 26 rounds, same-family judges giving 10/10 where another model found P0 errors, parallel clean clones draining disk to 0 GiB, and UX judges scoring ugly layouts 10/10. The [docs page](./docs/engineering/standing-judge.md) covers when to reach for it and what a working loop looks like.

## Contributing

Bug reports and ideas are welcome when they come from a real session. See [SCOPE.md](./SCOPE.md) for the bar, and [`.out-of-scope/`](./.out-of-scope/) for what's already been decided. Maintainer rules live in [AGENTS.md](./AGENTS.md).

## License

[MIT](./LICENSE)
