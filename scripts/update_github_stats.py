#!/usr/bin/env python3
"""
更新 GitHub 统计数据
需要安装: pip install pyyaml requests
"""

import os
import sys
import yaml
import requests
from pathlib import Path
from datetime import datetime

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "_data"


def load_personal_config():
    """加载个人信息配置"""
    config_path = DATA_DIR / "personal.yml"
    if not config_path.exists():
        return None

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_github_username_from_url(url):
    """从 GitHub URL 中提取用户名"""
    if url:
        # 处理各种格式的 URL
        url = url.rstrip("/")
        if "github.com" in url:
            parts = url.split("github.com/")
            if len(parts) > 1:
                username = parts[1].split("/")[0]
                return username
    return None


def fetch_github_stats(username, token=None):
    """
    获取 GitHub 用户统计信息
    如果需要访问私有仓库，需要提供 GitHub token
    """
    stats = {
        "total_repos": 0,
        "total_commits": 0,
        "total_stars": 0,
        "total_followers": 0,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    if not username:
        print("未配置 GitHub 用户名")
        return stats

    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        # 获取用户信息
        user_url = f"https://api.github.com/users/{username}"
        response = requests.get(user_url, headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            stats["total_repos"] = user_data.get("public_repos", 0)
            stats["total_followers"] = user_data.get("followers", 0)

            # 获取仓库信息（计算总 stars）
            repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
            repos_response = requests.get(repos_url, headers=headers)

            if repos_response.status_code == 200:
                repos = repos_response.json()
                total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
                stats["total_stars"] = total_stars

                # 注意: GitHub API 不直接提供总提交数
                # 需要遍历所有仓库的提交，这可能会触发速率限制
                # 这里提供一个简化的实现
                print(f"成功获取 GitHub 统计数据:")
                print(f"  - 仓库数: {stats['total_repos']}")
                print(f"  - 关注者: {stats['total_followers']}")
                print(f"  - Stars: {stats['total_stars']}")
            else:
                print(f"警告: 无法获取仓库信息 (状态码: {repos_response.status_code})")
        else:
            print(f"错误: 无法获取用户信息 (状态码: {response.status_code})")
            if response.status_code == 404:
                print(f"提示: 用户 '{username}' 不存在或无法访问")
            elif response.status_code == 403:
                print("提示: API 速率限制，可能需要 GitHub token")

    except Exception as e:
        print(f"错误: 获取 GitHub 统计数据时出错: {e}")

    return stats


def save_github_stats(stats):
    """保存 GitHub 统计数据"""
    stats_file = DATA_DIR / "github_stats.yml"

    with open(stats_file, "w", encoding="utf-8") as f:
        yaml.dump({"stats": stats}, f, allow_unicode=True, default_flow_style=False)

    print(f"统计数据已保存到 {stats_file}")


def main():
    """主函数"""
    print("开始更新 GitHub 统计数据...")

    # 加载配置
    config = load_personal_config()
    if not config:
        print("未找到配置文件，跳过 GitHub 统计更新")
        return

    # 获取 GitHub 用户名
    github_url = config.get("social", {}).get("github", "")
    username = get_github_username_from_url(github_url)

    # 从环境变量获取 GitHub token（可选，用于提高 API 限制）
    token = os.environ.get("GITHUB_TOKEN")

    if not username:
        print("未配置 GitHub 用户名")
        print("提示: 在 _data/personal.yml 的 social.github 中配置您的 GitHub 链接")
        return

    # 获取统计数据
    stats = fetch_github_stats(username, token)

    # 保存统计数据
    save_github_stats(stats)

    print("GitHub 统计数据更新完成！")


if __name__ == "__main__":
    main()
