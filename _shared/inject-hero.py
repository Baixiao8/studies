#!/usr/bin/env python3
"""
INJECT HERO · 批量给 12 章插入 AI hero 图 + HTML 数据卡

为每章在 section-tag 之前插入:
1. <figure class="chapter-hero"> · AI 生成的章节封面
2. <div class="hero-keypoints"> · 4 个关键数据卡

已经有 hero 的章节(Ch1)会被跳过(检测 <figure class="chapter-hero">)。

用法:
  python3 _shared/inject-hero.py
"""

import re
from pathlib import Path

# ─── 每章的数据卡片(4 个 keypoint) ────────────────────
KEYPOINTS = {
    'ch01': {
        'caption': '跑步推离瞬间 · 关键关节的实时状态',
        'kp': [
            ('▸ 髋',     '伸展 <em>−10°</em>',  '推离时髋伸到峰值 · 臀大肌主推进 · 推进力 35% 来自这里'),
            ('▸ 踝',     '跖屈 <em>−20°</em>',  '跟腱弹性回弹 · 角速度 600°/s · 弹簧能量在 100 ms 内储释'),
            ('▸ 前膝',   '屈曲 <em>~90°</em>',  '摆动期前膝高抬 · 缩短腿转动惯量 · 跑得越快收得越高'),
            ('▸ 肩 · 肘', '摆臂 <em>~90°</em>',  '反平衡躯干旋转 · 守恒角动量 · 节省约 3% 跑步能量'),
        ],
    },
    'ch02': {
        'caption': '着地瞬间的力学指纹 · GRF 三分量',
        'kp': [
            ('▸ 冲击峰',  '<em>1.7 BW</em>',     '50 ms 内达峰 · 后跟着地者明显 · 跑步伤病的力学起点'),
            ('▸ 主峰',    '<em>2.7 BW</em>',     '负重相 + 推离相承担 · 膝/踝峰值负荷 · 跑步经济性核心'),
            ('▸ 跟腱储能', '<em>35 J/步</em>',    '跟腱弹簧储释 · 推进力 35%+ 来自这一弹性 · 非肌肉代谢'),
            ('▸ VALR',    '<em>60–100 BW/s</em>', '负载率 · 高 VALR = 应力骨折与胫骨夹痛风险高'),
        ],
    },
    'ch03': {
        'caption': '后侧链 · 跑步的推进引擎',
        'kp': [
            ('▸ 臀大肌',     '<em>主发动机</em>',     '髋伸主力 · 人类独有发达 · 走路时几乎不工作'),
            ('▸ 腘绳肌',     '<em>双关节</em>',       '摆动减速 · 冲刺拉伤多在末摆动期 · Nordic curl 预防 80%'),
            ('▸ 比目鱼肌',    '<em>慢肌 80%+</em>',  '被低估的耐力心脏 · 跖屈纯力 · 精英 CSA 显著大'),
            ('▸ 足底固有肌', '<em>沉睡英雄</em>',     '弹簧链终端 · 现代缓震鞋弱化它 · 单腿平衡训练激活'),
        ],
    },
    'ch04': {
        'caption': '三大供能系统 · 不是开关而是耦合',
        'kp': [
            ('▸ 磷酸原',  '<em>0–10s</em>',       '9 mmol/kg/s 最高功率 · 冲刺/起跑/最后冲线'),
            ('▸ 糖酵解',  '<em>10s–2min</em>',    '4.5 mmol/kg/s · 400-1500m 主力 · 乳酸是燃料不是废物'),
            ('▸ 有氧氧化', '<em>2min+</em>',      '1.2 mmol/kg/s · 马拉松 98% 靠它 · 容量近乎无限'),
            ('▸ 乳酸阈',  '<em>LT2 ≈ 4 mmol/L</em>', '1 小时全力上限 · 比 VO2max 更预测耐力表现'),
        ],
    },
    'ch05': {
        'caption': '氧的输送链 · 中央 vs 外周',
        'kp': [
            ('▸ VO2max',  '<em>70–85</em> ml/kg/min', '精英长跑天花板 · Bjørn Dæhlie 96 史上最高 · 遗传度 50%'),
            ('▸ RHR',     '<em>40–55</em> bpm',     '训练有素静息心率 · 心血管效率最便宜的内部仪表'),
            ('▸ 每搏量',   '<em>200+</em> mL',       '精英 SV · 离心性肥大 · HIIT 主要刺激'),
            ('▸ Fick',    'Q × (a-vO2 diff)',       '中央(心) 75% + 外周(线粒体) 25%'),
        ],
    },
    'ch06': {
        'caption': '组织级别的适应 · 三个时间常数',
        'kp': [
            ('▸ 肌肉',   '<em>4–6 周</em>',     '神经驱动先,纤维肥大后 · 训练响应最快的组织'),
            ('▸ 肌腱',   '<em>6–12 月</em>',    '慢变量 · 跟腱/髌腱伤病的根源 · 与肌肉的时间错配'),
            ('▸ 骨重塑', '<em>季度级</em>',     'Wolff 定律 · 微损伤+修复循环 · 应力骨折阈值'),
            ('▸ I 型纤维','<em>精英 80%+</em>', '慢肌耐疲劳 · 精英长跑特征 · 转化有限'),
        ],
    },
    'ch07': {
        'caption': '从意图到动作 · 神经经济学',
        'kp': [
            ('▸ 中枢调节器', '<em>ACC 主动下调</em>',  '防真正力竭 · 先于肌肉投降 · Tim Noakes 模型'),
            ('▸ CPG',       '<em>脊髓节律</em>',     '跑步的"自动驾驶" · 边跑边想问题的神经基础'),
            ('▸ BDNF',      '<em>海马体 +2%</em>',   '跑步上调 · 神经新生 · 等效抗抑郁药效果'),
            ('▸ 跑者高潮',   '<em>内源大麻素</em>',   '不是内啡肽 · anandamide + CB1 受体 · Fuss 2015'),
        ],
    },
    'ch08': {
        'caption': '激素 · 免疫 · 热的三重风暴',
        'kp': [
            ('▸ 皮质醇',   '<em>急性升 / 慢性平</em>', '急性应激 · 过训慢性升 = 红旗 · 与睾酮比值是指标'),
            ('▸ URTI J 曲线','<em>中等 −50% / 极量 +6×</em>','>96 km/周风险陡升 · 开窗期 3-72 小时'),
            ('▸ REDs',     '<em>EA &lt; 30 kcal/kg</em>', '月经紊乱+骨密度↓ = 红旗 · 男女通用'),
            ('▸ 热适应',   '<em>14 天</em>',          '汗量↑ 钠浓度↓ 心率↓ · 5 天起部分适应'),
        ],
    },
    'ch09': {
        'caption': '能量经济学 · 燃料决定能跑多远',
        'kp': [
            ('▸ 双糖补给',  '<em>60–120 g/h</em>',  '葡萄糖+果糖 2:1 · GLUT5+SGLT1 双转运 · 训练肠道'),
            ('▸ 撞墙',     '<em>30 km · 临界</em>', '肌糖原 &lt; 80 mmol/kg 湿重 · 大脑保护性下调输出'),
            ('▸ 铁蛋白',   '<em>&gt; 30 ng/mL</em>', '女跑者高发缺铁 · hepcidin 抑制吸收 · 训练日错开'),
            ('▸ 维 D',     '<em>&gt; 30 ng/mL</em>', '免疫+骨+肌肉的底座 · 高纬度冬季 1000-2000 IU/d'),
        ],
    },
    'ch10': {
        'caption': '训练剂量学 · 刺激 + 恢复',
        'kp': [
            ('▸ 80/20 极化',  '<em>Z1 80% / Z3 15%</em>', 'Seiler 发现 · 精英分布 · 避开 Z3 灰区'),
            ('▸ ACWR',       '<em>0.8–1.3 sweet</em>',   '急慢性负荷比 · &gt;1.5 风险陡升'),
            ('▸ 力量训练',    '<em>RE +4–8%</em>',       '不增肌量 · 提神经驱动+肌腱刚度 · 5K +2-4%'),
            ('▸ 减量 taper',  '<em>3 周 −40-60%</em>',   '维持强度 · 表现 +1-3% · 过度减量 = 脱训'),
        ],
    },
    'ch11': {
        'caption': '伤病力学 · 累积过载的语言',
        'kp': [
            ('▸ 年发生率',  '<em>~50%</em>',     '80% 累积过载 · 20% 急性 · 既往史是最强风险因子'),
            ('▸ ACWR >1.5','<em>风险 ×2–5</em>', '跑量改变速度 > 跑量本身 · 这才是伤病预测核心'),
            ('▸ 跑者膝 PFPS','<em>占 20%</em>',   '髋外展弱+足旋前+VMO 弱 · 步频 +5-10% 见效'),
            ('▸ 跟腱康复',  '<em>Alfredson 12 周</em>', '离心训练 · 允许疼痛 ≤4/10 · 80% 显著改善'),
        ],
    },
    'ch12': {
        'caption': '极限 · 天赋 + 训练 + 装备 的乘积',
        'kp': [
            ('▸ VO2max 衰退', '<em>训练 −5%/dec</em>',  '未训练 −10% · 训练保留响应度 · 65 岁 ≈ 40 岁久坐'),
            ('▸ 男女反转',    '<em>300 mi+ ⇄</em>',     '5K-100K 男快 10% · 超长距女性可能赢 · 脂肪利用'),
            ('▸ ACTN3',      '<em>RR/RX/XX</em>',     '快慢肌比例 · 西非 RR 高频 · 单基因决定论是错的'),
            ('▸ 马拉松破二',   '<em>Joyner 1:57:58</em>', 'Kipchoge 1:59:40 · VO2max × %max × 1/RE'),
        ],
    },
}


