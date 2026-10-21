# 文章系列与合订 PDF

网页仍是多页：同一系列的文章互相链接，系列目录提供顺序和上一篇 / 下一篇。GitHub Actions 再按顺序把 Markdown 合并成一份 PDF，放到 `/assets/pdf/<slug>.pdf`。站点继续使用现在的 Jekyll 4.3，不更换生成器。

## 加一篇系列文章

1. 在 `_posts/` 新建 `YYYY-MM-DD-english-slug.md`。网页地址由文件名决定，例如 `2026-03-02-tensor-matricization.md` 对应 `/blog/2026/03/tensor-matricization/`。
2. 在 front matter 里写上系列和顺序：

```yaml
---
title: "模式展开：把张量写成矩阵"
date: 2026-03-02
categories: [研究笔记]
tags: [张量]
series: demo-tensor-notes
series_order: 2
excerpt: "列表和系列目录用的纯文本摘要。"
---
```

- `series`：系列 slug，只使用小写字母、数字和连字符。
- `series_order`：正整数。同一系列按它升序排列；相同序号再按日期、文件名。
- 正文里用站点路径互相链接，例如 `[记号](/blog/2026/03/tensor-notation/)`。PDF 构建会把这种链接改成对应章节锚点。

3. 若要目录标题和简介，在 `_data/series.yml` 增加一条，`slug` 必须和 front matter 一致：

```yaml
- slug: demo-tensor-notes
  title: "张量笔记：从符号到分解"
  description: "三篇短文，部署时合并为一份 PDF。"
```

这一项是可选的。没有它时，系列页用 slug 当标题，PDF 仍会生成。

生成的页面：

- `/blog/series/`：全部系列
- `/blog/series/<slug>/`：该系列目录；PDF 文件已存在时显示下载按钮

文章页顶部有系列名称，文末有目录、上一篇 / 下一篇。PDF 已生成时，文末也有下载链接。

## 公式

全站只用 kramdown 这一种写法，网页和 PDF 读的是同一份源稿。

行内公式两侧紧贴 `$$`，中间不要换行：

```markdown
阶为 $$N$$ 的元素记作 $$\mathcal{X}_{i_1 i_2 \ldots i_N}$$。
```

显示公式把 `$$` 单独放一行：

```markdown
$$
\| \mathcal{X} \|_F = \sqrt{\sum_{ijk} \mathcal{X}_{ijk}^{2}}.
$$
```

不要把显示公式写成一行里的 `$$ ... $$`，那会被当成行内公式。也不要改用 `$...$`、`\(...\)` 或 `\[...\]`：kramdown 不把它们当成数学，下标里的 `_` 会被吃掉。

围栏代码和行内代码里的美元符号会原样保留。公式不要写进代码块。

网页：`_config.yml` 里 `math_engine: mathjax`。kramdown 2 会把行内公式写成 `\(...\)`、把显示公式写成 `\[...\]`。文章页加载 MathJax 3（jsDelivr 的 `tex-chtml.js`），它默认就认这两种定界符，并且会跳过 `pre` 和 `code`。断网时，页面上仍能看到这两段 LaTeX 原文。

PDF：`scripts/build_series_pdfs.py` 把不跨行的 `$$...$$` 收成 pandoc 的 `$...$`，单独成行的 `$$` 块保持不动。pandoc 使用其自带的 `markdown`（含 `tex_math_dollars`）和 XeLaTeX。

## 本地重新生成 PDF

需要 pandoc、XeLaTeX（`texlive-xetex`）、`texlive-lang-chinese`（提供 `xeCJK`）和一种简体中文字体。Ubuntu 上可以执行：

```bash
bash scripts/install_pdf_deps.sh
python3 scripts/build_series_pdfs.py --self-test
python3 scripts/build_series_pdfs.py
bundle exec jekyll build
```

PDF 写到 `assets/pdf/<slug>.pdf`，并且被 git 忽略。Jekyll 在构建前就能看见这个文件时，系列目录才会渲染下载按钮；否则页面仍给出同一路径，说明要等部署生成。

只改文章、不改脚本时，重新跑 `python3 scripts/build_series_pdfs.py` 即可。

## CI 里怎么做

`.github/workflows/update-site.yml` 的「构建和部署」在 `jekyll build` 之前调用同一个脚本，把 PDF 放进 `assets/pdf/`，再由 Jekyll 复制到 `_site/assets/pdf/`。部署步骤仍只在 `main` / `master` 上运行。

PDF 步骤失败时：

- 日志里有 `::error::`，工作流最终标红
- 站点构建和部署继续，避免论文页和博客因为字体问题一起下线
- 当次部署的系列目录可能没有下载按钮

针对 pull request 和其他非默认分支，`.github/workflows/series-pdf.yml` 会生成 PDF 并上传为名为 `series-pdfs` 的 artifact，不会部署，也不会往 `master` 推送。

当前示例系列是 `demo-tensor-notes`（三篇中英文技术短文）。合订本路径：`/assets/pdf/demo-tensor-notes.pdf`。

## 字体、中文和公式

- 引擎是 XeLaTeX，不是 pdfLaTeX。中文靠 pandoc 模板里的 `CJKmainfont` 加 `xeCJK`。
- 脚本按顺序选择已安装的字体：`Noto Serif CJK SC`、`Noto Sans CJK SC`，以及思源 / Fandol / 文泉驿。GitHub 的 `ubuntu-latest` 需要安装 `fonts-noto-cjk`，系统里没有这些家族名时脚本会直接失败。
- 数学使用传统 TeX 字体（pandoc 默认的 amsmath），不加载 `unicode-math`，因此 `\mathcal`、`\mathbb`、`\mathbf` 按 LaTeX 习惯书写。
- 不要在 pandoc 元数据里设置 `lang: zh-CN`。那会让模板去加载 babel/polyglossia 的中文支持，在这套精简 TeX 安装里经常失败。中文由 `xeCJK` 负责。
- 正文从二级标题写起。脚本会把文章标题作为 PDF 的一级标题，并加上与文件名 slug 相同的锚点。
