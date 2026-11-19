# 常见问题

## 需要联网吗？需要 AI 账号吗？

都不需要。安装依赖时需要联网（仅第一次），之后生成 PPT 完全是本地操作。
不需要任何 AI 账号、API Key 或订阅。

## 和 PPT Master / Gamma 这类 AI PPT 工具有什么区别？

它们的核心逻辑是「AI 帮你写内容 + 排版」，通常需要 API Key、按量付费，
且很多产物是图片式 PPT（不能改字）。

校园演示工坊的逻辑是「你写好内容 + 工具帮你排版」：
- 免费、本地、零账号；
- 产物是原生可编辑的 PPTX。

它不帮你编内容——这样反而更适合校园场景，因为答辩和课件的内容必须是你自己的。

## 生成的 PPT 真的能编辑吗？

能。产物里的每个文字框、色块、圆形、线条都是 PowerPoint 原生对象。
实测一份 15 页 PPT 含 114 个独立形状、67 个可编辑文字对象、**0 张整页图片**。
打开后双击文字即可修改，色块和图形可直接选中、拖动、改颜色。

## 支持 WPS 吗？

支持。产物是标准 `.pptx` 格式，PowerPoint、WPS、Keynote 都能打开和编辑。

##  Bullet 太多会挤爆版面吗？

不会。工具会根据要点数量自动调整字号（17pt → 15pt → 13pt）。
但建议一页不超过 7 条，超过后虽然放得下，阅读体验会下降。

## 可以插入自己的图片吗？

当前版本专注于文字与形状版式，暂不支持在大纲里插入本地图片。
但你可以在生成后用 PowerPoint 打开，手动插入图片——因为版面是原生对象，插入和调整都很方便。
图片支持已在计划中，欢迎 PR。

## 中文显示正常吗？

正常。默认中文字体是「微软雅黑」，并已正确写入 East Asian 字体属性，
在 Windows / WPS 下显示无问题。Mac 用户可在主题里把字体改为「苹方」。

## 报错 `ModuleNotFoundError: No module named 'pptx'`

说明没装依赖。运行：

```bash
pip install -r requirements.txt
```

## 报错 `No matching distribution found`

可能是 pip 镜像源没同步。强制用官方源：

```bash
pip install python-pptx -i https://pypi.org/simple
```

## 支持哪些 Python 版本？

Python 3.8 及以上。开发测试环境为 Python 3.13。

## 怎么贡献新场景 / 新主题？

见 [CONTRIBUTING.md](../CONTRIBUTING.md)。很简单——场景就是一段大纲模板，主题就是一组配色。
