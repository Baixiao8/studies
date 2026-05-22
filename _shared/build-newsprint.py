#!/usr/bin/env python3
"""
NEWSPRINT THEME BUILDER · 报刊风浅色版生成器

把暗色版章节 HTML 转换成 Newsprint 浅色版预览页。

工作流:
1. 读章节原始 HTML(reports/.../chapters/chXX.html)
2. SVG 颜色批量反色(暗色→浅色)
3. 章节内容包装进 Newsprint masthead + 章节标题 + footer
4. 输出独立 HTML 预览页

用法:
  python3 _shared/build-newsprint.py <chapter_html> <output_path>
例如:
  python3 _shared/build-newsprint.py reports/2026-05-running-science/chapters/ch01.html preview-newsprint-ch1.html
"""

import re
import sys
from pathlib import Path


# ─── SVG 颜色映射(暗色 → Newsprint 浅色) ─────────────────
SVG_COLOR_MAP = {
    # 暗色背景下的米白线条/文字 → 浅色背景下的深灰墨色
    '#e8e4d8': '#1a1a1a',      # 主文字米白 → 标题黑
    '"#e8e4d8"': '"#1a1a1a"',
    '#a39e8d': '#4a4a4a',      # 软米白(次级文字) → 描述灰
    '#6a665a': '#888888',      # 暗米白 → 日期灰
    '#3d3d36': '#c4bca4',      # 暗分隔线 → 浅纸张分隔线
    '#2e2e29': '#d4cdb5',      # 更暗分隔线
    '#1e1e1a': '#ebe5d3',      # 卡片深底 → 软纸张色

    # 强调色:金色 → 报刊红
    '#d4a548': '#a8423b',
    '"#d4a548"': '"#a8423b"',
    '#8a6f3a': '#7a3530',      # 暗金 → 深红棕

    # 学科色调整为印刷低饱和版
    '#b54848': '#a8423b',      # 力学红 → 报刊红
    '#d57979': '#a8423b',      # 反共识高亮红
    '#c47f17': '#7a5230',      # 训练橙 → 印刷棕
    '#e0a25a': '#7a5230',      # 浅训练橙
    '#4a6fa5': '#1f3a5f',      # 生理蓝 → 报刊蓝
    '#8fb8df': '#1f3a5f',      # 浅生理蓝
    '#6a8b3d': '#4a6b3a',      # 力量绿
    '#a3cca3': '#4a6b3a',
    '#9c4bb5': '#5c3a6b',      # 神经紫
    '#c084d8': '#5c3a6b',
    '#3d8b6e': '#3a6b5c',      # 恢复青绿
    '#6db8a0': '#3a6b5c',
    '#d97a3c': '#7a5230',      # 营养橙 → 印刷棕
    '#b56565': '#a8423b',      # 伤病红
    '#c93f3f': '#a8423b',      # 比赛红
}


def remap_svg_colors(html: str) -> str:
    """批量替换 SVG 内的颜色值"""
    for old, new in SVG_COLOR_MAP.items():
        html = html.replace(old, new)
    return html


def fix_asset_paths(html: str) -> str:
    """从 chapters/ 装配到根目录预览页,assets/ 路径要加前缀"""
    # ch01.html 用 src="assets/..."(相对于装配后的 reports/.../index.html)
    # preview-newsprint-ch1.html 在仓库根目录,需要完整路径
    return html.replace(
        'src="assets/',
        'src="reports/2026-05-running-science/assets/'
    )


def extract_section_content(html: str) -> tuple:
    """从 <section>...</section> 里提取内容 (返回 inner HTML)"""
    m = re.search(r'<section[^>]*>(.*?)</section>', html, re.DOTALL)
    if not m:
        return None, html
    return m.group(0), m.group(1)


def render_newsprint_page(chapter_html: str, chapter_num: str, chapter_title: str) -> str:
    """生成完整的 Newsprint 预览页"""

    # 1. 提取章节内容
    full_section, inner = extract_section_content(chapter_html)
    if not full_section:
        return None

    # 2. SVG 颜色反色
    inner = remap_svg_colors(inner)

    # 2.5. 修正图片路径(根目录预览页需要完整路径)
    inner = fix_asset_paths(inner)

    # 3. 去掉原 section-tag/section-h/section-sub (我们用 Newsprint 风格重新做标题区)
    # 实际上保留原 .section-tag/.section-h/.section-sub,但 CSS 改成 Newsprint 浅色样式
    # 这样 HTML 结构不动,只换皮

    # 章节内容包装在新的 Newsprint container 里
    return PAGE_TEMPLATE.format(
        chapter_num=chapter_num,
        chapter_title=chapter_title,
        inner=inner
    )


