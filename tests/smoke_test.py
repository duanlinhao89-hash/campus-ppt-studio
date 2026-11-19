"""冒烟测试：端到端验证解析器与渲染引擎。

运行：python tests/smoke_test.py
"""

import os
import sys
import tempfile

# 让脚本能 import 到包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from campus_ppt.parser import parse
from campus_ppt.builder import build_deck
from campus_ppt.themes import THEMES, list_themes
from campus_ppt.scenes import SCENES

from pptx import Presentation

SAMPLE = """---
title: 测试演示
author: 测试作者
theme: academic
---

@cover
# 测试标题
副标题

@toc
- 第一项
- 第二项

@content
## 内容页
- 要点一
- 要点二

@stats
## 数据页
- 95% | 准确率

@timeline
## 时间轴
- 阶段一 | 做了什么

@two_col
## 双栏
@left
- 左一
@right
- 右一

@quote
测试金句
— 出处

@thanks
## 谢谢
"""


def check(cond, msg):
    if cond:
        print(f"  ✓ {msg}")
    else:
        raise AssertionError(msg)


def main():
    print("=== 解析器测试 ===")
    deck = parse(SAMPLE, fmt="markdown")
    check(len(deck.slides) == 8, f"解析出 8 页（实际 {len(deck.slides)}）")
    check(deck.meta.get("theme") == "academic", "主题元数据解析正确")
    check(deck.slides[0].layout == "cover", "封面布局识别正确")
    check(len(deck.slides[5].right_items) == 1, "双栏右列解析正确")

    print("\n=== 渲染测试 ===")
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "out.pptx")
        build_deck(deck, out)
        check(os.path.getsize(out) > 5000, "PPTX 文件已生成")
        prs = Presentation(out)
        check(len(prs.slides) == 8, "PPTX 含 8 页")
        ratio = prs.slide_width / prs.slide_height
        check(abs(ratio - 16 / 9) < 0.01, "画布为 16:9")

        editable = 0
        pictures = 0
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.shape_type == 13:
                    pictures += 1
                if shape.has_text_frame and shape.text_frame.text.strip():
                    editable += 1
        check(editable > 15, f"含 {editable} 个可编辑文字对象")
        check(pictures == 0, "无整页图片")

    print("\n=== 场景与主题测试 ===")
    check(len(SCENES) == 4, "4 个场景模板")
    check(len(THEMES) == 4, "4 套主题")
    check(len(list_themes()) == 4, "主题列表接口正常")

    print("\n全部通过 ✓")


if __name__ == "__main__":
    main()
