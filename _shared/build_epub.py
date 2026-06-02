#!/usr/bin/env python3
"""
BUILD EPUB · v1.0 · 把 reports/<slug>/index.html 装配成 EPUB 电子书

用法:
    tools/.venv/bin/python3 _shared/build_epub.py reports/<slug>

输入:
    reports/<slug>/index.html       (build.py 装配后的完整 inline HTML)
    reports/<slug>/assets/ch*-hero.jpg

输出:
    reports/<slug>/<slug>.epub       (1-15 MB,完整书本版 · 含 SVG/table 渲染 PNG)

完整功能:
  · 章节内容(h1.section-h + h3 + p + callout + tldr + chip)保留
  · 章节封面图 hero JPG 嵌入
  · inline SVG 用 Playwright 渲染成 PNG 嵌入
  · <table> 用 Playwright 渲染成 PNG 嵌入
  · 多级 TOC(章 + 节)→ 微信读书 / Apple Books 听书可跳节点
  · 移除运行时 UI(sticky-nav / mini-toc / reader 按钮 / progress-bar)
"""

import sys
import re
import shutil
import zipfile
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from xml.sax.saxutils import escape as xml_escape

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("[build_epub] 需要装 bs4: pip install beautifulsoup4 lxml")

# playwright 惰性导入(只在「看版」渲染 PNG 时需要;听书版 --audio 免此依赖)


# ============== 配置 ==============
EPUB_TEMPLATES = Path(__file__).parent / 'epub_templates'

# Playwright 渲染 viewport
RENDER_VIEWPORT = {'width': 900, 'height': 1400}

# 章节里要移除的运行时 UI 元素(EPUB reader 不需要)
REMOVE_SELECTORS = [
    '.reader-entry-btn',     # 听这章 / 听此节 按钮
    '.mini-toc',             # 右侧悬浮目录
    '.progress-bar',         # 顶部进度条
    '.sticky-nav',           # 顶部 sticky 导航
    '.reader-overlay',       # 听书 overlay
    'script',                # 所有 script
    '.chapter-toc',          # 章节内 mini-TOC(EPUB reader 自带 nav)
    '.reading-meta',         # 阅读时间标记
    '.tooltip',              # 术语 hover 浮窗
]


