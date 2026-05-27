#!/usr/bin/env python3
"""Embed 10 chapter hero images into 运动科学手册.html.

Insert a .ch-hero block right inside each <section id="sN">'s .container,
before the .section-tag div. Also append CSS for .ch-hero in the style block.
"""
import re
from pathlib import Path

SRC = Path("/Users/baixiao/白笑/claude/运动健康/运动科学手册.html")
html = SRC.read_text(encoding="utf-8")

# ============================================================================
# 1. Add CSS for .ch-hero before </style>
# ============================================================================
CH_HERO_CSS = """
  /* =================================================================
     v4 CHAPTER HERO IMAGES — full-width 16:9 cinematic banners
     ================================================================= */
  .ch-hero {
    position: relative;
    width: 100%;
    margin: 0 0 56px;
    border-radius: 4px;
    overflow: hidden;
    background: var(--bg-deep);
    aspect-ratio: 16 / 9;
    max-height: 460px;
  }
  .ch-hero img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    filter: contrast(1.04) brightness(0.94);
  }
  .ch-hero::after {
    content: '';
    position: absolute;
    inset: 0;
    pointer-events: none;
    background: linear-gradient(180deg,
        transparent 50%,
        rgba(14,14,12,0.55) 88%,
        rgba(14,14,12,0.92) 100%);
  }
  @media (max-width: 880px) {
    .ch-hero { margin-bottom: 36px; max-height: 280px; }
  }

"""

assert "</style>" in html
html = html.replace("</style>", CH_HERO_CSS + "</style>", 1)
print("✓ CSS added")

# ============================================================================
# 2. Insert .ch-hero block at the start of each section's .container
# ============================================================================
# Pattern: <section id="sN" ...>\s*<div class="container">
# Insert immediately after <div class="container">

inserted = 0
for n in range(1, 11):
    pattern = rf'(<section id="s{n}"[^>]*>\s*<div class="container">)'
    hero_block = f'\n    <div class="ch-hero"><img src="images/s{n}_hero.jpg" alt="" loading="lazy"></div>'
    m = re.search(pattern, html)
    if not m:
        print(f"✗ s{n}: anchor not found")
        continue
    html = html.replace(m.group(0), m.group(0) + hero_block, 1)
    inserted += 1
    print(f"✓ s{n}: hero inserted")

print(f"\n{inserted}/10 inserted")

SRC.write_text(html, encoding="utf-8")
print(f"  size: {len(html):,} chars / {html.count(chr(10))+1} lines")
