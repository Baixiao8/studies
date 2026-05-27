#!/usr/bin/env python3
"""Apply all v2 polish edits to 运动科学手册.html.

Uses regex extraction from the live file (instead of hard-coded OLD strings)
to avoid full-width vs ASCII punctuation mismatches.
"""
import re
from pathlib import Path

SRC = Path("/Users/baixiao/白笑/claude/运动健康/运动科学手册.html")
html = SRC.read_text(encoding="utf-8")


def replace_by_regex(html, pattern, replacement, name):
    """Replace first regex match with literal replacement. Asserts match."""
    m = re.search(pattern, html, re.S)
    if not m:
        raise SystemExit(f"✗ pattern not found: {name}")
    return html.replace(m.group(0), replacement, 1)


# ============================================================================
# 1. CSS additions
# ============================================================================
CSS_ADDITIONS = """
  /* ===== 顶部阅读进度条 ===== */
  .progress-bar {
    position: fixed; top: 0; left: 0; height: 2px; width: 0;
    background: linear-gradient(90deg, var(--accent) 0%, #e8c068 100%);
    box-shadow: 0 0 8px rgba(212, 165, 72, 0.5);
    z-index: 9999; transition: width 0.08s linear; will-change: width;
  }

  /* ===== Hero 章节预览卡片 ===== */
  .hero-toc {
    display: grid; grid-template-columns: repeat(2, 1fr);
    gap: 12px; margin: 38px 0 8px;
  }
  .hero-toc .card {
    position: relative; padding: 16px 18px 16px 20px;
    background: var(--bg-card); border: 1px solid var(--line);
    border-left: 3px solid var(--ch-color, var(--accent));
    border-radius: 4px; text-decoration: none; color: inherit;
    transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
    display: block;
  }
  .hero-toc .card:hover {
    transform: translateX(2px) translateY(-1px);
    background: #23231f;
    border-color: var(--ch-color, var(--accent));
  }
  .hero-toc .card .num {
    font-family: "JetBrains Mono", monospace; font-size: 11px;
    color: var(--accent); letter-spacing: 0.04em;
    display: block; margin-bottom: 6px;
  }
  .hero-toc .card .title {
    font-size: 17px; font-weight: 700; color: var(--ink);
    line-height: 1.3; margin-bottom: 6px;
    font-family: "Noto Serif SC", "PingFang SC", serif;
  }
  .hero-toc .card .desc {
    font-size: 13px; color: var(--ink-soft); line-height: 1.55;
  }
  @media (max-width: 720px) {
    .hero-toc { grid-template-columns: 1fr; }
    .hero-toc .card .title { font-size: 15.5px; }
  }

  /* ===== 分享提示横幅 ===== */
  .share-note {
    margin: 18px 0 0; padding: 12px 18px;
    border: 1px dashed var(--c-psych);
    background: rgba(156, 75, 181, 0.08);
    border-radius: 4px; font-size: 13.5px;
    line-height: 1.65; color: var(--ink-soft);
  }
  .share-note strong { color: var(--c-psych); font-weight: 600; letter-spacing: 0.02em; }
  .share-note .mark { display: inline-block; color: var(--c-psych); font-size: 14px; margin: 0 2px; }

  /* ===== 文献引用 inline ===== */
  .ref {
    font-family: "JetBrains Mono", monospace; font-size: 10.5px;
    color: var(--ink-faint); letter-spacing: 0.04em;
    margin-left: 4px; opacity: 0.85;
  }
"""

assert "</style>\n</head>" in html
html = html.replace("</style>\n</head>", CSS_ADDITIONS + "\n</style>\n</head>", 1)
print("✓ 01 CSS")

# ============================================================================
# 2. Progress bar div after <body>
# ============================================================================
assert "</head>\n<body>" in html
html = html.replace(
    "</head>\n<body>",
    '</head>\n<body>\n<div class="progress-bar" id="progressBar"></div>',
    1,
)
print("✓ 02 Progress bar div")

# ============================================================================
# 3. Hero TOC + Share Note before </header>
# ============================================================================
HERO_TOC = """    </div>

    <nav class="hero-toc" aria-label="章节导航">
      <a class="card" href="#s1" style="--ch-color: var(--c-physio);">
        <span class="num">01 · 5 min</span>
        <div class="title">生理基础</div>
        <div class="desc">能量系统、HR 区间、VO2max、乳酸阈、跑步经济、体温调节，跑步背后的身体逻辑。</div>
      </a>
      <a class="card" href="#s2" style="--ch-color: var(--c-theory);">
        <span class="num">02 · 6 min</span>
        <div class="title">训练理论</div>
        <div class="desc">5 大主流流派 + 挪威双阈值，理解差异才能为自己选对路径，而不是盲跟课表。</div>
      </a>
      <a class="card" href="#s3" style="--ch-color: var(--c-session);">
        <span class="num">03 · 5 min</span>
        <div class="title">课表机理</div>
        <div class="desc">每种课刺激什么生理通路：长距、间歇、节奏、法特莱克。理解后不再天天间歇。</div>
      </a>
      <a class="card" href="#s4" style="--ch-color: var(--c-strength);">
        <span class="num">04 · 5 min</span>
        <div class="title">力量与跑姿</div>
        <div class="desc">跑者最被低估的一块，提升跑步经济性 + 抗伤的最高 ROI，每周两次即可见效。</div>
      </a>
      <a class="card" href="#s5" style="--ch-color: var(--c-nutrition);">
        <span class="num">05 · 6 min</span>
        <div class="title">营养水合</div>
        <div class="desc">比赛日最容易拿到也最常丢掉的 10%：碳水周期、赛日补给、电解质策略全梳理。</div>
      </a>
      <a class="card" href="#s6" style="--ch-color: var(--c-recovery);">
        <span class="num">06 · 4 min</span>
        <div class="title">睡眠恢复</div>
        <div class="desc">训练只是打开适应通道，恢复才真正完成适应。睡眠、冷热疗、主动恢复全套手段。</div>
      </a>
      <a class="card" href="#s7" style="--ch-color: var(--c-psych);">
        <span class="num">07 · 4 min</span>
        <div class="title">运动心理</div>
        <div class="desc">破三最后 5% 拼的是脑子：撞墙判断、长距孤独、自我对话、注意策略实操指南。</div>
      </a>
      <a class="card" href="#s8" style="--ch-color: var(--c-injury);">
        <span class="num">08 · 5 min</span>
        <div class="title">伤病康复</div>
        <div class="desc">跑者年均伤病率 50-79%，多数源于负荷管理失误。ACWR、回归跑步原则与常见伤病。</div>
      </a>
      <a class="card" href="#s9" style="--ch-color: var(--c-race);">
        <span class="num">09 · 12 min</span>
        <div class="title">比赛 &amp; Taper</div>
        <div class="desc">23 周训练能否兑现，看赛前 2 周减量 + 赛日执行。A/B/C 目标、GI、天气、撞墙重启。</div>
      </a>
      <a class="card" href="#s10" style="--ch-color: var(--c-post);">
        <span class="num">10 · 5 min</span>
        <div class="title">赛后 &amp; 冷知识</div>
        <div class="desc">比赛跑完不是结束：恢复节奏、复盘方法，外加碳板、热适应等业内前沿话题。</div>
      </a>
      <a class="card" href="#appendix" style="--ch-color: var(--accent); grid-column: 1 / -1;">
        <span class="num">附 · 参考</span>
        <div class="title">附录 · VDOT × Pace 大表</div>
        <div class="desc">VDOT 配速对照、关键数字、术语表、推荐阅读、自勉清单。</div>
      </a>
    </nav>

    <div class="share-note">
      <strong>分享提示：</strong>文中标记 <span class="mark">◐</span>「你的数据」的紫色卡片是个人样本数据（共 6 处），队友阅读时可直接跳过；其余 99% 内容人人适用。
    </div>
  </div>
</header>"""

