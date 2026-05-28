#!/usr/bin/env python3
"""
REPORT AUDIT · 报告自检脚本

按 PRINCIPLES.md 八条铁律 + 写作禁区 跑一遍报告目录,
缺哪一项立刻报错。装配前后都可以跑。

用法:
    python3 _shared/check-report.py reports/<slug>
    python3 _shared/check-report.py reports/2026-05-anthropic-academy

也可以扫所有报告:
    python3 _shared/check-report.py --all

输出:
    OK / WARN / FAIL 三级,FAIL 退出码非零(可接 CI)。
"""

import os
import re
import sys
import json
from pathlib import Path


# ─── 检查规则 · 每项一个函数,返回 (level, message) ──────────

LEVEL_OK = "OK"
LEVEL_WARN = "WARN"
LEVEL_FAIL = "FAIL"


def check_index_exists(report_dir, files):
    """index.html 是装配产物,build.py 跑过就该有"""
    index = report_dir / "index.html"
    if not index.exists():
        return LEVEL_WARN, "index.html 不存在(可能没跑 build.py · 单文件 SPA 报告可忽略)"
    return LEVEL_OK, f"index.html 已存在 · {index.stat().st_size // 1024} KB"


def check_sticky_nav(report_dir, files):
    """五件套铁律 · sticky-nav 横向章节导航"""
    if files["index_text"] is None:
        return LEVEL_WARN, "index.html 不存在,跳过 sticky-nav 检查"
    if '<nav class="sticky-nav">' not in files["index_text"]:
        return LEVEL_FAIL, "缺 sticky-nav · hero 末尾应有 <nav class=\"sticky-nav\"> 横向章节导航"
    # 抠 sticky-nav 块内文本,只数它里面的章节链接
    m = re.search(r'<nav class="sticky-nav">([\s\S]*?)</nav>', files["index_text"])
    nav_html = m.group(1) if m else ""
    links = re.findall(r'<a href="#s(\d+)"', nav_html)
    sections = set(re.findall(r'<section id="s(\d+)"', files["index_text"]))
    nav_set = set(links)
    if nav_set != sections and len(sections) > 0:
        missing = sections - nav_set
        extra = nav_set - sections
        msg = []
        if missing: msg.append(f"nav 漏了章节 #{','.join(sorted(missing, key=int))}")
        if extra: msg.append(f"nav 多了不存在的 #{','.join(sorted(extra, key=int))}")
        return LEVEL_FAIL, "sticky-nav 跟章节对不上 · " + " · ".join(msg)
    return LEVEL_OK, f"sticky-nav 存在 · {len(nav_set)} 个章节链接"


def check_progress_bar(report_dir, files):
    """五件套铁律 · 顶部进度条"""
    if files["index_text"] is None:
        return LEVEL_WARN, "index.html 不存在,跳过"
    if 'class="progress-bar"' not in files["index_text"] and 'id="progressBar"' not in files["index_text"]:
        return LEVEL_FAIL, "缺顶部进度条 · 应有 <div class=\"progress-bar\" id=\"progressBar\">"
    return LEVEL_OK, "progress-bar 存在"


def check_reader_bootstrap(report_dir, files):
    """听书组件接入 · PRINCIPLES 第十节"""
    if files["index_text"] is None:
        return LEVEL_WARN, "index.html 不存在,跳过"
    has_css = 'reader-bootstrap.css' in files["index_text"]
    has_js = 'reader-bootstrap.js' in files["index_text"]
    if not has_css and not has_js:
        return LEVEL_WARN, "未接入听书组件 · 建议在 hero 加 reader-bootstrap.css,footer 加 reader-bootstrap.js"
    if not has_css or not has_js:
        return LEVEL_WARN, f"听书组件只接了一半 · css={has_css} js={has_js}"
    return LEVEL_OK, "听书组件已接入"


def check_hero_exists(report_dir, files):
    hero = report_dir / "parts" / "00_hero.html"
    if not hero.exists():
        return LEVEL_FAIL, "缺 parts/00_hero.html"
    return LEVEL_OK, "hero 存在"


