#!/usr/bin/env python3
"""obsidian2jekyll.py 的回归测试：python3 scripts/tests/test_obsidian2jekyll.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from obsidian2jekyll import ROOT, convert  # noqa: E402

used: list[str] = []
out = convert((HERE / "obsidian" / "sample.md").read_text(encoding="utf-8"), ROOT / "_posts", used)
checks = [
    ("[模式展开：把张量写成矩阵](/blog/2026/03/tensor-matricization/)" in out, "slug 链接应使用文章标题"),
    ("[记号](/blog/2026/03/tensor-notation/)" in out, "别名链接"),
    ("[CP 分解](/blog/2026/03/cp-decomposition/)" in out, "按 title 查找"),
    ("{: .block-tip }" in out and "{: .block-warning }" in out, "callout 类型"),
    ("$$\\|\\mathcal{X}\\|_F$$" in out, "行内公式"),
    ("![obsidian-test.png](/assets/img/obsidian-test.png)\n" in out, "原尺寸图片"),
    ('![obsidian-test.png](/assets/img/obsidian-test.png){: width="300"}' in out, "限宽图片"),
    ('s = "[[不转换]] $x$"' in out, "代码块保持原样"),
    ("[[" not in out.replace('"[[不转换]]', ""), "不应残留 [[ ]]"),
    (used == ["obsidian-test.png", "obsidian-test.png"], "记录用到的图片"),
]
bad = [m for ok, m in checks if not ok]
if bad:
    print(out)
    raise SystemExit("失败：" + "；".join(bad))
print("obsidian2jekyll ok")