assert "    </div>\n  </div>\n</header>" in html
html = html.replace("    </div>\n  </div>\n</header>", HERO_TOC, 1)
print("✓ 03 Hero TOC")

# ============================================================================
# 4. VDOT replacement (§2.4)
# ============================================================================
NEW_VDOT = """    <h4>你的 VDOT</h4>
    <p>把目标代入 Daniels 表里看：当前能力 <strong>全马 3:20</strong> 对应 <strong>VDOT 48</strong>，恰好对应 <strong>10K 39:00</strong> —— 这是一致、不偏科的画像，说明 5K/10K 端速度与全马耐力匹配，问题不在某一极。<strong>破三（sub-3:00）= VDOT 54</strong>，全马 2:58:21。从 48 跳到 54 是 6 个 VDOT 点，相当于 <strong>VO2max 当量提升约 12.5%</strong>。</p>
    <p>23 周拿下 6 个点：<strong>可行，但属激进区间</strong>。业内经验值 —— 精英级每年 1-2 点、中等水平每年 3-5 点、新手通过结构化训练首年 5-8 点。你不算新手所以涨幅天花板更低，6 点要求训练量、营养、睡眠三项同时不掉链子，任何一环放水都会变成「涨 3-4 点 + PB 但没破三」。<span class="ref">(Daniels 2014)</span></p>
    <table>
      <thead><tr><th>VDOT</th><th>全马</th><th>半马</th><th>10K</th><th>5K</th></tr></thead>
      <tbody>
        <tr><td>48</td><td><span class="mono">3:21:29</span></td><td><span class="mono">1:36:09</span></td><td><span class="mono">39:00</span></td><td><span class="mono">18:48</span></td></tr>
        <tr><td>50</td><td><span class="mono">3:14:06</span></td><td><span class="mono">1:32:34</span></td><td><span class="mono">37:31</span></td><td><span class="mono">18:05</span></td></tr>
        <tr><td>52</td><td><span class="mono">3:05:58</span></td><td><span class="mono">1:29:15</span></td><td><span class="mono">36:09</span></td><td><span class="mono">17:24</span></td></tr>
        <tr><td>54</td><td><span class="mono">2:58:21</span></td><td><span class="mono">1:26:15</span></td><td><span class="mono">34:54</span></td><td><span class="mono">16:48</span></td></tr>
      </tbody>
    </table>
    <div class="callout ops">
      <div class="label">OPS</div>
      <p>每 4-6 周用一次 5K/10K 测试或半马模拟反推当前 VDOT，对照训练配速表更新 E/M/T/I/R 五档配速。涨 1 点 ≈ 全马快 3-4 分钟。完整 VDOT × 配速大表见 <a href="#appendix" style="color:var(--accent)">附录 A.2</a>。</p>
    </div>"""

html = replace_by_regex(
    html,
    r'<h4>你的 VDOT</h4>\s*<p>你的现状.*?睡眠不崩）。</p>',
    NEW_VDOT,
    "§2.4 VDOT block",
)
print("✓ 04 VDOT fix")

# ============================================================================
# 5. §5.1 per-kg replacement
# ============================================================================
NEW_KG = """    <h3><span class="pre">5.1</span>日常宏量营养</h3>
    <p class="lead">所有数字按 <strong>每 kg 体重</strong> 给出 —— 绝对克数只对某个体重的人成立。不同队友体重不一，请按自己的 kg 算。下表附 60/70/80 kg 三档示例。</p>
    <h4>碳水化合物 (Carbs)</h4>
    <ul>
      <li><strong>4-7 g/kg/day</strong>：轻松日取低端，大强度/长距日取高端</li>
      <li><strong>7-10 g/kg/day</strong>：连续高强度 / 大跑量训练日</li>
      <li>赛前 carb load（36-48h）：<strong>8-12 g/kg/day</strong>（8-10 g/kg 是更现实目标，12 g/kg 多数人胃肠不耐受）</li>
    </ul>
    <h4>蛋白质</h4>
    <ul>
      <li>耐力运动员需要 <strong>1.6-2.0 g/kg/day</strong>（比一般人高 50-80%）</li>
      <li>分散到 4-5 餐，每餐 0.3-0.4 g/kg，吸收效率最优</li>
      <li>训练后 30-60 分钟窗口含 20-30 g 高质量蛋白（乳清 / 鸡蛋 / 鱼）</li>
    </ul>
    <h4>脂肪</h4>
    <ul>
      <li>不必刻意限制，<strong>25-35% 总热量</strong>合理</li>
      <li>优质来源：橄榄油、坚果、深海鱼（omega-3 抗炎）</li>
      <li><strong>Keto / 低碳 / 生酮</strong> 对马拉松<em>不推荐</em>。脂肪氧化能力提升换不来糖酵解供能损失</li>
    </ul>
    <h4>三档体重示例</h4>
    <table>
      <thead><tr><th>体重</th><th>日常碳水/天</th><th>Carb Load/天</th><th>蛋白/天</th><th>赛中/h</th></tr></thead>
      <tbody>
        <tr><td><span class="mono">60 kg</span></td><td><span class="mono">240-420 g</span></td><td><span class="mono">480-600 g</span></td><td><span class="mono">96-120 g</span></td><td><span class="mono">60-90 g</span></td></tr>
        <tr><td><span class="mono">70 kg</span></td><td><span class="mono">280-490 g</span></td><td><span class="mono">560-700 g</span></td><td><span class="mono">112-140 g</span></td><td><span class="mono">60-90 g</span></td></tr>
        <tr><td><span class="mono">80 kg</span></td><td><span class="mono">320-560 g</span></td><td><span class="mono">640-800 g</span></td><td><span class="mono">128-160 g</span></td><td><span class="mono">60-90 g</span></td></tr>
      </tbody>
    </table>
    <div class="callout note">
      <div class="label">NOTE</div>
      <p>赛中碳水（60-90 g/h）与体重弱相关、与强度+肠道耐受度强相关。80 kg 与 60 kg 跑者同配速下肝糖耗速差异远小于直觉。<span class="ref">(Burke et al. 2019; Thomas et al. 2016)</span></p>
    </div>"""