# ─── 整页模板 ─────────────────────────────────────────────
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{chapter_title} · Newsprint 试点 · 跑步的科学解构</title>
<meta name="description" content="Newsprint 浅色版试点 · 第 {chapter_num} 章">
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --paper: #f0ebdd;          /* 泛黄纸张 */
    --paper-soft: #ebe5d3;
    --paper-deep: #e1d9bf;
    --ink: #1a1a1a;            /* 标题黑 */
    --ink-soft: #2c2c2c;       /* 正文 */
    --ink-mid: #4a4a4a;        /* 描述 */
    --ink-tertiary: #6e6e6e;
    --ink-faint: #888888;      /* 日期灰 */
    --line: #1a1a1a;
    --line-soft: #c4bca4;      /* 浅分隔线 */
    --red: #a8423b;            /* 报刊红 */
    --blue: #1f3a5f;
    --green: #4a6b3a;
    --brown: #7a5230;
    --purple: #5c3a6b;
    --teal: #3a6b5c;

    /* callout 颜色 */
    --c-sharp-bg: rgba(168, 66, 59, 0.06);
    --c-sharp-line: var(--red);
    --c-ops-bg: rgba(58, 107, 92, 0.06);
    --c-ops-line: var(--teal);
    --c-you-bg: rgba(92, 58, 107, 0.06);
    --c-you-line: var(--purple);
    --c-note-bg: rgba(60, 60, 60, 0.04);
    --c-note-line: var(--ink-faint);
    --c-story-bg: rgba(122, 82, 48, 0.07);
    --c-story-line: var(--brown);

    /* 学科色(印刷低饱和版) */
    --c-theory: #a8423b;       /* 力学红 */
    --c-physio: #1f3a5f;       /* 生理蓝 */
    --c-strength: #4a6b3a;     /* 力量/解剖绿 */
    --c-session: #7a5230;      /* 训练橙→棕 */
    --c-nutrition: #7a5230;
    --c-recovery: #3a6b5c;
    --c-psych: #5c3a6b;
    --c-injury: #a8423b;
    --c-race: #a8423b;
    --accent: var(--red);
    --accent-soft: #7a3530;
    --ink: var(--ink);
    --ink-soft: var(--ink-mid);
    --ink-faint: var(--ink-faint);
    --bg: var(--paper);
    --bg-card: var(--paper-soft);
    --bg-deep: var(--paper-deep);
    --bg-soft: var(--paper-soft);
    --line-strong: var(--ink);
  }}

  html {{ scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }}

  body {{
    background: var(--paper);
    color: var(--ink-soft);
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                 -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.72;
    min-height: 100vh;
  }}

  /* 纸张纹理 */
  body::before {{
    content: "";
    position: fixed;
    inset: 0;
    background-image:
      radial-gradient(circle at 25% 25%, rgba(0,0,0,0.012) 1px, transparent 1px),
      radial-gradient(circle at 75% 75%, rgba(0,0,0,0.012) 1px, transparent 1px);
    background-size: 4px 4px;
    pointer-events: none;
    z-index: 0;
  }}

  .page {{
    max-width: 880px;          /* 比首页窄,优化长文阅读宽度 */
    margin: 0 auto;
    padding: 24px 28px 80px;
    position: relative;
    z-index: 1;
  }}

  /* ─── 简化报头 ─── */
  .masthead {{
    border-top: 1px solid var(--line);
    border-bottom: 3px double var(--line);
    padding: 10px 0 8px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: "JetBrains Mono", monospace;
    font-size: 10.5px;
    letter-spacing: 0.16em;
    color: var(--ink-faint);
    text-transform: uppercase;
  }}
  .masthead-left a {{
    color: var(--ink);
    font-weight: 700;
    text-decoration: none;
    letter-spacing: 0.04em;
  }}
  .masthead-left a:hover {{ color: var(--red); }}

  /* ─── 章节标题区(替代原 section-tag/section-h/section-sub) ─── */
  .container {{ }}

  .section-tag {{
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.22em;
    color: var(--red);
    text-transform: uppercase;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .section-tag .num {{
    background: var(--ink);
    color: var(--paper);
    padding: 3px 9px;
    font-weight: 700;
    letter-spacing: 0.06em;
  }}

  .section-h {{
    font-family: "Inter Tight", -apple-system, "PingFang SC", sans-serif;
    font-weight: 800;
    font-size: 56px;
    line-height: 1.05;
    letter-spacing: -0.028em;
    color: var(--ink);
    margin-bottom: 12px;
  }}
  .section-h .en {{
    display: block;
    font-family: "Inter Tight", sans-serif;
    font-weight: 500;
    font-style: italic;
    font-size: 22px;
    color: var(--ink-mid);
    margin-top: 8px;
    letter-spacing: -0.012em;
  }}

  .section-sub {{
    font-size: 16px;
    color: var(--ink-mid);
    line-height: 1.65;
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--line-soft);
  }}

  /* ─── 子标题 ─── */
  h3 {{
    font-family: "Inter Tight", sans-serif;
    font-weight: 800;
    font-size: 28px;
    color: var(--ink);
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin: 48px 0 14px;
    padding-top: 28px;
    border-top: 3px double var(--line);
  }}
  h3 .pre {{
    display: inline-block;
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--red);
    margin-right: 12px;
    vertical-align: middle;
  }}
  h4 {{
    font-family: "Inter Tight", sans-serif;
    font-weight: 700;
    font-size: 19px;
    color: var(--ink);
    letter-spacing: -0.012em;
    margin: 28px 0 10px;
  }}

  /* ─── 正文 ─── */
  p {{
    font-size: 16px;
    line-height: 1.78;
    color: var(--ink-soft);
    margin: 0 0 16px;
  }}
  p.lead {{
    font-size: 18px;
    color: var(--ink-mid);
    line-height: 1.68;
    margin-bottom: 22px;
  }}
  strong {{ color: var(--ink); font-weight: 700; }}
  em {{ color: var(--ink); font-style: italic; }}
  ul, ol {{ margin: 0 0 18px 22px; }}
  ul li, ol li {{ font-size: 15.5px; line-height: 1.72; margin: 6px 0; color: var(--ink-soft); }}
  ul li::marker {{ color: var(--ink-faint); }}
  ol li::marker {{ color: var(--red); font-family: "JetBrains Mono", monospace; font-weight: 700; }}

  /* ─── TLDR ─── */
  .tldr {{
    margin: 28px 0;
    padding: 22px 26px;
    background: var(--paper-soft);
    border-left: 3px solid var(--ink);
    border-right: 1px solid var(--line-soft);
    border-top: 1px solid var(--line-soft);
    border-bottom: 1px solid var(--line-soft);
  }}
  .tldr .label {{
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.22em;
    color: var(--red);
    text-transform: uppercase;
    margin-bottom: 10px;
  }}
  .tldr p {{
    font-family: "Inter Tight", sans-serif;
    font-weight: 600;
    font-size: 21px;
    line-height: 1.45;
    color: var(--ink);
    letter-spacing: -0.015em;
    margin: 0;
  }}

  /* ─── Callout 系列 ─── */
  .callout {{
    margin: 24px 0;
    padding: 18px 22px;
    background: var(--paper-soft);
    border-left: 3px solid var(--ink-faint);
    position: relative;
  }}
  .callout .label {{
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.2em;
    color: var(--ink-faint);
    text-transform: uppercase;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .callout p {{
    font-size: 15px;
    line-height: 1.7;
    margin: 6px 0;
  }}

  .callout.sharp {{ background: var(--c-sharp-bg); border-left-color: var(--red); }}
  .callout.sharp .label {{ color: var(--red); }}
  .callout.sharp .label::before {{ content: "✕"; }}

  .callout.ops {{ background: var(--c-ops-bg); border-left-color: var(--teal); }}
  .callout.ops .label {{ color: var(--teal); }}
  .callout.ops .label::before {{ content: "✓"; }}

  .callout.you {{ background: var(--c-you-bg); border-left-color: var(--purple); }}
  .callout.you .label {{ color: var(--purple); }}
  .callout.you .label::before {{ content: "◐"; }}

  .callout.note {{ background: var(--c-note-bg); border-left-color: var(--ink-faint); }}
  .callout.note .label::before {{ content: "i"; font-style: italic; }}

  .callout.story {{ background: var(--c-story-bg); border-left-color: var(--brown); }}
  .callout.story .label {{ color: var(--brown); }}
  .callout.story .label::before {{ content: "◆"; }}
  .callout.story p {{
    font-size: 16px;
    font-style: italic;
    color: var(--ink-soft);
    line-height: 1.7;
  }}

  /* ─── Number Strip ─── */
  .number-strip {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    margin: 28px 0;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
  }}
  .number-strip .item {{
    padding: 18px 16px;
    border-right: 1px solid var(--line-soft);
  }}
  .number-strip .item:last-child {{ border-right: none; }}
  .number-strip .label {{
    font-family: "JetBrains Mono", monospace;
    font-size: 9.5px;
    font-weight: 600;
    letter-spacing: 0.2em;
    color: var(--ink-faint);
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  .number-strip .num {{
    font-family: "Inter Tight", sans-serif;
    font-weight: 800;
    font-size: 32px;
    line-height: 1;
    color: var(--ink);
    letter-spacing: -0.025em;
    font-feature-settings: "tnum";
  }}
  .number-strip .sub {{
    font-size: 12px;
    color: var(--ink-tertiary);
    margin-top: 6px;
    line-height: 1.4;
  }}

  /* ─── SVG 矢量图 ─── */
  .svg-frame {{
    margin: 32px 0;
    padding: 20px;
    background: var(--paper-soft);
    border: 1px solid var(--line-soft);
    overflow-x: auto;
  }}
  .svg-frame svg {{ display: block; width: 100%; min-width: 540px; }}
  .svg-caption {{
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    letter-spacing: 0.16em;
    color: var(--ink-faint);
    text-align: center;
    text-transform: uppercase;
    margin-top: 14px;
    padding-top: 10px;
    border-top: 1px solid var(--line-soft);
  }}
  svg text {{ font-family: "JetBrains Mono", monospace; }}

  /* ─── 表格 ─── */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 24px 0;
    font-size: 14.5px;
    border-top: 3px double var(--line);
    border-bottom: 3px double var(--line);
  }}
  th {{
    text-align: left;
    font-family: "JetBrains Mono", monospace;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.18em;
    color: var(--ink);
    padding: 10px 12px;
    border-bottom: 1px solid var(--line);
    background: var(--paper-soft);
    text-transform: uppercase;
  }}
  td {{
    padding: 11px 12px;
    border-bottom: 1px solid var(--line-soft);
    color: var(--ink-soft);
    line-height: 1.55;
    font-size: 14px;
  }}
  td.mono-cell {{ font-family: "JetBrains Mono", monospace; font-size: 13px; color: var(--red); }}

  /* ─── Card / Grid ─── */
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; margin: 24px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }}
  .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; margin: 24px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }}
  .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; margin: 24px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }}

  .card {{
    padding: 18px 20px;
    border-right: 1px solid var(--line-soft);
  }}
  .grid-2 .card:nth-child(2n), .grid-3 .card:nth-child(3n), .grid-4 .card:nth-child(4n) {{ border-right: none; }}
  .card h4 {{ font-size: 15px; color: var(--red); margin: 0 0 10px; }}
  .card p {{ font-size: 13.5px; line-height: 1.6; margin: 4px 0; }}
  .card .big {{
    font-family: "Inter Tight", sans-serif;
    font-weight: 800;
    font-size: 36px;
    line-height: 1;
    color: var(--ink);
    margin: 8px 0 6px;
    letter-spacing: -0.025em;
  }}
  .card .unit {{ font-size: 13px; color: var(--ink-faint); font-family: "JetBrains Mono", monospace; }}
  .card .desc {{ font-size: 13px; color: var(--ink-tertiary); line-height: 1.55; }}

  /* ─── Chip / Term ─── */
  .chip {{
    display: inline-block;
    padding: 2px 7px;
    font-family: "JetBrains Mono", monospace;
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 0.04em;
    background: var(--paper-soft);
    color: var(--ink);
    border: 1px solid var(--line-soft);
    line-height: 1.5;
    vertical-align: baseline;
  }}
  .term {{
    color: var(--ink);
    border-bottom: 1px dashed var(--ink-faint);
    cursor: help;
  }}
  .mono {{ font-family: "JetBrains Mono", monospace; font-size: 0.9em; color: var(--ink-mid); }}
  .ref {{ font-family: "JetBrains Mono", monospace; font-size: 10.5px; color: var(--ink-faint); letter-spacing: 0.04em; }}

  /* ─── Status list ─── */
  .status-list {{ list-style: none; padding: 0; margin: 18px 0; }}
  .status-list li {{
    padding: 6px 0 6px 28px;
    position: relative;
    border-bottom: 1px solid var(--line-soft);
    font-size: 14.5px;
    line-height: 1.6;
  }}
  .status-list li:last-child {{ border-bottom: none; }}
  .status-list li::before {{
    position: absolute;
    left: 0;
    top: 6px;
    font-family: "JetBrains Mono", monospace;
    font-size: 14px;
    font-weight: 700;
  }}
  .status-list li.do::before {{ content: "✓"; color: var(--teal); }}
  .status-list li.dont::before {{ content: "✕"; color: var(--red); }}
  .status-list li.warn::before {{ content: "!"; color: var(--brown); }}

  /* ─── Chapter recap ─── */
  .chapter-recap {{
    margin: 48px 0 24px;
    padding: 28px 32px;
    background: var(--paper-soft);
    border-top: 3px double var(--line);
    border-bottom: 3px double var(--line);
  }}
  .chapter-recap .label {{
    font-family: "JetBrains Mono", monospace;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.22em;
    color: var(--red);
    text-transform: uppercase;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .chapter-recap .label::before {{ content: "★"; }}
  .chapter-recap h4 {{
    font-family: "Inter Tight", sans-serif;
    font-weight: 800;
    font-size: 22px;
    color: var(--ink);
    letter-spacing: -0.018em;
    margin: 0 0 14px;
  }}
  .chapter-recap ol {{
    list-style: none;
    counter-reset: recap;
    padding: 0;
    margin: 0;
  }}
  .chapter-recap ol li {{
    counter-increment: recap;
    padding: 8px 0 8px 28px;
    border-bottom: 1px solid var(--line-soft);
    position: relative;
    font-size: 14.5px;
    line-height: 1.6;
  }}
  .chapter-recap ol li:last-child {{ border-bottom: none; }}
  .chapter-recap ol li::before {{
    content: counter(recap, decimal-leading-zero);
    position: absolute;
    left: 0;
    top: 8px;
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 700;
    color: var(--red);
  }}

  /* ─── Reading meta ─── */
  .reading-meta {{
    display: flex;
    gap: 22px;
    padding: 10px 0;
    margin: 14px 0 28px;
    border-top: 1px solid var(--line-soft);
    border-bottom: 1px solid var(--line-soft);
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    letter-spacing: 0.16em;
    color: var(--ink-faint);
    text-transform: uppercase;
    flex-wrap: wrap;
  }}
  .reading-meta .meta-item {{ display: flex; align-items: center; gap: 6px; }}

  /* ─── Compare 2 ─── */
  .compare-2 {{
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    margin: 24px 0;
    border: 1px solid var(--line);
  }}
  .compare-2 .col {{ padding: 16px 18px; }}
  .compare-2 .col.primary {{ background: var(--paper-soft); }}
  .compare-2 .divider {{ width: 1px; background: var(--line-soft); }}

  /* ─── Footer ─── */
  .footer {{
    margin-top: 56px;
    padding: 24px 0 8px;
    border-top: 3px double var(--line);
    text-align: center;
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    color: var(--ink-faint);
    text-transform: uppercase;
    line-height: 1.8;
  }}
  .footer a {{ color: var(--ink-mid); text-decoration: underline; }}
  .footer a:hover {{ color: var(--red); }}

  /* ─── 试点条幅 ─── */
  .trial-banner {{
    background: var(--red);
    color: var(--paper);
    padding: 14px 28px;
    margin: -24px -28px 28px;
    font-family: "JetBrains Mono", monospace;
    font-size: 10.5px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    text-align: center;
  }}
  .trial-banner a {{ color: var(--paper); text-decoration: underline; }}

  /* ─── Responsive ─── */
  @media (max-width: 720px) {{
    .page {{ padding: 16px 18px 60px; }}
    .trial-banner {{ margin: -16px -18px 24px; padding: 12px 18px; font-size: 9.5px; letter-spacing: 0.14em; }}
    .section-h {{ font-size: 36px; }}
    .section-h .en {{ font-size: 16px; }}
    .section-sub {{ font-size: 14.5px; }}
    p {{ font-size: 15.5px; line-height: 1.78; }}
    p.lead {{ font-size: 16.5px; }}
    h3 {{ font-size: 22px; margin: 40px 0 12px; padding-top: 24px; }}
    h4 {{ font-size: 17px; }}
    .tldr {{ padding: 18px 20px; }}
    .tldr p {{ font-size: 18px; }}
    .callout {{ padding: 16px 18px; }}
    .number-strip {{ grid-template-columns: 1fr 1fr; }}
    .number-strip .item:nth-child(2) {{ border-right: none; }}
    .number-strip .item:nth-child(1),
    .number-strip .item:nth-child(2) {{ border-bottom: 1px solid var(--line-soft); }}
    .grid-2, .grid-3, .grid-4 {{ grid-template-columns: 1fr; }}
    .card {{ border-right: none; border-bottom: 1px solid var(--line-soft); }}
    .card:last-child {{ border-bottom: none; }}
    .chapter-recap {{ padding: 22px 22px; margin: 40px 0 20px; }}
    .chapter-recap h4 {{ font-size: 19px; }}
    .masthead {{ flex-direction: column; gap: 4px; }}
  }}
</style>
</head>
<body>

<main class="page">

  <div class="trial-banner">
    📰 试点版 · Newsprint 浅色风格 · <a href="https://baixiao8.github.io/studies/reports/2026-05-running-science/#s1" target="_blank">对照暗色版</a>
  </div>

  <!-- 简化报头 -->
  <header class="masthead">
    <div class="masthead-left">
      <a href="https://baixiao8.github.io/studies/preview-newsprint.html">← STUDIES 首页</a>
    </div>
    <div>跑步的科学解构 · 第 {chapter_num} 章 · 试点</div>
  </header>

  <!-- 章节内容(从原 ch01.html 抽取) -->
  {inner}

  <!-- 试点反馈区 -->
  <div class="callout note" style="margin-top: 56px;">
    <div class="label">试点 · 反馈点</div>
    <p>这是 Newsprint 浅色风格在长文阅读场景下的试点。如果你读完这章感觉<em>不疲劳、字号舒适、节奏好</em>,那我们可以把全 12 章迁移到这个风格。如果有任何不适(刺眼/小/拥挤/对比度问题),告诉我具体哪里。</p>
  </div>

  <!-- Footer -->
  <div class="footer">
    白笑研究报告库 · 第 01 期 · 2026 年 5 月 22 日<br>
    Newsprint 风格试点 · 第 {chapter_num} 章<br>
    <a href="https://baixiao8.github.io/studies/">baixiao8.github.io / studies</a>
  </div>

</main>

</body>
</html>
"""


# ─── Main ────────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python3 build-newsprint.py <chapter_html> <output_path>')
        sys.exit(1)

    chapter_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    chapter_html = chapter_path.read_text(encoding='utf-8')

    # 提取章节号(从 section id="sN" 或文件名)
    m = re.search(r'id="s(\d+)"', chapter_html)
    chapter_num = m.group(1).zfill(2) if m else '01'

    # 章节标题(从 h1.section-h)
    m_title = re.search(r'<h1 class="section-h">(.*?)<', chapter_html, re.DOTALL)
    chapter_title = m_title.group(1).strip() if m_title else f'第 {chapter_num} 章'

    output_html = render_newsprint_page(chapter_html, chapter_num, chapter_title)
    if output_html is None:
        print('错误:无法提取章节内容')
        sys.exit(1)

    output_path.write_text(output_html, encoding='utf-8')
    print(f'✓ 试点页生成: {output_path}')
    print(f'  章节: 第 {chapter_num} 章 - {chapter_title}')
    print(f'  文件大小: {output_path.stat().st_size:,} bytes')
