#!/usr/bin/env python3
"""
RESEARCH REPORT BUILDER · v1.0

把 parts/00_hero.html + 05_intro.html + chapters/ch*.html + 95_antithesis.html + 99_footer.html
拼装成单页 HTML,并自动注入:
  - 章节阅读时间 (基于中文字数 ÷ 350 字/分钟)
  - 章节内目录 chapter-toc (从 h3 提取)
  - 章末 5 分钟回顾 (从 _recap.json 注入)

用法:
  python3 _shared/build.py <report_dir>
例如:
  python3 _shared/build.py reports/2026-05-running-science/

输出:
  <report_dir>/index.html
"""

import os
import re
import sys
import json
from pathlib import Path
from html.parser import HTMLParser


# ─── 配置 ──────────────────────────────────────────────────
CHARS_PER_MINUTE_CN = 350  # 中文阅读速度参考


# ─── SVG 颜色反色映射(暗色 → Newsprint 浅色) ────────────────
SVG_COLOR_MAP = {
    # 暗色背景下的米白线条/文字 → 浅色背景下的深灰墨色
    '#e8e4d8': '#1a1a1a',      # 主文字米白 → 标题黑
    '#a39e8d': '#4a4a4a',      # 软米白(次级文字) → 描述灰
    '#6a665a': '#888888',      # 暗米白 → 日期灰
    '#3d3d36': '#c4bca4',      # 暗分隔线 → 浅纸张分隔线
    '#2e2e29': '#d4cdb5',      # 更暗分隔线
    '#1e1e1a': '#ebe5d3',      # 卡片深底 → 软纸张色
    '#0e0e0c': '#f0ebdd',      # 主背景 → Newsprint 米黄
    '#1a1a17': '#ebe5d3',      # 副背景 → 浅纸张
    '#1a1a18': '#ebe5d3',      # 副背景变体

    # 强调色:金色 → 报刊红
    '#d4a548': '#a8423b',
    '#8a6f3a': '#7a3530',
    '#e8c068': '#a8423b',      # 进度条渐变色

    # 学科色 · 主色调整为印刷低饱和版
    '#b54848': '#a8423b',      # 力学红
    '#d57979': '#a8423b',      # 反共识高亮红 → 深红
    '#c47f17': '#7a5230',      # 训练橙
    '#e0a25a': '#7a5230',      # 浅训练橙
    '#4a6fa5': '#1f3a5f',      # 生理蓝
    '#8fb8df': '#1f3a5f',      # 浅生理蓝
    '#6a8b3d': '#4a6b3a',      # 力量绿
    '#a3cca3': '#4a6b3a',      # 浅力量绿
    '#9c4bb5': '#5c3a6b',      # 神经紫
    '#c084d8': '#5c3a6b',      # 浅神经紫
    '#c89ad8': '#5c3a6b',      # 紫色变体
    '#3d8b6e': '#3a6b5c',      # 恢复青绿
    '#6db8a0': '#3a6b5c',      # 浅恢复
    '#d97a3c': '#7a5230',      # 营养橙
    '#b56565': '#a8423b',      # 伤病粉红
    '#c93f3f': '#a8423b',      # 比赛红
    '#e89090': '#a8423b',      # 浅红变体(反共识)
    '#94cdcd': '#3a6b5c',      # 浅青(long 训练)
    '#e09b9b': '#a8423b',      # 浅红变体 2
    '#c8c89a': '#7a5230',      # 浅灰绿
    '#aac0c5': '#3a6b5c',      # 浅灰青

    # 进度/标志类
    '#5a7fa5': '#1f3a5f',      # post 蓝
}


def remap_svg_colors(html: str) -> str:
    """章节 HTML 里的 SVG 颜色批量反色为 Newsprint 浅色版"""
    for old, new in SVG_COLOR_MAP.items():
        html = html.replace(old, new)
    return html


# ─── 工具函数 ──────────────────────────────────────────────

def count_chinese_chars(html: str) -> int:
    """统计中文字符数(去除标签和英文)"""
    # 去 HTML 标签
    text = re.sub(r'<[^>]+>', ' ', html)
    # 去脚本/样式
    text = re.sub(r'<style[\s\S]*?</style>', ' ', text)
    text = re.sub(r'<script[\s\S]*?</script>', ' ', text)
    # 统计中文字符
    cn = re.findall(r'[一-鿿]', text)
    return len(cn)


