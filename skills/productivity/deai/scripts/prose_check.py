#!/usr/bin/env python3
"""Rule-based AI-pattern scan for Chinese prose (Markdown or plain text).

Usage:
  python3 prose_check.py FILE [FILE...]  (.md, .txt or .docx) [--json] [--baseline ORIGINAL] [--lexicon EXTRA.md] [--no-sd]

  --baseline ORIGINAL  比对改写前原稿的限定词（可能、如果、未必、仅等），任何一组变少即判不通过。
  --lexicon EXTRA.md   追加项目词表，格式同 references/blacklist.md（红：/黄：/正则：/抽象：/防御正则：）。
  --no-sd              不检查句长标准差（短文本、摘要用）。
  --json               输出 JSON。

Exit code 1 when any check fails. Passing the script does not mean the prose is natural;
paragraph-level judging decides. A non-Chinese draft (Chinese characters under 30% of
Chinese characters plus Latin words in the body, the same rule aigc_detect.py routes by) is
reported as skipped, with "skipped": true in JSON. It exits 0 unless --baseline finds
dropped hedges; the hedge check covers English hedges too.
"""
import json
import re
import statistics
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep the skill folder free of __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent))
from aigc_detect import read_input  # noqa: E402  (.md/.txt as-is, .docx body text; no torch import)

HERE = Path(__file__).resolve().parent
BLACKLIST = HERE.parent / "references" / "blacklist.md"

# 每 1000 汉字的上限，超过即判不通过
YELLOW_PER_K = 6.0
PATTERN_PER_K = 1.0
SELFREF_PER_K = 3.0
ABSTRACT_PER_K = 8.0
DEFENSE_PER_K = 0.5
MIN_SENT_SD = 8.0

CITE_RX = r"〔REF:[^〕]+〕|\[\d+(?:[-–,，]\d+)*\]|\[@[^\]]+\]"


def load_lists(paths):
    red, yellow, regex, abstract, defense = [], [], [], [], []
    for path in paths:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.startswith("红："):
                red += [w.strip() for w in line[2:].split("，") if w.strip()]
            elif line.startswith("黄："):
                yellow += [w.strip() for w in line[2:].split("，") if w.strip()]
            elif line.startswith("正则："):
                regex.append(line[3:].strip())
            elif line.startswith("抽象："):
                abstract += [w.strip() for w in line[3:].split("，") if w.strip()]
            elif line.startswith("防御正则："):
                defense.append(line[5:].strip())
    red = [w.replace("……", "") for w in red if w.replace("……", "")]
    return red, yellow, regex, abstract, defense


