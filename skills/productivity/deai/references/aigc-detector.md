# 本地 AIGC 检测器

`scripts/aigc_detect.py` 给中文或英文文稿（.md、.txt、.docx）逐段打 AI 概率分。`--lang auto` 按汉字占比（≥30% 判为中文）选检测器组。它是口味参考，和知网、维普、PaperPass、Turnitin 没有换算关系。本地低分不代表送检低分。

## 安装

Python 解释器按这个顺序找（`scripts/aigc` 包装脚本已实现）：

1. 环境变量 `AIGC_PY`。已有装好 torch 和 transformers 的虚拟环境就指过去。
2. `~/.cache/deai/venv/bin/python`（`DEAI_VENV` 可改位置）。

两者都没有时，新建：

```bash
uv venv ~/.cache/deai/venv --python 3.12
uv pip install --python ~/.cache/deai/venv/bin/python torch transformers accelerate huggingface_hub
# 首次运行联网下载权重，缓存到 ~/.cache/huggingface/hub。默认中文两个检测器约 0.8 GB，英文两个（desklib、mpu-en）约 2.2 GB
AIGC_ONLINE=1 $S/scripts/aigc FILE.md
```

脚本平时以 `HF_HUB_OFFLINE=1` 运行，避免每次联网检查卡住。换新检测器时加 `AIGC_ONLINE=1` 跑一次。

## 运行

```bash
$S/scripts/aigc FILE.md                         # 默认 mpu + mpu-short，每 1.4 万字约 10 秒（Apple Silicon MPS）
$S/scripts/aigc FILE.md --json
$S/scripts/aigc FILE.md --all-paragraphs        # 打印每段分数
$S/scripts/aigc FILE.md > out/aigc-r3.txt        # 给 judge 读
```

预处理：删 Markdown 标题、表格、图片行、表题图题、"资料来源：""注："行、HTML 注释、代码块、〔REF:…〕和 [n] 引文标记；按空行分段；短于 40 字的段落跳过；超过 512 token 的段落按句切块，按长度加权平均。

## 检测器

| 键 | 模型 | 结论 |
|---|---|---|
| mpu | yuchuantian/AIGC_detector_zhv3（2025-06，训练语料含 DeepSeek-V3、GPT-4-Turbo、Qwen2.5-72B 和推理模型） | 主判据。唯一能分开 AI 稿和人写稿的开源中文模型 |
| mpu-short | yuchuantian/AIGC_detector_zhv3short | 第二意见，100 字以下的短段用它复核 |
| mpu-v2、hc3 | 2023 年的模型 | 对当前 AI 稿全打 0，已失效 |
| anx | AnxForever/chinese-ai-detector-bert | 分离度弱（AI 稿 20%，人工 4% 至 9%） |
| lm | Qwen2.5 基座 + 指令版上的 Fast-DetectGPT 和 Binoculars | 对 Qwen 自己生成的文本有效，对其他模型起草的稿子方向相反。只作对照 |
| desklib | desklib/ai-text-detector-v1.01（DeBERTa-v3-large，RAID 榜第一） | 英文主判据。人写求职信和 AI 求职信分得开 |
| mpu-en | yuchuantian/AIGC_detector_env3 | 英文第二意见。对正式英文误报高 |
| vanguard | ShantanuT01/vanguard-ai-text-detector（ModernBERT-large，PAN-CLEF 2026） | 已接入，未校准 |
| hc3-en | Hello-SimpleAI/chatgpt-detector-roberta（2023） | 对当前 AI 稿基本打 0，已失效，只作对照 |

## 怎么读数

看整篇"超阈值段落比例"（mpu，阈值 0.5），不看单段。

校准数据（mpu，标为 AI 的段落比例）：

| 样本 | 比例 |
|---|---:|
| ChatGPT 发布前答辩的人写 MBA 论文三篇（2022，共 195 段） | 18%、31%、44% |
| 代理起草、未改写的章节 | 70% 至 90% |
| 经过本 skill 循环改写的章节 | 0% 至 9% |

人写论文里被打高分的多是区位、政策、租金这类说明性文字。三篇人写论文合计在阈值 0.5 下误报 28%，阈值 0.9 下约 13%。

目标：mpu 段落比例 ≤10%。这是口味参照：低于人写基线，说明文本已经离开了典型 AI 腔。它本身不是目标。分数下降应当来自补具体对象、真实数据和访谈细节，不能来自为了骗过模型的同义替换或口语化。

## 英文读数

默认检测器组 `desklib,mpu-en`。校准（2026-10-02，阈值 0.5，段均分）：

| 样本 | desklib | mpu-en |
|---|---:|---:|
| 人写求职信，Harvard OCS 指南 2017、2019 年范例 6 篇 | 0.19 至 0.50，其中 1 篇 1.00 | 0.41 至 1.00 |
| 人写央行演讲（Yellen 2015、Powell 2018、BIS 2017） | 0.86、0.59、0.40 | 0.63、0.60、0.38 |
| 人写央行招聘启事 1 篇 | 0.68 | 0.87 |
| Claude 起草的求职信两版 | 0.64、0.39 | 0.96、0.99 |
| Gemini 起草的求职信 | 0.96，每段 ≥0.79 | 1.00 |

读法：
- 求职信这类文体用 desklib。人写范例 6 篇里 5 篇均分 ≤0.50；Gemini 稿 0.96。
- mpu-en 对人写求职信也常给 0.8 以上，单独用分不开，只作第二意见。
- 两个检测器都给每段 0.99 以上，基本可以判为 AI 腔。
- hc3-en、fdg、bino 在这组样本上分不开，Binoculars 把 Gemini 稿判得比人写稿更像人。

## 局限

1. 段落越短越不稳。
2. 人工对照只有三篇论文，从 PDF 抽取重排，可能残留噪声。
3. 零样本方法依赖打分模型和起草模型同源。1.5B 和 3B 都失败，7B 未测。
4. 英文校准：人写求职信 6 篇（从 PDF 抽取，分段少），演讲 3 篇，启事 1 篇。样本小，结论只作参考，配合 judge 用。