def main(report_dir_arg, visual=False, output_name=None):
    report_dir = Path(report_dir_arg).resolve()
    if not report_dir.is_dir():
        sys.exit(f"[build_epub] 报告目录不存在: {report_dir}")

    index_html = report_dir / 'index.html'
    if not index_html.exists():
        sys.exit(f"[build_epub] 找不到 index.html(请先跑 _shared/build.py): {index_html}")

    slug = report_dir.name
    print(f"\n[build_epub] 处理 {slug}")

    # 1. 解析 HTML
    print(f"  [1/6] 解析 HTML ...")
    with open(index_html, encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    metadata = extract_metadata(soup, slug)
    chapters_data = extract_chapters(soup)
    print(f"        解析到 {len(chapters_data)} 个章节")

    # 2-3. 在临时目录里构建资产
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        images_dir = tmpdir_path / 'images'
        images_dir.mkdir()

        # 收集 inline CSS(用于 SVG/table 渲染时正确解析 var(--c-theory) 等)
        css_content = collect_inline_css(soup)

        # 2. 渲染 SVG / table 为 PNG(默认听书优化跳过,免 Playwright;--visual 才渲染)
        if visual:
            print(f"  [2/6] 用 Playwright 渲染 SVG / table 为 PNG ...")
            figure_assets = render_figures(chapters_data, css_content, images_dir)
            print(f"        渲染 {len(figure_assets)} 张图")
        else:
            figure_assets = []
            print(f"  [2/6] 听书优化 · 跳过 SVG / table 渲染")

        # 3. 拷贝 chapter hero JPG
        print(f"  [3/6] 拷贝章节封面图 ...")
        hero_assets = copy_hero_images(chapters_data, report_dir, images_dir)
        print(f"        拷贝 {len(hero_assets)} 张封面图")

        # 4. 生成每章 xhtml
        print(f"  [4/6] 生成章节 xhtml ...")
        chapter_paths = []
        for idx, ch in enumerate(chapters_data, 1):
            path = tmpdir_path / f'chapter{idx:02d}.xhtml'
            path.write_text(build_chapter_xhtml(ch, idx, audio=not visual), encoding='utf-8')
            chapter_paths.append(path)

        # 5. 生成 nav.xhtml + content.opf
        print(f"  [5/6] 生成 nav.xhtml + content.opf ...")
        nav_path = tmpdir_path / 'nav.xhtml'
        nav_path.write_text(build_nav_xhtml(chapters_data), encoding='utf-8')

        opf_path = tmpdir_path / 'content.opf'
        opf_path.write_text(
            build_content_opf(metadata, chapters_data, figure_assets + hero_assets),
            encoding='utf-8'
        )

        # 6. 打包 EPUB
        print(f"  [6/6] 打包 EPUB zip ...")
        output = report_dir / (output_name or f'{slug}.epub')
        package_epub(
            output=output,
            opf_path=opf_path,
            nav_path=nav_path,
            chapter_paths=chapter_paths,
            images_dir=images_dir,
        )

    size_mb = output.stat().st_size / 1024 / 1024
    print(f"\n[build_epub] ✅ 完成")
    print(f"  输出: {output}")
    print(f"  大小: {size_mb:.1f} MB")
    print(f"  导入微信读书: 我 → 书架 → 导入图书 → 选 .epub 文件\n")


# ================== HTML 解析 ==================

def extract_metadata(soup, slug):
    """提取 EPUB metadata"""
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else slug

    desc_tag = soup.find('meta', attrs={'name': 'description'})
    description = desc_tag.get('content', '') if desc_tag else ''

    # 从 slug 提取 YYYY-MM(e.g. 2026-05-running-science)
    date_match = re.match(r'(\d{4}-\d{2})', slug)
    date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m')

    # 稳定 identifier(基于 slug 的 hash)
    identifier = f'urn:uuid:{hashlib.md5(slug.encode()).hexdigest()}'

    modified = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    return {
        'slug': slug,
        'title': title,
        'description': description,
        'date': date,
        'identifier': identifier,
        'modified': modified,
    }


def extract_chapters(soup):
    """提取章节列表 · 顺序:intro → chapters → antithesis"""
    chapters = []
    seen_ids = set()

    # 按 DOM 顺序遍历 section,只挑可作"章节"的
    for sec in soup.find_all('section'):
        sec_id = sec.get('id', '')
        sec_classes = sec.get('class', [])

        # 排除已经处理的、嵌套的、非 chapter 性质的
        if sec_id in seen_ids:
            continue
        is_chapter = 'chapter' in sec_classes
        is_intro_or_antithesis = sec_id in ('intro', 'antithesis')
        if not (is_chapter or is_intro_or_antithesis):
            continue

        ch = parse_chapter(sec)
        if ch:
            chapters.append(ch)
            seen_ids.add(sec_id)

    return chapters


def parse_chapter(section):
    """解析单个 section → 章节数据 dict"""
    sec_id = section.get('id', '')

    h1 = section.find('h1', class_='section-h') or section.find('h1')
    if not h1:
        return None

    # 清理 h1 副本(去 reader 按钮、抽出英文副标题)
    h1_clone = BeautifulSoup(str(h1), 'lxml').find('h1')
    for btn in h1_clone.select('.reader-entry-btn'):
        btn.decompose()

    en_span = h1_clone.find('span', class_='en')
    en_subtitle = en_span.get_text(strip=True) if en_span else None
    if en_span:
        en_span.decompose()

    title = h1_clone.get_text(strip=True)

    # section-tag(章节编号 chip)
    tag_el = section.find(class_='section-tag')
    tag_text = tag_el.get_text(' ', strip=True) if tag_el else None

    # 子节(h3 → 多级 TOC)
    sub_sections = []
    for h3 in section.find_all('h3'):
        h3_id = h3.get('id', '')
        h3_clone = BeautifulSoup(str(h3), 'lxml').find('h3')
        for btn in h3_clone.select('.reader-entry-btn'):
            btn.decompose()

        pre = h3_clone.find(class_='pre')
        pre_text = pre.get_text(strip=True) if pre else ''
        if pre:
            pre.decompose()

        sub_text = h3_clone.get_text(strip=True)
        sub_sections.append({
            'id': h3_id,
            'pre': pre_text,
            'text': sub_text,
        })

    return {
        'id': sec_id,
        'title': title,
        'en_subtitle': en_subtitle,
        'tag': tag_text,
        'sub_sections': sub_sections,
        'section_html': section,  # bs4 element,操作它直接 mutate soup
    }


def collect_inline_css(soup):
    """收集所有 inline <style> 的 CSS"""
    parts = []
    for style in soup.find_all('style'):
        parts.append(style.get_text())
    return '\n'.join(parts)


# ================== Playwright 渲染 ==================

def render_figures(chapters_data, css_content, images_dir):
    """把所有章节内的 SVG + table 渲染成 PNG"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("[build_epub] 看版 EPUB 需要 playwright;听书版请加 --audio(免依赖)")

    figure_assets = []
    counter = 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=RENDER_VIEWPORT)

        for ch_idx, ch in enumerate(chapters_data, 1):
            section = ch['section_html']

            # 找所有 SVG(嵌在 figure 里的也算)
            svgs = section.find_all('svg')
            for svg in svgs:
                counter += 1
                name = f'fig-ch{ch_idx:02d}-{counter:03d}.png'
                png_path = images_dir / name
                if render_element_to_png(page, str(svg), css_content, png_path):
                    figure_assets.append({'name': name, 'kind': 'svg'})
                    replace_with_img(svg, f'images/{name}', alt='Figure')

            # 找所有 table
            tables = section.find_all('table')
            for table in tables:
                counter += 1
                name = f'fig-ch{ch_idx:02d}-{counter:03d}.png'
                png_path = images_dir / name
                if render_element_to_png(page, str(table), css_content, png_path):
                    figure_assets.append({'name': name, 'kind': 'table'})
                    replace_with_img(table, f'images/{name}', alt='Table')

        browser.close()

    return figure_assets


def render_element_to_png(page, element_html, css_content, output_path):
    """单 element 渲染成 PNG"""
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <style>
    body {{
      margin: 0;
      padding: 24px;
      background: #f0ebdd;
      font-family: "PingFang SC", -apple-system, sans-serif;
      color: #2c2c2c;
    }}
    /* 把原项目的 CSS 全部注入,以便 var(--c-theory) 等正确解析 */
    {css_content}
  </style>
</head>
<body>
{element_html}
</body>
</html>"""

    try:
        page.set_content(full_html, wait_until='load')
        # 选择渲染目标 element(SVG 或 table)
        if element_html.lstrip().startswith('<svg') or '<svg' in element_html[:200]:
            loc = page.locator('svg').first
        else:
            loc = page.locator('table').first

        loc.screenshot(path=str(output_path), omit_background=False)
        return True
    except Exception as e:
        print(f"        ⚠️ 渲染失败 {output_path.name}: {e}")
        return False


def replace_with_img(element, src, alt='Figure'):
    """把 bs4 element 替换成 <img>"""
    img_html = f'<img src="{src}" alt="{xml_escape(alt)}"/>'
    new_img = BeautifulSoup(img_html, 'html.parser').img
    element.replace_with(new_img)


# ================== Hero 图拷贝 ==================

def copy_hero_images(chapters_data, report_dir, images_dir):
    """拷贝 chapter hero JPG + 把 img src 改成 EPUB 内部路径"""
    hero_assets = []
    copied_names = set()

    for ch in chapters_data:
        section = ch['section_html']
        for img in section.find_all('img'):
            src = img.get('src', '')
            if not src or src.startswith('http') or src.startswith('data:') or src.startswith('images/'):
                # 跳过 http / data: / 已被 render_figures 替换过的
                continue

            original = report_dir / src
            if not original.exists():
                print(f"        ⚠️ 图片不存在: {src}")
                continue

            name = original.name  # e.g. ch01-hero.jpg
            target = images_dir / name
            if name not in copied_names:
                shutil.copyfile(original, target)
                copied_names.add(name)
                hero_assets.append({'name': name, 'kind': original.suffix.lstrip('.').lower()})

            img['src'] = f'images/{name}'

    return hero_assets


# ================== EPUB 文件生成 ==================

# audio 模式:被「听书替身」取代的视觉块(替身紧跟其后时,删掉它)
_AUDIO_VISUAL_CLASSES = ('svg-frame', 'number-strip', 'hero-keypoints',
                         'grid-3', 'table-wrap', 'fig', 'figure')


def _is_visual_block(el):
    """el 是否「只给眼睛看」的视觉块(听书无意义)"""
    if el is None or not getattr(el, 'name', None):
        return False
    if el.name in ('table', 'svg', 'figure'):
        return True
    classes = el.get('class', []) or []
    return any(c in classes for c in _AUDIO_VISUAL_CLASSES)


def apply_audio_substitution(section_clone):
    """听书版:.audio-only 替身取代紧跟在它前面的视觉块"""
    for audio_el in section_clone.select('.audio-only'):
        prev = audio_el.find_previous_sibling()
        if _is_visual_block(prev):
            prev.decompose()


_AUDIO_ARROWS = re.compile(r'[▸▼▲△▽◆◇●○■□★☆►◄▶◀➤‣»«]')


def clean_audio_noise(section_clone):
    """听书版:清掉装饰符号(▸▼★…)和分隔中点,免得 TTS 念出杂音"""
    for node in list(section_clone.find_all(string=True)):
        if node.parent is None:
            continue
        s = str(node)
        s2 = _AUDIO_ARROWS.sub('', s)
        s2 = s2.replace(' · ', '，').replace(' ·', '').replace('· ', '')
        if s2 != s:
            node.replace_with(s2)


def build_chapter_xhtml(ch, idx, audio=False):
    """生成单章 xhtml(audio=True 走听书版:删冗余视觉块/参考文献,留替身)"""
    section = ch['section_html']

    # clone 一份做清理,避免 mutate 原 soup
    section_clone = BeautifulSoup(str(section), 'lxml').find('section')
    if section_clone is None:
        # fallback: bs4 解析出来可能用 html 包,把 section 拿出来
        section_clone = BeautifulSoup(str(section), 'html.parser').find('section')

    remove = list(REMOVE_SELECTORS)
    if audio:
        # 听书版额外移除:人工标记的冗余视觉块 .no-audio、参考文献 .ref
        remove += ['.no-audio', '.ref', '.pre']  # .pre=小节编号(★.1/4.2),听书念标题即可,不念编号
    for selector in remove:
        for el in section_clone.select(selector):
            el.decompose()

    if audio:
        apply_audio_substitution(section_clone)
        clean_audio_noise(section_clone)

    # 章节 inner HTML
    content_html = ''.join(str(c) for c in section_clone.children).strip()

    title = xml_escape(ch['title'])
    ch_id = xml_escape(ch['id'])

    template = (EPUB_TEMPLATES / 'chapter.xhtml.tmpl').read_text(encoding='utf-8')
    return template \
        .replace('{{ chapter_title }}', title) \
        .replace('{{ chapter_id }}', ch_id) \
        .replace('{{ chapter_content }}', content_html)


def build_nav_xhtml(chapters_data):
    """生成多级 TOC(章 + 节)"""
    entries = []
    for idx, ch in enumerate(chapters_data, 1):
        ch_title = xml_escape(ch['title'])
        href = f'chapter{idx:02d}.xhtml'

        sub_html = ''
        if ch['sub_sections']:
            sub_items = []
            for sub in ch['sub_sections']:
                if not sub['text']:
                    continue
                pre = sub['pre']
                label = f'{pre} {sub["text"]}'.strip() if pre else sub['text']
                sub_href = f'{href}#{sub["id"]}' if sub['id'] else href
                sub_items.append(
                    f'        <li><a href="{xml_escape(sub_href)}">{xml_escape(label)}</a></li>'
                )
            if sub_items:
                sub_html = '\n      <ol>\n' + '\n'.join(sub_items) + '\n      </ol>\n    '

        entries.append(f'    <li><a href="{href}">{ch_title}</a>{sub_html}</li>')

    toc_entries = '\n'.join(entries)

    template = (EPUB_TEMPLATES / 'nav.xhtml.tmpl').read_text(encoding='utf-8')
    return template.replace('{{ toc_entries }}', toc_entries)


def build_content_opf(metadata, chapters_data, image_assets):
    """生成 OPF manifest + spine"""
    chapter_items = []
    spine_items = []
    for idx in range(1, len(chapters_data) + 1):
        item_id = f'ch{idx:02d}'
        href = f'chapter{idx:02d}.xhtml'
        chapter_items.append(
            f'    <item id="{item_id}" href="{href}" media-type="application/xhtml+xml"/>'
        )
        spine_items.append(f'    <itemref idref="{item_id}"/>')

    image_items = []
    seen_names = set()
    for img in image_assets:
        name = img['name']
        if name in seen_names:
            continue
        seen_names.add(name)

        item_id = 'img_' + re.sub(r'[^\w]', '_', name)
        ext = name.rsplit('.', 1)[1].lower() if '.' in name else ''
        media_type = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'svg': 'image/svg+xml',
            'webp': 'image/webp',
        }.get(ext, 'application/octet-stream')
        image_items.append(
            f'    <item id="{item_id}" href="images/{name}" media-type="{media_type}"/>'
        )

    template = (EPUB_TEMPLATES / 'content.opf.tmpl').read_text(encoding='utf-8')
    return template \
        .replace('{{ identifier }}', metadata['identifier']) \
        .replace('{{ title }}', xml_escape(metadata['title'])) \
        .replace('{{ date }}', metadata['date']) \
        .replace('{{ description }}', xml_escape(metadata['description'])) \
        .replace('{{ modified }}', metadata['modified']) \
        .replace('{{ chapter_items }}', '\n'.join(chapter_items)) \
        .replace('{{ image_items }}', '\n'.join(image_items)) \
        .replace('{{ spine_items }}', '\n'.join(spine_items))


