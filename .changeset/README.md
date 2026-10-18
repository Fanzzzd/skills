# Changesets

Every change to a skill's behaviour ships with a changeset. Run `npm run changeset`, pick the bump, and write one line a user would want to read in the changelog. The Release workflow turns pending changesets into a "chore: version skills" PR; merging it bumps `package.json`, `.claude-plugin/plugin.json` and `CHANGELOG.md` together.