html = replace_by_regex(
    html,
    r'<h3><span class="pre">5\.1</span>日常宏量营养</h3>.*?Keto / 低碳 / 生酮</strong> 对马拉松<em>不推荐</em>。脂肪氧化能力提升换不来糖酵解供能损失</li>\s*</ul>',
    NEW_KG,
    "§5.1 per-kg",
)
print("✓ 05 per-kg")

# ============================================================================
# 6. §5.4 carb 1:0.8 enhancement (append a deeper subsection after existing ul)
# ============================================================================
ADD_RATIO_DETAIL = """
    <h4>5.4.1 为什么是 1:0.8 而不是 2:1</h4>
    <p>早年（2004-2015）推荐的混合比例是 <strong>2:1（葡 2 + 果 1）</strong>。Jeukendrup 团队 2020 年后更新为 <strong>1:0.8</strong>，原因是高摄入场景（&gt;90 g/h）下，更多果糖比例反而能减少胃肠不适、提升氧化率到 ~1.75 g/min。<strong>市售凝胶里：Maurten 320 / SiS Beta Fuel 已采用 1:0.8；GU、Cliff Shot Bloks 仍是 2:1</strong> —— 读配料表比读营销页有用。日常训练 60 g/h 以下两种都行；目标超 80 g/h，认准新比例。<span class="ref">(Jeukendrup 2020; King et al. 2022)</span></p>
    <h4>训练胃 (Gut Training)</h4>"""

# Replace the spot where "训练胃 (Gut Training)" h4 starts with ratio detail + that h4
html = replace_by_regex(
    html,
    r'\s*<h4>训练胃 \(Gut Training\)</h4>',
    ADD_RATIO_DETAIL,
    "§5.4 ratio insertion point",
)
print("✓ 06 carb 1:0.8")

# ============================================================================
# 7. §6.1 sleep replacement
# ============================================================================
NEW_SLEEP = """    <h3><span class="pre">6.1</span>睡眠为什么决定一切</h3>
    <h4>睡眠期间发生什么</h4>
    <ul>
      <li><strong>深度 NREM 睡眠</strong>：生长激素分泌高峰，蛋白合成、骨修复、糖原储存</li>
      <li><strong>REM 睡眠</strong>：神经整合（学习运动模式）、心理修复、情绪调节</li>
      <li><strong>整夜分泌的睾酮 / 皮质醇调控</strong>，决定第二天的训练耐受能力</li>
    </ul>
    <h4>「急性剥夺」vs「慢性不足」：别搞混</h4>
    <p>常见说法「每晚少睡 1 小时 → VO2max -3%」是<strong>偷换概念</strong>。原始 Reilly &amp; Edwards (1993) 研究的是<strong>急性完全剥夺一晚睡眠</strong>后第二天的力竭测试表现，约下降 3% —— 这是一次性极端情境，不是「每天少睡 1 小时」的累积效应。</p>
    <p>真正影响跑者的是<strong>慢性睡眠不足</strong>，机制完全不同：(1) 皮质醇基线升高 → 肌肉合成代谢受损；(2) 糖原储备效率下降 10-15%；(3) 免疫功能下降 → 上呼吸道感染概率升高；(4) <strong>受伤风险显著上升</strong> —— Milewski (2014) 对青少年运动员的研究显示，每晚睡眠 &lt;8 小时者运动损伤风险是 ≥8 小时者的 <strong>1.7 倍</strong>。VO2max 这种生理顶值在慢性少睡下通常变化不大，但<strong>训练耐受度、恢复速度、伤病率</strong>才是真正被磨损的指标。</p>
    <table>
      <thead><tr><th>睡眠场景</th><th>影响</th><th>研究依据</th></tr></thead>
      <tbody>
        <tr><td>1 晚完全剥夺</td><td>力竭跑表现 -3%，反应时间 ≈ 血液酒精 0.08%</td><td>Reilly &amp; Edwards 1993</td></tr>
        <tr><td>连续 1 周 &lt; 6h/晚</td><td>注意力 -10-15%、糖原储备效率下降</td><td>Mah 2011</td></tr>
        <tr><td>慢性 &lt; 8h</td><td>RHR 上升、皮质醇升高、<strong>伤病风险 +1.7x</strong></td><td>Milewski 2014; Watson 2017</td></tr>
      </tbody>
    </table>
    <div class="callout note">
      <div class="label">NOTE</div>
      <p>Reilly &amp; Edwards 是单晚全剥夺设计（n=8、力竭跑）；Milewski 是 112 名运动员的横断面流行病学。前者描述「急性极端」，后者描述「慢性常态」。把单次实验外推到日常作息会得出夸张结论 —— 但后者足以解释为何长期 6 小时党更容易伤。</p>
    </div>"""

html = replace_by_regex(
    html,
    r'<h3><span class="pre">6\.1</span>睡眠为什么决定一切</h3>.*?<td>1 晚 &lt; 4h</td><td>反应时间相当于<strong>血液酒精浓度 0\.08%</strong></td></tr>\s*</tbody>\s*</table>',
    NEW_SLEEP,
    "§6.1 sleep block",
)
print("✓ 07 sleep")

# ============================================================================
# 8. §10.3 carbon shoe replacement
# ============================================================================
NEW_SHOE = """    <h3><span class="pre">10.3</span>顶级前沿 #1 · 碳板跑鞋 —— 4% 是 Nike 的，不是所有碳板鞋的</h3>
    <p>「碳板鞋提升跑步经济性 4%」这个数字来自 Hoogkamer (2018) —— 但那是<strong>特定测试条件下、Nike Vaporfly 4% 原型对照传统竞速鞋</strong>的实验室结果，由 Nike 资助。后续独立 meta-analysis 显示真实情况复杂得多：Healey &amp; Hoogkamer (2022)、Knopp et al. (2023) 综合多品牌数据，<strong>平均提升 2-4%</strong>，<strong>个体差异 0-6%</strong> —— 有约 10% 跑者穿上反而变慢（步态匹配不上摇杆几何）。</p>
    <p>厚泡棉（PEBA 中底）+ 碳板的「超鞋」组合里，碳板本身只贡献约 0.3-0.8%，<strong>真正的提升来自 PEBA 中底的能量回弹</strong>。所以「看到碳板就以为有 4%」是品牌营销造成的误读。</p>
    <ul>
      <li>对中前掌跑者收益更大（碳板对触地短的人响应更好）</li>
      <li>对触地时间 &gt; 260ms 的后跟跑者收益较小</li>
      <li>训练里穿便宜鞋、比赛日穿超鞋，是性价比最优组合</li>
      <li>训练里只穿超鞋 → 跟腱 / 小腿肌肉适应能力下降</li>
    </ul>
    <div class="callout sharp">
      <div class="label">SHARP TAKE</div>
      <p><strong>不是所有碳板鞋等价</strong>。4% 是 Nike Vaporfly 系列的专属数字；Adidas Adios Pro、Asics Metaspeed Sky/Edge 独立测试约 2-3%；二三线品牌的「碳板鞋」如果用 EVA 或低端 TPU 中底，提升可能 &lt;1%。<strong>判断标准看中底材料，不看碳板</strong> —— PEBA / Pebax 才是关键词。买之前花 30 分钟试跑，看自己步态吃不吃这套几何。<span class="ref">(Hoogkamer et al. 2018; Healey &amp; Hoogkamer 2022; Knopp et al. 2023)</span></p>
    </div>"""

