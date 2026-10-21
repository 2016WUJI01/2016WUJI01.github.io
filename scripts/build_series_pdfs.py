#!/usr/bin/env python3
"""把每个文章系列按 series_order 合并，并用 pandoc + XeLaTeX 打成一份 PDF。

网页使用 kramdown 的公式约定：行内 $$...$$ ，显示公式用单独成行的 $$。
pandoc 把成对的 $$ 当成显示公式，因此这里只把不跨行的 $$...$$ 收成 $...$。
显示公式块、围栏代码和行内代码保持原样。

输出：assets/pdf/<series-slug>.pdf
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"
SERIES_YML = ROOT / "_data" / "series.yml"
PERSONAL_YML = ROOT / "_data" / "personal.yml"
PDF_DIR = ROOT / "assets" / "pdf"

SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
POST_NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
FENCE_RE = re.compile(r"(^```.*?^```[ \t]*$)", re.M | re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
DISPLAY_MATH_RE = re.compile(r"(?ms)^[ \t]*\$\$[ \t]*\n.*?\n[ \t]*\$\$[ \t]*$")
INLINE_MATH_RE = re.compile(r"\$\$([^\n$]+?)\$\$")
POST_LINK_RE = re.compile(
    r"\]\(\s*/blog/\d{4}/\d{2}/([A-Za-z0-9_-]+)/?\s*\)"
)
# kramdown 块级 IAL（如 callout 的 {: .block-tip }）pandoc 不认识，上面整行删掉；
# 图片宽度 {: width="300"} 改成 pandoc 的 {width=300px}；站内 /assets/ 图片改成仓库内绝对路径。
IMG_WIDTH_RE = re.compile(r"\)\{:\s*width=\"?(\d+)\"?\s*\}")
SITE_ASSET_RE = re.compile(r"\]\(\s*/assets/")
CJK_FONT_PREFERENCE = (
    "Noto Serif CJK SC",
    "Noto Sans CJK SC",
    "Source Han Serif SC",
    "Source Han Sans SC",
    "FandolSong",
    "AR PL UMing CN",
    "WenQuanYi Zen Hei",
)


def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            raw = "".join(lines[1:index])
            body = "".join(lines[index + 1 :])
            data = yaml.safe_load(raw) or {}
            if not isinstance(data, dict):
                data = {}
            return data, body
    return {}, text


def load_series_meta() -> dict:
    if not SERIES_YML.exists():
        return {}
    raw = yaml.safe_load(SERIES_YML.read_text(encoding="utf-8")) or []
    meta = {}
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and str(item.get("slug") or "").strip():
                meta[str(item["slug"]).strip()] = item
    elif isinstance(raw, dict):
        for slug, item in raw.items():
            meta[str(slug)] = item if isinstance(item, dict) else {}
    return meta


def load_author() -> str:
    if PERSONAL_YML.exists():
        data = yaml.safe_load(PERSONAL_YML.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict) and data.get("name"):
            return str(data["name"]).strip()
    return "吴嘉顺"


def series_order(value) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"-?\d+", value.strip()):
        return int(value.strip())
    return 0


def collect_posts() -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    if not POSTS_DIR.exists():
        return grouped
    for path in sorted(POSTS_DIR.glob("*.md")):
        data, body = split_front_matter(path.read_text(encoding="utf-8"))
        slug = str(data.get("series") or "").strip()
        if not slug:
            continue
        match = POST_NAME_RE.match(path.name)
        anchor = match.group(2) if match else path.stem
        date_text = ""
        if match:
            year, month, day = match.group(1).split("-")
            date_text = f"{year}年{int(month):02d}月{int(day):02d}日"
        elif data.get("date"):
            date_text = str(data["date"])
        grouped.setdefault(slug, []).append(
            {
                "title": str(data.get("title") or anchor),
                "order": series_order(data.get("series_order")),
                "date_text": date_text,
                "date_sort": match.group(1) if match else "",
                "anchor": anchor,
                "body": body,
                "path": path,
            }
        )
    for posts in grouped.values():
        posts.sort(key=lambda post: (post["order"], post["date_sort"], post["anchor"]))
    return grouped


def _protect(pattern: re.Pattern, text: str, token: str, store: list[str]) -> str:
    def hold(match: re.Match) -> str:
        store.append(match.group(0))
        return f"\x00{token}{len(store) - 1}\x00"

    return pattern.sub(hold, text)


def _restore(text: str, token: str, store: list[str]) -> str:
    for index, chunk in enumerate(store):
        text = text.replace(f"\x00{token}{index}\x00", chunk)
    return text


def adapt_markdown_for_pandoc(text: str) -> str:
    """把 kramdown 行内公式改成 pandoc 行内公式，并把站内文章链接改成 PDF 锚点。"""
    pieces = FENCE_RE.split(text)
    converted = []
    for piece in pieces:
        if piece.startswith("```"):
            converted.append(piece)
            continue
        inline_code: list[str] = []
        displays: list[str] = []
        segment = _protect(INLINE_CODE_RE, piece, "CODE", inline_code)
        segment = _protect(DISPLAY_MATH_RE, segment, "DISP", displays)
        segment = INLINE_MATH_RE.sub(r"$\1$", segment)
        segment = POST_LINK_RE.sub(r"](#\1)", segment)
        segment = re.sub(r"(?m)^\{:[^}\n]*\}[ \t]*\n?", "", segment)
        segment = IMG_WIDTH_RE.sub(r"){width=\1px}", segment)
        segment = SITE_ASSET_RE.sub(lambda m: "](" + str(ROOT) + "/assets/", segment)
        segment = _restore(segment, "DISP", displays)
        segment = _restore(segment, "CODE", inline_code)
        converted.append(segment)
    text = "".join(converted)
    text = text.replace("<!--more-->", "")
    return text


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def build_combined_markdown(slug: str, meta: dict, posts: list[dict], author: str) -> str:
    title = str(meta.get("title") or slug).strip()
    description = str(meta.get("description") or "").strip()
    lines = [
        "---",
        f"title: {yaml_string(title)}",
        f"author: {yaml_string(author)}",
        f"date: {dt.date.today().isoformat()}",
        "---",
        "",
        "本 PDF 按 `series_order` 合并该系列的网页文章，由 pandoc 与 XeLaTeX 生成。网页上各篇仍分页显示，并带有目录与上一篇 / 下一篇。",
        "",
    ]
    if description:
        lines.extend([description, ""])
    for post in posts:
        lines.append(f"# {post['title']} {{#{post['anchor']}}}")
        lines.append("")
        if post["date_text"]:
            lines.extend([f"*{post['date_text']}*", ""])
        lines.extend([adapt_markdown_for_pandoc(post["body"]).strip(), "", ""])
    return "\n".join(lines).rstrip() + "\n"


def list_font_families() -> set[str]:
    if not shutil.which("fc-list"):
        return set()
    try:
        output = subprocess.check_output(
            ["fc-list", ":lang=zh", "family"],
            text=True,
            errors="replace",
        )
    except (OSError, subprocess.CalledProcessError):
        return set()
    families = set()
    for line in output.splitlines():
        for part in line.split(","):
            name = part.strip()
            if name:
                families.add(name)
    return families


def detect_cjk_font() -> str:
    families = list_font_families()
    for name in CJK_FONT_PREFERENCE:
        if name in families:
            return name
    for name in sorted(families):
        if "CJK SC" in name or name.startswith("Source Han"):
            return name
    raise SystemExit(
        "找不到中文字体。请安装 fonts-noto-cjk（需要 Noto Serif CJK SC 或 Noto Sans CJK SC），然后重跑。"
    )


def require_tool(name: str, hint: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"找不到 {name}。{hint}")


def build_pdf(slug: str, markdown: str, font: str) -> Path:
    if not SLUG_RE.fullmatch(slug):
        raise RuntimeError(f"系列 slug 只能包含字母、数字、连字符和下划线：{slug}")
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    output = PDF_DIR / f"{slug}.pdf"
    with tempfile.TemporaryDirectory(prefix="series-pdf-") as tmp:
        source = Path(tmp) / f"{slug}.md"
        source.write_text(markdown, encoding="utf-8")
        command = [
            "pandoc",
            str(source),
            "--from=markdown",
            "--pdf-engine=xelatex",
            "--toc",
            "--toc-depth=2",
            "--number-sections",
            "-V",
            "papersize=a4",
            "-V",
            "geometry:margin=2.4cm",
            "-V",
            "colorlinks=true",
            "-V",
            f"CJKmainfont={font}",
            "-o",
            str(output),
        ]
        print(f"==> {slug}: pandoc → {output.relative_to(ROOT)}", flush=True)
        print("    " + " ".join(command[:8]) + " ...", flush=True)
        result = subprocess.run(command, text=True, capture_output=True)
        if result.stdout.strip():
            print(result.stdout)
        if result.stderr.strip():
            print(result.stderr, file=sys.stderr)
        if result.returncode != 0:
            raise RuntimeError(f"{slug} 的 PDF 生成失败（pandoc 退出码 {result.returncode}）")
    if not output.exists() or output.stat().st_size < 1000:
        raise RuntimeError(f"{slug} 的 PDF 没有写出来或文件过小：{output}")
    print(f"    完成，{output.stat().st_size} 字节", flush=True)
    return output


def self_test() -> None:
    sample = """\
