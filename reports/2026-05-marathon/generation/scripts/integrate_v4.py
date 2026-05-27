#!/usr/bin/env python3
"""Integrate 20 visualized section fragments into 运动科学手册.html.

Each fragment in /tmp/manual_frags/sec_X_Y.html replaces the corresponding
<h3 …>X.Y …</h3> ... block (up to the next <h3) in the main HTML.

Agent fragments use:
  <section class="chapter" id="sec-X-Y"> ... </section>  with <h3>§X.Y title</h3>
Self-written fragments use raw <h3><span class="pre">X.Y</span>title</h3> directly.

Normalization rules during insertion:
  - strip any wrapping <section class="chapter">...</section>
  - convert  <h3>§X.Y title</h3>  →  <h3><span class="pre">X.Y</span>title</h3>
"""
import re
from pathlib import Path

SRC = Path("/Users/baixiao/白笑/claude/运动健康/运动科学手册.html")
FRAGS = Path("/tmp/manual_frags")

html = SRC.read_text(encoding="utf-8")
print(f"original: {len(html):,} chars, {html.count(chr(10))+1} lines")

# Map: section number -> fragment file
SECTIONS = [
    "1.5", "1.6", "1.7",
    "2.5", "2.6",
    "4.2", "4.6",
    "6.3",
    "7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "7.8",
    "8.1",
    "9.4", "9.5",
    "10.5",
]


def normalize_fragment(content: str, sec_num: str) -> str:
    """Normalize agent fragment into manual's native h3 format."""
    # strip wrapping <section class="chapter">...</section>
    content = re.sub(
        r'^\s*<section\s+class="chapter"[^>]*>\s*',
        '',
        content,
        flags=re.S,
    )
    content = re.sub(
        r'^\s*<section\s+id="sec-[^"]*"[^>]*>\s*',
        '',
        content,
        flags=re.S,
    )
    content = re.sub(
        r'\s*</section>\s*$',
        '',
        content,
        flags=re.S,
    )

    # convert  <h3>§X.Y title</h3>  →  <h3><span class="pre">X.Y</span>title</h3>
    # Note the §  symbol that agents prepended
    content = re.sub(
        rf'<h3>§{re.escape(sec_num)}\s*(.+?)</h3>',
        rf'<h3><span class="pre">{sec_num}</span>\1</h3>',
        content,
        count=1,
    )
    # also handle "<h3>X.Y title</h3>" without §
    content = re.sub(
        rf'<h3>{re.escape(sec_num)}\s+(.+?)</h3>',
        rf'<h3><span class="pre">{sec_num}</span>\1</h3>',
        content,
        count=1,
    )
    return content.strip()


def replace_section(html: str, sec_num: str, new_content: str) -> str:
    """Find <h3>...<span class="pre">X.Y</span>...</h3> in html and replace
    everything up to (but not including) the next <h3 with new_content."""
    # Build regex: start at <h3><span class="pre">X.Y</span>, capture up to next <h3 or section close
    pattern = re.compile(
        rf'<h3><span class="pre">{re.escape(sec_num)}</span>.*?'
        rf'(?=<h3><span class="pre">|</div>\s*</section>)',
        re.S,
    )
    m = pattern.search(html)
    if not m:
        raise ValueError(f"section {sec_num} not found in main HTML")
    old_block = m.group(0)
    # Add trailing whitespace before the next h3
    new_block = new_content + "\n\n    "
    return html.replace(old_block, new_block, 1)


fail = []
for sec in SECTIONS:
    frag_path = FRAGS / f"sec_{sec.replace('.', '_')}.html"
    if not frag_path.exists():
        fail.append((sec, "fragment file missing"))
        continue
    raw = frag_path.read_text(encoding="utf-8")
    try:
        normalized = normalize_fragment(raw, sec)
        html = replace_section(html, sec, normalized)
        print(f"  ✓ §{sec}: {len(raw):,} → replaced")
    except Exception as e:
        fail.append((sec, str(e)))
        print(f"  ✗ §{sec}: {e}")

if fail:
    print(f"\n✗ {len(fail)} sections failed:")
    for s, e in fail:
        print(f"  §{s}: {e}")
else:
    print(f"\n✓ all {len(SECTIONS)} sections replaced")

# bump version
html = html.replace("v2 · 2026.05", "v4 · 2026.05", 1)
html = html.replace("SPORTS SCIENCE FIELD MANUAL · 2026.05.21 · v2",
                    "SPORTS SCIENCE FIELD MANUAL · 2026.05.21 · v4", 1)

SRC.write_text(html, encoding="utf-8")
print(f"\nwritten: {len(html):,} chars, {html.count(chr(10))+1} lines")
