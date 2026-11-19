# 贡献指南

欢迎让这套工具变得更好。无论是新增场景、设计主题、改进版式还是补充文档，都很有价值。

## 你可以怎么贡献

- **新增场景模板**：把你熟悉场景的大纲结构（答辩 / 说课 / 班会 / 社团等）沉淀成模板，放进 `campus_ppt/scenes.py`。
- **设计新主题**：在 `campus_ppt/themes.py` 里新增一套配色，注意对比度和投影可读性。
- **改进版式**：优化 `builder.py` 里的某个布局，让排版更美观或更耐用。
- **新增页面布局**：比如「团队成员页」「参考文献页」「二维码页」等。
- **补充文档 / 示例**：写清楚用法，或补充一个真实场景的示例大纲。
- **修复 Bug**：发现问题直接提 Issue 或 PR。

## 开发环境

```bash
git clone https://github.com/duanlinhao89-hash/campus-ppt-studio.git
cd campus-ppt-studio
pip install -r requirements.txt
python -m campus_ppt build examples/示例-光合作用.md -o /tmp/out.pptx
python tests/smoke_test.py
```

## 贡献流程

1. Fork 本仓库；
2. 新建分支：`git checkout -b feat/你的改动`；
3. 提交改动，写清楚改了什么、为什么；
4. Push 到你的分支，发起 Pull Request；
5. 在 PR 里说明改动动机与影响。

## 内容规范

- 场景模板要**通用**：不要写死某个学校/个人的信息，用 `[方括号]` 占位。
- 主题要**克制**：同色系主色+强调色，保证投影可读。
- 保持「可编辑优先」：任何版式都不能用整页图片替代。
- 新增布局后，更新 `docs/大纲语法.md` 并补一个示例。

## 行为准则

友善、就事论事。批评代码可以尖锐，批评人请克制。

## 许可

你的贡献默认视为同意以 MIT 协议发布。
