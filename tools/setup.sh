#!/bin/bash
# 一键准备本地构建环境 · Studies EPUB build
#
# 资产分层(L2 工具链全局):
#   - venv 装在 ~/白笑/.tools/venvs/studies-build/(机器全局,一次装好所有项目共用)
#   - 各项目 tools/.venv 是软链接,指向上面那个全局位置
#   - chromium 装在 ~/Library/Caches/ms-playwright/(playwright 自带全局缓存)
#
# 用法:
#   cd <项目根> && bash tools/setup.sh
#
# 这个脚本在任何 studies 风格的项目里跑都一样:
#   - L2 全局 venv 已存在 → 只建 symlink(秒级)
#   - L2 全局 venv 不存在 → 创建 + 装包 + 装 chromium(3-5 分钟)

set -e

# ─── 路径定义 ─────────────────────────────────────────
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GLOBAL_TOOLS="$HOME/白笑/.tools"
GLOBAL_VENV="$GLOBAL_TOOLS/venvs/studies-build"
PROJECT_VENV="$PROJECT_ROOT/tools/.venv"

# ─── 1. 确保 L2 全局 venv 存在 ─────────────────────────
if [ -e "$GLOBAL_VENV/bin/python3" ] || [ -L "$GLOBAL_VENV/bin/python3" ]; then
    echo "[1/3] ✓ L2 全局 venv 已存在 · $GLOBAL_VENV"
else
    echo "[1/3] L2 全局 venv 不存在,创建中(只装一次,以后所有项目共用)..."
    mkdir -p "$GLOBAL_TOOLS/venvs"
    python3 -m venv "$GLOBAL_VENV"

    echo "      升级 pip..."
    "$GLOBAL_VENV/bin/pip" install --upgrade pip --quiet

    echo "      装 Python 依赖(playwright / bs4 / lxml)..."
    "$GLOBAL_VENV/bin/pip" install -r "$PROJECT_ROOT/tools/requirements.txt" --quiet

    echo "      装 Chromium 浏览器(~92 MB,3-5 分钟,共享缓存)..."
    "$GLOBAL_VENV/bin/playwright" install chromium

    # 顺手创建一份 README,告诉未来的自己这是啥
    if [ ! -f "$GLOBAL_TOOLS/README.md" ]; then
        cat > "$GLOBAL_TOOLS/README.md" << 'EOF'
# ~/白笑/.tools/ · 工具链全局目录

L2 资产分层:跨项目共享的构建工具,装一次所有项目共用。

各项目通过 symlink 接入:
    ln -s ~/白笑/.tools/venvs/studies-build <项目>/tools/.venv

不要 commit 进任何 git 仓——这是机器本地资产。
完整说明见 studies/PRINCIPLES.md 第十一节 · 资产分层。
EOF
    fi
fi

# ─── 2. 本项目软链接到 L2 ────────────────────────────
if [ -L "$PROJECT_VENV" ]; then
    EXISTING_TARGET=$(readlink "$PROJECT_VENV")
    if [ "$EXISTING_TARGET" = "$GLOBAL_VENV" ]; then
        echo "[2/3] ✓ 本项目 symlink 已指向 L2,无需变更"
    else
        echo "[2/3] symlink 已存在但指向了别处($EXISTING_TARGET),更新中..."
        rm "$PROJECT_VENV"
        ln -s "$GLOBAL_VENV" "$PROJECT_VENV"
    fi
elif [ -d "$PROJECT_VENV" ]; then
    echo "[2/3] 检测到本项目有<旧的真目录 venv>,重命名为 .venv.old 备份后切换到 L2..."
    mv "$PROJECT_VENV" "$PROJECT_VENV.old"
    ln -s "$GLOBAL_VENV" "$PROJECT_VENV"
    echo "      ⚠️  老 venv 备份在 $PROJECT_VENV.old(确认新版没问题可手动 rm -rf 删)"
else
    echo "[2/3] 建立本项目 symlink..."
    ln -s "$GLOBAL_VENV" "$PROJECT_VENV"
fi

# ─── 3. 验证 ────────────────────────────────────────
echo "[3/3] 验证 venv 可用..."
"$PROJECT_VENV/bin/python3" -c "from playwright.sync_api import sync_playwright; import bs4, lxml; print('      ✓ playwright + bs4', bs4.__version__, '+ lxml', lxml.__version__)"

echo ""
echo "✅ 准备完成"
echo ""
echo "用法:"
echo "  $PROJECT_VENV/bin/python3 _shared/build_epub.py reports/<slug>"
echo ""
echo "或激活 venv:"
echo "  source $PROJECT_VENV/bin/activate"
echo "  python3 _shared/build_epub.py reports/<slug>"
echo "  deactivate"
echo ""
echo "💡 L2 全局 venv 在 $GLOBAL_VENV"
echo "   要装新工具/升级版本,在 L2 里改一次,所有项目自动生效"