html = replace_by_regex(
    html,
    r'<h3><span class="pre">10\.3</span>顶级前沿 #1 · 碳板跑鞋</h3>.*?训练里只穿碳板 → 跟腱 / 小腿肌肉适应能力下降</li>\s*</ul>',
    NEW_SHOE,
    "§10.3 carbon shoe",
)
print("✓ 08 carbon shoe")

# ============================================================================
# 9. §10.8 menstrual rewrite
# ============================================================================
NEW_MENS = """    <h3><span class="pre">10.8</span>顶级前沿 #6 · 女性月经周期训练 —— 个体化是唯一靠谱的协议</h3>
    <p>过去 20 年运动科学绝大多数样本来自男性 —— 按 Elliott-Sale et al. (2021) 系统综述统计，<strong>女性受试者在运动科学论文中占比不到 6%</strong>，且多集中在「低风险窗口」。所以任何写得很笃定的「经期训练协议」都需要打折看。下面是当前 Stacy Sims、Elliott-Sale 等研究者整理的主流认识，按四个阶段拆解：</p>
    <div class="grid-4">
      <div class="card">
        <h4>卵泡期 Day 1-14</h4>
        <p class="desc">雌激素从低位回升、黄体酮极低。整体生理状态<strong>最接近男性基线</strong> —— 疼痛阈值高、热应激低、糖原利用效率好。是排力量、VO2max 强度课、PB 测试的<strong>黄金窗口</strong>。</p>
      </div>
      <div class="card">
        <h4>排卵期 ≈ Day 14</h4>
        <p class="desc">雌激素峰、基础体温升 <span class="mono">0.3-0.5°C</span>。<strong>热应激敏感度上升</strong>，夏天高强度课要主动补水降温，否则 HRmax 会比正常高 5+ bpm。</p>
      </div>
      <div class="card">
        <h4>黄体期 Day 14-28</h4>
        <p class="desc">黄体酮 + 雌激素双高。<strong>静息心率 +5-10 bpm</strong>、感觉吃力但实际等效负荷不变。RPE 会骗你 —— 按心率/配速训练比按感觉训练更准。蛋白需求上升 ~12%。</p>
      </div>
      <div class="card">
        <h4>经前期 + 经期</h4>
        <p class="desc">黄体酮骤降、可能水钠潴留。经期前 2-3 天许多人感觉最差；月经开始后<strong>反而常常缓解</strong>。月经期间铁损失需要饮食或补剂补足。</p>
      </div>
    </div>
    <p><strong>关键原则</strong>：上面这些阶段差异在<strong>群体平均</strong>上成立，但<strong>个体差异极大</strong> —— 有些女性整周期表现波动 &lt;3%，有些 &gt;15%。<strong>唯一靠谱的做法是自己追踪 3-6 个月</strong>：用日历或 App 记每天的静息心率、睡眠质量、训练 RPE、配速。3 个周期后规律自然浮现，再据此调整训练安排（比如把高强度课往卵泡期前移）。<strong>不要直接照抄别人的协议、更不要套 FemTech App 默认推荐</strong>。</p>
    <div class="callout sharp">
      <div class="label">SHARP TAKE</div>
      <p><strong>反主流提醒</strong>：FemTech App 流行的「经期不训练 / 黄体期只做轻松跑」是过度简化，且<strong>正好搞反了</strong> —— 多项研究（含 Bruinvels 2021）显示<strong>规律运动反而显著降低经期不适和经前综合症</strong>。运动科学界仍在追赶男性数据约 30 年，所有现存的「周期化训练协议」都属于<strong>初代假说</strong>而非定论。把这些当默认起点、用自己 3-6 个月数据验证，而不是当圣经。<span class="ref">(Sims &amp; Yeager 2019; Sims 2022; Elliott-Sale et al. 2021; Bruinvels et al. 2021)</span></p>
    </div>"""

html = replace_by_regex(
    html,
    r'<h3><span class="pre">10\.8</span>顶级前沿 #6 · 女性月经周期训练</h3>.*?月经期前 3-5 天可能出现.{1,3}假过训.{1,3} → 别误判</li>\s*</ul>',
    NEW_MENS,
    "§10.8 menstrual",
)
print("✓ 09 menstrual")

