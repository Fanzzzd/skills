# Skills

[![Check](https://github.com/Fanzzzd/skills/actions/workflows/check.yml/badge.svg)](https://github.com/Fanzzzd/skills/actions/workflows/check.yml)

Agent skills I run on my own projects every week. They work in Claude Code, Codex, and any agent that reads `SKILL.md`.

There are two so far. The first is a gate. Coding agents stop when they think they're done, and "keep going until it's perfect" turns into a loop that never ends or a loop that ends on a guess. `standing-judge` puts a fresh, read-only judge between the agent and "done". Each round the judge scores a frozen commit and lists findings. The agent fixes them and proves the fixes. Then the agent rules whether development continues.

The second, `deai`, revises Chinese or English prose that reads like an AI wrote it. It locks every fact, citation and hedge before touching a sentence, and checks the result with local detectors and two independent judges.

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

- **[standing-judge](./skills/engineering/standing-judge/SKILL.md)**: Run a gate loop where a fresh read-only judge scores the work every round and rules whether development continues, until the bar passes, a plateau or budget stops it, or only owner decisions remain. [Docs](./docs/engineering/standing-judge.md).

### Productivity

- **[deai](./skills/productivity/deai/SKILL.md)**: Make Chinese or English prose (theses, reports, articles, cover letters) read like a domain author wrote it, without losing facts, citations, hedges or terms. A rule scanner, local AIGC detectors routed by language, and a two-judge revision loop. The skill body is in Chinese. [Docs](./docs/productivity/deai.md).

## How `standing-judge` works

```
gate file ──> freeze SHA ──> fresh judge (clean clone, own evidence)
                 ^                         │
                 │                    scores + findings
                 │                         v
          ship + log round <── prove <── verify each finding, fix
                                           │
                                      verdict:
  PANEL | PASS | OWNER | BUDGET | PLATEAU | REWRITE | CONTINUE
```

- **The bar is binary and frozen.** "No finding of medium or higher" or "every P0 passes" decides PASS. Scores from 0 to 10 track progress beside it. Thresholds never move to let the work pass.
- **The judge gathers its own evidence.** It runs the app, drives the flows, reruns the benchmark, and quotes the reference product side by side. A judge fed the fixer's screenshots sees only what the fixer picked.
- **Six gate kinds:** code, parity with a named product, black-box UX persona, performance with a noise floor and interleaved A/B runs, prose, and research where the judge picks the benchmark.
- **PASS needs a panel.** One judge's 10 covers only its dimensions, so before PASS a panel of judges with other lenses, on other models where possible, takes one more look.

Every rule comes from a loop that went wrong in a real session: a judge scoring GitHub stars against a repo, an end-to-end suite that quit the user's running app, a 39-round loop with no stop rule, a research agent grading itself on its own benchmark. The [docs page](./docs/engineering/standing-judge.md) covers when to reach for it and what a working loop looks like.

## Contributing

Bug reports and ideas are welcome when they come from a real session. See [SCOPE.md](./SCOPE.md) for the bar, and [`.out-of-scope/`](./.out-of-scope/) for what's already been decided. Maintainer rules live in [AGENTS.md](./AGENTS.md).

## License

[MIT](./LICENSE)