def package_epub(output, opf_path, nav_path, chapter_paths, images_dir):
    """打包成 EPUB zip"""
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        # mimetype 必须第一个,不压缩
        zinfo = zipfile.ZipInfo('mimetype')
        zinfo.compress_type = zipfile.ZIP_STORED
        zf.writestr(zinfo, 'application/epub+zip')

        # META-INF
        zf.write(EPUB_TEMPLATES / 'container.xml', 'META-INF/container.xml')

        # OEBPS
        zf.write(opf_path, 'OEBPS/content.opf')
        zf.write(nav_path, 'OEBPS/nav.xhtml')
        zf.write(EPUB_TEMPLATES / 'stylesheet.css', 'OEBPS/styles/main.css')

        for ch_path in chapter_paths:
            zf.write(ch_path, f'OEBPS/{ch_path.name}')

        for img_path in sorted(images_dir.iterdir()):
            if img_path.is_file():
                zf.write(img_path, f'OEBPS/images/{img_path.name}')


# ================== 入口 ==================

if __name__ == '__main__':
    argv = sys.argv[1:]
    visual = '--visual' in argv      # 默认听书优化;--visual 产带图看版(需 playwright)
    output_name = None
    if '-o' in argv:
        i = argv.index('-o')
        output_name = argv[i + 1]
        del argv[i:i + 2]
    pos = [a for a in argv if not a.startswith('-')]
    if len(pos) != 1:
        sys.exit("用法: python3 _shared/build_epub.py reports/<slug> [-o 输出名.epub] [--visual]\n"
                 "  默认产听书优化版(免 playwright);--visual 产带图看版")
    main(pos[0], visual=visual, output_name=output_name)
