#!/usr/bin/env python3
"""
Audio Generator · 用 Edge TTS 把报告章节生成 MP3 + SRT 字幕 + 段落时间戳

特点:
- 完全免费(Microsoft Azure Neural TTS,via edge-tts 社区库)
- 中文神经音色(默认云希 / 可选晓晓 / 云阳 / 云健等)
- 同时输出 MP3 + SRT + JSON 段落级时间戳
- 用 BeautifulSoup 严格过滤(嵌套 div / SVG / 表格 / 装饰)
- 语义增强:反共识/协议/章节加前缀朗读
- 用 sentence text 精确匹配 + cumulative anchor 做时间戳对齐

用法:
  python3 _shared/audio-gen.py reports/2026-05-running-science/chapters/ch04.html
  python3 _shared/audio-gen.py reports/2026-05-running-science/chapters --all
  python3 _shared/audio-gen.py reports/.../chapters/ch04.html --voice Xiaoxiao
  python3 _shared/audio-gen.py reports/.../chapters/ch04.html --skip-audio   # 只重做时间戳
"""

import sys
import re
import asyncio
import json
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print('❌ 需要: python3 -m pip install edge-tts')
    sys.exit(1)

try:
    from bs4 import BeautifulSoup, NavigableString
except ImportError:
    print('❌ 需要: python3 -m pip install beautifulsoup4 lxml')
    sys.exit(1)


# ─── 配置 ────────────────────────────────────────────────────
VOICES = {
    'Yunxi':     'zh-CN-YunxiNeural',       # 男 · 阳光 · 推荐长篇专业(默认)
    'Xiaoxiao':  'zh-CN-XiaoxiaoNeural',    # 女 · 温暖 · 经典
    'Yunyang':   'zh-CN-YunyangNeural',     # 男 · 专业可靠 · 新闻
    'Yunjian':   'zh-CN-YunjianNeural',     # 男 · 激情 · 体育
    'Xiaoyi':    'zh-CN-XiaoyiNeural',      # 女 · 活泼
    'Yunxia':    'zh-CN-YunxiaNeural',      # 男 · 可爱
}
DEFAULT_VOICE_KEY = 'Yunxi'

# 黑名单(必须与 _shared/READER_RULES.md 完全一致)
EXCLUDE_TAGS = ['svg', 'table', 'script', 'style', 'figure', 'noscript']
EXCLUDE_CLASS_PATTERNS = [
    'hero', 'hero-keypoints', 'hero-toc-section', 'hero-toc',
    'number-strip', 'section-tag',
    'sticky-nav', 'mini-toc', 'progress-bar',
    'ref', 'chip',
    'svg-frame', 'svg-caption',
    'reader-trigger', 'reader-overlay', 'reader-mini',
    'kp', 'kp-tag', 'kp-value', 'kp-desc',  # hero keypoint 细分
]

# 白名单(对应 reader.js INCLUDE_TAGS)
INCLUDE_TAGS = ['h2', 'h3', 'h4', 'p', 'li', 'blockquote']


def has_excluded_class(tag, exclude_classes):
    """检查元素自身或其祖先是否带有黑名单 class"""
    node = tag
    while node and hasattr(node, 'get'):
        classes = node.get('class') or []
        if any(cls in exclude_classes for cls in classes):
            return True
        node = getattr(node, 'parent', None)
    return False


def has_excluded_ancestor(tag, exclude_tags):
    """检查元素是否在黑名单 tag 内"""
    parent = tag.parent
    while parent and hasattr(parent, 'name'):
        if parent.name in exclude_tags:
            return True
        parent = parent.parent
    return False


