#!/usr/bin/env bash
set -euo pipefail

# Maintainer script, not an installer. Symlinks every skill in this repo
# (including private/, which is gitignored) into the local harness skill
# directories, so a `git pull` keeps them current. Skips deprecated/.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DESTS=("$HOME/.claude/skills" "$HOME/.agents/skills")

while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  name="$(basename "$src")"
  for dest in "${DESTS[@]}"; do
    mkdir -p "$dest"
    target="$dest/$name"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "skip $target: a real directory is in the way, move it first" >&2
      continue
    fi
    ln -sfn "$src" "$target"
    echo "linked $name -> $target"
  done
done < <(find "$REPO/skills" "$REPO/private" -name SKILL.md -not -path '*/deprecated/*' -print0 2>/dev/null)