def paragraphs(text):
    """Body paragraphs only: skip headings, tables, captions, source notes, quotes, code."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    out = []
    for block in re.split(r"\n\s*\n", text):
        b = block.strip()
        if not b or b.startswith(("#", "|", "!", "资料来源", "数据来源", "来源：", "注：", ">")):
            continue
        if re.match(r"^[表图]\s*[0-9A-Z]+[-－.．]?\d*\s", b):
            continue
        out.append(b)
    return out


def han(s):
    return len(re.findall(r"[一-鿿]", s))


def is_chinese(body):
    """Same rule as aigc_detect.detect_lang, applied to body paragraphs: Chinese characters are
    at least 30% of (Chinese characters + Latin words), ignoring inline code and URLs."""
    prose = re.sub(r"`[^`\n]*`|https?://\S+", " ", body)
    cjk = han(prose)
    return cjk >= 0.3 * max(1, cjk + len(re.findall(r"[A-Za-z]+", prose)))


def length(body):
    """Chinese characters for a Chinese draft, Latin words otherwise."""
    return han(body) if is_chinese(body) else len(re.findall(r"[A-Za-z]+", body))


def sentences(p):
    p = re.sub(CITE_RX, "", p)
    return [s for s in re.split(r"[。！？；!?;]", p) if han(s) >= 2]


def ctx(p, w, start=None):
    i = p.find(w) if start is None else start
    return p[max(0, i - 12): i + len(w) + 12]


def check(path, red, yellow, regex, abstract, defense, sd_check=True):
    text = read_input(path)
    paras = paragraphs(text)
    body = "\n".join(paras)
    k = max(han(body) / 1000, 0.001)
    r = {"file": str(path), "han": han(body), "paragraphs": len(paras), "red": [], "yellow": {},
         "patterns": [], "list_lines": [], "bold": 0, "flat_runs": [], "self_ref": 0, "fail": []}

    for n, p in enumerate(paras, 1):
        for w in red:
            if w in p:
                r["red"].append({"para": n, "word": w, "ctx": ctx(p, w)})
        for rx in regex:
            for m in re.finditer(rx, p):
                r["patterns"].append({"para": n, "rx": rx, "ctx": m.group(0)[:40]})
        lens = [han(s) for s in sentences(p)]
        for j in range(len(lens) - 2):
            a, b, c = lens[j:j + 3]
            if min(a, b, c) >= 12 and max(a, b, c) - min(a, b, c) <= 5:
                r["flat_runs"].append({"para": n, "lens": [a, b, c]})
                break
    r["abstract"] = {w: body.count(w) for w in abstract if body.count(w)}
    r["defense"] = [{"para": n, "ctx": m.group(0)[:30]} for n, p in enumerate(paras, 1)
                    for rx in defense for m in re.finditer(rx, p)]
    r["evidence"] = {
        "citations": len(re.findall(CITE_RX, body)),
        "numbers": len(re.findall(r"\d+(?:\.\d+)?\s*(?:%|％|万|亿|家|个|项|次|天|周|月|年|人|件|元|台|条)", body)),
        "todo": text.count("【待补"),
    }
    for w in yellow:
        c = body.count(w)
        if c:
            r["yellow"][w] = c
    r["self_ref"] = sum(body.count(w) for w in ("本文", "本研究", "笔者"))
    r["bold"] = body.count("**")
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    r["list_lines"] = [l[:40] for l in prose.splitlines() if re.match(r"^\s*([-*+]|\d+\.)\s+", l)]
    all_lens = [han(s) for p in paras for s in sentences(p)]
    r["sent_len_mean"] = round(statistics.mean(all_lens), 1) if all_lens else 0
    r["sent_len_sd"] = round(statistics.pstdev(all_lens), 1) if all_lens else 0

    ysum = sum(r["yellow"].values())
    if r["red"]:
        r["fail"].append(f"红色词 {len(r['red'])} 处")
    if len(r["patterns"]) / k > PATTERN_PER_K:
        r["fail"].append(f"句式命中 {len(r['patterns'])} 处，超过每千字 {PATTERN_PER_K}")
    if ysum / k > YELLOW_PER_K:
        r["fail"].append(f"黄色词 {ysum} 处，每千字 {ysum / k:.1f}，上限 {YELLOW_PER_K}")
    if r["self_ref"] / k > SELFREF_PER_K:
        r["fail"].append(f"本文/本研究/笔者 {r['self_ref']} 处，每千字 {r['self_ref'] / k:.1f}，上限 {SELFREF_PER_K}")
    asum = sum(r["abstract"].values())
    if asum / k > ABSTRACT_PER_K:
        r["fail"].append(f"抽象名词 {asum} 处，每千字 {asum / k:.1f}，上限 {ABSTRACT_PER_K}")
    if len(r["defense"]) / k > DEFENSE_PER_K:
        r["fail"].append(f"防御性声明 {len(r['defense'])} 处，每千字 {len(r['defense']) / k:.1f}，上限 {DEFENSE_PER_K}")
    if r["bold"] or r["list_lines"]:
        r["fail"].append("正文有加粗或列表行")
    if sd_check and len(all_lens) >= 10 and r["sent_len_sd"] < MIN_SENT_SD:
        r["fail"].append(f"句长标准差 {r['sent_len_sd']}，低于 {MIN_SENT_SD}")
    return r


# 同义组：组内互换不算丢失，组合计数变少才算
# Each group is a list of regexes, matched as one alternation so a longer form ("大约")
# is counted once and not again as its inner character. Single characters that are
# usually part of other words get context: 不仅 is not 仅, 合约 is not 约, 崇尚 is not 尚.
NUM = "[为合莫近\\d一二两三四五六七八九十百千万几〇零数]"
HEDGES_ZH = {
    "可能": ["可能", "或许", "也许"],
    "条件": ["如果", "假如", "倘若", "如有", "若(?!干)"],
    "未必": ["未必", "不一定", "不见得"],
    "单独": ["单独", "单凭", "仅凭", "只凭", "仅以", "仅从"],
    "充分": ["充分", "完全"],
    "部分": ["部分", "一些", "某些"],
    "程度": ["(?<!计)较", "相对"],
    "尚未": ["尚(?=[未无不待需难])", "还没", "还未", "仍未", "暂未"],
    "仅": ["仅仅", "(?<!不)仅", "只限", "只是"],
    "约": ["大约", "约" + "(?=" + NUM + ")", "左右", "前后"],
}
_EN_NUM = r"(?=\s+(?:\d|[$£€~]|one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty|forty|fifty|a hundred|a thousand|half|a third|a quarter|a dozen))"
HEDGES_EN = {
    "may": ["may", "might", "could", "possibly", "perhaps", "likely"],
    "if": ["if", "unless", "provided"],
    "some": ["some", "partly", "partially", "several"],
    "only": ["only", "solely", "merely"],
    "about": ["about" + _EN_NUM, "approximately", "roughly", "around" + _EN_NUM],
}


def hedge_counts(text):
    t = re.sub(CITE_RX, "", text)
    out = {g: len(re.findall("|".join(ws), t)) for g, ws in HEDGES_ZH.items()}
    low = t.lower()
    for g, ws in HEDGES_EN.items():
        n = len(re.findall(r"\b(?:" + "|".join(ws) + r")\b", low))
        if n:
            out["en:" + g] = n
    return out


def compare_baseline(r, baseline):
    cur = hedge_counts(read_input(r["file"]))
    base = hedge_counts(read_input(baseline))
    keys = sorted(set(cur) | set(base), key=lambda x: (x.startswith("en:"), x))
    r["hedges"] = {h: (base.get(h, 0), cur.get(h, 0)) for h in keys}
    r["hedge_drops"] = {h: v for h, v in r["hedges"].items() if v[1] < v[0]}
    cur_len = length("\n".join(paragraphs(read_input(r["file"]))))
    base_len = length("\n".join(paragraphs(read_input(baseline))))
    r["length_unit"] = "words" if r.get("skipped") else "han"
    r["baseline_len"], r["current_len"] = base_len, cur_len
    r["length_delta_pct"] = round(100.0 * (cur_len - base_len) / base_len, 1) if base_len else None
    if r["hedge_drops"]:
        r["fail"].append("限定词比原稿少：" + "，".join(f"{h} {a}→{b}" for h, (a, b) in r["hedge_drops"].items()))


def main():
    argv = sys.argv[1:]
    opts = {}
    for flag in ("--baseline", "--lexicon"):
        if flag in argv:
            i = argv.index(flag)
            opts[flag] = argv[i + 1]
            del argv[i:i + 2]
    as_json = "--json" in argv
    sd_check = "--no-sd" not in argv
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print(__doc__)
        return 2
    lists = load_lists([BLACKLIST] + ([opts["--lexicon"]] if "--lexicon" in opts else []))
    reports = [check(f, *lists, sd_check=sd_check) for f in files]
    for r in reports:
        if not is_chinese("\n".join(paragraphs(read_input(r["file"])))):
            r["skipped"] = True
            r["fail"] = []
    if "--baseline" in opts:
        for r in reports:
            compare_baseline(r, opts["--baseline"])
    if as_json:
        print(json.dumps(reports, ensure_ascii=False, indent=1))
    else:
        for r in reports:
            print(f"== {r['file']}  正文汉字 {r['han']}  段落 {r['paragraphs']}  "
                  f"句长均值 {r['sent_len_mean']} 标准差 {r['sent_len_sd']}  本文类自称 {r['self_ref']}")
            for h in r["red"]:
                print(f"  红 段{h['para']} {h['word']}：…{h['ctx']}…")
            for h in r["patterns"]:
                print(f"  式 段{h['para']} {h['ctx']}")
            if r["yellow"]:
                top = sorted(r["yellow"].items(), key=lambda x: -x[1])[:12]
                print("  黄 " + "，".join(f"{w}{c}" for w, c in top))
            if r["abstract"]:
                top = sorted(r["abstract"].items(), key=lambda x: -x[1])[:12]
                print("  抽 " + "，".join(f"{w}{c}" for w, c in top))
            for h in r["defense"]:
                print(f"  防 段{h['para']} {h['ctx']}")
            for l in r["list_lines"][:5]:
                print(f"  列 {l}")
            e = r["evidence"]
            print(f"  证据 引文标记{e['citations']} 带单位数字{e['numbers']} 待补{e['todo']}")
            for f in r["flat_runs"][:10]:
                print(f"  平 段{f['para']} 连续句长 {f['lens']}")
            if "hedges" in r:
                print("  限定词（原稿→现稿） " + "，".join(f"{h} {a}→{b}" for h, (a, b) in r["hedges"].items()))
                d = r["length_delta_pct"]
                unit = "词" if r["length_unit"] == "words" else "字"
                print(f"  篇幅 原稿 {r['baseline_len']}{unit} → 现稿 {r['current_len']}{unit}（{'' if d is None else f'{d:+}%'}）")
            if r.get("skipped"):
                tail = "；" + "；".join(r["fail"]) if r["fail"] else ""
                print("  结果：规则扫描跳过（非中文稿，英文稿看检测器和 judge）" + tail)
                continue
            print("  结果：" + ("不通过：" + "；".join(r["fail"]) if r["fail"] else "通过"))
    return 1 if any(r["fail"] for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
