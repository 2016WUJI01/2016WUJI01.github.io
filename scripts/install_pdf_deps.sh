#!/usr/bin/env bash
# 在 ubuntu 上安装系列 PDF 所需的 pandoc、XeLaTeX 与中文字体。
# 供 GitHub Actions 调用；本地缺依赖时也可以手动执行。
set -euo pipefail

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  pandoc \
  texlive-xetex \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-lang-chinese \
  fonts-noto-cjk \
  lmodern \
  python3-yaml
