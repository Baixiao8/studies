#!/usr/bin/env python3
"""
Audio Generator · 用 Edge TTS 把报告章节生成 MP3 + SRT 字幕

特点:
- 完全免费(Microsoft Azure Neural TTS,via edge-tts 社区库)
- 中文神经音色(默认云希 / 可选晓晓 / 云阳 / 云健等)
- 同时输出 MP3 音频 + SRT 字幕(含词级时间戳)
- 自动过滤 SVG / 表格 / 装饰元素(遵守 READER_RULES.md 黑名单)
- 语义增强:反共识/协议/章节加前缀朗读

用法:
  python3 _shared/audio-gen.py reports/2026-05-running-science/chapters/ch04.html
  python3 _shared/audio-gen.py reports/2026-05-running-science/chapters/ch04.html --voice Xiaoxiao
  python3 _shared/audio-gen.py reports/2026-05-running-science/chapters --all

输出:
  reports/.../audio/ch04.mp3       (MP3 音频)
  reports/.../audio/ch04.srt       (SRT 字幕,词级时间戳)
  reports/.../audio/ch04.json      (段落级时间戳映射,前端用)
"""

import sys
import re
import asyncio
import json
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print('❌ 需要安装: python3 -m pip install edge-tts')
    sys.exit(1)


# ─── 配置 ────────────────────────────────────────────────────
VOICES = {
    'Yunxi':     'zh-CN-YunxiNeural',       # 男 · 阳光 · 推荐长篇专业
    'Xiaoxiao':  'zh-CN-XiaoxiaoNeural',    # 女 · 温暖 · 经典
    'Yunyang':   'zh-CN-YunyangNeural',     # 男 · 专业可靠 · 新闻
    'Yunjian':   'zh-CN-YunjianNeural',     # 男 · 激情 · 体育
    'Xiaoyi':    'zh-CN-XiaoyiNeural',      # 女 · 活泼
    'Yunxia':    'zh-CN-YunxiaNeural',      # 男 · 可爱
}
DEFAULT_VOICE_KEY = 'Yunxi'

# 黑名单(必须与 _shared/READER_RULES.md 一致)
# 注意:reader.js 也用同一份名单,这里是 SSR 版
EXCLUDE_TAGS = ['svg', 'table', 'script', 'style']
EXCLUDE_CLASSES = [
    'hero', 'hero-keypoints', 'hero-toc-section',
    'number-strip', 'section-tag',
    'sticky-nav', 'mini-toc', 'progress-bar',
    'ref', 'chip',
    'svg-frame', 'svg-caption',
    'reader-trigger', 'reader-overlay', 'reader-mini',
]

INCLUDE_TAGS_RE = re.compile(r'<(h2|h3|h4|p|li|blockquote)([^>]*)>(.*?)</\1>', re.DOTALL | re.IGNORECASE)


def strip_excluded(html: str) -> str:
    """移除所有黑名单 selector 对应的 HTML 块"""
    # 1. 移除完整的 SVG / 表格 / script / style 块
    for tag in EXCLUDE_TAGS:
        html = re.sub(
            rf'<{tag}\b[^>]*>.*?</{tag}>',
            ' ',
            html,
            flags=re.DOTALL | re.IGNORECASE
        )
    # 2. 移除有 EXCLUDE class 的 div / figure / section / span
    for cls in EXCLUDE_CLASSES:
        # 匹配 <div class="xxx clsname yyy" ...>...</div> 任意 wrap
        for wrap in ['div', 'figure', 'section', 'span', 'aside', 'nav', 'header']:
            pattern = rf'<{wrap}[^>]*class="[^"]*\b{cls}\b[^"]*"[^>]*>.*?</{wrap}>'
            html = re.sub(pattern, ' ', html, flags=re.DOTALL | re.IGNORECASE)
    return html


def html_to_text(html: str) -> str:
    """剥离 HTML 标签,保留纯文本"""
    # 去 HTML 实体
    html = (html.replace('&nbsp;', ' ')
                .replace('&amp;', '&')
                .replace('&lt;', '<')
                .replace('&gt;', '>')
                .replace('&quot;', '"')
                .replace('&#39;', "'"))
    # 剥 tag
    html = re.sub(r'<[^>]+>', '', html)
    # 合并空白
    html = re.sub(r'\s+', ' ', html)
    return html.strip()