def check_footer_exists(report_dir, files):
    footer = report_dir / "parts" / "99_footer.html"
    if not footer.exists():
        return LEVEL_FAIL, "缺 parts/99_footer.html"
    return LEVEL_OK, "footer 存在"


def check_chapters_exist(report_dir, files):
    chapters_dir = report_dir / "chapters"
    if not chapters_dir.exists():
        return LEVEL_WARN, "没有 chapters/ 目录(B 模式单文件 SPA 报告可忽略)"
    chapters = sorted(chapters_dir.glob("ch*.html"))
    if not chapters:
        return LEVEL_FAIL, "chapters/ 下没有 ch*.html"
    files["chapters"] = chapters
    return LEVEL_OK, f"{len(chapters)} 个章节"


def check_chapter_required_blocks(report_dir, files):
    """每章五件套 · TL;DR · 章末 recap · story 钩子"""
    if not files.get("chapters"):
        return LEVEL_WARN, "无 chapters 可检查"

    failures = []
    for ch in files["chapters"]:
        text = ch.read_text(encoding="utf-8")
        name = ch.name
        if 'class="tldr"' not in text:
            failures.append(f"{name} 缺 .tldr 章首 ELEVATOR PITCH")
        if 'class="section-h"' not in text and '<h1 class="section-h"' not in text:
            failures.append(f"{name} 缺 h1.section-h 章节标题")
        if 'class="section-tag"' not in text:
            failures.append(f"{name} 缺 .section-tag 章节编号 chip")
        # recap 不在 chapter 里,是 build.py 注入,只在 index.html 装配后验证
        # story 是建议不是强制(短章可没),记 WARN 别 FAIL

    if failures:
        return LEVEL_FAIL, "章节缺必备块 · " + " | ".join(failures[:5]) + (" 等..." if len(failures) > 5 else "")
    return LEVEL_OK, f"{len(files['chapters'])} 个章节都含 tldr + section-h + section-tag"


def check_chapter_recap_injected(report_dir, files):
    """build.py 装配后,index.html 里每章末尾都应有 .chapter-recap"""
    if files["index_text"] is None:
        return LEVEL_WARN, "index.html 不存在,跳过 recap 装配检查"
    if not files.get("chapters"):
        return LEVEL_WARN, "无 chapters 可对比"
    section_count = len(re.findall(r'<section id="s\d+"', files["index_text"]))
    recap_count = files["index_text"].count('class="chapter-recap"')
    if recap_count < section_count - 1:  # 序言 ch00 可以不带 recap
        return LEVEL_FAIL, f"index.html 里只有 {recap_count} 个 chapter-recap,但有 {section_count} 个 section · build.py 没注入完整?"
    return LEVEL_OK, f"{recap_count} 个 chapter-recap 已注入"


