# 运动科学手册 · Marathon Manual

> 面向冲击全马 sub-3 的中级跑者的运动科学技术手册
> 线上地址：**https://baixiao8.github.io/study/marathon/**

---

## 项目简介

一本面向**中级及以上长距离跑者 / 越野跑者**的深度技术手册，覆盖从能量代谢到比赛策略、从训练理论到康复康养的完整知识体系。23 周上马 2026 sub-3 备战版。

**核心特点**
- **诚恳尖锐**：每章带「尖锐共识」callout，敢说反主流观点
- **数据驱动**：33 张 SVG 数据图表 + VDOT × 配速大表 + ACWR 仪表盘
- **视觉化**：10 张 AI 生成章节扉页（即梦 4.5） + 暗色 editorial 风格 + 苹方字体
- **个性化**：含基于 6 个月 Coros 数据的「你的数据 ◐」紫色 callout（队友可跳过）
- **可执行**：每章配 OPS 实操建议、SHARP TAKE 尖锐结论、引用真实研究文献

---

## 内容结构

| 章 | 主题 | 阅读时长 |
|---|---|---|
| §1 | 生理基础 · 能量系统 / HR 区间 / VO2max / 乳酸阈 / RE | 5 min |
| §2 | 训练理论 · 5 大流派 + 挪威双阈值 | 6 min |
| §3 | 课表机理 · LSD / Tempo / Intervals / MP / Strides | 5 min |
| §4 | 力量与跑姿 · 8 个动作 + 跑姿要素 | 5 min |
| §5 | 营养水合 · 碳水周期 + 60-120 g/h 补给 | 6 min |
| §6 | 睡眠恢复 · 8h+ 协议 + HRV 决策树 | 4 min |
| §7 | 运动心理 · 8 个子主题（动机/目标/IZOF/注意/对话/调速器/可视化/Burnout） | 4 min |
| §8 | 伤病康复 · 5 大伤 + ACWR + 痛感分级 | 5 min |
| §9 | 比赛 & Taper · 含 A/B/C 目标、GI、天气、撞墙重启等 12 节 | 12 min |
| §10 | 赛后 & 业内前沿 · 碳板 / CGM / 热适应 / 高原 / 女性周期 | 5 min |
| ∞ | 附录 · VDOT × 配速大表 + 术语表 + 推荐阅读 | 查表 |

总长度：**6 300 行 / 310 KB HTML**

---

## 仓库目录结构

```
marathon/
├── README.md              ← 你正在看的
├── ARCHITECTURE.md        ← 内容架构 + 视觉系统 + 命名约定
├── CHANGELOG.md           ← v1 → v4 迭代史
├── 项目文档.md             ← 项目状态、关键决策、待办
├── index.html             ← 主交付（GitHub Pages 入口）
├── images/                ← 10 张 AI 章节扉页（s1-s10_hero.jpg）
├── archive/               ← 历史版本备份
├── generation/
│   ├── scripts/           ← 集成 / 压缩 / 嵌入图片的 Python 工具链
│   └── prompts/           ← AI 图生成 prompts（v1/v2/v3）
├── knowledge/             ← 知识库（训练理论 / 比赛策略 / 营养水合 / 心理康复）
└── memory/                ← Agent 记忆（项目上下文 / 用户档案）
```

---

## 怎么参与 / 二次开发

如果你想基于这份手册做修改或衍生版本：

1. **改内容**：直接编辑 `index.html`
2. **重新生成 AI 图**：用 `generation/prompts/hero_v3.py` 模板（已验证 text-safe）
3. **替换 SVG / 嵌入新图**：参考 `generation/scripts/embed_heroes.py`
4. **批量集成新章节**：参考 `generation/scripts/integrate_v4.py`
5. 提交：常规 `git push`，GitHub Pages 自动 30-60 秒重新部署

---

## 致谢与引用

文中所有「尖锐共识」 / 「SHARP TAKE」后的 `(Author Year)` 标注都对应真实研究文献。核心引用源：

- **训练**：Daniels' Running Formula 3rd ed · Pfitzinger *Advanced Marathoning* · Seiler (polarized) · Casado (Norwegian)
- **营养**：Jeukendrup 2014/2020 · Burke 2008/2021 · Hew-Butler 2015
- **生理**：Joyner & Coyle 2008 · Brooks 2018 · Holloszy 1967
- **心理**：Noakes 2011 · Blanchfield 2014 · Hanin 1997
- **伤病**：Gabbett 2016 (ACWR) · Lipman 2017 (NSAID + AKI)
- **女性**：Sims 2019/2022 · Elliott-Sale 2021

---

*Last updated: 2026-05-21 · v4*