def estimate_reading_time(html: str) -> int:
    """估算阅读时间(分钟,最少 1 分钟)"""
    chars = count_chinese_chars(html)
    minutes = max(1, round(chars / CHARS_PER_MINUTE_CN))
    return minutes


def extract_h3_list(html: str):
    """提取 h3 列表 [(id, num, text), ...] · 先抓 attrs 再抠 id"""
    # 匹配 <h3 ...attrs...>inner</h3>
    h3_pattern = re.compile(r'<h3([^>]*)>(.*?)</h3>', re.DOTALL)
    items = []
    for i, m in enumerate(h3_pattern.finditer(html), 1):
        attrs = m.group(1)
        inner = m.group(2)
        # 从 attrs 抠 id
        id_match = re.search(r'id="([^"]+)"', attrs)
        h3_id = id_match.group(1) if id_match else ''
        # 提取 .pre 编号
        pre_match = re.search(r'<span class="pre">([^<]+)</span>', inner)
        num = pre_match.group(1).strip() if pre_match else ''
        # 去掉 pre 取纯文本
        text = re.sub(r'<[^>]+>', '', inner)
        if pre_match:
            text = text.replace(pre_match.group(1), '', 1).strip()
        text = text.strip()
        items.append({'id': h3_id, 'num': num, 'text': text, 'idx': i})
    return items


def ensure_h3_ids(html: str, section_id: str) -> str:
    """给 section 内的 h3 加 id 如果没有"""
    counter = [0]
    def replace(m):
        counter[0] += 1
        full = m.group(0)
        if 'id=' in full:
            return full
        # 在 <h3 后面加 id
        new_id = f'{section_id}-h3-{counter[0]}'
        return re.sub(r'<h3', f'<h3 id="{new_id}"', full, count=1)
    return re.sub(r'<h3[^>]*>.*?</h3>', replace, html, flags=re.DOTALL)


def build_reading_meta(minutes: int, chars: int, h3_count: int) -> str:
    """生成 reading-meta HTML 片段"""
    return f'''
  <div class="reading-meta">
    <div class="meta-item"><span class="icon">◷</span><span class="value">约 {minutes} 分钟阅读</span></div>
    <div class="meta-item"><span class="icon">◆</span><span class="value">{chars:,} 字</span></div>
    <div class="meta-item"><span class="icon">§</span><span class="value">{h3_count} 个小节</span></div>
  </div>
'''


def build_chapter_toc(h3_list, section_id: str) -> str:
    """生成 chapter-toc(章节内目录)HTML 片段"""
    if len(h3_list) < 3:
        return ''  # 小节太少不需要 toc
    items_html = []
    for h3 in h3_list:
        num = h3['num']
        text = h3['text']
        h3_id = h3['id']
        items_html.append(
            f'    <li><a href="#{h3_id}"><span class="num">{num}</span>'
            f'<span class="title">{text}</span></a></li>'
        )
    return f'''
  <details class="chapter-toc" open>
    <summary class="label" style="cursor:pointer; list-style:none;">▾ 本章 {len(h3_list)} 节 · 点击跳转</summary>
    <ol>
{chr(10).join(items_html)}
    </ol>
  </details>
'''


def upgrade_final_note_to_recap(html: str, recap_data: dict, chapter_id: str) -> str:
    """
    把最后的 callout.note "本章核心命题"/"本章核心数学小结" 升级成 .chapter-recap,
    或在结尾插入新的 chapter-recap(如果 recap_data 中有 chapter_id 的回顾)
    """
    if chapter_id not in recap_data:
        return html

    recap = recap_data[chapter_id]
    recap_html = f'''
  <div class="chapter-recap">
    <div class="label">★ 5-MINUTE RECAP · 五分钟回顾</div>
    <h4>{recap['title']}</h4>
    <ol>
{chr(10).join(f"      <li>{point}</li>" for point in recap['points'])}
    </ol>
  </div>
'''
    # 插入到 ref 之前(如果有),否则插入到 </div></section> 之前
    if '<p class="ref">' in html:
        html = html.replace('<p class="ref">', recap_html + '\n  <p class="ref">', 1)
    else:
        # 在最后一个 </div></section> 之前插入
        html = html.replace('</div>\n</section>', recap_html + '\n</div>\n</section>', 1)
    return html