def extract_segments(html_file: Path):
    """
    从章节 HTML 提取「段落」列表,每段含:
    - id: data-reader-id 或自动生成
    - tag: h2 / h3 / h4 / p / li
    - css_classes: 完整 class string
    - text: 纯文本(已剥 HTML / 已加语义前缀)
    """
    content = html_file.read_text(encoding='utf-8')
    content = strip_excluded(content)

    segments = []
    auto_id = 0

    for m in INCLUDE_TAGS_RE.finditer(content):
        tag = m.group(1).lower()
        attrs = m.group(2)
        inner = m.group(3)

        # 跳过 .label callout 标签(单独跳过避免重复朗读)
        cls_match = re.search(r'class="([^"]*)"', attrs)
        css_classes = cls_match.group(1) if cls_match else ''
        if 'label' in css_classes.split():
            continue

        # 获取 reader-id(优先用现有)
        id_match = re.search(r'data-reader-id="([^"]+)"', attrs)
        seg_id = id_match.group(1) if id_match else f'auto-{auto_id}'
        auto_id += 1

        text = html_to_text(inner)
        if not text or len(text) < 2:
            continue

        # 语义增强:加上下文提示词,提高 TTS 自然度
        prefix = ''
        if 'sharp' in css_classes:
            prefix = '反共识。 '
        elif 'protocol' in css_classes and tag == 'h4':
            prefix = '协议。 '
        elif 'you' in css_classes and tag == 'p':
            # 第二人称剧本仅首段加前缀(简化:只对 .you label 后第一个 p 加)
            pass
        elif tag == 'h2':
            prefix = '本章。 '
        elif tag == 'h3':
            prefix = '小节。 '

        text = prefix + text

        # 删除 .stop 块标识前缀("⚠ 何时停")避免读得别扭
        text = re.sub(r'⚠?\s*何时停\s*', '何时停。 ', text)

        segments.append({
            'id': seg_id,
            'tag': tag,
            'classes': css_classes,
            'text': text,
        })

    return segments


def build_ssml_text(segments):
    """
    把所有段落串成一段长文本,段间加 SSML <break> 控制停顿
    edge-tts 不完全支持 SSML,我们用文字停顿(标点 + 段落分隔)
    """
    parts = []
    for seg in segments:
        text = seg['text']
        if seg['tag'] in ('h2', 'h3'):
            parts.append(f'\n\n{text}\n\n')
        elif seg['tag'] == 'h4':
            parts.append(f'\n{text}\n')
        else:
            parts.append(text)
    return ' '.join(parts)


def hns_to_sec(hns):
    """edge-tts 用 HNS(100 纳秒) → 秒"""
    return hns / 10_000_000.0


async def generate_audio(text: str, voice: str, mp3_path: Path, srt_path: Path):
    """生成 MP3 + 自己写 SRT(edge-tts 7.x 用 SentenceBoundary)
    返回 boundaries 列表:[{offset_sec, duration_sec, text}, ...]
    """
    communicate = edge_tts.Communicate(text, voice)
    audio_chunks = []
    boundaries = []

    async for chunk in communicate.stream():
        t = chunk.get('type')
        if t == 'audio':
            audio_chunks.append(chunk['data'])
        elif t in ('SentenceBoundary', 'WordBoundary'):
            boundaries.append({
                'start': hns_to_sec(chunk['offset']),
                'duration': hns_to_sec(chunk['duration']),
                'text': chunk.get('text', '').strip(),
            })

    mp3_path.write_bytes(b''.join(audio_chunks))

    # 生成 SRT(自写,不依赖 SubMaker)
    srt_lines = []
    for i, b in enumerate(boundaries, 1):
        start = b['start']
        end = start + b['duration']
        srt_lines.append(str(i))
        srt_lines.append(f'{_fmt_srt_time(start)} --> {_fmt_srt_time(end)}')
        srt_lines.append(b['text'])
        srt_lines.append('')
    srt_path.write_text('\n'.join(srt_lines), encoding='utf-8')

    return boundaries


def _fmt_srt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')


