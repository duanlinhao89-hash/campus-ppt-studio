"""大纲解析器。

把一份轻量 Markdown 大纲，解析成构建器可用的 Deck 数据结构。

大纲语法（示例）：
    ---
    title: 我的毕业答辩
    theme: academic
    author: 张三
    date: 2026 年 5 月
    subtitle: 某课题的研究与实践
    ---

    @cover
    # 基于深度学习的图像识别研究
    张三 · 计算机学院

    @toc
    - 研究背景
    - 方法设计
    - 实验结果

    @content
    ## 研究背景
    - 痛点一：人工识别效率低
    - 痛点二：准确率不足

    @stats
    ## 实验结果
    - 96.5% | 准确率
    - 3.2x  | 推理提速

    @thanks
    ## 谢谢观看

支持的布局指令（@xxx）：
    cover / toc / section / content / two_col / stats / timeline / quote / thanks
"""

import json
import re
from dataclasses import dataclass, field

# 合法的布局指令
VALID_LAYOUTS = {
    "cover", "toc", "section", "content", "two_col",
    "stats", "timeline", "quote", "thanks",
}

LAYOUT_DEFAULT = "content"


@dataclass
class Slide:
    """一页幻灯片。"""
    layout: str
    title: str = ""
    subtitle: str = ""
    bullets: list = field(default_factory=list)
    left_title: str = ""
    left_items: list = field(default_factory=list)
    right_title: str = ""
    right_items: list = field(default_factory=list)
    stats: list = field(default_factory=list)       # [(value, label), ...]
    timeline: list = field(default_factory=list)    # [(time, text), ...]
    quote: str = ""
    attribution: str = ""
    note: str = ""


@dataclass
class Deck:
    """一份演示文稿。"""
    meta: dict
    slides: list = field(default_factory=list)


def _strip_inline(text):
    """去掉行内强调符号（** / __ / `），保留纯文字。"""
    text = re.sub(r"[*_`]{1,2}", "", text)
    return text.strip()


def _parse_frontmatter(lines):
    """解析开头的 --- ... --- 元数据块，返回 (meta, 剩余行)。"""
    meta = {}
    if not lines or lines[0].strip() != "---":
        return meta, lines
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return meta, lines
    for line in lines[1:end]:
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
    return meta, lines[end + 1:]


def _new_slide(layout):
    return Slide(layout=layout)


def parse_markdown(text):
    """解析 Markdown 大纲文本为 Deck。"""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    meta, lines = _parse_frontmatter(lines)

    slides = []
    current = None
    # two_col 的列切换标记
    in_right = False
    # quote 布局允许多行正文
    quote_lines = []

    def flush_quotes():
        nonlocal quote_lines, current
        if quote_lines and current is not None:
            current.quote = " ".join(q.strip() for q in quote_lines if q.strip())
            quote_lines = []

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        # 空行跳过
        if not stripped:
            continue

        # 注释跳过
        if stripped.startswith("<!--") or stripped.startswith("//"):
            continue

        # 布局指令 @layout
        if stripped.startswith("@"):
            directive = stripped[1:].strip().lower()
            # 支持 @two_col 里的列切换 @right，@left
            if directive == "right":
                in_right = True
                continue
            if directive == "left":
                in_right = False
                continue
            flush_quotes()
            if current is not None:
                slides.append(current)
            layout = directive if directive in VALID_LAYOUTS else LAYOUT_DEFAULT
            current = _new_slide(layout)
            in_right = False
            continue

        # 若还没有任何 @ 指令，第一段文字自动开一页 content
        if current is None:
            current = _new_slide(LAYOUT_DEFAULT)

        # 标题：# 或 ##
        if stripped.startswith("#"):
            flush_quotes()
            title = _strip_inline(re.sub(r"^#+\s*", "", stripped))
            if not current.title:
                current.title = title
            elif current.layout == "quote":
                quote_lines.append(title)
            else:
                current.subtitle = title
            continue

        # 列表项
        if stripped.startswith("- ") or stripped.startswith("* "):
            flush_quotes()
            item = _strip_inline(stripped[2:])
            # stats: "值 | 标签"
            if current.layout == "stats" and "|" in item:
                value, label = item.split("|", 1)
                current.stats.append((value.strip(), label.strip()))
            # timeline: "时间 | 事件"
            elif current.layout == "timeline" and "|" in item:
                when, what = item.split("|", 1)
                current.timeline.append((when.strip(), what.strip()))
            # two_col 用 @right 切列
            elif current.layout == "two_col" and in_right:
                current.right_items.append(item)
            else:
                current.bullets.append(item)
            continue

        # quote 正文多行累积
        if current.layout == "quote":
            quote_lines.append(_strip_inline(stripped))
            continue

        # section 布局：非标题文字作为副标题
        if current.layout == "section" and not current.subtitle:
            current.subtitle = _strip_inline(stripped)
            continue

        # 普通文字：第一条作为副标题/署名，之后作为要点
        if not current.subtitle and current.layout in ("cover", "thanks"):
            current.subtitle = _strip_inline(stripped)
        elif not current.subtitle and current.layout in ("section",):
            current.subtitle = _strip_inline(stripped)
        else:
            current.bullets.append(_strip_inline(stripped))

    flush_quotes()
    if current is not None:
        slides.append(current)

    # 若完全没写 @ 指令但用了 ## 分节，做一个兜底：按 ## 拆页
    if len(slides) == 1 and not any(
        ln.strip().startswith("@") for ln in lines
    ):
        slides = _fallback_split_slides(lines, meta)

    return Deck(meta=meta, slides=slides)


def _fallback_split_slides(lines, meta):
    """用户没写 @ 指令时，按 ## 标题拆成 content 页。"""
    slides = []
    current = None
    for raw in lines:
        s = raw.strip()
        if not s or s == "---" or (":" in s and current is None):
            continue
        if s.startswith("## ") or s.startswith("# "):
            if current:
                slides.append(current)
            current = _new_slide(LAYOUT_DEFAULT)
            current.title = _strip_inline(re.sub(r"^#+\s*", "", s))
            continue
        if s.startswith(("- ", "* ")):
            if current is None:
                current = _new_slide(LAYOUT_DEFAULT)
            current.bullets.append(_strip_inline(s[2:]))
            continue
        if current is not None:
            current.bullets.append(_strip_inline(s))
    if current:
        slides.append(current)
    return slides or [_new_slide(LAYOUT_DEFAULT)]


def parse_json(text):
    """解析 JSON 大纲（供程序化调用）。"""
    obj = json.loads(text)
    meta = obj.get("meta", {})
    slides = []
    for item in obj.get("slides", []):
        s = _new_slide(item.get("layout", LAYOUT_DEFAULT))
        for key in (
            "title", "subtitle", "left_title", "right_title",
            "quote", "attribution", "note",
        ):
            if key in item:
                setattr(s, key, item[key])
        for key in (
            "bullets", "left_items", "right_items", "stats", "timeline",
        ):
            if key in item:
                setattr(s, key, item[key])
        slides.append(s)
    return Deck(meta=meta, slides=slides)


def parse(text, fmt="markdown"):
    """统一解析入口。fmt: markdown / json / auto。"""
    if fmt == "auto":
        fmt = "json" if text.lstrip().startswith("{") else "markdown"
    if fmt == "json":
        return parse_json(text)
    return parse_markdown(text)