def check_recaps_json(report_dir, files):
    """_recaps.json 章节数应等于 chapters 数"""
    recap_file = report_dir / "parts" / "_recaps.json"
    if not recap_file.exists():
        return LEVEL_WARN, "没 _recaps.json(B 模式可忽略)"
    try:
        recaps = json.loads(recap_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return LEVEL_FAIL, f"_recaps.json 解析失败 · {e}"

    if files.get("chapters"):
        ch_count = len(files["chapters"])
        recap_count = len(recaps)
        if recap_count != ch_count:
            return LEVEL_FAIL, f"_recaps.json 有 {recap_count} 条,但 chapters 有 {ch_count} 个 · 对不上"
    # 每个 recap 应有 title + points
    bad = [k for k, v in recaps.items() if "title" not in v or "points" not in v]
    if bad:
        return LEVEL_FAIL, f"_recaps.json 字段不全 · {bad}"
    return LEVEL_OK, f"_recaps.json {len(recaps)} 条,字段完整"


def check_chinese_quotes(report_dir, files):
    """禁区 · 中文弯引号 (用 「」《》 代替)"""
    if files["index_text"] is None:
        return LEVEL_WARN, "index.html 不存在,跳过"
    text = files["index_text"]
    # 抠掉 CSS/JS/code 块
    text_clean = re.sub(r"<style[\s\S]*?</style>", "", text)
    text_clean = re.sub(r"<script[\s\S]*?</script>", "", text_clean)
    text_clean = re.sub(r"<pre[\s\S]*?</pre>", "", text_clean)
    text_clean = re.sub(r"<code[\s\S]*?</code>", "", text_clean)

    curly = re.findall(r"[“”‘’]", text_clean)
    if curly:
        # 给几个上下文
        samples = []
        for m in list(re.finditer(r"[“”‘’]", text_clean))[:3]:
            ctx = text_clean[max(0, m.start()-20):m.end()+20]
            samples.append(ctx.strip())
        return LEVEL_FAIL, f"发现 {len(curly)} 个中文弯引号 · 应用 「」 或 《》 · 示例:{samples[0][:50]}..."
    return LEVEL_OK, "无中文弯引号"


def check_no_emoji_decoration(report_dir, files):
    """禁区 · emoji 装饰(★ ⚠ 等印刷符号允许,真 emoji 不允许)"""
    if files["index_text"] is None:
        return LEVEL_WARN, "index.html 不存在,跳过"
    text = files["index_text"]
    text_clean = re.sub(r"<style[\s\S]*?</style>", "", text)
    text_clean = re.sub(r"<script[\s\S]*?</script>", "", text_clean)

    # 主流 emoji 范围 U+1F300-U+1FAFF 和 U+2600-U+27BF(部分符号)的常见 emoji
    emoji_chars = re.findall(r"[\U0001F300-\U0001FAFF]", text_clean)
    if emoji_chars:
        from collections import Counter
        cnt = Counter(emoji_chars)
        return LEVEL_WARN, f"发现 {len(emoji_chars)} 个 emoji · 出现最多的:{dict(cnt.most_common(3))}(★ ⚠ 这些印刷符号 OK,但真 emoji 装饰应避免)"
    return LEVEL_OK, "无 emoji 装饰(印刷符号 ★ ⚠ 等不算)"


def check_translation_smell(report_dir, files):
    """禁区 · 翻译腔句式"""
    if files["index_text"] is None:
        return LEVEL_WARN, "index.html 不存在,跳过"
    text = files["index_text"]
    text_clean = re.sub(r"<style[\s\S]*?</style>", "", text)
    text_clean = re.sub(r"<script[\s\S]*?</script>", "", text_clean)
    # 抠掉 HTML 标签留纯文本
    text_clean = re.sub(r"<[^>]+>", " ", text_clean)

    # 真翻译腔模式 · 避免误报正常中文(「在循环中」「在写代码时」这种合法)
    patterns = {
        "在 X 的过程中": r"在[一-鿿]{1,10}的过程中",
        "在 X 进行的时候": r"在[一-鿿]{1,10}进行(?:的时候|时)",
        "由 X 所": r"由[一-鿿]{1,6}所",  # 「由我们所做的事」
        "的过程是": r"的过程是",
        "由 X 负责": r"由[一-鿿]{1,6}负责(?![人事])",
        "进行了 X 的 X": r"进行了[一-鿿]{1,8}的",
        "使得 X 能够": r"使得[一-鿿]{1,10}能够",
    }
    hits = []
    for name, pat in patterns.items():
        matches = re.findall(pat, text_clean)
        if matches:
            hits.append(f"{name}×{len(matches)}")
    if hits:
        return LEVEL_WARN, "翻译腔嫌疑 · " + " · ".join(hits)
    return LEVEL_OK, "无明显翻译腔"


def check_ref_lists(report_dir, files):
    """每章末尾应有 p.ref 引用列表"""
    if not files.get("chapters"):
        return LEVEL_WARN, "无 chapters 可检查"
    missing = []
    for ch in files["chapters"]:
        text = ch.read_text(encoding="utf-8")
        if 'class="ref"' not in text and "主要参考" not in text:
            missing.append(ch.name)
    if missing:
        return LEVEL_WARN, f"章节缺 p.ref 引用列表 · {','.join(missing[:5])}"
    return LEVEL_OK, f"{len(files['chapters'])} 章都有 p.ref"


def check_callout_class_names(report_dir, files):
    """常见笔误:callout 类名拼错(callout-sharp / callouts-sharp 等)"""
    if not files.get("chapters"):
        return LEVEL_WARN, "无 chapters 可检查"
    # 已知合法的 callout 二级类(PRINCIPLES.md 第三节 + 各报告扩展)
    valid_callouts = {
        "sharp", "ops", "you", "note", "story",  # PRINCIPLES.md 第三节核心五种
        "protocol",  # marathon / running / rehab 的章末协议清单
        "stop",  # marathon / running 的就医警示
        "plain",  # marathon 的白话翻译
        "red", "gold", "green", "blue",  # 其他报告通用色调
    }
    issues = []
    for ch in files["chapters"]:
        text = ch.read_text(encoding="utf-8")
        # 找所有 callout 后跟的二级 class
        cls = re.findall(r'class="callout\s+(\w+)"', text)
        for c in cls:
            if c not in valid_callouts:
                issues.append(f"{ch.name}: callout.{c}")
    if issues:
        return LEVEL_WARN, "可能的 callout 笔误 · " + " · ".join(issues[:5])
    return LEVEL_OK, "callout 类名都合法"


# ─── 运行 ──────────────────────────────────────────────

CHECKS = [
    ("索引文件", check_index_exists),
    ("Hero 文件", check_hero_exists),
    ("Footer 文件", check_footer_exists),
    ("章节文件", check_chapters_exist),
    ("Sticky Nav 横向导航", check_sticky_nav),
    ("顶部进度条", check_progress_bar),
    ("听书组件接入", check_reader_bootstrap),
    ("章节必备块 tldr/section-h/section-tag", check_chapter_required_blocks),
    ("章末 recap 注入", check_chapter_recap_injected),
    ("_recaps.json 完整性", check_recaps_json),
    ("p.ref 引用列表", check_ref_lists),
    ("callout 类名", check_callout_class_names),
    ("禁区 · 中文弯引号", check_chinese_quotes),
    ("禁区 · emoji 装饰", check_no_emoji_decoration),
    ("禁区 · 翻译腔嫌疑", check_translation_smell),
]


def audit_report(report_dir):
    report_dir = Path(report_dir).resolve()
    if not report_dir.exists():
        print(f"[ERROR] 报告目录不存在: {report_dir}")
        return 2

    print(f"\n{'='*64}")
    print(f"AUDIT · {report_dir.name}")
    print(f"{'='*64}")

    # 预读 index.html(如果有)
    index_file = report_dir / "index.html"
    files = {
        "index_text": index_file.read_text(encoding="utf-8") if index_file.exists() else None,
    }

    levels = []
    width = 42
    for name, check_fn in CHECKS:
        try:
            level, msg = check_fn(report_dir, files)
        except Exception as e:
            level, msg = LEVEL_FAIL, f"检查抛错 · {type(e).__name__}: {e}"
        levels.append(level)
        icon = {"OK": "✓", "WARN": "△", "FAIL": "✗"}[level]
        color = {"OK": "\033[32m", "WARN": "\033[33m", "FAIL": "\033[31m"}[level]
        reset = "\033[0m"
        print(f"  {color}{icon} {level:<4}{reset}  {name:<{width}}  {msg}")

    # 汇总
    n_ok = levels.count(LEVEL_OK)
    n_warn = levels.count(LEVEL_WARN)
    n_fail = levels.count(LEVEL_FAIL)
    total = len(levels)
    print(f"\n  汇总:{n_ok}/{total} OK · {n_warn} WARN · {n_fail} FAIL")
    return 1 if n_fail > 0 else 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    if sys.argv[1] == "--all":
        root = Path(__file__).parent.parent / "reports"
        exit_code = 0
        for d in sorted(root.iterdir()):
            if d.is_dir() and (d / "parts").exists():
                code = audit_report(d)
                if code: exit_code = code
        return exit_code

    return audit_report(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