def build_segment_timestamps(segments, boundaries):
    """
    根据 boundaries(SentenceBoundary)+ 段落顺序,
    生成"段落 ID → 起始秒数"映射
    """
    # 取每个段落首 8 个非空白字符作锚点
    def norm(s):
        return re.sub(r'[\s\W_]+', '', s)

    mapping = []
    boundary_cursor = 0

    # 把所有 boundary 文本拼成一个累积字符串,索引每个 boundary 的累积位置
    cum_chars = ''
    cum_index = []  # cum_index[i] = boundaries[i] 在累积字符串里的起始偏移
    for b in boundaries:
        cum_index.append(len(cum_chars))
        cum_chars += norm(b['text'])

    norm_segments_pos = 0  # 在累积字符串里的搜索游标
    for seg in segments:
        anchor = norm(seg['text'])[:8]
        if not anchor:
            continue
        idx_in_cum = cum_chars.find(anchor, norm_segments_pos)
        if idx_in_cum < 0:
            # 退而求其次:用前 5 个字
            anchor = norm(seg['text'])[:5]
            if anchor:
                idx_in_cum = cum_chars.find(anchor, norm_segments_pos)

        if idx_in_cum >= 0:
            # 找到对应的 boundary index
            bi = 0
            for j, pos in enumerate(cum_index):
                if pos <= idx_in_cum:
                    bi = j
                else:
                    break
            start_sec = boundaries[bi]['start']
            mapping.append({
                'id': seg['id'],
                'tag': seg['tag'],
                'start': round(start_sec, 2),
                'preview': seg['text'][:30] + ('...' if len(seg['text']) > 30 else '')
            })
            norm_segments_pos = idx_in_cum + len(anchor)
        else:
            # 找不到:估算(上一段时间 + 长度 / 5)
            prev = mapping[-1]['start'] if mapping else 0
            mapping.append({
                'id': seg['id'],
                'tag': seg['tag'],
                'start': round(prev + len(seg['text']) / 5, 2),
                'preview': seg['text'][:30],
                'estimated': True,
            })

    return mapping


async def process_chapter(html_file: Path, voice_key: str = DEFAULT_VOICE_KEY, out_dir: Path = None):
    """处理单章节:提取 → 生成 MP3 + SRT → 输出段落时间戳 JSON"""
    voice = VOICES.get(voice_key, VOICES[DEFAULT_VOICE_KEY])
    print(f'[audio-gen] === {html_file.name} ===')
    print(f'[audio-gen] 音色: {voice}')

    segments = extract_segments(html_file)
    print(f'[audio-gen] 提取 {len(segments)} 个段落')

    text = build_ssml_text(segments)
    chars = len(text)
    print(f'[audio-gen] 字符数: {chars:,}')
    print(f'[audio-gen] 预估时长: ~{chars / 280:.1f} 分钟(1.0x)')

    # 输出目录
    if out_dir is None:
        out_dir = html_file.parent.parent / 'audio'
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = html_file.stem
    mp3_path = out_dir / f'{stem}.mp3'
    srt_path = out_dir / f'{stem}.srt'
    json_path = out_dir / f'{stem}.json'

    # 生成
    print(f'[audio-gen] 生成中...(约 {chars / 1500:.1f} 分钟)')
    boundaries = await generate_audio(text, voice, mp3_path, srt_path)
    print(f'[audio-gen] 收到 {len(boundaries)} 个 boundary 时间戳')

    # 段落映射
    mapping = build_segment_timestamps(segments, boundaries)
    json_path.write_text(
        json.dumps({
            'voice': voice,
            'duration_estimate_sec': round(chars / 280 * 60, 1),
            'segments': mapping,
        }, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    print(f'[audio-gen] ✓ MP3: {mp3_path.relative_to(html_file.parent.parent.parent.parent)} '
          f'({mp3_path.stat().st_size / 1024:.0f} KB)')
    print(f'[audio-gen] ✓ SRT: {srt_path.stat().st_size / 1024:.0f} KB '
          f'/ {len(mapping)} 段映射')
    print(f'[audio-gen] ✓ JSON: {json_path.relative_to(html_file.parent.parent.parent.parent)}')
    print()


def main():
    if len(sys.argv) < 2:
        print('用法: python3 audio-gen.py <chapter.html|chapters_dir> [--voice Yunxi|Xiaoxiao|...] [--all]')
        sys.exit(1)

    target = Path(sys.argv[1])
    voice_key = DEFAULT_VOICE_KEY
    do_all = False

    for arg in sys.argv[2:]:
        if arg.startswith('--voice='):
            voice_key = arg.split('=')[1]
        elif arg == '--voice' and sys.argv.index(arg) + 1 < len(sys.argv):
            voice_key = sys.argv[sys.argv.index(arg) + 1]
        elif arg == '--all':
            do_all = True

    if target.is_dir():
        files = sorted(target.glob('ch*.html'))
        if not do_all:
            print(f'[audio-gen] 目录模式,加 --all 才会跑全部({len(files)} 章)')
            sys.exit(1)
    else:
        files = [target]

    for f in files:
        asyncio.run(process_chapter(f, voice_key))


if __name__ == '__main__':
    main()
