<div align="center">

<img src="assets/banner.svg" alt="校园演示工坊" width="100%">

# 校园演示工坊 · Campus PPT Studio

**写一份大纲，生成一份每个字都能改的 PPT。**

面向学生和老师：毕业答辩、教学课件、学术汇报、班级活动——
用纯文本写大纲，一条命令生成**原生可编辑**的 `.pptx`。
无需 AI 账号、无需 API Key、无需联网，本地一秒出片。

[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](requirements.txt)
[![status](https://img.shields.io/badge/status-active-success.svg)](CHANGELOG.md)
[![editable](https://img.shields.io/badge/output-native%20editable%20PPTX-orange.svg)](#为什么可编辑很重要)
[![PRs](https://img.shields.io/badge/PRs-welcome-orange.svg)](CONTRIBUTING.md)

</div>

---

## 为什么做这个

你大概见过很多「AI 一键生成 PPT」：输入一句话，几分钟吐出一份好看的幻灯片。
但打开 PowerPoint 想改一个字——**改不了**。因为每一页都是一张图片。

交作业要改成自己的数据、答辩前导师要调一页、课件要换成班级的名字……
一旦不能编辑，就只能重新生成，或者放弃。

**校园演示工坊** 走的是另一条路：

> 它不追求「凭空生成内容」，而是把你写好的大纲，
> 排成一份**每个文字框、每个色块、每个图形都能点开修改**的原生 PPT。
> 你负责想清楚讲什么，它负责版面好看。

而且它**零 AI 依赖**：不需要注册账号、不需要 API Key、不联网、不花钱。
克隆下来装上依赖就能用，产出完全属于你。

## 它能帮你做什么

- **学生 · 毕业答辩**：按「背景→方法→结果→创新→展望」的标准结构，快速搭出答辩骨架，把精力放在讲什么上。
- **老师 · 教学课件**：目标、概念对比、重点难点、课堂练习、小结，一套课件结构模板直接填空。
- **学术党 · 论文汇报**：研究动机、方法对比、实验结果数据卡、结论局限，符合学术汇报的表达习惯。
- **班委 / 老师 · 班级活动**：班会、家长会、社团活动，带时间轴和活动数据的活泼版式。

一套工具，覆盖你在校园里要做 PPT 的绝大多数场合。

## 为什么「可编辑」很重要

| 对比 | 图片式 AI PPT | 校园演示工坊（原生可编辑） |
|---|---|---|
| 产物 | 每页是一张图片 | 真正的文本框 / 形状 / 色块 |
| 改一个字 | 改不了，只能重新生成 | 双击就能改 |
| 换班级名 / 数据 | 几乎不可能 | 选中即改 |
| 调整布局 | 不行 | 拖动即可 |
| 二次加工 | 不支持 | 完全自由 |

实测：一份 15 页的答辩 PPT，包含 **114 个独立形状、67 个可编辑文字对象、0 张整页图片**。

## 快速开始

### 1. 安装

```bash
git clone https://github.com/duanlinhao89-hash/campus-ppt-studio.git
cd campus-ppt-studio
pip install -r requirements.txt
```

只需一个依赖：`python-pptx`。Python 3.8+ 即可。

### 2. 三步生成

```bash
# 第 1 步：选一个场景，生成大纲模板
python -m campus_ppt init --scene thesis -o 我的答辩.md

# 第 2 步：用记事本打开 我的答辩.md，把 [方括号] 里的内容换成你的

# 第 3 步：生成 PPTX
python -m campus_ppt build 我的答辩.md -o 我的答辩.pptx
```

打开 `我的答辩.pptx`，每个字、每个色块都能在 PowerPoint / WPS 里直接改。

### 3. 换主题

```bash
python -m campus_ppt build 我的答辩.md -o 我的答辩.pptx --theme fresh
```

四套主题任选：`academic`（学术蓝）、`fresh`（清新绿）、`vital`（活力橙）、`ink`（墨韵灰）。

```bash
python -m campus_ppt themes   # 查看全部主题
python -m campus_ppt scenes   # 查看全部场景
```

## 大纲语法（很简单）

大纲就是一个 Markdown 文件。用 `@布局` 标记每一页，用 `#` 写标题，用 `-` 写要点：

```markdown
---
title: 我的演示
author: 张三
theme: academic
---

@cover
# 演示主标题
副标题 / 署名

@toc
- 第一部分
- 第二部分

@content
## 这一页的标题
- 要点一
- 要点二

@stats
## 核心数据
- 95% | 准确率
- 3.2x | 提速

@thanks
## 谢谢观看
```

支持 9 种页面布局：`cover` 封面、`toc` 目录、`section` 章节页、`content` 内容页、
`two_col` 双栏、`stats` 数据卡、`timeline` 时间轴、`quote` 金句、`thanks` 致谢。

完整语法见 [`docs/大纲语法.md`](docs/大纲语法.md)。

## 内置场景

| 场景 | 命令 | 默认主题 | 结构 |
|---|---|---|---|
| 毕业答辩 | `init --scene thesis` | 学术蓝 | 背景→目标方法→工作结果→创新不足→总结 |
| 教学课件 | `init --scene courseware` | 清新绿 | 目标→概念→重点→案例→练习→小结 |
| 学术汇报 | `init --scene paper` | 学术蓝 | 动机→相关方法→实验→结论展望 |
| 班级活动 | `init --scene class` | 活力橙 | 背景→流程→数据→分工→倡议 |

## 仓库结构

```
campus-ppt-studio/
├── README.md                  # 你正在看的这份
├── LICENSE                    # MIT 协议
├── CONTRIBUTING.md            # 贡献指南
├── CHANGELOG.md               # 更新记录
├── requirements.txt           # 依赖（只有一个）
├── campus_ppt/                # 核心代码
│   ├── __init__.py
│   ├── __main__.py            # python -m 入口
│   ├── cli.py                 # 命令行
│   ├── parser.py              # 大纲解析
│   ├── builder.py             # PPTX 渲染引擎
│   ├── themes.py              # 配色主题
│   └── scenes.py              # 四大场景模板
├── examples/                  # 示例大纲 + 成品预览
│   ├── 毕业答辩.md
│   ├── 教学课件.md
│   ├── 学术汇报.md
│   ├── 班级活动.md
│   ├── 示例-光合作用.md
│   └── preview/
├── docs/                      # 使用文档
│   ├── 大纲语法.md
│   ├── 主题与配色.md
│   └── FAQ.md
├── assets/
│   └── banner.svg
└── tests/
    └── smoke_test.py          # 冒烟测试
```

## 适合谁

- 需要做**毕业答辩**、课程展示、社团竞聘的学生；
- 需要制作**教学课件**、说课、公开课的老师；
- 需要**学术汇报**、论文宣讲的研究生与青年学者；
- 需要组织**班会**、家长会、社团活动的班委与老师；
- 任何想「先把内容写好，再快速排成好看 PPT」的人。

## 设计原则

1. **可编辑优先**：产物永远是原生对象，不是图片。
2. **零依赖负担**：除 python-pptx 外无第三方库，不联网、不要账号。
3. **内容为王**：工具只管排版，讲什么由你决定——不编造内容、不产生幻觉。
4. **场景化**：内置校园四大场景的成熟结构，开箱即用。
5. **克制美观**：每套主题只用主色+强调色+中性色，不花哨。

## 文档

- [大纲语法](docs/大纲语法.md) —— 9 种布局的完整写法
- [主题与配色](docs/主题与配色.md) —— 四套主题与自定义方法
- [FAQ](docs/FAQ.md) —— 常见问题

## 贡献

欢迎新增场景模板、设计主题、改进版式、补充文档。请先读 [CONTRIBUTING.md](CONTRIBUTING.md)。
哪怕只是提一个 Issue 说「希望支持某某场景」，也很有价值。

## 许可

MIT License —— 自由使用、修改、分享，只需保留署名。详见 [LICENSE](LICENSE)。

---

<div align="center">

**如果这套工具帮你省下了做 PPT 的时间，给个 ⭐ Star 吧。**

Made for students and teachers who'd rather think than fiddle with layouts.

</div>
