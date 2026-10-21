# 吴嘉顺的学术主页

站点地址：<https://2016wuji01.github.io>

- 首页：Jon Barron 风格的单页，源文件 `_pages/index.html`，个人信息读 `_data/personal.yml`，论文读 `_bibliography/papers.bib`。
- 博客、笔记、文章系列：基于 [al-folio](https://github.com/alshedivat/al-folio)（主题以 gem `al_folio_core` 引入，本仓库只放覆盖文件）。
- 论文：`_bibliography/papers.bib`。`scripts/update_publications.py` 每周从 Google Scholar 追加新论文，不删除、不覆盖已有条目。
- 文章系列与合订 PDF：见 `docs/series-and-pdf.md`。
- Obsidian 笔记：`python3 scripts/obsidian2jekyll.py 笔记.md _posts/YYYY-MM-DD-slug.md --attachments 附件目录`，支持 `[[链接]]`、`![[图片.png|300]]`、callout、`$公式$`。

## 本地预览

```bash
bundle install
bundle exec jekyll serve      # http://localhost:4000
python3 scripts/build_series_pdfs.py   # 需要 pandoc + XeLaTeX，见 scripts/install_pdf_deps.sh
```

## 部署

`.github/workflows/update-site.yml` 在推送 master 时构建并部署到 `gh-pages` 分支。
仓库 Settings → Pages 的发布来源需要设为 `gh-pages` 分支根目录。
