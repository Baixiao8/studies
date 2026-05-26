#!/bin/bash
# 一键安装本地构建工具 · Studies EPUB build environment
# 用法: cd 运动健康 && bash tools/setup.sh

set -e

# 切到项目根目录(以本脚本所在目录为参照)
cd "$(dirname "$0")/.."

echo "[1/4] 创建 Python 虚拟环境 tools/.venv ..."
python3 -m venv tools/.venv

echo "[2/4] 升级 pip ..."
tools/.venv/bin/pip install --upgrade pip --quiet

echo "[3/4] 装 Python 依赖(playwright / beautifulsoup4 / lxml)..."
tools/.venv/bin/pip install -r tools/requirements.txt --quiet

echo "[4/4] 装 Chromium 浏览器(~92 MB,几分钟)..."
tools/.venv/bin/playwright install chromium

echo ""
echo "✅ 安装完成"
echo ""
echo "用法:"
echo "  tools/.venv/bin/python3 _shared/build_epub.py reports/<slug>"
echo ""
echo "或者激活 venv:"
echo "  source tools/.venv/bin/activate"
echo "  python3 _shared/build_epub.py reports/<slug>"
echo "  deactivate"