# ============================================================================
# 10. §9 — append 8 new subsections before closing </section>
# ============================================================================
S9_NEW_CONTENT = """    <h3><span class="pre">9.8</span><span class="pre">A/B/C TIERS</span> 三档目标体系</h3>
    <p>顶级业余圈的潜规则：从不设单一目标。单目标的致命缺陷在于它把整场比赛变成一个二元判决 —— 要么 PR 要么崩盘。一旦起跑发现顶风、体感重、心率漂得早，你的大脑会在 25K 处做出灾难性决策：「反正破不了三了，那我躺平」。三档目标把 42.195km 拆成了<strong>可滑动的决策框架</strong>，而不是一次性赌博。</p>
    <p>设定逻辑（以 PR 3:20、目标破三为例）：</p>
    <ul>
      <li><strong>A 目标</strong>（90% 把握）：3:00 整 = <span class="mono">4:15/km</span>，对应近 6 周训练数据可支撑的最优表现</li>
      <li><strong>B 目标</strong>（95% 把握）：3:05 = <span class="mono">4:23/km</span>，状态一般也能拿下的 PR</li>
      <li><strong>C 目标</strong>（98% 把握）：3:10 = <span class="mono">4:30/km</span>，崩盘后的兜底，仍是 PR</li>
    </ul>
    <div class="callout ops">
      <div class="label">OPS</div>
      <p>降档触发信号（任一出现立即切下一档）：① 10K 时平均心率比阈值高 5bpm 以上；② 25K 体感从 RPE 6 跳到 RPE 8；③ 连续两个 1K 分段步频下降 4+ spm；④ 出汗停止 + 皮肤起鸡皮（热射病前兆，直接 C 档或退赛）。</p>
    </div>
    <div class="callout sharp">
      <div class="label">SHARP TAKE</div>
      <p>「我就是冲 A 不留余地」的跑者大概率跑出比 C 还差的成绩 <span class="ref">(Stevinson &amp; Biddle 1998)</span>。比赛是认知任务，不是意志力测试 —— 预设撤退路径的人最终跑得更快，因为他们 30K 后还有脑子做决策。</p>
    </div>

    <h3><span class="pre">9.9</span><span class="pre">GI / BATHROOM</span> 早晨肠胃与厕所策略</h3>
    <p>业余跑者退赛/掉链子三大隐形杀手：撞墙、抽筋、厕所。前两个有人讨论，第三个被严重低估 —— 上马起跑前的 portaloo 队伍能排 20-30 分钟，起跑后 10K 内便意上来就是地狱。</p>
    <p><strong>起跑前 3 小时早餐</strong>（约 4:00 AM，目标 1-1.5 g/kg 碳水，低脂低纤维低蛋白）：</p>
    <ul>
      <li>方案 A：白吐司 2 片 + 蜂蜜 2 勺 + 香蕉 1 根 ≈ <span class="mono">85g 碳水</span></li>
      <li>方案 B：即食燕麦 50g + 蜂蜜 + 1 根香蕉 + 少量盐 ≈ <span class="mono">75g 碳水</span></li>
      <li>液体：300-500ml 含糖运动饮料，不要纯水（冲淡电解质）</li>
    </ul>
    <p><strong>咖啡因 timing</strong>：起床即喝（4:00）1 杯黑咖啡 ≈ 100mg，起跑前 30-45 分钟（6:30 左右）补 1 粒 100-200mg 咖啡因片。总剂量 3-6 mg/kg 体重区间最优 <span class="ref">(Burke 2008)</span>。</p>
    <p><strong>排便流程定型</strong>：赛前 8-12 周的所有长距训练日，严格复制赛日早晨节奏（同样时间起、同样早餐、同样咖啡）。让肠道形成条件反射，出门前必排空。</p>
    <div class="callout sharp">
      <div class="label">SHARP TAKE</div>
      <p>Imodium（洛哌丁胺）在跑者论坛被神化，实际上是双刃剑 —— 它掩盖了你需要解决的真问题（乳糖不耐/纤维过多/紧张性肠综合症），且会增加运动中肠缺血风险。健康跑者不要碰，IBS 患者请医生开方。</p>
    </div>
    <div class="callout ops">
      <div class="label">OPS</div>
      <p>起跑前最后一次厕所：起跑前 15-20 分钟，不是 5 分钟（队太长来不及）。如果到点还没便意，就放弃这次，起跑后 5K 处通常有移动厕所。带 2 张折叠纸巾塞口袋 —— portaloo 经常没纸。</p>
    </div>

    <h3><span class="pre">9.10</span><span class="pre">WEATHER</span> 天气四案应对</h3>
    <p>上海马拉松 10 月底比赛日历史温度区间 <span class="mono">8-22°C</span>，主导风 NE 4-8 m/s。2017 年下过雨 + 大风，2019 年闷热 22°C，2023 年理想 14°C。不要赌天气，准备四套方案。</p>
    <table>
      <thead><tr><th>场景</th><th>装备调整</th><th>配速调整</th><th>补给策略</th></tr></thead>
      <tbody>
        <tr><td>雨（任何温度）</td><td>薄帽舌（防雨水入眼）、贴胸贴防止 T 恤渗透磨乳头、绑鞋带打死结</td><td>前 10K 慢 3-5 秒/km（防滑 + 控温）</td><td>正常，但凝胶包装要先撕开放到口袋外</td></tr>
        <tr><td>风 &gt;6m/s</td><td>薄风衣可起跑后扔/收腰、戴薄手套防失温</td><td>顶风段不追配速，看心率不超阈值即可</td><td>顺风段不要冲，留体力给顶风段</td></tr>
        <tr><td>寒（&lt;10°C）</td><td>臂套（可中途撸下）、薄手套、起跑前垃圾袋保暖</td><td>前 5K 慢 5 秒/km 让身体进入工作状态</td><td><strong>易忘喝水</strong>：每个补给点必须含一口，凉天脱水更隐蔽</td></tr>
        <tr><td>暑（&gt;22°C）</td><td>白色帽 + 轻薄网眼背心、海绵随身</td><td>每升 5°C 慢 5-8 秒/km <span class="ref">(Ely 2007)</span></td><td>每站必停，水浇头 + 颈、电解质增加 30%</td></tr>
      </tbody>
    </table>
    <div class="callout note">
      <div class="label">NOTE</div>
      <p>上马高架段（前 20K）风速比地面预报高 1.5-2 倍，且无遮挡。NE 主导风意味着内环高架向东段顶风，提前心理建设。</p>
    </div>

    <h3><span class="pre">9.11</span><span class="pre">NSAID WARNING</span> 赛中止痛药 —— 别碰</h3>
    <div class="callout sharp">
      <div class="label">SHARP TAKE</div>
      <p>跑者圈最危险的「经验之谈」之一：「起跑前吞两粒布洛芬压住膝盖痛」。这能让你住院。Western States 100 的研究显示，赛中服用 NSAID 的选手急性肾损伤（AKI）风险显著升高，血清肌酐异常率比对照组高一倍以上 <span class="ref">(Lipman 2017)</span>。</p>
    </div>
    <p>机制层面：马拉松本身会让肾血流减少 30-50%（血液优先供应肌肉和皮肤散热），布洛芬/萘普生通过抑制 COX-1/2 进一步收缩肾小球入球小动脉。脱水状态下两者叠加 = 急性肾小管坏死。同时 NSAID 抑制肾脏自由水排泄，与过量饮水叠加会显著放大<strong>运动相关低钠血症 (EAH)</strong> 风险 <span class="ref">(Hew-Butler 2015)</span> —— 这是马拉松唯一可能直接致死的并发症。</p>
    <p>对乙酰氨基酚（扑热息痛）对肾相对安全但对肝有剂量依赖性损伤，且镇痛效果对运动性肌肉痛微乎其微。</p>
    <div class="callout ops">
      <div class="label">OPS</div>
      <p>正确做法：① 训练期能不吃就不吃，把疼痛当成信号而非敌人；② 赛中绝对不吃任何止痛药；③ 真有持续疼痛（尤其单侧、定点、刺痛）立刻退赛找医生 —— 那是伤病预警，不是要你镇压的噪音；④ 赛后 24 小时内也尽量不吃 NSAID，等水合恢复、尿色清亮后再考虑。</p>
    </div>

    <h3><span class="pre">9.12</span><span class="pre">WALL PROTOCOL</span> 撞墙重启六步法</h3>
    <p>撞墙不是意志力问题 —— 是肝糖原耗尽（约 30-35K）叠加中枢疲劳的生理事件。多数业余跑者撞墙后做的所有事都是错的：加速试图「挺过去」、否认信号、灌咖啡因、吃止痛药。正确反应是一个冷静的剧本。</p>
    <ol>
      <li><strong>识别（放下否认）</strong>：步频突然下降 5+ spm；心率应该飙升却反而走平/下降；视野边缘模糊；突然涌起强烈负面情绪（「我为什么要跑步」）。这些信号同时出现就是撞墙，不是「状态差」。</li>
      <li><strong>5 秒内降速</strong>：立刻慢 20-30 秒/km。呼吸从 3 步 1 呼切到 4 步 1 呼，强制副交感神经介入。</li>
      <li><strong>5 分钟内补糖</strong>：30-60g 快速碳水 —— 1-2 包凝胶 + 一杯运动饮料 + 1 粒盐丸（500mg 钠）。糖入血再到肌肉需要 8-15 分钟，所以越早越好。</li>
      <li><strong>切换目标</strong>：A/B 档已失效，切到 C 档或「完赛不走」。明确放弃 PR 反而能解锁心理资源。</li>
      <li><strong>1K 分割法</strong>：剩下的距离拆成 1km 一段，每完成 1km 给自己一次正反馈（「过了一个」）。大脑无法处理「还有 12 公里」，但能处理「再一公里」。</li>
      <li><strong>不要做的事</strong>：① 不要再加咖啡因（此时已过半衰期高峰，只会心悸）；② 不要止痛药（见 9.11）；③ 不要冲刺补救（进一步耗尽糖原导致彻底崩盘）；④ 不要走走停停（走比慢跑更难重启，肌肉一冷会抽筋）。</li>
    </ol>
    <div class="callout note">
      <div class="label">NOTE</div>
      <p>真正的预防是 90 分钟内 60-90g/h 碳水摄入 <span class="ref">(Jeukendrup 2014)</span>，而不是撞墙后的抢救。但即使预防到位，30K 后仍有 15-20% 概率撞墙 —— 所以剧本必须背熟。</p>
    </div>

    <h3><span class="pre">9.13</span><span class="pre">RACE TRAVEL</span> 异地赛事旅行协议</h3>
    <p>队里有人飞外地参赛，旅行本身就能毁掉 12 周训练。规则不复杂，但每条都有人踩坑。</p>
    <ul>
      <li><strong>时差换算</strong>：每跨 1 时区需要约 1 天调整，向东比向西难 40-50% <span class="ref">(Waterhouse 2007)</span>。北京飞东京（+1h）调一天，飞欧洲（-6h）至少提前 5-7 天到。</li>
      <li><strong>饮食锁定</strong>：抵达后第一餐就按当地赛日时间吃。<strong>赛前 72 小时不试任何新食物</strong> —— 异地的「特色早餐」是 GI 灾难的最常见来源。</li>
      <li><strong>起床节奏</strong>：赛前 3 天就把起床时间调到比赛日起床时间（通常 4:00-4:30 AM）。比赛日不要是你第一次这么早起。</li>
      <li><strong>核心装备随身</strong>：比赛鞋、比赛服、号码布、凝胶、电解质 —— 全部进登机随身包。托运箱可以丢，这几样不能。</li>
      <li><strong>睡眠</strong>：自带枕套（嗅觉熟悉度对入睡时间影响显著）、自带耳塞眼罩。赛前两晚比赛前一晚更重要 —— 前一晚兴奋失眠不影响表现，前两晚失眠才影响 <span class="ref">(Fullagar 2015)</span>。</li>
      <li><strong>高原</strong>：海拔 &gt;1500m 的赛地有「中间窗口最差」陷阱 —— 抵达 2-5 天是急性高原反应高峰。要么提前 7-14 天适应，要么赛前 &lt;24 小时到（没时间产生反应）。中间 3-5 天到是最糟糕的选择。</li>
    </ul>
    <div class="callout ops">
      <div class="label">OPS</div>
      <p>航班选择优先级：① 不能转机（行李丢失风险）；② 抵达时间 ≤ 比赛日前 48 小时；③ 飞行中每小时起来活动 5 分钟 + 喝 200ml 水防深静脉血栓。落地后第一件事不是睡觉 —— 是出去走 30 分钟接触阳光重置生物钟。</p>
    </div>

    <h3><span class="pre">9.14</span><span class="pre">COURSE RECON</span> 赛道预习方法论</h3>
    <p>90% 的业余跑者对赛道的「研究」就是开赛道图看 5 秒然后关掉。这等于没看。真正的 recon 是让你的大脑在比赛时拥有「地图」 —— 知道下一段是上坡/顶风/补给点，决策质量会高 30%。</p>
    <ol>
      <li><strong>坡度图 (elevation profile)</strong>：从官方网站或 Strava 段获取。用红笔标记所有坡度 &gt;2% 的段（无论上下），记录起止公里数。上马整体平坦，但杨浦大桥（约 15-16K）和南浦大桥引桥是真坡。</li>
      <li><strong>5 个关键 anchor 点</strong>：5K（初始配速校验）/ 半程（分段目标 + 是否切档）/ 25K（撞墙前哨）/ 32K（撞墙带核心）/ 39K（最后冲刺触发点）。每个点提前想好「到这里我应该是什么状态/做什么」。</li>
      <li><strong>风向叠加</strong>：看赛前 48 小时天气预报，把风向画在赛道图上。上马 10/25 主导风 NE，意味着前 20K 高架东向段顶风，后半段沿黄浦江南下顺风（理论上）。</li>
      <li><strong>补给与厕所点</strong>：背下来位置 + 间距。上马补给约每 2.5-5km 一个，知道「下一个站还有多远」能控制是否多停。</li>
      <li><strong>上马具体地标记忆</strong>：外滩起 → 南京路 → 内环高架 → 龙阳路 → 杨浦大桥 → 北外滩 → 复兴公园终点。前 20K 高架居多 —— 影响 GPS 信号（配速跳动）、视野单调（心理疲劳）、且无遮阴。</li>
    </ol>
    <div class="callout sharp">
      <div class="label">SHARP TAKE</div>
      <p>赛道熟悉度的价值不在于「知道怎么跑」，而在于消除不确定性 —— 大脑在已知环境中的运动调控比未知环境节能 5-10% <span class="ref">(Marcora 2009)</span>。这就是为什么主场选手的成绩往往超出训练数据预期。</p>
    </div>

    <h3><span class="pre">9.15</span><span class="pre">SKIN &amp; FOOT</span> 皮肤摩擦与脚部防护</h3>
    <p>退赛原因 top 5 里有三个是皮肤/脚问题（起泡、流血摩擦、趾甲脱落）。这些都 100% 可预防，但需要在赛前两周就开始执行，赛日早晨补救来不及。</p>
    <p><strong>凡士林部署点</strong>（全身约用量 30-40g，赛前 30 分钟厚涂）：</p>
    <ul>
      <li>脚趾间（每个缝隙）、脚弓、足跟后缘</li>
      <li>内大腿根、腹股沟、坐骨结节（短裤接缝区）</li>
      <li>腋下两侧</li>
      <li>男士：乳头 + 周围 2cm（或用 Compeed/医用胶带十字贴）</li>
      <li>女士：bra 下缘环线、肩带与皮肤接触点</li>
    </ul>
    <p><strong>袜子</strong>：长距离（&gt;30K）首选五趾袜 —— 趾间摩擦是长距起泡最常见位置。材质选 CoolMax/美利奴混纺，绝对不要纯棉。袜厚度必须和你已穿过 200+ km 的训练袜一致。</p>
    <p><strong>趾甲</strong>：赛前 5-7 天剪平（不是剪短），剪到指甲边缘不超过趾尖肉、刚好不戳鞋头即可。剪太短反而磨 —— 指甲的存在是保护趾尖软组织的。下坡跑黑趾甲多半是鞋码偏小 + 趾甲过长共同作用。</p>
    <p><strong>比赛鞋</strong>：必须在比赛前完成至少 <strong>1 次 30km+ 长距测试</strong> + 1 次马配训练。竞速鞋（碳板）寿命短，跑过 200-300km 后回弹衰减明显。比赛鞋赛前里程控制在 80-150km 区间最佳 —— 既磨合好，又没疲劳。</p>
    <div class="callout sharp">
      <div class="label">SHARP TAKE</div>
      <p>「赛日穿新鞋有仪式感」是社交媒体毒鸡汤。任何赛日首次使用的装备（鞋、袜、短裤、bra、GPS 表带）都可能在 35K 处变成你的敌人。仪式感留给抵达终点拍照那一刻。</p>
    </div>
    <div class="callout ops">
      <div class="label">OPS</div>
      <p>赛日早晨摩擦急救包（放赛前存包内）：备用 Compeed 水泡贴 2 片、医用胶带 1 小卷、小包凡士林。出发前最后 10 分钟做一次全身摩擦点检查 —— 发现任何已有的擦伤/红点，当场贴 Compeed，不要赌它「应该没事」。</p>
    </div>

  </div>
</section>"""

