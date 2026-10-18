#!/usr/bin/env python3
"""Fill {PLACEHOLDER}s in a prompt template.

Usage: render_prompt.py TEMPLATE KEY=VALUE [KEY=VALUE...]
  SOURCES may be a comma-separated list of paths or @file (one path per line);
  it is rendered as an indented bullet list. RULES, SCRIPTS, SKILL default to this skill's paths.
Unfilled placeholders are left visible and reported on stderr.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES = str(HERE.parent / "references")
SCRIPTS = str(HERE)
SKILL = str(HERE.parent)


def bullets(v):
    if v.startswith("@"):
        items = [l.strip() for l in Path(v[1:]).read_text(encoding="utf-8").splitlines() if l.strip()]
    else:
        items = [x.strip() for x in v.split(",") if x.strip()]
    return "\n".join(f"   - `{x}`" for x in items) if items else "   - （主持人未列出资料来源；只核对稿内前后一致和引文标记）"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    tpl = Path(sys.argv[1]).read_text(encoding="utf-8")
    vals = {"RULES": RULES, "SCRIPTS": SCRIPTS, "SKILL": SKILL, "SOURCES": "", "PROJECT_RULES": "（无）"}
    for kv in sys.argv[2:]:
        k, _, v = kv.partition("=")
        vals[k] = v
    vals["SOURCES"] = bullets(vals["SOURCES"])
    out = re.sub(r"\{([A-Z_]+)\}", lambda m: vals.get(m.group(1), m.group(0)), tpl)
    left = sorted(set(re.findall(r"\{([A-Z_]+)\}", out)))
    if left:
        print("unfilled: " + ", ".join(left), file=sys.stderr)
    sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
