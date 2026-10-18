"""Local AIGC "taste" judge for Chinese and English prose. Per-paragraph scores from open-source
detectors. The language router (--lang auto) picks the detector set from the text. Not a substitute for CNKI/维普/PaperPass/Turnitin; see
references/aigc-detector.md in this skill for calibration and limits.

Run through the wrapper (picks $AIGC_PY, else the skill's .venv). Default detectors are
MPU zh-v3 + zh-v3-short, ~10 s per 14k Chinese chars on Apple Silicon:

  scripts/aigc FILE.md
  scripts/aigc FILE.md --json
  scripts/aigc FILE.md --detectors mpu,lm       # + zero-shot Qwen scores
  scripts/aigc FILE.md --detectors mpu,mpu-short,mpu-v2,hc3,anx,lm
  scripts/aigc letter.docx                       # English: auto-routes to desklib + mpu-en

Input: .md / .txt, or .docx (body text read straight from word/document.xml).

Language router (--lang auto|zh|en): auto counts CJK characters; >= 30% of letters → zh.
Default detectors when --detectors is not given:
  zh  mpu,mpu-short
  en  desklib,mpu-en

One-time setup. The script runs with HF_HUB_OFFLINE=1, so fetch weights once with AIGC_ONLINE=1:

  uv venv ~/.cache/deai/venv --python 3.12
  uv pip install --python ~/.cache/deai/venv/bin/python torch transformers accelerate huggingface_hub
  AIGC_ONLINE=1 scripts/aigc FILE.md

Reading the numbers: judge the document-level "flagged %", not single paragraphs. Pre-ChatGPT
human MBA theses score 18-44% flagged on mpu; agent drafts score 70-90%.

Detectors (--detectors, comma separated):
  mpu        yuchuantian/AIGC_detector_zhv3       P(AI), 0..1. Default flag threshold 0.5.
  mpu-short  yuchuantian/AIGC_detector_zhv3short  P(AI), tuned for short texts.
  mpu-v2     yuchuantian/AIGC_detector_zhv2       P(AI), 2023 version (older LLMs).
  hc3        Hello-SimpleAI/chatgpt-detector-roberta-chinese  P(ChatGPT), HC3 2023 data.
  anx        AnxForever/chinese-ai-detector-bert  P(AI), temperature 0.8165 as its card says.
  mpu-en     yuchuantian/AIGC_detector_env3       English MPU, same family as mpu. P(AI).
  hc3-en     Hello-SimpleAI/chatgpt-detector-roberta  English HC3 (2023). P(ChatGPT).
  desklib    desklib/ai-text-detector-v1.01       English. DeBERTa-v3-large, #1 on the RAID leaderboard. P(AI).
  vanguard   ShantanuT01/vanguard-ai-text-detector  English. ModernBERT-large, PAN-CLEF 2026. P(AI).
  lm         Zero-shot. One forward pass of Qwen2.5 base + instruct gives two numbers:
             fdg  = Fast-DetectGPT analytic criterion (sampling=base, scoring=instruct).
                    Higher = more AI-like.
             bino = Binoculars score (observer=base, performer=instruct).
                    Lower = more AI-like.
             Raw scores have no universal threshold. The defaults (--fdg-threshold,
             --bino-threshold) are the ~90th/10th percentile of paragraph scores on
             pre-ChatGPT human MBA theses (i.e. ~10% human FPR). On text drafted by
             non-Qwen models they point the wrong way; reference only.

Preprocessing: drops Markdown headings, tables, image lines, table/figure captions (表x-x / 图x-x),
"资料来源：" / "注：" lines, HTML comments, code fences, 〔REF:...〕 markers and [n]
citation markers; splits on blank lines; paragraphs shorter than --min-chars are skipped.
Long paragraphs are chunked on sentence boundaries to each model's max length, and the
paragraph score is the length-weighted mean of chunk scores.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Weights are cached after the first download. Offline mode stops transformers from
# re-checking the hub on every load (that check hung for minutes on this network).
# Set AIGC_ONLINE=1 for the first run of a new detector.
if os.environ.get("AIGC_ONLINE") != "1":
    os.environ.setdefault("HF_HUB_OFFLINE", "1")

CLASSIFIERS = {
    # name: (hf id, index of the AI label, temperature)
    "mpu": ("yuchuantian/AIGC_detector_zhv3", 1, 1.0),
    "mpu-short": ("yuchuantian/AIGC_detector_zhv3short", 1, 1.0),
    "mpu-v2": ("yuchuantian/AIGC_detector_zhv2", 1, 1.0),
    "hc3": ("Hello-SimpleAI/chatgpt-detector-roberta-chinese", 1, 1.0),
    "anx": ("AnxForever/chinese-ai-detector-bert", 1, 0.8165),
    "mpu-en": ("yuchuantian/AIGC_detector_env3", 1, 1.0),
    "hc3-en": ("Hello-SimpleAI/chatgpt-detector-roberta", 1, 1.0),
    "vanguard": ("ShantanuT01/vanguard-ai-text-detector", 1, 1.0),
}
# Classifiers that need a custom head (mean-pooled encoder + 1-logit linear, sigmoid).
POOLED = {
    "desklib": ("desklib/ai-text-detector-v1.01", 768),
}
DEFAULT_DETECTORS = {"zh": "mpu,mpu-short", "en": "desklib,mpu-en"}


def detect_lang(text: str) -> str:
    """zh when Chinese characters are at least 30% of (Chinese characters + Latin words) in
    the prose, ignoring code fences, inline code and URLs. prose_check.py uses the same rule."""
    prose = re.sub(r"```.*?```", " ", text, flags=re.S)
    prose = re.sub(r"`[^`\n]*`|https?://\S+", " ", prose)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", prose))
    words = len(re.findall(r"[A-Za-z]+", prose))
    return "zh" if cjk >= 0.3 * max(1, cjk + words) else "en"


def read_input(path: str) -> str:
    """Markdown/text as-is; .docx paragraphs joined by blank lines (no python-docx needed)."""
    if not path.lower().endswith(".docx"):
        return Path(path).read_text(encoding="utf-8")
    import html
    import zipfile

    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    paras = []
    for body in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        body = re.sub(r"<w:(br|cr)/>", "<w:t>\n</w:t>", body)
        body = re.sub(r"<w:tab/>", "<w:t>\t</w:t>", body)
        txt = html.unescape("".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", body)))
        paras.append(txt)
    return "\n\n".join(paras)
LM_SIZES = {
    "0.5B": ("Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct"),
    "1.5B": ("Qwen/Qwen2.5-1.5B", "Qwen/Qwen2.5-1.5B-Instruct"),
    "3B": ("Qwen/Qwen2.5-3B", "Qwen/Qwen2.5-3B-Instruct"),
    "7B": ("Qwen/Qwen2.5-7B", "Qwen/Qwen2.5-7B-Instruct"),
}

# ---------------------------------------------------------------- text preprocessing

SKIP_LINE = re.compile(
    r"^\s*(!\[|\||#|```|<!--|-->|>?\s*(资料来源|数据来源|来源|注)[：:]|(表|图)\s*[0-9A-Z]+[-－.．][0-9]+\s+\S[^。]{0,60}$)"
)


def extract_paragraphs(md: str, min_chars: int, lang: str = "zh") -> tuple[list[str], int]:
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    paras, buf, skipped = [], [], 0

    def flush():
        nonlocal skipped
        if buf:
            p = ("" if lang == "zh" else " ").join(x.strip() for x in buf)
            p = re.sub(r"〔REF:[^〕]*〕", "", p)
            p = re.sub(r"\[\d+(?:[-–,，]\d+)*\]", "", p)
            p = re.sub(r"\*\*|__|`", "", p)
            p = re.sub(r"^\s*([-*+]|\d+[.、)])\s+", "", p)
            p = p.strip()
            if len(p) >= min_chars:
                paras.append(p)
            elif p:
                skipped += 1
            buf.clear()

    for line in md.splitlines():
        if not line.strip():
            flush()
            continue
        if SKIP_LINE.match(line):
            flush()
            continue
        buf.append(line)
    flush()
    return paras, skipped


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？；])|(?<=[.!?;])\s+", text)
    return [p if re.search(r"[\u4e00-\u9fff]", p) else p + " " for p in parts if p]


def chunk_by_tokens(text: str, count_tokens, max_tokens: int) -> list[str]:
    if count_tokens(text) <= max_tokens:
        return [text]
    chunks, cur = [], ""
    for s in split_sentences(text):
        if cur and count_tokens(cur + s) > max_tokens:
            chunks.append(cur)
            cur = ""
        while count_tokens(s) > max_tokens:  # a single very long sentence
            cut = max_tokens  # BERT-zh and Qwen are ~1 token per Chinese char or fewer
            chunks.append(s[:cut])
            s = s[cut:]
        cur += s
    if cur:
        # merge a tiny tail into the previous chunk's scoring by keeping it separate but weighted
        chunks.append(cur)
    return chunks


# ---------------------------------------------------------------- device


def pick_device(arg: str):
    import torch

    if arg != "auto":
        return torch.device(arg)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


# ---------------------------------------------------------------- classifiers


def run_classifier(name: str, paras: list[str], device) -> list[float]:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    hf_id, ai_idx, temp = CLASSIFIERS[name]
    tok = AutoTokenizer.from_pretrained(hf_id)
    model = AutoModelForSequenceClassification.from_pretrained(hf_id).to(device).eval()
    max_tok = 510
    out = []
    for p in paras:
        chunks = chunk_by_tokens(p, lambda t: len(tok.tokenize(t)), max_tok)
        probs, weights = [], []
        for c in chunks:
            enc = tok(c, return_tensors="pt", truncation=True, max_length=512).to(device)
            with torch.no_grad():
                logits = model(**enc).logits[0].float() / temp
            if logits.shape[-1] == 1:
                probs.append(torch.sigmoid(logits[0]).item())
            else:
                probs.append(torch.softmax(logits, -1)[ai_idx].item())
            weights.append(len(c))
        out.append(sum(a * w for a, w in zip(probs, weights)) / sum(weights))
    del model
    return out


def run_pooled(name: str, paras: list[str], device) -> list[float]:
    """desklib-style head: mean-pool the encoder output, one linear logit, sigmoid."""
    import torch
    from safetensors.torch import load_file
    from transformers import AutoConfig, AutoModel, AutoTokenizer
    from huggingface_hub import snapshot_download

    hf_id, max_len = POOLED[name]
    path = snapshot_download(hf_id)
    tok = AutoTokenizer.from_pretrained(path)
    enc_model = AutoModel.from_config(AutoConfig.from_pretrained(path))
    head = torch.nn.Linear(enc_model.config.hidden_size, 1)
    state = {}
    for f in Path(path).glob("*.safetensors"):
        state.update(load_file(str(f)))
    if not state:
        state = torch.load(next(Path(path).glob("*.bin")), map_location="cpu")
    enc_model.load_state_dict({k[len("model."):]: v for k, v in state.items() if k.startswith("model.")}, strict=False)
    head.load_state_dict({k[len("classifier."):]: v for k, v in state.items() if k.startswith("classifier.")})
    enc_model, head = enc_model.to(device).eval(), head.to(device).eval()
    out = []
    for p in paras:
        chunks = chunk_by_tokens(p, lambda t: len(tok.tokenize(t)), max_len - 2)
        probs, weights = [], []
        for c in chunks:
            e = tok(c, return_tensors="pt", truncation=True, max_length=max_len).to(device)
            with torch.no_grad():
                h = enc_model(**e)[0].float()
                m = e["attention_mask"].unsqueeze(-1).float()
                pooled = (h * m).sum(1) / m.sum(1).clamp(min=1e-9)
                probs.append(torch.sigmoid(head(pooled))[0, 0].item())
            weights.append(len(c))
        out.append(sum(a * w for a, w in zip(probs, weights)) / sum(weights))
    del enc_model, head
    return out


# ---------------------------------------------------------------- zero-shot (Fast-DetectGPT + Binoculars)


def run_lm(paras: list[str], device, size: str, max_tokens: int) -> tuple[list[float], list[float]]:
    """Fast-DetectGPT analytic criterion (Bao et al., ICLR 2024; reference = base,
    scoring = instruct, as in the repo's falcon-7b / falcon-7b-instruct setting) and
    Binoculars (Hans et al., ICML 2024; observer = base, performer = instruct)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    base_id, inst_id = LM_SIZES[size]
    tok = AutoTokenizer.from_pretrained(base_id)
    dtype = torch.float16 if device.type in ("mps", "cuda") else torch.float32
    base = AutoModelForCausalLM.from_pretrained(base_id, dtype=dtype).to(device).eval()
    inst = AutoModelForCausalLM.from_pretrained(inst_id, dtype=dtype).to(device).eval()

    def score_chunk(text: str) -> tuple[float, float, int]:
        ids = tok(text, return_tensors="pt").input_ids[:, :max_tokens].to(device)
        with torch.no_grad():
            lb = base(ids).logits[:, :-1].float()
            li = inst(ids).logits[:, :-1].float()
        labels = ids[:, 1:]
        # vocab sizes of base and instruct can differ in padding; align
        v = min(lb.shape[-1], li.shape[-1])
        lb, li = lb[..., :v], li[..., :v]
        # Fast-DetectGPT analytic: reference distribution = base, scoring log-probs = instruct
        lp_score = torch.log_softmax(li, -1)
        p_ref = torch.softmax(lb, -1)
        ll = lp_score.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
        mean_ref = (p_ref * lp_score).sum(-1)
        var_ref = (p_ref * lp_score.square()).sum(-1) - mean_ref.square()
        fdg = ((ll.sum() - mean_ref.sum()) / var_ref.sum().sqrt()).item()
        # Binoculars: log-ppl under performer / cross-perplexity(observer -> performer)
        ppl = -ll.mean()
        x_ppl = -(p_ref * lp_score).sum(-1).mean()
        bino = (ppl / x_ppl).item()
        return fdg, bino, labels.shape[1]

    fdgs, binos = [], []
    for p in paras:
        chunks = chunk_by_tokens(p, lambda t: len(tok(t).input_ids), max_tokens)
        rs = [score_chunk(c) for c in chunks]
        w = [r[2] for r in rs]
        fdgs.append(sum(r[0] * x for r, x in zip(rs, w)) / sum(w))
        binos.append(sum(r[1] * x for r, x in zip(rs, w)) / sum(w))
    del base, inst
    return fdgs, binos


# ---------------------------------------------------------------- main


def summarize(values, paras, threshold, higher_is_ai=True):
    lens = [len(p) for p in paras]
    flagged = [(v >= threshold) if higher_is_ai else (v <= threshold) for v in values]
    return {
        "mean": sum(values) / len(values),
        "mean_char_weighted": sum(v * n for v, n in zip(values, lens)) / sum(lens),
        "threshold": threshold,
        "direction": "higher=AI" if higher_is_ai else "lower=AI",
        "flagged_paragraphs": sum(flagged),
        "flagged_pct": 100.0 * sum(flagged) / len(values),
        "flagged_chars_pct": 100.0 * sum(n for f, n in zip(flagged, lens) if f) / sum(lens),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--detectors", default=None, help="comma list; default depends on --lang")
    ap.add_argument("--lang", default="auto", choices=["auto", "zh", "en"])
    ap.add_argument("--lm-size", default="1.5B", choices=list(LM_SIZES))
    ap.add_argument("--lm-max-tokens", type=int, default=512)
    ap.add_argument("--min-chars", type=int, default=40)
    ap.add_argument("--threshold", type=float, default=0.5, help="flag threshold for classifier P(AI)")
    ap.add_argument("--fdg-threshold", type=float, default=None)
    ap.add_argument("--bino-threshold", type=float, default=None)
    ap.add_argument("--rank-by", default=None, help="detector key to rank top-10 (default: first detector)")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all-paragraphs", action="store_true", help="print every paragraph row in text mode")
    a = ap.parse_args()

    default_fdg = {"1.5B": 0.72, "3B": 0.65}.get(a.lm_size, 0.0)
    default_bino = {"1.5B": 0.94, "3B": 0.95}.get(a.lm_size, 1.0)
    fdg_thr = a.fdg_threshold if a.fdg_threshold is not None else default_fdg
    bino_thr = a.bino_threshold if a.bino_threshold is not None else default_bino

    raw = read_input(a.file)
    lang = detect_lang(raw) if a.lang == "auto" else a.lang
    detectors = a.detectors or DEFAULT_DETECTORS[lang]
    paras, skipped = extract_paragraphs(raw, a.min_chars, lang)
    if not paras:
        sys.exit("no paragraphs found")
    device = pick_device(a.device)
    scores: dict[str, list[float]] = {}
    summary: dict[str, dict] = {}
    for d in [x.strip() for x in detectors.split(",") if x.strip()]:
        if d in POOLED:
            scores[d] = run_pooled(d, paras, device)
            summary[d] = summarize(scores[d], paras, a.threshold, True)
        elif d in CLASSIFIERS:
            scores[d] = run_classifier(d, paras, device)
            summary[d] = summarize(scores[d], paras, a.threshold, True)
        elif d == "lm":
            f, b = run_lm(paras, device, a.lm_size, a.lm_max_tokens)
            scores["fdg"], scores["bino"] = f, b
            summary["fdg"] = summarize(f, paras, fdg_thr, True)
            summary["bino"] = summarize(b, paras, bino_thr, False)
        else:
            sys.exit(f"unknown detector {d}")

    keys = list(scores)
    rank = a.rank_by or keys[0]
    sign = -1 if rank == "bino" else 1
    order = sorted(range(len(paras)), key=lambda i: -sign * scores[rank][i])[: a.top]
    rows = [
        {"idx": i + 1, "chars": len(p), **{k: round(scores[k][i], 4) for k in keys}, "head": p[:40]}
        for i, p in enumerate(paras)
    ]
    result = {
        "file": a.file,
        "lang": lang,
        "detectors": detectors,
        "paragraphs_scored": len(paras),
        "paragraphs_skipped_short": skipped,
        "chars_scored": sum(len(p) for p in paras),
        "lm_size": a.lm_size if "fdg" in scores else None,
        "device": str(device),
        "summary": summary,
        "top": [rows[i] for i in order],
        "rank_by": rank,
        "paragraphs": rows,
    }
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return

    print(f"{a.file}\n语言 {lang}，检测器 {detectors}\n段落 {len(paras)} 个（{result['chars_scored']} 字符），跳过短段 {skipped} 个，设备 {device}")
    for k, s in summary.items():
        print(
            f"  {k:10s} mean={s['mean']:.3f} weighted={s['mean_char_weighted']:.3f} "
            f"flagged={s['flagged_paragraphs']}/{len(paras)} ({s['flagged_pct']:.0f}% 段, "
            f"{s['flagged_chars_pct']:.0f}% 字) thr={s['threshold']} {s['direction']}"
        )
    hdr = "  ".join(f"{k:>7s}" for k in keys)
    print(f"\nTop {a.top} most AI-like by {rank}:\n  #   chars  {hdr}  text")
    for i in order:
        r = rows[i]
        vals = "  ".join(f"{r[k]:7.3f}" for k in keys)
        print(f"{r['idx']:4d} {r['chars']:6d}  {vals}  {r['head']}")
    if a.all_paragraphs:
        print(f"\nAll paragraphs:\n  #   chars  {hdr}  text")
        for r in rows:
            vals = "  ".join(f"{r[k]:7.3f}" for k in keys)
            print(f"{r['idx']:4d} {r['chars']:6d}  {vals}  {r['head']}")


if __name__ == "__main__":
    main()