# Find §9 closing — match the unique "最后 2 km 把储备用完" line then </section>
m = re.search(r'(<li>.{1,3}最后 2 km 把储备用完。.{1,3}</li>\s*</ul></p>\s*</div>\s*)</div>\s*</section>', html, re.S)
if not m:
    raise SystemExit("✗ §9 closing pattern not found")
old = m.group(0)
new = m.group(1) + S9_NEW_CONTENT
html = html.replace(old, new, 1)
print("✓ 10 §9 expansions (8 new subsections)")

# ============================================================================
# 11. Appendix VDOT chart
# ============================================================================
# Renumber A.2 → A.3, A.3 → A.4, A.4 → A.5
for old_n, new_n in [('A.2', 'A.3'), ('A.3', 'A.4'), ('A.4', 'A.5')]:
    pat = f'<h3><span class="pre">{old_n}</span>'
    new = f'<h3><span class="pre">{new_n}</span>'
    # Do replacements in reverse order to avoid cascading mistakes
# Actually we need to do in REVERSE order: A.4 first, then A.3, then A.2
for old_n, new_n in [('A.4', 'A.5'), ('A.3', 'A.4'), ('A.2', 'A.3')]:
    pat = f'<h3><span class="pre">{old_n}</span>'
    rep = f'<h3><span class="pre">{new_n}</span>'
    if pat in html:
        html = html.replace(pat, rep, 1)