def extract_segments(html_file: Path):
    """
    用 BeautifulSoup 从章节 HTML 严格提取「可朗读段落」
    返回 list of dict: {id, tag, classes, text}
    """
    content = html_file.read_text(encoding='utf-8')
    soup = BeautifulSoup(content, 'lxml')

    # 1. 整体删除黑名单 tag(svg/table/script/style/figure/noscript)
    for tag_name in EXCLUDE_TAGS:
        for el in soup.find_all(tag_name):
            el.decompose()

    # 2. 整体删除带黑名单 class 的元素(嵌套子元素也会一并消失)
    exclude_classes = set(EXCLUDE_CLASS_PATTERNS)
    # 多轮遍历:可能嵌套 div 删除后又暴露下一层
    for _ in range(5):
        removed = 0
        # 每轮重新 find,因为 decompose 后 DOM 树会变
        targets = []
        for el in soup.find_all(class_=True):
            if el.parent is None or not getattr(el, 'attrs', None):
                continue
            classes = el.attrs.get('class') or []
            if any(cls in exclude_classes for cls in classes):
                targets.append(el)
        for el in targets:
            if el.parent is not None:
                el.decompose()
                removed += 1
        if removed == 0:
            break

    # 3. 提取 INCLUDE_TAGS 元素的文本
    segments = []
    auto_id = 0
    seen_texts = set()  # 去重(嵌套 li 内 p 可能重复)

    for tag in soup.find_all(INCLUDE_TAGS):
        # 跳过 decomposed 元素(只过滤 parent=None,不用 attrs 因为空 dict 是 falsy 会误杀)
        if tag.parent is None:
            continue
        # 跳过空白
        text = tag.get_text(separator=' ', strip=True)
        if not text or len(text) < 2:
            continue

        # 跳过 callout .label(只有装饰,内容简短)
        attrs = getattr(tag, 'attrs', None) or {}
        classes = attrs.get('class') or []
        parent_attrs = getattr(tag.parent, 'attrs', None) or {} if tag.parent else {}
        parent_classes = parent_attrs.get('class') or []

        if 'label' in classes:
            continue
        # 跳过 chapter-recap 内的某些装饰(如 "▼ 本章核心要点")
        if re.match(r'^[▼▲★▸◆■]\s', text):
            text = re.sub(r'^[▼▲★▸◆■]\s+', '', text)

        # 去重(同一段落不重复)
        text_key = text[:50]
        if text_key in seen_texts:
            continue
        seen_texts.add(text_key)

        # 清理多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        if not text or len(text) < 2:
            continue

        # 拿 reader-id 或自动生成
        seg_id = tag.get('data-reader-id') or f'auto-{auto_id}'
        auto_id += 1

        # 检测父级 callout 类型,加语义前缀
        callout_classes = set()
        node = tag
        while node:
            if getattr(node, 'attrs', None):
                for c in (node.attrs.get('class') or []):
                    callout_classes.add(c)
            node = getattr(node, 'parent', None)
            if node is None or not getattr(node, 'name', None) or node.name in ('body', 'html'):
                break

        tag_name = tag.name
        prefix = ''
        is_first_in_callout = False
        if 'callout' in callout_classes or 'sharp' in callout_classes or 'protocol' in callout_classes:
            # 找它在 callout 内是否是第一个 INCLUDE 段
            callout_el = tag.find_parent(class_=['callout', 'sharp', 'protocol', 'ops', 'you', 'story'])
            if callout_el:
                first_p = None
                for ch in callout_el.find_all(['p', 'li', 'h4'], recursive=True):
                    if 'label' in (ch.get('class') or []):
                        continue
                    first_p = ch
                    break
                if first_p is tag:
                    is_first_in_callout = True

        if 'sharp' in callout_classes and is_first_in_callout:
            prefix = '反共识。 '
        elif 'protocol' in callout_classes and tag_name == 'h4':
            prefix = '协议。 '
        elif 'you' in callout_classes and is_first_in_callout:
            prefix = '设身处地。 '
        elif 'story' in callout_classes and is_first_in_callout:
            prefix = '故事。 '
        elif tag_name == 'h2':
            prefix = '本章。 '
        elif tag_name == 'h3':
            prefix = '小节。 '

        text = prefix + text

        # 替换 .stop 块前缀(避免读出 emoji)
        text = re.sub(r'^[⚠]\s*何时停\s*', '何时停。 ', text)

        # 去除 emoji(听书时不需要)
        text = re.sub(r'[🎧📊⭐❌✅⚠️🔴🟡🟢]', '', text)

        segments.append({
            'id': seg_id,
            'tag': tag_name,
            'classes': ' '.join(classes),
            'text': text.strip(),
        })

    return segments


def build_combined_text(segments):
    """把所有段落串成一段长文本,段间适当停顿(标点 + 段落分隔)"""
    parts = []
    for seg in segments:
        text = seg['text']
        if seg['tag'] in ('h2', 'h3'):
            # 标题前后双换行 → 边读边换行 → 自然停顿
            parts.append(f'\n\n{text}\n\n')
        elif seg['tag'] == 'h4':
            parts.append(f'\n{text}\n')
        else:
            parts.append(text)
    return ' '.join(parts)


# ─── 音频生成 + 时间戳 ────────────────────────────────────────

def hns_to_sec(hns):
    """edge-tts 用 HNS(100 纳秒)→ 秒"""
    return hns / 10_000_000.0


def _fmt_srt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')


MAX_CHUNK_CHARS = 4500  # Edge TTS 单次请求字数上限(保守留余量)


