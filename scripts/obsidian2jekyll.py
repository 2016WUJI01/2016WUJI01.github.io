#!/usr/bin/env python3
"""把 Obsidian 笔记转成本站 kramdown 文章。

支持：
- [[笔记]]、[[笔记|别名]]、[[笔记#小节]]：转成站内文章链接（按文件名、slug 或 title 查找 _posts）。
- ![[图片.png]]、![[图片.png|300]]、![[图片.png|说明文字]]：转成 /assets/img/ 下的图片，数字表示宽度（像素）。
- > [!note] / [!tip] / [!warning] / [!danger] 等 callout：转成 al-folio 的 block-tip / block-warning / block-danger。
- 行内公式 $...$：转成 kramdown 的 $$...$$。显示公式、围栏代码保持不变。

用法：
    python3 scripts/obsidian2jekyll.py 输入.md 输出.md [--posts _posts] [--attachments 附件目录]
给了 --attachments 时，把用到的图片复制到 assets/img/。
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "assets" / "img"
POST_NAME_RE = re.compile(r"^(\d{4})-(\d{2})-\d{2}-(.+)$")
FENCE_RE = re.compile(r"(^```.*?^```[ \t]*$)", re.M | re.S)
EMBED_RE = re.compile(r"!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]*))?(?:\|([^\]]+))?\]\]")
CALLOUT_RE = re.compile(r"^> \[!(\w+)\][+-]? ?(.*)\n((?:>.*\n?)*)", re.M)
INLINE_MATH_RE = re.compile(r"(?<![\$\\])\$(?!\$)([^\n$]+?)(?<!\\)\$(?!\$)")
CALLOUT_CLASS = {
    "note": "block-tip", "info": "block-tip", "tip": "block-tip", "hint": "block-tip",
    "abstract": "block-tip", "summary": "block-tip", "example": "block-tip", "quote": "block-tip",
    "question": "block-warning", "warning": "block-warning", "attention": "block-warning",
    "danger": "block-danger", "caution": "block-danger", "error": "block-danger", "bug": "block-danger",
}


def front_title(path: Path) -> str | None:
    m = re.search(r'^title:\s*"?(.*?)"?\s*$', path.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def find_post(name: str, posts: Path) -> Path:
    name = name.strip()
    for f in sorted(posts.glob("*.md")):
        m = POST_NAME_RE.match(f.stem)
        if f.stem == name or (m and m.group(3) == name) or front_title(f) == name:
            return f
    raise SystemExit(f"找不到被链接的笔记：{name}（在 {posts} 里按文件名、slug、title 都没找到）")


def post_url(f: Path) -> str:
    y, mo, slug = POST_NAME_RE.match(f.stem).groups()
    return f"/blog/{y}/{mo}/{slug}/"


def anchor(heading: str) -> str:
    return re.sub(r"\s+", "-", heading.strip().lower())


def convert(text: str, posts: Path, used_images: list[str]) -> str:
    m = re.match(r"(---\n.*?\n---\n)(.*)", text, re.S)
    fm, body = (m.group(1), m.group(2)) if m else ("", text)
    parts = FENCE_RE.split(body)
    for i in range(0, len(parts), 2):
        b = parts[i]

        def embed(mm: re.Match) -> str:
            name, opt = mm.group(1).strip(), (mm.group(2) or "").strip()
            used_images.append(name)
            src = "/assets/img/" + name.replace(" ", "%20")
            if opt.isdigit():
                return f'![{name}]({src}){{: width="{opt}"}}'
            return f"![{opt or name}]({src})"

        b = EMBED_RE.sub(embed, b)

        def link(mm: re.Match) -> str:
            f = find_post(mm.group(1), posts)
            url = post_url(f) + (f"#{anchor(mm.group(2))}" if mm.group(2) else "")
            return f"[{mm.group(3) or front_title(f) or mm.group(1)}]({url})"

        b = WIKILINK_RE.sub(link, b)

        def callout(mm: re.Match) -> str:
            kind, title, rest = mm.group(1).lower(), mm.group(2).strip(), mm.group(3)
            return f"> **{title or kind.title()}**\n>\n{rest.rstrip()}\n{{: .{CALLOUT_CLASS.get(kind, 'block-tip')} }}\n"

        b = CALLOUT_RE.sub(callout, b)
        b = INLINE_MATH_RE.sub(r"$$\1$$", b)
        parts[i] = b
    return fm + "".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--posts", default=str(ROOT / "_posts"))
    ap.add_argument("--attachments", help="Obsidian 附件目录；给出时把用到的图片复制到 assets/img/")
    a = ap.parse_args()
    used: list[str] = []
    out = convert(Path(a.src).read_text(encoding="utf-8"), Path(a.posts), used)
    Path(a.dst).write_text(out, encoding="utf-8")
    if a.attachments:
        IMG_DIR.mkdir(parents=True, exist_ok=True)
        for name in used:
            src = Path(a.attachments) / name
            if not src.exists():
                print(f"警告：附件不存在 {src}", file=sys.stderr)
                continue
            shutil.copy2(src, IMG_DIR / name)
    print(f"已写出 {a.dst}；图片 {len(used)} 张")


if __name__ == "__main__":
    main()
