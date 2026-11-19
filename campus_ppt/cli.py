"""命令行入口。

用法：
    python -m campus_ppt build 大纲.md -o 输出.pptx
    python -m campus_ppt build 大纲.md -o 输出.pptx --theme fresh
    python -m campus_ppt themes
    python -m campus_ppt init --scene thesis -o 我的答辩.md
"""

import argparse
import os
import sys

from . import __version__
from .parser import parse
from .builder import build_deck
from .themes import get_theme, list_themes
from .scenes import SCENES, get_scene, render_scene_template


def cmd_build(args):
    if not os.path.exists(args.input):
        print(f"错误：找不到大纲文件 {args.input}", file=sys.stderr)
        return 1
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()
    try:
        deck = parse(text, fmt=args.format)
    except Exception as e:
        print(f"错误：解析大纲失败 —— {e}", file=sys.stderr)
        return 1
    # 命令行主题覆盖大纲里的设定
    if args.theme:
        deck.meta["theme"] = args.theme
    if args.author:
        deck.meta["author"] = args.author
    if args.date:
        deck.meta["date"] = args.date
    if args.title:
        deck.meta["title"] = args.title

    out = args.output
    if not out:
        base = os.path.splitext(os.path.basename(args.input))[0]
        out = base + ".pptx"
    outdir = os.path.dirname(os.path.abspath(out))
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)
    try:
        build_deck(deck, out)
    except Exception as e:
        print(f"错误：生成 PPTX 失败 —— {e}", file=sys.stderr)
        return 1
    theme = get_theme(deck.meta.get("theme", ""))
    print(f"✓ 生成成功：{out}")
    print(f"  幻灯片 {len(deck.slides)} 页  ·  主题「{theme.name}」")
    print("  所有文字/形状均为原生可编辑对象，可在 PowerPoint 中直接修改。")
    return 0


def cmd_themes(args):
    print("可用主题：\n")
    for t in list_themes():
        print(f"  {t['key']:<10} {t['name']:<8} {t['description']}")
    print("\n用法：python -m campus_ppt build 大纲.md -o 输出.pptx --theme fresh")
    return 0


def cmd_scenes(args):
    print("内置场景模板：\n")
    for key, scene in SCENES.items():
        print(f"  {key:<12} {scene['name']}")
        print(f"               {scene['description']}")
    print("\n用法：python -m campus_ppt init --scene thesis -o 我的答辩.md")
    return 0


def cmd_init(args):
    scene = get_scene(args.scene)
    content = render_scene_template(scene)
    out = args.output or f"{args.scene}_大纲.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ 已生成 {scene['name']} 大纲模板：{out}")
    print(f"  用文本编辑器打开、替换括号内容，然后运行：")
    print(f"  python -m campus_ppt build {out} -o 我的演示.pptx")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="campus_ppt",
        description="校园演示工坊：把结构化大纲变成原生可编辑的 PPTX",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command")

    b = sub.add_parser("build", help="根据大纲生成 PPTX")
    b.add_argument("input", help="大纲文件（.md / .json）")
    b.add_argument("-o", "--output", help="输出 .pptx 路径")
    b.add_argument("-f", "--format", default="auto",
                   choices=["auto", "markdown", "json"], help="大纲格式")
    b.add_argument("--theme", help="覆盖主题（academic/vital/fresh/ink）")
    b.add_argument("--title", help="覆盖演示标题")
    b.add_argument("--author", help="覆盖作者")
    b.add_argument("--date", help="覆盖日期")
    b.set_defaults(func=cmd_build)

    t = sub.add_parser("themes", help="列出可用主题")
    t.set_defaults(func=cmd_themes)

    sc = sub.add_parser("scenes", help="列出内置场景模板")
    sc.set_defaults(func=cmd_scenes)

    ini = sub.add_parser("init", help="生成一个场景大纲模板")
    ini.add_argument("--scene", default="thesis",
                     help="场景 key（thesis/courseware/paper/class）")
    ini.add_argument("-o", "--output", help="输出大纲文件路径")
    ini.set_defaults(func=cmd_init)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