def wrap_tables_for_mobile(html: str) -> str:
    """给所有 <table> 自动包 <div class="table-wrap"> 让小屏可横向滚动"""
    # 已经在 .table-wrap 里的 table 跳过(避免重复包)
    def wrap(m):
        full = m.group(0)
        # 检查 table 前 80 字符是否已经有 table-wrap
        start = m.start()
        prefix = html[max(0, start-80):start]
        if 'class="table-wrap"' in prefix:
            return full
        return f'<div class="table-wrap">{full}</div>'
    return re.sub(r'<table[\s\S]*?</table>', wrap, html)


def inject_chapter_enhancements(html: str, recap_data: dict) -> str:
    """处理单个章节 HTML:加 ID、reading-meta、chapter-toc、5 分钟回顾、table wrap"""
    # 找到 section id
    sec_match = re.search(r'<section[^>]*\bid="(s\d+)"', html)
    if not sec_match:
        return html
    section_id = sec_match.group(1)

    # v6.1 修复:给 section 加 class="chapter"(让 CSS content-visibility + reader.js 都能识别)
    # 只在没有 class 时加(避免重复)
    html = re.sub(
        r'<section(\s+(?!class=)[^>]*)?id="(s\d+)"',
        lambda m: '<section' + (m.group(1) or '') + ' class="chapter" id="' + m.group(2) + '"',
        html,
        count=1
    )

    # -1) SVG 颜色反色:把暗色版 SVG 颜色批量映射成 Newsprint 浅色
    html = remap_svg_colors(html)

    # 0) 给所有 table 包 .table-wrap (移动端横向滚动)
    html = wrap_tables_for_mobile(html)

    # 1) 给 h3 加 id
    html = ensure_h3_ids(html, section_id)

    # 2) 提取 h3 列表
    h3_list = extract_h3_list(html)

    # 3) 计算 reading-meta
    chars = count_chinese_chars(html)
    minutes = max(1, round(chars / CHARS_PER_MINUTE_CN))
    reading_meta = build_reading_meta(minutes, chars, len(h3_list))

    # 4) 生成 chapter-toc
    chapter_toc = build_chapter_toc(h3_list, section_id)

    # 5) 注入位置:section-sub 之后
    # 寻找 </p>\n\n  <div class="tldr"> 这样的边界
    # 改为在 section-sub <p> 之后插入
    insert_block = reading_meta + chapter_toc
    # 在第一个 <div class="tldr"> 之前插入
    if '<div class="tldr">' in html:
        html = html.replace('<div class="tldr">', insert_block + '\n  <div class="tldr">', 1)
    elif '<p class="section-sub">' in html:
        # 在 section-sub 这段 p 之后插入
        html = re.sub(
            r'(<p class="section-sub">[^<]*</p>)',
            r'\1\n' + insert_block,
            html, count=1
        )

    # 6) 章末 5 分钟回顾(从 recap_data 注入)
    html = upgrade_final_note_to_recap(html, recap_data, section_id)

    return html


# ─── 主流程 ────────────────────────────────────────────────