# ─── 生成 HTML 片段 ──────────────────────────────────
def build_hero_block(chapter_id: str) -> str:
    """生成 hero figure + keypoints 数据卡 HTML"""
    if chapter_id not in KEYPOINTS:
        return ''

    data = KEYPOINTS[chapter_id]
    caption = data['caption']
    kps = data['kp']

    kp_html = '\n'.join([
        f'''    <div class="kp">
      <span class="kp-tag">{tag}</span>
      <span class="kp-value">{value}</span>
      <p class="kp-desc">{desc}</p>
    </div>'''
        for tag, value, desc in kps
    ])

    return f'''  <!-- 章节封面 · AI 生成插画 + HTML 数据标注 -->
  <figure class="chapter-hero">
    <img src="assets/{chapter_id}-hero.jpg" alt="跑者剪影 · 章节封面" loading="lazy">
    <figcaption>FIG 0 · {caption}</figcaption>
  </figure>

  <!-- 关键数据卡片 · 4 个关键数据点 -->
  <div class="hero-keypoints">
{kp_html}
  </div>

'''


def inject_into_chapter(chapter_path: Path) -> bool:
    """在章节 HTML 的 section-tag 之前插入 hero block"""
    chapter_id = chapter_path.stem  # 'ch02' 等
    html = chapter_path.read_text(encoding='utf-8')

    # 跳过已经有 chapter-hero 的(Ch1 之前手动加过)
    if 'class="chapter-hero"' in html:
        # 替换旧的 hero block(用新的标准版本)
        # 用 regex 删除旧的 chapter-hero figure 块 + hero-keypoints 块
        pattern = r'\s*<!-- 章节封面[\s\S]*?</div>\s*\n\s*\n'
        html = re.sub(pattern, '\n\n', html, count=1)

    # 找到 section-tag,在它之前插入 hero block
    hero_block = build_hero_block(chapter_id)
    if not hero_block:
        print(f'  ⚠ {chapter_id}: 没有 keypoints 数据,跳过')
        return False

    # 在第一个 <div class="section-tag"> 之前插入
    new_html, count = re.subn(
        r'(<div class="section-tag">)',
        hero_block + r'  \1',
        html,
        count=1
    )

    if count == 0:
        print(f'  ✗ {chapter_id}: 没找到 section-tag,跳过')
        return False

    chapter_path.write_text(new_html, encoding='utf-8')
    print(f'  ✓ {chapter_id}: hero + 4 keypoints 已注入')
    return True


# ─── Main ───────────────────────────────────────────
if __name__ == '__main__':
    chapters_dir = Path('reports/2026-05-running-science/chapters')
    chapters = sorted(chapters_dir.glob('ch*.html'))

    print(f'[inject-hero] 处理 {len(chapters)} 个章节')
    print()

    success = 0
    for ch in chapters:
        if inject_into_chapter(ch):
            success += 1

    print()
    print(f'✓ 完成: {success}/{len(chapters)} 章节注入成功')
