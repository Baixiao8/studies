#!/usr/bin/env python3
"""v3 visualization integration:
- Add CSS components (chips, status-list, metric cards, comparison, bar, timeline, etc.)
- Insert 6 main SVGs (energy, lactate, distribution, carb-load, ACWR, taper)
- Insert 6 workout sparklines + sleep donut + A/B/C cascade
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, "/tmp")
from v3_payloads import (
    CSS_COMPONENTS,
    SVG_ENERGY, SVG_LACTATE, SVG_DISTRIBUTION, SVG_CARBLOAD,
    SVG_ACWR, SVG_TAPER, SVG_SLEEP, SVG_ABC,
    SPARK_LSD, SPARK_TEMPO, SPARK_INTERVAL, SPARK_REP, SPARK_MP, SPARK_STRIDES,
)

SRC = Path("/Users/baixiao/白笑/claude/运动健康/运动科学手册.html")
html = SRC.read_text(encoding="utf-8")


def insert_after_anchor(html, anchor_regex, payload, name):
    """Insert payload immediately after the first match of anchor_regex."""
    m = re.search(anchor_regex, html, re.S)
    if not m:
        raise SystemExit(f"✗ anchor not found: {name}")
    end = m.end()
    return html[:end] + "\n\n    " + payload + "\n" + html[end:]


# ============================================================================
# 1. Add CSS components before </style>
# ============================================================================
assert "</style>\n</head>" in html
html = html.replace("</style>\n</head>", CSS_COMPONENTS + "\n</style>\n</head>", 1)
print("✓ 01 CSS components")

# ============================================================================
# 2. Insert SVG_ENERGY into §1.1 (after the closing of "三大能量系统" intro)
# ============================================================================
# Anchor: end of </p> right after the §1.1 h3
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">1\.1</span>三大能量系统</h3>\s*<p[^>]*>.*?</p>',
    SVG_ENERGY,
    "§1.1 energy systems",
)
print("✓ 02 SVG_ENERGY → §1.1")

# ============================================================================
# 3. Insert SVG_LACTATE into §1.4
# ============================================================================
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">1\.4</span>乳酸阈.*?</h3>\s*<p[^>]*>.*?</p>',
    SVG_LACTATE,
    "§1.4 lactate",
)
print("✓ 03 SVG_LACTATE → §1.4")

# ============================================================================
# 4. Insert SVG_DISTRIBUTION into §2.2 (after first <p> of 强度分布)
# ============================================================================
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">2\.2</span>强度分布.*?</h3>\s*<p[^>]*>.*?</p>',
    SVG_DISTRIBUTION,
    "§2.2 distribution",
)
print("✓ 04 SVG_DISTRIBUTION → §2.2")

# ============================================================================
# 5. Insert workout sparklines in §3 before each subsection's body
# ============================================================================
# §3.1 LSD
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">3\.1</span>长距离慢跑.*?</h3>',
    SPARK_LSD,
    "§3.1 LSD sparkline",
)
# §3.2 Tempo
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">3\.2</span>节奏跑.*?</h3>',
    SPARK_TEMPO,
    "§3.2 Tempo sparkline",
)
# §3.3 Intervals
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">3\.3</span>间歇训练.*?</h3>',
    SPARK_INTERVAL,
    "§3.3 Interval sparkline",
)
# §3.4 MP
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">3\.4</span>马拉松配速.*?</h3>',
    SPARK_MP,
    "§3.4 MP sparkline",
)
# §3.5 Strides
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">3\.5</span>Strides.*?</h3>',
    SPARK_STRIDES,
    "§3.5 Strides sparkline",
)
print("✓ 05 5 workout sparklines → §3")

# ============================================================================
# 6. Insert SVG_CARBLOAD into §5.3 (carb load)
# ============================================================================
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">5\.3</span>比赛 carb load.*?</h3>\s*<p[^>]*>.*?</p>',
    SVG_CARBLOAD,
    "§5.3 carb load timeline",
)
print("✓ 06 SVG_CARBLOAD → §5.3")

# ============================================================================
# 7. Insert SVG_SLEEP into §6.1
# ============================================================================
# Insert right before §6.2 (after §6.1 closes)
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">6\.1</span>睡眠为什么决定一切</h3>',
    SVG_SLEEP,
    "§6.1 sleep donut",
)
print("✓ 07 SVG_SLEEP → §6.1")

# ============================================================================
# 8. Insert SVG_ACWR into §8.2
# ============================================================================
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">8\.2</span>ACWR.*?</h3>\s*<p[^>]*>.*?</p>',
    SVG_ACWR,
    "§8.2 ACWR gauge",
)
print("✓ 08 SVG_ACWR → §8.2")

# ============================================================================
# 9. Insert SVG_TAPER into §9.1
# ============================================================================
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">9\.1</span>Taper · 减量协议</h3>',
    SVG_TAPER,
    "§9.1 taper chart",
)
print("✓ 09 SVG_TAPER → §9.1")

# ============================================================================
# 10. Insert SVG_ABC into §9.8 (A/B/C tiers)
# ============================================================================
html = insert_after_anchor(
    html,
    r'<h3><span class="pre">9\.8</span><span class="pre">A/B/C TIERS</span>.*?</h3>\s*<p[^>]*>.*?</p>',
    SVG_ABC,
    "§9.8 A/B/C cascade",
)
print("✓ 10 SVG_ABC → §9.8")

# ============================================================================
# 11. Bump version
# ============================================================================
html = html.replace("v2 · 2026.05", "v3 · 2026.05")
html = html.replace("v2", "v3", 1)  # one more bump in footer if not yet
print("✓ 11 Version bumped to v3")

# ============================================================================
SRC.write_text(html, encoding="utf-8")
print()
print(f"✓ v3 integration complete")
print(f"  file size: {len(html):,} chars  ({len(html)/1024:.1f} KB)")
print(f"  line count: {html.count(chr(10)) + 1}")
