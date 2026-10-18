#!/usr/bin/env bash
# Run independent judges in parallel on one file. Run from the project root.
#
# Usage: run_judges.sh <tag> <file> <out-dir> [aigc-txt|auto] [sources]
#   tag       round label, e.g. ch04-r3
#   file      the draft to judge
#   out-dir   where reports go: <out>/<tag>-codex.md, <out>/<tag>-claude.md (+ .log)
#   aigc-txt  detector output for the judges to read; "auto" (default) runs scripts/aigc
#             into <out>/aigc-<tag>.txt
#   sources   comma-separated source paths, or @list.txt (one path per line)
# Env: JUDGES   comma list from {codex,claude}; default: whichever CLIs are installed
#      CODEX_MODEL, CLAUDE_MODEL   model overrides; default: each CLI's own default
#      JP       judge prompt template (default templates/judge-prompt.md)
set -u
S="$(cd "$(dirname "$0")" && pwd)"
if [ $# -lt 3 ]; then
  sed -n '2,14p' "$0" >&2
  exit 2
fi
TAG="$1"; CUR="$2"; OUT="$3"; AIGC="${4:-auto}"; SRC="${5:-}"
mkdir -p "$OUT"
if [ -z "${JUDGES:-}" ]; then
  JUDGES=""
  command -v codex >/dev/null && JUDGES="codex"
  command -v claude >/dev/null && JUDGES="${JUDGES:+$JUDGES,}claude"
fi
if [ -z "$JUDGES" ]; then
  echo "No judge CLI found: install claude or codex, or set JUDGES." >&2
  exit 2
fi
if [ "$AIGC" = "auto" ]; then
  AIGC="$OUT/aigc-$TAG.txt"
  "$S/aigc" "$CUR" > "$AIGC" 2>"$OUT/aigc-$TAG.log" || echo "(检测器未运行，见 $OUT/aigc-$TAG.log)" > "$AIGC"
fi
P=$(python3 "$S/render_prompt.py" "${JP:-$S/../templates/judge-prompt.md}" \
  "CURRENT=$CUR" "AIGC=$AIGC" "SOURCES=$SRC")
if [[ "$JUDGES" == *codex* ]]; then
  codex exec ${CODEX_MODEL:+-m "$CODEX_MODEL"} -s read-only -C "$PWD" --skip-git-repo-check \
    -o "$OUT/$TAG-codex.md" "$P" < /dev/null > "$OUT/$TAG-codex.log" 2>&1 &
fi
if [[ "$JUDGES" == *claude* ]]; then
  claude -p "$P" ${CLAUDE_MODEL:+--model "$CLAUDE_MODEL"} --add-dir "$S/.." \
    --allowedTools "Read,Grep,Glob,Bash(python3 $S/prose_check.py:*)" \
    > "$OUT/$TAG-claude.md" 2> "$OUT/$TAG-claude.log" &
fi
wait
for f in "$OUT/$TAG-codex.md" "$OUT/$TAG-claude.md"; do
  [ -s "$f" ] && echo "$f: $(wc -c < "$f") bytes; $(grep -m1 -o '行文通过[：:][^，。 ]*' "$f" 2>/dev/null)"
done
exit 0
