"""配色主题系统。

每个主题定义一套克制的配色与字体。所有颜色用 6 位 hex（不带 # 前缀也可，
内部会统一处理）。设计原则：一套演示只用一个主色 + 一个强调色 + 中性色。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """一套演示主题。

    primary:   主色（封面大色块、章节页背景）
    accent:    强调色（标题装饰条、关键数字、序号）
    ink:       正文深色
    muted:     辅助灰（副标题、页脚、图注）
    bg:        页面背景（默认近白）
    surface:   浅色卡片底
    on_primary:主色背景上的文字色
    cn_font:   中文字体
    en_font:   英文字体
    """

    key: str
    name: str
    description: str
    primary: str
    accent: str
    ink: str
    muted: str
    bg: str
    surface: str
    on_primary: str
    cn_font: str = "微软雅黑"
    en_font: str = "Calibri"


THEMES = {
    "academic": Theme(
        key="academic",
        name="学术蓝",
        description="沉稳、可信，适合毕业答辩与学术汇报",
        primary="1F3A5F",
        accent="2E6FB7",
        ink="1B2430",
        muted="6B7787",
        bg="FFFFFF",
        surface="F2F6FB",
        on_primary="FFFFFF",
    ),
    "vital": Theme(
        key="vital",
        name="活力橙",
        description="明快、有感染力，适合社团与班级活动",
        primary="C85A17",
        accent="E8873A",
        ink="2B211B",
        muted="8A7A6E",
        bg="FFFDF9",
        surface="FDF1E7",
        on_primary="FFFFFF",
    ),
    "fresh": Theme(
        key="fresh",
        name="清新绿",
        description="自然、清爽，适合教学课件与科普",
        primary="1E6B54",
        accent="3FA07C",
        ink="1B2B26",
        muted="6E847C",
        bg="FCFFFD",
        surface="EDF7F2",
        on_primary="FFFFFF",
    ),
    "ink": Theme(
        key="ink",
        name="墨韵灰",
        description="克制、高级，适合说课与正式汇报",
        primary="2E3338",
        accent="B4472F",
        ink="202429",
        muted="7C848C",
        bg="FFFFFF",
        surface="F3F4F5",
        on_primary="FFFFFF",
    ),
}


def get_theme(key):
    """按 key 取主题，找不到时回退到学术蓝。"""
    return THEMES.get((key or "").lower(), THEMES["academic"])


def list_themes():
    """返回可展示的主题摘要列表。"""
    return [
        {
            "key": t.key,
            "name": t.name,
            "description": t.description,
        }
        for t in THEMES.values()
    ]
