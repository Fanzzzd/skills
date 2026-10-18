# Maintaining this repo

Agent skills, one folder per skill, organized into buckets under `skills/`:

- `engineering/`: promoted. Shipped in the plugin, listed in the README, has a docs page.
- `productivity/`: promoted, for non-code work. Same rules as `engineering/`.
- `in-progress/`: public on purpose, feedback wanted, not shipped in the plugin, no docs page.
- `deprecated/`: retired. Not shipped, not linked.

`private/` holds skills tied to one private codebase. It is gitignored and must never be published. `scripts/link-skills.sh` links it locally like any other bucket.

## Invariants

`npm run check` (`scripts/check.mjs`) enforces every rule in this list, and CI runs it on every push to `main` and every pull request. Fix what it reports; never weaken the check to pass.

- A skill folder's name equals the `name` in its `SKILL.md` frontmatter. The `description` stays under 1024 characters.
- Every skill has `agents/openai.yaml` beside `SKILL.md` with Codex picker metadata (`interface.display_name`, `interface.short_description`).
- The promoted set equals `.claude-plugin/plugin.json`'s `skills` array, exactly. Each promoted skill is linked from the top-level `README.md` and its bucket `README.md`, and has a docs page at `docs/<bucket>/<name>.md`. No other skill has a docs page.
- `.claude-plugin/plugin.json`'s `version` equals `package.json`'s. Only `npm run version` changes either.
- No em dashes in prose. Rewrite the sentence with a period, comma, colon or parentheses; never substitute a character blindly. A dash quoted as data (a blacklist entry, a regex) goes in a code span, which the check skips.
- Every relative link resolves.

Run `claude plugin validate . --strict` after touching either manifest.

## Writing skills

`SKILL.md` is for the agent; the docs page is for a human choosing a tool. Never copy one into the other. A docs page carries **What it does**, **When to reach for it**, the skill's own middle sections, **Common questions** and **It's working if**, in that order, and no install commands (those live in the README only).

Every rule in a skill earns its place from a failure seen in a real session. When a rule changes, say in the changeset which failure drove it.

A skill that names another skill tells the agent to call the Skill tool with that name. It never links into another skill's folder.

## Releasing

Every behaviour change ships with a changeset (`npm run changeset`). Merging to `main` makes the Release workflow open or update a "chore: version skills" PR; merging that PR bumps versions, writes `CHANGELOG.md` and tags the release. Plugin installs update when `plugin.json`'s version moves.

Issues are judged against [SCOPE.md](./SCOPE.md).
