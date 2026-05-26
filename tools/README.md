# tools/ · 本地构建工具

> 这里是**只在你本机用**的构建工具,**不部署**到 GitHub Pages。

## 目录

- `.venv/` — Python 虚拟环境(自动生成,在 `.gitignore`,**不进 git**)
- `requirements.txt` — Python 依赖锁定
- `setup.sh` — 一键安装(创建 venv + 装依赖 + 装 Chromium)
- `README.md` — 本文件

## 首次安装

```bash
cd 运动健康
bash tools/setup.sh
```

约 3-5 分钟(Chromium ~92 MB 下载是大头)。Chromium 安装到 `~/Library/Caches/ms-playwright/`,跟项目无关。

## 跑构建

```bash
# 直接用 venv 里的 python
tools/.venv/bin/python3 _shared/build_epub.py reports/2026-05-running-science

# 或者激活 venv 再跑
source tools/.venv/bin/activate
python3 _shared/build_epub.py reports/2026-05-running-science
deactivate
```

## 工具职责

| 依赖 | 用途 |
|---|---|
| Playwright + Chromium | headless 浏览器,把 inline SVG / 复杂 `<table>` 渲染成 PNG 嵌入 EPUB |
| beautifulsoup4 + lxml | HTML 解析,提取章节 / 子节 / 内容 |

## 哪些进 git,哪些不进

| 项 | git? | 理由 |
|---|---|---|
| `requirements.txt` | ✅ 进 | 团队/未来的你要能复现环境 |
| `setup.sh` | ✅ 进 | 一键安装入口 |
| `README.md` | ✅ 进 | 文档 |
| `.venv/` | ❌ 不进 | 本地虚拟环境,每个 Mac 自己装 |
| Chromium 缓存 | ❌ 不进 | 在 `~/Library/Caches/` 而非项目内 |

## 重装 / 修复

如果 `.venv` 坏了 / Python 版本变了:

```bash
rm -rf tools/.venv
bash tools/setup.sh
```
