#!/usr/bin/env python3
"""
从 Google Scholar 更新论文数据
需要安装: pip install scholarly beautifulsoup4 requests
"""

import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime

try:
    from scholarly import scholarly
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("错误: 请安装必需的依赖包:")
    print("pip install scholarly beautifulsoup4 requests pyyaml")
    sys.exit(1)

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "_data"
PUBLICATIONS_DIR = ROOT_DIR / "_publications"

def load_personal_config():
    """加载个人信息配置"""
    config_path = DATA_DIR / "personal.yml"
    if not config_path.exists():
        print(f"警告: 未找到配置文件 {config_path}")
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_scholar_id_from_url(url):
    """从 Google Scholar URL 中提取用户 ID"""
    if 'user=' in url:
        return url.split('user=')[1].split('&')[0]
    return None

def fetch_publications_from_scholar(user_id):
    """
    从 Google Scholar 获取论文列表
    注意: Google Scholar 可能会限制频繁请求，建议使用 API 或手动维护
    """
    publications = []
    
    try:
        print(f"正在获取 Google Scholar 用户 {user_id} 的论文...")
        author = scholarly.search_author_id(user_id)
        author = scholarly.fill(author)
        
        for pub in author.get('publications', []):
            pub_filled = scholarly.fill(pub)
            pub_data = {
                'title': pub_filled.get('bib', {}).get('title', ''),
                'authors': ', '.join(pub_filled.get('bib', {}).get('author', [])),
                'year': pub_filled.get('bib', {}).get('pub_year', ''),
                'venue': pub_filled.get('bib', {}).get('venue', ''),
                'link': pub_filled.get('pub_url', ''),
                'citations': pub_filled.get('num_citations', 0)
            }
            if pub_data['title']:
                publications.append(pub_data)
        
        print(f"成功获取 {len(publications)} 篇论文")
        
    except Exception as e:
        print(f"错误: 无法从 Google Scholar 获取数据: {e}")
        print("提示: 您可以手动维护论文数据，或使用其他数据源")
    
    return publications

def fetch_publications_from_manual():
    """
    从手动维护的文件中读取论文数据
    支持格式: _publications/*.md 或 _publications/publications.yml
    """
    publications = []
    
    # 检查是否有 YAML 文件
    yaml_file = PUBLICATIONS_DIR / "publications.yml"
    if yaml_file.exists():
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                publications.extend(data)
    
    # 检查 Markdown 文件
    for md_file in PUBLICATIONS_DIR.glob("*.md"):
        if md_file.name == "README.md":
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 简单的 Markdown 解析（可以改进）
            # 这里假设使用 YAML front matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        front_matter = yaml.safe_load(parts[1])
                        publications.append(front_matter)
                    except:
                        pass
    
    return publications

def save_publications(publications):
    """保存论文数据到 _publications 目录"""
    PUBLICATIONS_DIR.mkdir(exist_ok=True)
    
    # 按年份分组
    by_year = {}
    for pub in publications:
        year = pub.get('year', '未知')
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(pub)
    
    # 保存为单独的 Markdown 文件
    for year, pubs in by_year.items():
        for idx, pub in enumerate(pubs):
            # 生成文件名
            title_slug = pub.get('title', 'untitled').lower()
            title_slug = ''.join(c if c.isalnum() or c in '- ' else '' for c in title_slug)
            title_slug = '-'.join(title_slug.split()[:5])  # 限制长度
            filename = f"{year}-{idx+1:02d}-{title_slug}.md"
            filepath = PUBLICATIONS_DIR / filename
            
            # 生成 Markdown 内容
            content = f"""---
title: "{pub.get('title', '')}"
authors: "{pub.get('authors', '')}"
year: {year}
venue: "{pub.get('venue', '')}"
"""
            if pub.get('link'):
                content += f'link: "{pub.get("link")}"\n'
            
            if pub.get('links'):
                content += 'links:\n'
                for link in pub.get('links', []):
                    content += f'  - name: "{link.get("name", "")}"\n'
                    content += f'    url: "{link.get("url", "")}"\n'
            
            content += "---\n\n"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    print(f"已保存 {len(publications)} 篇论文到 {PUBLICATIONS_DIR}")

def main():
    """主函数"""
    print("开始更新论文数据...")
    
    # 加载配置
    config = load_personal_config()
    if not config:
        print("使用手动维护的论文数据...")
        publications = fetch_publications_from_manual()
    else:
        scholar_config = config.get('scholar', {})
        user_id = scholar_config.get('user_id')
        scholar_url = config.get('social', {}).get('google_scholar', '')
        
        if scholar_url and not user_id:
            user_id = get_scholar_id_from_url(scholar_url)
        
        if user_id:
            publications = fetch_publications_from_scholar(user_id)
        else:
            print("未配置 Google Scholar 用户 ID，使用手动维护的数据...")
            publications = fetch_publications_from_manual()
    
    if publications:
        save_publications(publications)
        print("论文数据更新完成！")
    else:
        print("未找到论文数据。")
        print("提示: 您可以:")
        print("1. 在 _data/personal.yml 中配置 Google Scholar 用户 ID")
        print("2. 在 _publications/ 目录下手动创建论文文件")

if __name__ == "__main__":
    main()

