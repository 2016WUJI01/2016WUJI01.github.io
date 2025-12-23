# 学术主页

使用 Jekyll 和 GitHub Actions 构建的个人学术主页。

## 功能特性

- 🎨 简洁现代的界面设计
- 📝 自动更新论文列表（Google Scholar）
- 📊 自动更新 GitHub 统计信息
- 📖 博客文章支持
- 🔄 GitHub Actions 自动化部署
- 📱 响应式设计，支持移动端

## 快速开始

### 1. 配置个人信息

编辑 `_data/personal.yml` 文件，填写您的个人信息：

```yaml
name: "您的姓名"
title: "您的职位"
affiliation: "您的机构"
email: "your.email@example.com"
```

### 2. 配置 Google Scholar（可选）

在 `_data/personal.yml` 中配置 Google Scholar 信息：

```yaml
scholar:
  user_id: "YOUR_SCHOLAR_ID" # 从 Google Scholar 个人主页 URL 获取
```

或者在 `social.google_scholar` 中填写完整的 Google Scholar 链接。

### 3. 配置 GitHub（可选）

在 `_data/personal.yml` 中配置 GitHub 链接：

```yaml
social:
  github: "https://github.com/yourusername"
```

### 4. 本地开发

```bash
# 安装依赖
bundle install

# 启动本地服务器
bundle exec jekyll serve

# 访问 http://localhost:4000
```

### 5. 部署到 GitHub Pages

1. 将代码推送到 GitHub 仓库
2. 在仓库设置中启用 GitHub Pages（选择 main/master 分支）
3. GitHub Actions 会自动构建和部署站点

## 目录结构

```
├── _config.yml          # Jekyll 配置
├── _data/               # 数据文件
│   ├── personal.yml     # 个人信息
│   └── github_stats.yml # GitHub 统计（自动生成）
├── _layouts/            # 布局模板
├── _includes/           # 组件
├── _posts/              # 博客文章
├── _publications/       # 论文（自动生成或手动维护）
├── assets/              # 静态资源
├── scripts/             # 自动化脚本
└── .github/workflows/   # GitHub Actions 工作流
```

## 添加博客文章

在 `_posts/` 目录下创建 Markdown 文件，文件名格式：`YYYY-MM-DD-title.md`

```markdown
---
title: "文章标题"
date: 2024-01-01
---

文章内容...
```

## 手动添加论文

在 `_publications/` 目录下创建 Markdown 文件：

```markdown
---
title: "论文标题"
authors: "作者1, 作者2"
year: 2024
venue: "会议/期刊名称"
link: "https://example.com/paper"
---
```

## 自动化更新

GitHub Actions 会在以下情况自动运行：

- 每周一自动更新论文和统计数据
- 代码推送到 main/master 分支时自动部署
- 手动触发工作流

## 自定义样式

编辑 `assets/css/style.scss` 来自定义样式。

## 许可证

MIT License