见 $$a_i$$ 与 $$\\mathcal{X}_{ijk}$$。

$$
\\| \\mathcal{X} \\|_F = \\sqrt{\\sum_i a_i}
$$

行内代码 `$$not math$$` 保持不变。

```python
def keep():
    return "$$a_i$$"
```

下一篇是[展开](/blog/2026/03/tensor-matricization/)。

> **提示**
>
> callout 正文
{: .block-tip }

![a.png](/assets/img/a.png){: width="300"}
"""
    converted = adapt_markdown_for_pandoc(sample)
    checks = [
        ("$a_i$" in converted, "行内公式应变成单个 $"),
        ("$\\mathcal{X}_{ijk}$" in converted, "带下标的行内公式应保留反斜杠"),
        ("\n$$\n" in converted or converted.count("$$") >= 2, "显示公式的 $$ 应保留"),
        ('return "$$a_i$$"' in converted, "围栏代码里的 $$ 不能改"),
        ("`$$not math$$`" in converted, "行内代码里的 $$ 不能改"),
        ("](#tensor-matricization)" in converted, "站内文章链接应改成 PDF 锚点"),
        ("/blog/2026/03/" not in converted, "正文里的系列链接应被替换"),
        ("{: .block-tip }" not in converted, "kramdown IAL 行应删除"),
        ("{width=300px}" in converted, "图片宽度应改成 pandoc 写法"),
        (f"]({ROOT}/assets/img/a.png)" in converted, "站内图片应指向仓库文件"),
    ]
    failed = [message for ok, message in checks if not ok]
    if failed:
        print(converted)
        raise SystemExit("公式转换自检失败：\n- " + "\n- ".join(failed))
    matter, body = split_front_matter("---\ntitle: \"一\"\nseries: demo\nseries_order: 2\n---\n\n正文 $$x$$\n")
    if matter.get("series") != "demo" or series_order(matter.get("series_order")) != 2:
        raise SystemExit("front matter 解析自检失败")
    if "$$x$$" not in body:
        raise SystemExit("front matter 剥离自检失败")
    print("self-test ok")


def main() -> None:
    parser = argparse.ArgumentParser(description="为每个文章系列生成合订 PDF")
    parser.add_argument("--self-test", action="store_true", help="只检查 Markdown 转换，不调用 pandoc")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return

    require_tool("pandoc", "CI 镜像需要安装 pandoc。")
    require_tool("xelatex", "CI 镜像需要 texlive-xetex，以便用 XeLaTeX 排中文和公式。")
    font = detect_cjk_font()
    print(f"使用中文字体：{font}")

    meta = load_series_meta()
    grouped = collect_posts()
    author = load_author()
    if not grouped:
        print("没有带 series 字段的文章，跳过 PDF。")
        return

    for slug, info in meta.items():
        if slug not in grouped:
            print(f"::warning::系列 {slug} 在 _data/series.yml 中，但没有文章。", file=sys.stderr)

    failures = []
    for slug in list(meta.keys()) + sorted(set(grouped) - set(meta)):
        posts = grouped.get(slug)
        if not posts:
            continue
        print(f"==> 系列 {slug}：{len(posts)} 篇")
        for post in posts:
            print(f"    {post['order']:>3}  {post['path'].name}")
        try:
            markdown = build_combined_markdown(slug, meta.get(slug, {}), posts, author)
            build_pdf(slug, markdown, font)
        except Exception as exc:  # noqa: BLE001 — 汇总后一次性失败，日志里保留每一份
            failures.append(f"{slug}: {exc}")
            print(f"::error::{exc}", file=sys.stderr)

    if failures:
        print("PDF 生成失败：", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
