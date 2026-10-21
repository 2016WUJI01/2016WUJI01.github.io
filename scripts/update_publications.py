#!/usr/bin/env python3
"""维护 _bibliography/papers.bib（al-folio 的论文列表来源）。

做法：
1. 读现有 papers.bib，已有条目原样保留（手工加的 selected、abbr、pdf 等字段不会被覆盖）。
2. 从 Google Scholar（_data/personal.yml 的 scholar.user_id）取论文，标题不在 bib 里的才追加。
3. 从不删除条目。Scholar 访问失败时不改文件，退出码 0，CI 继续。

用法：
    python3 scripts/update_publications.py            # 联网更新
    python3 scripts/update_publications.py --dry-run  # 只打印将追加的条目
需要：pip install -r scripts/requirements.txt
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "_bibliography" / "papers.bib"
PERSONAL = ROOT / "_data" / "personal.yml"
SELF_NAMES = ("Jiashun Wu", "Wu, Jiashun")
_HYPHENS = "\u2010\u2011\u2012\u2013\u2014\u2212"


def clean(text) -> str:
    text = "".join("-" if c in _HYPHENS else c for c in str(text or ""))
    return re.sub(r"\s+", " ", text).strip()


def norm_title(title: str) -> str:
    t = unicodedata.normalize("NFKD", clean(title)).lower()
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", t)


def existing_titles(bib_text: str) -> set[str]:
    return {norm_title(m) for m in re.findall(r"^\s*title\s*=\s*\{(.+?)\},?\s*$", bib_text, re.M)}


def existing_keys(bib_text: str) -> set[str]:
    return set(re.findall(r"^@\w+\{([^,\s]+),", bib_text, re.M))


def bib_authors(raw) -> str:
    if isinstance(raw, list):
        names = raw
    else:
        names = re.split(r"\s+and\s+|,\s*", clean(raw))
    return " and ".join(n.strip() for n in names if n.strip())


def make_key(authors: str, year: str, title: str, taken: set[str]) -> str:
    first = authors.split(" and ")[0].split()[-1] if authors else "anon"
    word = next((w for w in re.findall(r"[A-Za-z]+", title) if len(w) > 3), "paper")
    base = re.sub(r"[^a-z0-9]", "", f"{first}{year}{word}".lower())
    key, n = base, 2
    while key in taken:
        key, n = f"{base}{n}", n + 1
    taken.add(key)
    return key


def to_bibtex(pub: dict, key: str) -> str:
    fields = [("title", pub["title"]), ("author", pub["authors"]), ("journal", pub.get("venue", "")),
              ("year", pub.get("year", "")), ("html", pub.get("link", ""))]
    body = ",\n".join(f"  {k:<7} = {{{v}}}" for k, v in fields if v)
    return f"@article{{{key},\n{body}\n}}\n"


def fetch_scholar(user_id: str) -> list[dict]:
    from scholarly import scholarly  # 延迟导入：--help 和自检不需要联网依赖

    author = scholarly.fill(scholarly.search_author_id(user_id), sections=["publications"])
    pubs = []
    for p in author.get("publications", []):
        p = scholarly.fill(p)
        bib = p.get("bib", {}) or {}
        if not bib.get("title"):
            continue
        pubs.append({
            "title": clean(bib["title"]),
            "authors": bib_authors(bib.get("author", "")),
            "venue": clean(bib.get("journal") or bib.get("venue") or bib.get("conference") or ""),
            "year": str(bib.get("pub_year", "")),
            "link": p.get("pub_url", ""),
        })
    return pubs


def main() -> None:
    ap = argparse.ArgumentParser(description="把 Google Scholar 新论文追加到 _bibliography/papers.bib")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    personal = yaml.safe_load(PERSONAL.read_text(encoding="utf-8")) or {}
    user_id = (personal.get("scholar") or {}).get("user_id")
    if not user_id:
        print("未配置 scholar.user_id，跳过")
        return
    text = BIB.read_text(encoding="utf-8") if BIB.exists() else "---\n---\n\n"
    try:
        pubs = fetch_scholar(user_id)
    except Exception as exc:  # Scholar 常常限流；不改文件
        print(f"::warning::Google Scholar 获取失败，papers.bib 保持不变：{exc}")
        return

    titles, keys, added = existing_titles(text), existing_keys(text), []
    for pub in sorted(pubs, key=lambda p: p.get("year", ""), reverse=True):
        if norm_title(pub["title"]) in titles:
            continue
        titles.add(norm_title(pub["title"]))
        added.append(to_bibtex(pub, make_key(pub["authors"], pub.get("year", ""), pub["title"], keys)))
    if not added:
        print(f"没有新论文（Scholar 共 {len(pubs)} 篇）")
        return
    print(f"新增 {len(added)} 篇：\n" + "\n".join(added))
    if not args.dry_run:
        BIB.write_text(text.rstrip() + "\n\n" + "\n".join(added), encoding="utf-8")


if __name__ == "__main__":
    main()