print("✓ 11a Renumbered A.2-A.4 → A.3-A.5")

# Insert VDOT chart as new A.2
VDOT_CHART = """    <h3><span class="pre">A.2</span>VDOT × Race Time × Training Pace 大表</h3>
    <p>Daniels' Running Formula (3rd ed.) VDOT 表的浓缩版，覆盖业余跑者从入门到精英边缘的常见区间。配速单位 <span class="mono">min:sec/km</span>。</p>
    <p><strong>怎么用</strong>：(1) <em>反查</em> —— 拿近 4 周内最近一次的 5K、10K 或半马完赛时间，找到对应行，那就是当前 VDOT；(2) <em>定训练配速</em> —— 同一行右侧五档 E/M/T/I/R 就是你近期所有训练课的目标配速；(3) <em>设目标</em> —— 目标比赛时间往上反推 VDOT，差值即为周期内需提升的点数（业余 16-24 周合理目标 +2-4 点，+6 点已属激进）。</p>
    <table>
      <thead>
        <tr>
          <th>VDOT</th><th>全马</th><th>半马</th><th>10K</th><th>5K</th><th>1500m</th>
          <th>E</th><th>M</th><th>T</th><th>I</th><th>R/400m</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>45</td><td><span class="mono">3:34:59</span></td><td><span class="mono">1:42:17</span></td><td><span class="mono">41:21</span></td><td><span class="mono">19:57</span></td><td><span class="mono">5:30</span></td><td><span class="mono">5:38-6:11</span></td><td><span class="mono">4:57</span></td><td><span class="mono">4:38</span></td><td><span class="mono">4:16</span></td><td><span class="mono">1:38</span></td></tr>
        <tr><td>47</td><td><span class="mono">3:26:00</span></td><td><span class="mono">1:38:27</span></td><td><span class="mono">39:46</span></td><td><span class="mono">19:11</span></td><td><span class="mono">5:17</span></td><td><span class="mono">5:25-5:57</span></td><td><span class="mono">4:46</span></td><td><span class="mono">4:28</span></td><td><span class="mono">4:07</span></td><td><span class="mono">1:34</span></td></tr>
        <tr><td><strong>48</strong></td><td><span class="mono">3:21:29</span></td><td><span class="mono">1:36:09</span></td><td><span class="mono">39:00</span></td><td><span class="mono">18:48</span></td><td><span class="mono">5:10</span></td><td><span class="mono">5:19-5:50</span></td><td><span class="mono">4:41</span></td><td><span class="mono">4:23</span></td><td><span class="mono">4:03</span></td><td><span class="mono">1:32</span></td></tr>
        <tr><td>50</td><td><span class="mono">3:14:06</span></td><td><span class="mono">1:32:34</span></td><td><span class="mono">37:31</span></td><td><span class="mono">18:05</span></td><td><span class="mono">4:58</span></td><td><span class="mono">5:08-5:38</span></td><td><span class="mono">4:31</span></td><td><span class="mono">4:15</span></td><td><span class="mono">3:55</span></td><td><span class="mono">1:30</span></td></tr>
        <tr><td>52</td><td><span class="mono">3:05:58</span></td><td><span class="mono">1:29:15</span></td><td><span class="mono">36:09</span></td><td><span class="mono">17:24</span></td><td><span class="mono">4:47</span></td><td><span class="mono">4:58-5:27</span></td><td><span class="mono">4:22</span></td><td><span class="mono">4:06</span></td><td><span class="mono">3:47</span></td><td><span class="mono">1:26</span></td></tr>
        <tr><td><strong>54</strong></td><td><span class="mono">2:58:21</span></td><td><span class="mono">1:26:15</span></td><td><span class="mono">34:54</span></td><td><span class="mono">16:48</span></td><td><span class="mono">4:37</span></td><td><span class="mono">4:49-5:17</span></td><td><span class="mono">4:14</span></td><td><span class="mono">3:58</span></td><td><span class="mono">3:40</span></td><td><span class="mono">1:23</span></td></tr>
        <tr><td>55</td><td><span class="mono">2:54:44</span></td><td><span class="mono">1:24:47</span></td><td><span class="mono">34:19</span></td><td><span class="mono">16:30</span></td><td><span class="mono">4:32</span></td><td><span class="mono">4:44-5:12</span></td><td><span class="mono">4:10</span></td><td><span class="mono">3:54</span></td><td><span class="mono">3:37</span></td><td><span class="mono">1:22</span></td></tr>
        <tr><td>56</td><td><span class="mono">2:51:24</span></td><td><span class="mono">1:23:24</span></td><td><span class="mono">33:46</span></td><td><span class="mono">16:14</span></td><td><span class="mono">4:28</span></td><td><span class="mono">4:40-5:07</span></td><td><span class="mono">4:06</span></td><td><span class="mono">3:51</span></td><td><span class="mono">3:34</span></td><td><span class="mono">1:21</span></td></tr>
        <tr><td>58</td><td><span class="mono">2:45:13</span></td><td><span class="mono">1:20:48</span></td><td><span class="mono">32:43</span></td><td><span class="mono">15:42</span></td><td><span class="mono">4:19</span></td><td><span class="mono">4:32-4:58</span></td><td><span class="mono">3:59</span></td><td><span class="mono">3:45</span></td><td><span class="mono">3:28</span></td><td><span class="mono">1:19</span></td></tr>
        <tr><td>60</td><td><span class="mono">2:39:35</span></td><td><span class="mono">1:18:09</span></td><td><span class="mono">31:43</span></td><td><span class="mono">15:13</span></td><td><span class="mono">4:11</span></td><td><span class="mono">4:24-4:50</span></td><td><span class="mono">3:52</span></td><td><span class="mono">3:39</span></td><td><span class="mono">3:23</span></td><td><span class="mono">1:17</span></td></tr>
      </tbody>
    </table>
    <div class="callout note">
      <div class="label">区间说明</div>
      <p><strong>E</strong> = Easy（60-79% HRmax）；<strong>M</strong> = Marathon Pace；<strong>T</strong> = Threshold（乳酸阈，「舒服地难」，20-60 min）；<strong>I</strong> = Interval（VO2max，单组 3-5 min）；<strong>R</strong> = Repetition（无氧/经济性，单组 200-600m）。加粗行：48 = 全马 3:20，54 = 破三。<span class="ref">(Daniels 2014)</span></p>
    </div>

    """

