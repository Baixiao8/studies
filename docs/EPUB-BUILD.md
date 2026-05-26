# EPUB Build · 工作流文档

> 把 `reports/<slug>/` 装配成 EPUB 电子书,供微信读书 / Apple Books 等离线阅读 + 听书。
>
> 决策依据见 `PRD-epub-export-analysis.md` v1.6(2026-05-26 改为"决定做")。

---

## 一次性安装

```bash
cd 运动健康
bash tools/setup.sh
```

约 3-5 分钟。安装内容:

| 内容 | 位置 | 大小 |
|---|---|---|
| Python venv | `tools/.venv/` | ~50 MB |
| Playwright + bs4 + lxml | `tools/.venv/lib/` | ~30 MB |
| Chromium 浏览器 | `~/Library/Caches/ms-playwright/` | ~92 MB |

**Chromium 不进项目仓库**,只在你 Mac 本机。

---

## 跑构建

### 跑单个报告的 EPUB

```bash
tools/.venv/bin/python3 _shared/build_epub.py reports/2026-05-running-science
```

### 跟 HTML 一起 build(推荐,集成模式)

```bash
tools/.venv/bin/python3 _shared/build.py reports/2026-05-running-science
```

build.py 会先装配 HTML(`index.html`),然后自动调用 build_epub.py 生成 `<slug>.epub`。

### 输出

```
reports/<slug>/
├── index.html         (网页版,已有)
├── <slug>.epub        🆕 新增 EPUB 文件
├── parts/
├── chapters/
└── assets/
```

EPUB 文件通过 GitHub Pages 直接 serve,用户点首页「📥 EPUB」按钮即下载。

---

## EPUB 包含什么(完整书本版)

| 元素 | 处理 |
|---|---|
| 章节内容(h1 / h3 / p / em / strong) | 保留 |
| 章节封面图(`assets/chXX-hero.jpg`) | **嵌入** |
| inline SVG 数据图表 | **Chromium 渲染成 PNG 嵌入**(用 var(--c-theory) 等 CSS 变量正确渲染) |
| `<table>` 表格 | **Chromium 渲染成 PNG 嵌入**(保证视觉一致) |
| `.callout`(sharp / ops / you / story / protocol / stop) | 保留 + 简化样式 |
| `.tldr` / `.section-tag` / `.chip` / `.plain` | 保留 + 简化样式 |
| Tooltip(术语 hover) | 内嵌进文本(EPUB 无 JS) |
| Mini-TOC / 进度条 / Reader 听书组件 | 移除(EPUB reader 自带 nav + TTS) |

---

## 多级 TOC(听书节点跳转)

EPUB `nav.xhtml` 生成两级目录:

```
└── 01 章节大标题(从 h1.section-h)
    ├── 1.1 子节(从 h3 + .pre 编号)
    ├── 1.2 子节
    └── 1.3 子节
└── 02 章节大标题
    ├── 2.1 子节
    ...
```

微信读书 / Apple Books 等听书 APP 都能识别这种层级目录,**听书时可跳节点**。

---

## EPUB 大小预估

| 报告 | 字数 | 章节 hero | 内嵌 SVG/table 数 | 估 EPUB 大小 |
|---|---|---|---|---|
| 跑步科学 | 137K | 12 张 JPG | ~50 张 SVG → PNG | ~8-12 MB |
| 康复科学 | 220K | 12 张 JPG | ~60 张 SVG → PNG | ~10-15 MB |

GitHub 单文件限制 100 MB,**远远不到**。

---

## 微信读书导入

1. 在 Mac 上跑 `build.py`
2. push 到 GitHub Pages
3. 微信读书 APP 选「我」→「我的书架」→「导入图书」(或者 PC 端登录上传)
4. 选 `<slug>.epub` 文件
5. 导入后可听书 + 跳节点

---

## 文件结构(EPUB 内部)

```
<slug>.epub (zip)
├── mimetype                            ← "application/epub+zip"(不压缩)
├── META-INF/
│   └── container.xml                   ← 指向 OEBPS/content.opf
└── OEBPS/
    ├── content.opf                     ← Manifest + Spine
    ├── nav.xhtml                       ← 多级 TOC
    ├── styles/
    │   └── main.css                    ← 内部样式
    ├── chapter01.xhtml ... chapter12.xhtml
    └── images/
        ├── ch01-hero.jpg
        ├── ch01-fig-01.png             ← SVG / table 渲染图
        └── ...
```

---

## 故障排查

### 问题:Playwright 报错 "Executable doesn't exist"

```bash
tools/.venv/bin/playwright install chromium
```

### 问题:venv 坏了

```bash
rm -rf tools/.venv
bash tools/setup.sh
```

### 问题:微信读书导入 EPUB 看不到节点

可能是 nav.xhtml 没生成多级 TOC。看 `<slug>.epub` 解压后的 `OEBPS/nav.xhtml` 是否有嵌套 `<ol>`。

### 问题:某个 SVG 渲染失败

跑 `tools/.venv/bin/python3 _shared/build_epub.py reports/<slug> --verbose` 看具体哪张失败,可能是 SVG 用了 Chromium 不支持的特性。

---

## CHANGELOG

| 日期 | 版本 | 改动 |
|---|---|---|
| 2026-05-26 | v1.0 | 初次实现 — 由 PRD v1.6 决策驱动 |
