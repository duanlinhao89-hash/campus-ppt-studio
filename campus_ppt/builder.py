"""PPTX 渲染引擎。

把 Deck 数据结构渲染为原生可编辑的 .pptx。
所有文字、形状、色块都是 PowerPoint 对象——打开后可逐个元素点选、修改、拖动，
而不是整页图片。

依赖：python-pptx（唯一第三方依赖）。
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

from .parser import Deck
from .themes import Theme, get_theme

# 16:9 画布
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def _rgb(hex_color):
    """hex 字符串转 RGBColor，兼容带/不带 #。"""
    h = hex_color.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class Builder:
    """把 Deck 渲染为 PPTX。"""

    def __init__(self, deck, theme=None):
        if not isinstance(deck, Deck):
            raise TypeError("deck 必须是 Deck 实例")
        self.deck = deck
        theme_key = deck.meta.get("theme", "")
        self.theme = theme if theme is not None else get_theme(theme_key)
        self.prs = Presentation()
        self.prs.slide_width = SLIDE_W
        self.prs.slide_height = SLIDE_H
        self.blank = self.prs.slide_layouts[6]
        self._page = 0
        self._total = len(deck.slides)

    # ---------- 底层绘制原语 ----------

    def _add_slide(self, bg=None):
        slide = self.prs.slides.add_slide(self.blank)
        self._page += 1
        color = bg or self.theme.bg
        bgfill = slide.background.fill
        bgfill.solid()
        bgfill.fore_color.rgb = _rgb(color)
        return slide

    def _rect(self, slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE):
        sp = slide.shapes.add_shape(shape, x, y, w, h)
        sp.fill.solid()
        sp.fill.fore_color.rgb = _rgb(fill)
        if line:
            sp.line.color.rgb = _rgb(line)
            sp.line.width = Pt(1)
        else:
            sp.line.fill.background()
        sp.shadow.inherit = False
        return sp

    def _textbox(self, slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
        box = slide.shapes.add_textbox(x, y, w, h)
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = 0
        tf.margin_right = 0
        tf.margin_top = 0
        tf.margin_bottom = 0
        return box, tf

    def _set_run(self, run, size, color, bold=False, font=None, italic=False):
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = _rgb(color)
        run.font.name = font or self.theme.en_font
        # 中文字体需要写入 eastAsia 属性
        rPr = run._r.get_or_add_rPr()
        ea = rPr.find(qn("a:ea"))
        if ea is None:
            ea = rPr.makeelement(qn("a:ea"), {})
            rPr.append(ea)
        ea.set("typeface", font or self.theme.cn_font)

    def _para(self, tf, text, size, color, bold=False, align=PP_ALIGN.LEFT,
              space_before=0, space_after=6, font=None, first=False,
              line_spacing=1.2, italic=False):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        p.alignment = align
        p.space_before = Pt(space_before)
        p.space_after = Pt(space_after)
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = text
        self._set_run(r, size, color, bold=bold, font=font, italic=italic)
        return p

    def _page_number(self, slide):
        """右下角页码（封面/致谢不显示时由调用方决定）。"""
        box, tf = self._textbox(
            slide, Inches(12.3), Inches(7.0), Inches(0.7), Inches(0.35),
            anchor=MSO_ANCHOR.MIDDLE,
        )
        self._para(
            tf, f"{self._page:02d}", 10, self.theme.muted,
            align=PP_ALIGN.RIGHT, first=True, space_after=0,
        )

    def _footer(self, slide, text=None):
        footer = text or self.deck.meta.get("footer", "")
        if not footer:
            return
        box, tf = self._textbox(
            slide, Inches(0.6), Inches(7.0), Inches(9.0), Inches(0.35),
            anchor=MSO_ANCHOR.MIDDLE,
        )
        self._para(tf, footer, 9.5, self.theme.muted, first=True, space_after=0)

    def _section_tag(self, slide, text):
        """页眉小标签：强调色短线 + 文字。"""
        self._rect(slide, Inches(0.62), Inches(0.52), Inches(0.34), Pt(3.2),
                   self.theme.accent)
        box, tf = self._textbox(
            slide, Inches(1.06), Inches(0.4), Inches(10), Inches(0.4),
            anchor=MSO_ANCHOR.MIDDLE,
        )
        self._para(tf, text, 11, self.theme.muted, bold=True, first=True,
                   space_after=0)

    # ---------- 各布局 ----------

    def layout_cover(self, s):
        slide = self._add_slide(bg=self.theme.primary)
        # 顶部细装饰条
        self._rect(slide, Inches(0.9), Inches(1.5), Inches(1.1), Pt(4),
                   self.theme.accent)
        title = s.title or self.deck.meta.get("title", "演示标题")
        box, tf = self._textbox(
            slide, Inches(0.9), Inches(2.0), Inches(11.5), Inches(2.6),
            anchor=MSO_ANCHOR.MIDDLE,
        )
        self._para(tf, title, 40, self.theme.on_primary, bold=True,
                   first=True, space_after=10, line_spacing=1.18)
        subtitle = s.subtitle or self.deck.meta.get("subtitle", "")
        if subtitle:
            self._para(tf, subtitle, 17, self.theme.on_primary,
                       space_after=0, line_spacing=1.3)
        # 底部信息行
        info_parts = [
            self.deck.meta.get("author", ""),
            self.deck.meta.get("date", ""),
        ]
        info = "   ·   ".join(p for p in info_parts if p)
        if info:
            box2, tf2 = self._textbox(
                slide, Inches(0.92), Inches(6.2), Inches(11), Inches(0.5),
            )
            self._para(tf2, info, 13, self.theme.on_primary, first=True,
                       space_after=0)

    def layout_toc(self, s):
        slide = self._add_slide()
        title = s.title or "目录"
        self._section_tag(slide, "CONTENTS")
        box, tf = self._textbox(slide, Inches(0.6), Inches(0.95),
                                Inches(11), Inches(0.9))
        self._para(tf, title, 30, self.theme.ink, bold=True, first=True,
                   space_after=0)
        items = s.bullets or []
        n = max(1, len(items))
        top = 2.15
        gap = min(0.92, 4.6 / n)
        for i, item in enumerate(items, 1):
            y = Inches(top + (i - 1) * gap)
            # 序号色块
            self._rect(slide, Inches(0.65), y, Inches(0.52), Inches(0.52),
                       self.theme.accent, shape=MSO_SHAPE.OVAL)
            nb, ntf = self._textbox(
                slide, Inches(0.65), y, Inches(0.52), Inches(0.52),
                anchor=MSO_ANCHOR.MIDDLE,
            )
            self._para(ntf, str(i), 16, "FFFFFF", bold=True, first=True,
                       align=PP_ALIGN.CENTER, space_after=0)
            tb, ttf = self._textbox(
                slide, Inches(1.4), y, Inches(10.5), Inches(0.52),
                anchor=MSO_ANCHOR.MIDDLE,
            )
            self._para(ttf, item, 19, self.theme.ink, first=True, space_after=0)
        self._footer(slide)
        self._page_number(slide)

    def layout_section(self, s):
        slide = self._add_slide(bg=self.theme.primary)
        # 左侧竖向强调条 + 大号半透明数字装饰
        self._rect(slide, Inches(0.9), Inches(2.0), Pt(4), Inches(2.4),
                   self.theme.accent)
        deco, dtf = self._textbox(
            slide, Inches(9.6), Inches(0.6), Inches(3.4), Inches(4.5),
            anchor=MSO_ANCHOR.MIDDLE,
        )
        digits = "".join(ch for ch in (s.title or "") if ch.isdigit())
        if digits:
            self._para(dtf, digits[:2], 150, self.theme.accent, bold=True,
                       first=True, align=PP_ALIGN.RIGHT, space_after=0)
        # 大号章节标题
        box, tf = self._textbox(
            slide, Inches(1.2), Inches(2.0), Inches(8.2), Inches(2.5),
            anchor=MSO_ANCHOR.MIDDLE,
        )
        self._para(tf, s.title or "", 40, self.theme.on_primary, bold=True,
                   first=True, space_after=12, line_spacing=1.15)
        if s.subtitle:
            self._para(tf, s.subtitle, 18, self.theme.on_primary,
                       space_after=0)

    def layout_content(self, s):
        slide = self._add_slide()
        self._section_tag(slide, self.deck.meta.get("section_label", ""))
        box, tf = self._textbox(slide, Inches(0.6), Inches(0.95),
                                Inches(12), Inches(0.9))
        self._para(tf, s.title, 30, self.theme.ink, bold=True, first=True,
                   space_after=0)
        # 标题下短横线
        self._rect(slide, Inches(0.62), Inches(1.82), Inches(0.7), Pt(3),
                   self.theme.accent)
        items = s.bullets or []
        if not items:
            self._footer(slide)
            self._page_number(slide)
            return
        top = 2.25
        n = len(items)
        avail = 4.5
        gap = min(0.82, avail / n)
        font_size = 17 if n <= 7 else (15 if n <= 9 else 13)
        for i, item in enumerate(items):
            y = Inches(top + i * gap)
            # 圆点
            self._rect(slide, Inches(0.68), y + Inches(0.13), Inches(0.12),
                       Inches(0.12), self.theme.accent, shape=MSO_SHAPE.OVAL)
            tb, ttf = self._textbox(
                slide, Inches(1.0), y, Inches(11.4), Inches(gap - 0.08),
                anchor=MSO_ANCHOR.MIDDLE,
            )
            self._para(ttf, item, font_size, self.theme.ink, first=True,
                       space_after=0, line_spacing=1.25)
        self._footer(slide)
        self._page_number(slide)

    def layout_two_col(self, s):
        slide = self._add_slide()
        self._section_tag(slide, self.deck.meta.get("section_label", ""))
        box, tf = self._textbox(slide, Inches(0.6), Inches(0.95),
                                Inches(12), Inches(0.9))
        self._para(tf, s.title, 30, self.theme.ink, bold=True, first=True,
                   space_after=0)
        self._rect(slide, Inches(0.62), Inches(1.82), Inches(0.7), Pt(3),
                   self.theme.accent)
        col_w = Inches(5.85)
        cols = [
            (Inches(0.62), s.left_title or "要点", s.left_items, self.theme.accent),
            (Inches(6.86), s.right_title or "说明", s.right_items, self.theme.muted),
        ]
        for x, heading, items, color in cols:
            # 卡片底
            self._rect(slide, x, Inches(2.25), col_w, Inches(4.5),
                       self.theme.surface)
            self._rect(slide, x, Inches(2.25), col_w, Pt(3.5), color)
            hb, htf = self._textbox(slide, x + Inches(0.3), Inches(2.5),
                                    col_w - Inches(0.6), Inches(0.55))
            self._para(htf, heading, 17, color, bold=True, first=True,
                       space_after=0)
            cb, ctf = self._textbox(slide, x + Inches(0.3), Inches(3.15),
                                    col_w - Inches(0.6), Inches(3.4))
            for j, item in enumerate(items):
                self._para(ctf, "•  " + item, 14.5, self.theme.ink,
                           first=(j == 0), space_after=11, line_spacing=1.3)
        self._footer(slide)
        self._page_number(slide)

    def layout_stats(self, s):
        slide = self._add_slide()
        self._section_tag(slide, self.deck.meta.get("section_label", ""))
        box, tf = self._textbox(slide, Inches(0.6), Inches(0.95),
                                Inches(12), Inches(0.9))
        self._para(tf, s.title, 30, self.theme.ink, bold=True, first=True,
                   space_after=0)
        self._rect(slide, Inches(0.62), Inches(1.82), Inches(0.7), Pt(3),
                   self.theme.accent)
        stats = s.stats or [
            (it.split("|")[0].strip(), it.split("|")[1].strip())
            if "|" in it else (it, "")
            for it in s.bullets
        ]
        n = max(1, len(stats))
        gap = Inches(0.3)
        total_w = SLIDE_W - Inches(1.24) - gap * (n - 1)
        card_w = int(total_w / n)
        for i, (value, label) in enumerate(stats):
            x = int(Inches(0.62) + i * (card_w + gap))
            self._rect(slide, x, Inches(2.5), card_w, Inches(3.3),
                       self.theme.surface)
            vb, vtf = self._textbox(
                slide, x, Inches(3.0), card_w, Inches(1.4),
                anchor=MSO_ANCHOR.MIDDLE,
            )
            vtext = value if isinstance(value, str) else str(value)
            vlen = len(vtext)
            self._para(vtf, vtext, 34 if vlen <= 6 else 24, self.theme.accent,
                       bold=True, first=True, align=PP_ALIGN.CENTER,
                       space_after=0)
            lb, ltf = self._textbox(
                slide, x + Inches(0.15), Inches(4.5), card_w - Inches(0.3),
                Inches(0.9), anchor=MSO_ANCHOR.TOP,
            )
            self._para(ltf, label, 14, self.theme.ink,
                       first=True, align=PP_ALIGN.CENTER, space_after=0)
        self._footer(slide)
        self._page_number(slide)

    def layout_timeline(self, s):
        slide = self._add_slide()
        self._section_tag(slide, self.deck.meta.get("section_label", ""))
        box, tf = self._textbox(slide, Inches(0.6), Inches(0.95),
                                Inches(12), Inches(0.9))
        self._para(tf, s.title, 30, self.theme.ink, bold=True, first=True,
                   space_after=0)
        self._rect(slide, Inches(0.62), Inches(1.82), Inches(0.7), Pt(3),
                   self.theme.accent)
        items = s.timeline or []
        n = max(1, len(items))
        # 水平轴线（居中偏上）
        axis_y = Inches(3.5)
        self._rect(slide, Inches(0.9), axis_y - Pt(1), Inches(11.5), Pt(2),
                   self.theme.surface)
        seg = 11.0 / n
        for i, (when, what) in enumerate(items):
            cx = Inches(1.0 + i * seg)
            # 节点圆
            self._rect(slide, cx, axis_y - Inches(0.12), Inches(0.24),
                       Inches(0.24), self.theme.accent, shape=MSO_SHAPE.OVAL)
            # 时间（轴上方）
            tb, ttf = self._textbox(slide, cx - Inches(0.75),
                                    axis_y - Inches(1.1), Inches(1.8),
                                    Inches(0.7), anchor=MSO_ANCHOR.BOTTOM)
            self._para(ttf, when, 15, self.theme.accent, bold=True, first=True,
                       align=PP_ALIGN.CENTER, space_after=0)
            # 事件（轴下方）
            eb, etf = self._textbox(slide, cx - Inches(0.75),
                                    axis_y + Inches(0.35), Inches(1.85),
                                    Inches(2.2), anchor=MSO_ANCHOR.TOP)
            self._para(etf, what, 13, self.theme.ink, first=True,
                       align=PP_ALIGN.CENTER, space_after=0, line_spacing=1.3)
        self._footer(slide)
        self._page_number(slide)

    def layout_quote(self, s):
        slide = self._add_slide(bg=self.theme.surface)
        # 大引号
        qb, qtf = self._textbox(slide, Inches(1.0), Inches(1.4),
                                Inches(2), Inches(1.2))
        self._para(qtf, "\u201C", 90, self.theme.accent, bold=True, first=True,
                   space_after=0)
        quote = s.quote or s.title
        ob, otf = self._textbox(slide, Inches(1.2), Inches(2.6),
                                Inches(10.9), Inches(2.6),
                                anchor=MSO_ANCHOR.MIDDLE)
        self._para(otf, quote, 28, self.theme.ink, first=True, space_after=0,
                   line_spacing=1.5, italic=True)
        if s.attribution:
            ab, atf = self._textbox(slide, Inches(1.25), Inches(5.6),
                                    Inches(10), Inches(0.6))
            self._para(atf, "—  " + s.attribution, 15, self.theme.muted,
                       first=True, space_after=0)

    def layout_thanks(self, s):
        slide = self._add_slide(bg=self.theme.primary)
        self._rect(slide, Inches(0.9), Inches(2.2), Inches(1.1), Pt(4),
                   self.theme.accent)
        box, tf = self._textbox(
            slide, Inches(0.9), Inches(2.6), Inches(11.5), Inches(2.2),
            anchor=MSO_ANCHOR.MIDDLE,
        )
        title = s.title or "谢谢观看"
        self._para(tf, title, 44, self.theme.on_primary, bold=True, first=True,
                   space_after=12)
        if s.subtitle:
            self._para(tf, s.subtitle, 17, self.theme.on_primary, space_after=0)

    LAYOUTS = {
        "cover": layout_cover,
        "toc": layout_toc,
        "section": layout_section,
        "content": layout_content,
        "two_col": layout_two_col,
        "stats": layout_stats,
        "timeline": layout_timeline,
        "quote": layout_quote,
        "thanks": layout_thanks,
    }

    def build(self):
        """渲染全部幻灯片，返回 Presentation 对象。"""
        if not self.deck.slides:
            raise ValueError("大纲里没有任何幻灯片")
        for s in self.deck.slides:
            renderer = self.LAYOUTS.get(s.layout, self.layout_content)
            renderer(self, s)
        return self.prs

    def save(self, path):
        """渲染并保存到 path。"""
        prs = self.build()
        prs.save(path)
        return path


def build_deck(deck, output, theme=None):
    """便捷函数：Deck -> .pptx 文件。"""
    return Builder(deck, theme=theme).save(output)