# Insert before A.3 术语表 (which used to be A.2)
ANCHOR = '<h3><span class="pre">A.3</span>术语表</h3>'
assert ANCHOR in html, "appendix A.3 anchor not found"
html = html.replace(ANCHOR, VDOT_CHART + ANCHOR, 1)
print("✓ 11 Appendix VDOT chart inserted as A.2")

# ============================================================================
# 12. Progress bar JS — insert before </body>
# ============================================================================
PROGRESS_JS = """
<script>
(function() {
  const bar = document.getElementById('progressBar');
  if (!bar) return;
  let ticking = false;
  function update() {
    const st = window.pageYOffset || document.documentElement.scrollTop;
    const sh = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const pct = sh > 0 ? (st / sh) * 100 : 0;
    bar.style.width = pct + '%';
    ticking = false;
  }
  window.addEventListener('scroll', function() {
    if (!ticking) {
      window.requestAnimationFrame(update);
      ticking = true;
    }
  }, { passive: true });
  update();
})();
</script>

"""
assert "</body>" in html
html = html.replace("</body>", PROGRESS_JS + "</body>", 1)
print("✓ 12 Progress bar JS")

# ============================================================================
# 13. Citation refs at sharp claims (8 high-impact)
# ============================================================================
def find_and_add_ref(html, keywords, citation):
    """Find first <p> or <li> containing all keywords, append citation before tag close."""
    import re as _re
    for tag in ('p', 'li', 'h4'):
        pat = _re.compile(rf'<{tag}>([^<]*?(?:<[^>]+>[^<]*?)*?)</{tag}>', _re.S)
        for m in pat.finditer(html):
            txt = m.group(1)
            if all(k in txt for k in keywords) and citation not in txt:
                old = m.group(0)
                new = f'<{tag}>{txt} <span class="ref">{citation}</span></{tag}>'
                return html.replace(old, new, 1)
    return None

CITATIONS = [
    (['乳酸是燃料', '废物'], '(Brooks 2018)'),
    (['80/20', '极化'], '(Seiler 2010)'),
    (['静态拉伸', '副作用'], '(Behm 2011)'),
    (['咖啡因', '3-6 mg/kg'], '(Burke 2008)'),
    (['冷水浴', '力量'], '(Roberts 2015; Fyfe 2019)'),
    (['自我对话', '18%'], '(Blanchfield 2014)'),
    (['ACWR', '0.8-1.3'], '(Gabbett 2016)'),
    (['Hoogkamer', '4%'], '(Hoogkamer 2018)'),
]
applied = 0
for kws, cit in CITATIONS:
    result = find_and_add_ref(html, kws, cit)
    if result is not None:
        html = result
        applied += 1
print(f"✓ 13 Citations applied: {applied}/{len(CITATIONS)}")

# ============================================================================
# 14. Bump version
# ============================================================================
html = html.replace("SPORTS SCIENCE FIELD MANUAL · v1 · 2026.05",
                    "SPORTS SCIENCE FIELD MANUAL · v2 · 2026.05", 1)
html = html.replace("SPORTS SCIENCE FIELD MANUAL · 2026.05.21 · v1",
                    "SPORTS SCIENCE FIELD MANUAL · 2026.05.21 · v2", 1)
print("✓ 14 version bumped")

# ============================================================================
SRC.write_text(html, encoding="utf-8")
print()
print(f"✓ v2 integration complete")
print(f"  file size: {len(html):,} chars  ({len(html)/1024:.1f} KB)")
print(f"  line count: {html.count(chr(10)) + 1}")
