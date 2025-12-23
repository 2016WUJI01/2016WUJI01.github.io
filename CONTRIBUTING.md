# 使用说明

## 首次设置

### 1. 更新个人信息

编辑 `_data/personal.yml`，填写您的真实信息：

- `name`: 您的姓名
- `title`: 职位（如：博士生、研究员等）
- `affiliation`: 所属机构
- `email`: 邮箱地址
- `photo`: 照片路径（将照片放在 `assets/images/` 目录下）
- `bio`: 个人简介
- `research_areas`: 研究领域列表
- `education`: 教育背景
- `experience`: 工作经历
- `social`: 社交链接

### 2. 配置 Google Scholar（可选）

如果您希望自动从 Google Scholar 更新论文：

1. 访问您的 Google Scholar 个人主页
2. 从 URL 中获取用户 ID（例如：`https://scholar.google.com/citations?user=ABC123` 中的 `ABC123`）
3. 在 `_data/personal.yml` 中设置：

```yaml
scholar:
  user_id: "ABC123"
```

或者在 `social.google_scholar` 中填写完整的链接。

**注意**: Google Scholar 可能会限制频繁请求。如果自动更新失败，您可以手动在 `_publications/` 目录下创建论文文件。

### 3. 配置 GitHub

在 `_data/personal.yml` 中设置 GitHub 链接：

```yaml
social:
  github: "https://github.com/yourusername"
```

这将用于自动获取 GitHub 统计数据。

### 4. 添加照片

将您的照片放在 `assets/images/` 目录下，然后在 `_data/personal.yml` 中设置路径：

```yaml
photo: "/assets/images/photo.jpg"
```

## 手动添加论文

在 `_publications/` 目录下创建 Markdown 文件，文件名格式：`YYYY-NN-title.md`

示例：

```markdown
---
title: "论文标题"
authors: "作者1, 作者2, 您的名字"
year: 2024
venue: "会议/期刊名称"
link: "https://example.com/paper"
links:
  - name: "PDF"
    url: "https://example.com/paper.pdf"
  - name: "arXiv"
    url: "https://arxiv.org/abs/xxxx.xxxxx"
---

论文摘要（可选）
```

## 添加博客文章

在 `_posts/` 目录下创建 Markdown 文件，文件名格式：`YYYY-MM-DD-title.md`

示例：

```markdown
---
title: "文章标题"
date: 2024-01-01
---

文章内容...
```

## 本地测试

```bash
# 安装 Ruby 和 Bundler（如果还没有）
# macOS: brew install ruby
# Ubuntu: sudo apt-get install ruby-full

# 安装依赖
bundle install

# 启动本地服务器
bundle exec jekyll serve

# 访问 http://localhost:4000
```

## 部署

1. 将代码推送到 GitHub 仓库
2. 在仓库设置中：
   - 进入 Settings > Pages
   - Source 选择 "GitHub Actions"
3. GitHub Actions 会自动构建和部署站点

## 自动化更新

GitHub Actions 会在以下情况自动运行：

- **定时任务**: 每周一 UTC 00:00（北京时间 08:00）自动更新论文和统计数据
- **代码推送**: 推送到 main/master 分支时自动构建和部署
- **手动触发**: 在 GitHub Actions 页面可以手动触发工作流

## 故障排除

### Google Scholar 更新失败

如果 Google Scholar 自动更新失败：

1. 检查 `_data/personal.yml` 中的 `scholar.user_id` 是否正确
2. Google Scholar 可能限制了访问频率，可以稍后重试
3. 可以手动在 `_publications/` 目录下创建论文文件

### GitHub 统计更新失败

如果 GitHub 统计更新失败：

1. 检查 `_data/personal.yml` 中的 `social.github` 是否正确
2. 如果您的仓库是私有的，可能需要设置 `GITHUB_TOKEN` secret

### Jekyll 构建失败

1. 检查 `_config.yml` 语法是否正确
2. 确保所有 YAML 文件格式正确
3. 查看 GitHub Actions 日志获取详细错误信息

## 自定义样式

编辑 `assets/css/style.scss` 来自定义样式。修改后需要重新构建站点。

## 获取帮助

如有问题，请查看：

- [Jekyll 文档](https://jekyllrb.com/docs/)
- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