def _split_into_chunks(text: str, max_chars: int = MAX_CHUNK_CHARS):
    """按段落 \\n\\n 切分,每块尽量接近 max_chars,不超过"""
    paragraphs = re.split(r'\n\n+', text)
    chunks = []
    current = []
    current_len = 0
    for p in paragraphs:
        plen = len(p)
        # 单个段落超长,硬切
        if plen > max_chars:
            if current:
                chunks.append('\n\n'.join(current))
                current = []
                current_len = 0
            # 按句号切
            sentences = re.split(r'(?<=[。!?\.\?])', p)
            sbuf = []
            sbuflen = 0
            for s in sentences:
                if sbuflen + len(s) > max_chars and sbuf:
                    chunks.append(''.join(sbuf))
                    sbuf = []
                    sbuflen = 0
                sbuf.append(s)
                sbuflen += len(s)
            if sbuf:
                chunks.append(''.join(sbuf))
        elif current_len + plen + 4 > max_chars and current:
            chunks.append('\n\n'.join(current))
            current = [p]
            current_len = plen
        else:
            current.append(p)
            current_len += plen + 4
    if current:
        chunks.append('\n\n'.join(current))
    return [c for c in chunks if c.strip()]


async def generate_audio(text: str, voice: str, mp3_path: Path, srt_path: Path):
    """生成 MP3 + 自写 SRT(自动分块处理超长文本),返回 boundaries 列表"""
    text_chunks = _split_into_chunks(text)
    print(f'[audio-gen] 文本分 {len(text_chunks)} 块(每块 ≤{MAX_CHUNK_CHARS} 字)')

    all_audio = []
    all_boundaries = []
    time_offset = 0.0

    for i, ctext in enumerate(text_chunks):
        print(f'[audio-gen]   块 {i + 1}/{len(text_chunks)} ({len(ctext)} 字)...', end='', flush=True)
        retries = 0
        last_err = None
        success = False
        while retries < 3 and not success:
            try:
                communicate = edge_tts.Communicate(ctext, voice)
                chunk_audio = []
                chunk_max_end = 0.0
                last_offset = 0.0
                async for msg in communicate.stream():
                    t = msg.get('type')
                    if t == 'audio':
                        chunk_audio.append(msg['data'])
                    elif t in ('SentenceBoundary', 'WordBoundary'):
                        off = hns_to_sec(msg['offset'])
                        dur = hns_to_sec(msg['duration'])
                        chunk_max_end = max(chunk_max_end, off + dur)
                        last_offset = off + dur
                        all_boundaries.append({
                            'start': time_offset + off,
                            'duration': dur,
                            'text': msg.get('text', '').strip(),
                        })
                all_audio.extend(chunk_audio)
                time_offset += chunk_max_end + 0.15  # 块间留 150ms 缓冲
                success = True
                print(' ✓')
            except Exception as e:
                last_err = e
                retries += 1
                if retries < 3:
                    print(f' 重试 {retries}/3 ({type(e).__name__})...', end='', flush=True)
                    await asyncio.sleep(2.0)
        if not success:
            print(f' ✗ 跳过(原因: {last_err})')

    mp3_path.write_bytes(b''.join(all_audio))

    # 自写 SRT
    srt_lines = []
    for i, b in enumerate(all_boundaries, 1):
        start = b['start']
        end = start + b['duration']
        srt_lines.append(str(i))
        srt_lines.append(f'{_fmt_srt_time(start)} --> {_fmt_srt_time(end)}')
        srt_lines.append(b['text'])
        srt_lines.append('')
    srt_path.write_text('\n'.join(srt_lines), encoding='utf-8')

    return all_boundaries


def normalize_for_match(s):
    """归一化字符串用于锚点匹配:去掉空白和标点,保留中英文数字"""
    return re.sub(r'[\s\W_]+', '', s, flags=re.UNICODE)