def build_report(report_dir: Path, external: bool = False):
    """
    默认行为: inline 全部 CSS/JS/glossary 进 index.html (推荐,无外部依赖)
    external=True: 用 <link>/<script> 引用 _shared/ 下的文件 (调试用)
    """
    parts_dir = report_dir / 'parts'
    chapters_dir = report_dir / 'chapters'
    shared_dir = report_dir.parent.parent / '_shared'
    # 默认 inline,只在 --external 时不 inline
    embed = not external

    # 加载 recap 数据(如果存在)
    recap_file = parts_dir / '_recaps.json'
    recap_data = {}
    if recap_file.exists():
        recap_data = json.loads(recap_file.read_text(encoding='utf-8'))

    # 按文件名顺序读取 chapter
    chapter_files = sorted(chapters_dir.glob('ch*.html'))
    print(f'[build] 发现 {len(chapter_files)} 个章节')

    chapter_htmls = []
    total_chars = 0
    total_minutes = 0
    for cf in chapter_files:
        html = cf.read_text(encoding='utf-8')
        chars = count_chinese_chars(html)
        minutes = max(1, round(chars / CHARS_PER_MINUTE_CN))
        total_chars += chars
        total_minutes += minutes
        enhanced = inject_chapter_enhancements(html, recap_data)
        chapter_htmls.append(enhanced)
        print(f'  [{cf.name}] {chars:,} 字 / 约 {minutes} 分钟阅读')

    # 拼装
    hero = (parts_dir / '00_hero.html').read_text(encoding='utf-8')
    intro = (parts_dir / '05_intro.html').read_text(encoding='utf-8') if (parts_dir / '05_intro.html').exists() else ''
    antithesis = (parts_dir / '95_antithesis.html').read_text(encoding='utf-8') if (parts_dir / '95_antithesis.html').exists() else ''
    footer = (parts_dir / '99_footer.html').read_text(encoding='utf-8')

    final = '\n'.join([
        hero,
        intro,
        '\n'.join(chapter_htmls),
        antithesis,
        footer,
    ])

    # ─── INLINE 模式 (默认) · 把所有外部资源内联进 HTML ───
    if embed:
        print('\n[build] INLINE 模式 · 把 CSS/JS/glossary 内联进单文件 HTML (默认)')
        # 1) 内联 CSS · 只 inline style.css
        #    v6.3 起 reader.css 不 inline,按需加载(见 99_footer.html bootstrap)
        for css_name in ['style.css']:
            css_path = shared_dir / css_name
            if not css_path.exists():
                continue
            css = css_path.read_text(encoding='utf-8')
            css_block = f'<style>\n/* === {css_name} === */\n{css}\n</style>'
            pattern = r'<link rel="stylesheet" href="\.\./\.\./_shared/' + re.escape(css_name) + r'[^"]*">'
            final = re.sub(pattern, lambda m, cb=css_block: cb, final)
        # 2) 内联 progress.js / mini-toc.js / tooltip.js / reader.js
        #    关键:JS 注释/字符串里如果包含 </script>,inline 后浏览器会提前关
        #    脚本块,触发 SyntaxError。必须先转义 </script> 为 <\/script>。
        # v6.3 · reader.js 不 inline,按需加载
        for js_name in ['progress.js', 'mini-toc.js', 'tooltip.js']:
            js = (shared_dir / js_name).read_text(encoding='utf-8')
            # 转义 </script> · 大小写不敏感(防 </SCRIPT> 等变体)
            js_safe = re.sub(r'</(script)>', r'<\\/\1>', js, flags=re.IGNORECASE)
            js_block = f'<script>\n{js_safe}\n</script>'
            final = re.sub(
                r'<script src="\.\./\.\./_shared/' + re.escape(js_name) + r'[^"]*" defer></script>',
                lambda m, jb=js_block: jb,
                final
            )
        # 3) 内联 glossary.json (tooltip.js fetch → window.__EMBEDDED_GLOSSARY__)
        #    词典 JSON 里也可能有 </script>,虽然概率低,但保险起见也转义
        glossary = (shared_dir / 'glossary.json').read_text(encoding='utf-8')
        glossary_safe = re.sub(r'</(script)>', r'<\\/\1>', glossary, flags=re.IGNORECASE)
        gloss_inject = f'\n<script>window.__EMBEDDED_GLOSSARY__ = {glossary_safe};</script>\n'
        final = final.replace('<body>\n', '<body>\n' + gloss_inject)

    output = report_dir / 'index.html'
    output.write_text(final, encoding='utf-8')

    print(f'\n[build] 装配完成')
    print(f'  总字数: {total_chars:,}')
    print(f'  总阅读时间: 约 {total_minutes} 分钟 ({total_minutes/60:.1f} 小时)')
    print(f'  输出: {output}')
    print(f'  大小: {output.stat().st_size:,} bytes')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python3 build.py <report_dir> [--external]')
        print('  默认 (推荐):内联全部资源 → 单文件 index.html (~750 KB)')
        print('  --external :用 <link>/<script> 引用 _shared/ (调试用)')
        print('例如: python3 _shared/build.py reports/2026-05-running-science')
        sys.exit(1)

    report_dir = Path(sys.argv[1]).resolve()
    if not report_dir.is_dir():
        print(f'错误: {report_dir} 不是目录')
        sys.exit(1)

    external = '--external' in sys.argv
    build_report(report_dir, external=external)