def build_segment_timestamps(segments, boundaries):
    """
    把段落和 boundary 对齐 → "段落 ID → 起始秒数" 映射

    算法:
    1. 把所有 boundaries 的文本归一化拼接成 cum_text
    2. 记录每个 boundary 在 cum_text 里的起始偏移
    3. 对每个段落,取首 8 个归一化字符作锚点
    4. 在 cum_text 里从游标 cursor 后找首次出现位置
    5. 反查这位置属于哪个 boundary,取其 start 秒
    """
    cum_text = ''
    boundary_start_in_cum = []
    for b in boundaries:
        boundary_start_in_cum.append(len(cum_text))
        cum_text += normalize_for_match(b['text'])

    mapping = []
    cursor = 0  # cum_text 里搜索游标(单调递进,防止回跳)

    for seg in segments:
        norm_seg = normalize_for_match(seg['text'])
        if not norm_seg:
            continue

        # 锚点长度依次尝试 12 / 8 / 5 / 3 个字
        found_pos = -1
        for anchor_len in [12, 8, 5, 3]:
            if len(norm_seg) < anchor_len:
                continue
            anchor = norm_seg[:anchor_len]
            pos = cum_text.find(anchor, cursor)
            if pos >= 0:
                found_pos = pos
                break

        if found_pos >= 0:
            # 二分查找:这个 pos 属于哪个 boundary
            lo, hi = 0, len(boundary_start_in_cum) - 1
            target_bi = 0
            while lo <= hi:
                mid = (lo + hi) // 2
                if boundary_start_in_cum[mid] <= found_pos:
                    target_bi = mid
                    lo = mid + 1
                else:
                    hi = mid - 1

            start_sec = boundaries[target_bi]['start']
            mapping.append({
                'id': seg['id'],
                'tag': seg['tag'],
                'start': round(start_sec, 2),
                'preview': seg['text'][:30] + ('...' if len(seg['text']) > 30 else ''),
            })
            cursor = found_pos + 1
        else:
            # 找不到 → 用上一段时间 + 长度估算
            prev_end = mapping[-1]['start'] if mapping else 0
            estimate = prev_end + len(seg['text']) / 5  # 5 字/秒
            mapping.append({
                'id': seg['id'],
                'tag': seg['tag'],
                'start': round(estimate, 2),
                'preview': seg['text'][:30],
                'estimated': True,
            })

    return mapping


# ─── 主流程 ──────────────────────────────────────────────────

async def process_chapter(html_file: Path, voice_key: str = DEFAULT_VOICE_KEY,
                           skip_audio: bool = False):
    """处理单章节"""
    voice = VOICES.get(voice_key, VOICES[DEFAULT_VOICE_KEY])
    print(f'[audio-gen] === {html_file.name} ({voice}) ===')

    segments = extract_segments(html_file)
    print(f'[audio-gen] 提取 {len(segments)} 个段落')

    text = build_combined_text(segments)
    chars = len(text)
    print(f'[audio-gen] 字符数 {chars:,}  预估时长 ~{chars / 280:.1f} min')

    out_dir = html_file.parent.parent / 'audio'
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = html_file.stem
    mp3_path = out_dir / f'{stem}.mp3'
    srt_path = out_dir / f'{stem}.srt'
    json_path = out_dir / f'{stem}.json'

    if skip_audio and mp3_path.exists() and srt_path.exists():
        # 只重做 JSON,从 SRT 读 boundaries
        print('[audio-gen] --skip-audio: 重用现有 MP3 + SRT')
        boundaries = []
        srt_content = srt_path.read_text(encoding='utf-8')
        blocks = re.findall(
            r'\d+\s+(\d+:\d+:\d+[,.]\d+)\s*-->\s*(\d+:\d+:\d+[,.]\d+)\s+([^\n]+)',
            srt_content
        )
        for start, end, btext in blocks:
            def s2sec(t):
                h, m, rest = t.split(':')
                s, ms = rest.replace('.', ',').split(',')
                return int(h) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, '0')[:3]) / 1000
            boundaries.append({
                'start': s2sec(start),
                'duration': s2sec(end) - s2sec(start),
                'text': btext.strip(),
            })
    else:
        print(f'[audio-gen] 生成中...(约 {chars / 1500:.1f} min)')
        boundaries = await generate_audio(text, voice, mp3_path, srt_path)

    print(f'[audio-gen] {len(boundaries)} boundary 时间戳')

    # 段落映射
    mapping = build_segment_timestamps(segments, boundaries)
    estimated_count = sum(1 for m in mapping if m.get('estimated'))

    json_path.write_text(
        json.dumps({
            'voice': voice,
            'chapter': stem,
            'duration_sec': round(boundaries[-1]['start'] + boundaries[-1]['duration'], 2) if boundaries else 0,
            'segments': mapping,
        }, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    print(f'[audio-gen] ✓ MP3 {mp3_path.stat().st_size / 1024:.0f} KB · '
          f'SRT {srt_path.stat().st_size / 1024:.0f} KB · '
          f'JSON {len(mapping)} 段映射 ({estimated_count} 估算)')
    print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = Path(sys.argv[1])
    voice_key = DEFAULT_VOICE_KEY
    do_all = False
    skip_audio = False

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith('--voice='):
            voice_key = a.split('=', 1)[1]
        elif a == '--voice' and i + 1 < len(args):
            voice_key = args[i + 1]
            i += 1
        elif a == '--all':
            do_all = True
        elif a == '--skip-audio':
            skip_audio = True
        i += 1

    if target.is_dir():
        files = sorted(target.glob('ch*.html'))
        if not do_all:
            print(f'目录模式需 --all (找到 {len(files)} 章)')
            sys.exit(1)
    else:
        files = [target]

    for f in files:
        asyncio.run(process_chapter(f, voice_key, skip_audio=skip_audio))


if __name__ == '__main__':
    main()
