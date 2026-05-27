# Marathon Manual 迭代记录

---

## v4 — 2026-05-21

### 🎨 视觉升级 · 章节扉页

10 张 AI 生成章节扉页(即梦 4.5),16:9 cinematic 全幅,统一黑底金线 editorial 风格。

- §1 跑者剪影 + 心血管 + 线粒体 + 能量流
- §2 体育场看台 + 数据点标尺
- §3 跑道透视 + 心电波
- §4 跑者解剖 + stress 红点
- §5 分子结构 + 水滴
- §6 月相 + HRV 波 + 地平线
- §7 头部剪影 + 大脑几何
- §8 膝关节解剖 + 红色 stress glow
- §9 跑者冲终点线 + 体育场剪影
- §10 跑者背影 + 日出地平线

### 🔧 工程化

- 新增 `images/` 目录承载 10 张 hero
- 新增 `.ch-hero` CSS 组件(16:9 容器 + 底部渐变过渡)
- 部署到 GitHub Pages: https://baixiao8.github.io/study/marathon/
- 编写 v3 prompt(去除"book / magazine"等触发印刷页面渲染的词)解决文字串扰

### 💰 成本
14 099 积分初始 - 已用 128 = 13 971 剩余(够生成 1 700+ 张)

---

## v3.3 — 2026-05-21

### 🎯 重做 §1.2 HR 区间作为视觉化样例

- 6 张参数概念卡(`.param-card`):HRmax / RHR / HRR / LTHR / AeT / Drift
- Karvonen 公式可视化盒(`.formula-box`):变量分色
- 三个坑点卡(`.pitfall-grid`):错→对对照
- 5 区训练大型 SVG:bpm 刻度 + 说话能力 + RPE + 主用途 + 典型课 + 80/20 分布叠加

### 🆕 引入 3 个新组件

- `.param-grid` + `.param-card` · 概念卡(顶部色条 + 缩写 + 中文名 + 定义 + 数据块 + tip)
- `.formula-box` · 公式可视化
- `.pitfall-grid` · 编号坑点卡

### 🔄 字体全局改苹方

- v3.2 字体 pass: 删衬线(Cormorant Garamond) + 等宽(JetBrains Mono),全部用 PingFang SC + 字重/字号/字距建立层级
- 数字加 `font-feature-settings: "tnum" 1`(等宽数字)保证表格对齐

---

## v3.1 — 2026-05-21

### 📐 垂直节奏(spacing pass)

8px 网格基准:

- section padding: 80 → 112px
- h3 margin-top: 40 → 72px
- callout margin: 24 → 36px; 连排时收紧到 20px
- svg-frame margin: 28 → 48px
- ul/li line-height: 1.7 → 1.78

---

## v3 — 2026-05-21

### 🖼 33 张 SVG 数据图表

- §1.1 三大能量系统(横轴时长 × 纵轴比例)
- §1.4 乳酸阈值 S 曲线
- §2.2 80/20 vs 阈值 vs 金字塔 三流派对比
- §3 各课表 sparkline(LSD / Tempo / Intervals / R / MP / Strides)
- §5.3 72h 赛前 carb load 时间线
- §6.1 睡眠分期环形图
- §8.2 ACWR 仪表盘
- §9.1 Taper 减量柱图
- §9.8 A/B/C 目标级联
- 等等

### 🧱 新组件

`.chip` · `.status-list` · `.metric-card` · `.compare-2` · `.bar-row` · `.timeline` · `.workout-card`

### 📚 §9 大扩展

新增 8 个赛日操作章节:9.8 A/B/C 三档目标 / 9.9 早晨 GI 厕所策略 / 9.10 天气四案 / 9.11 NSAID 警告 / 9.12 撞墙重启六步 / 9.13 异地赛事旅行 / 9.14 赛道预习 / 9.15 皮肤摩擦防护

### 🆕 视觉小件

- 顶部阅读进度条(滚动金线)
- Hero 章节预览卡片网格(11 张:10 章 + 附录)
- 分享提示横幅

---

## v2 — 2026-05-21

### 6 处事实修正

- VDOT 数字:3:20 = VDOT 48(原写 55)、破三 = VDOT 54(原写 62)
- 碳板鞋:4% 是 Nike Vaporfly 数据(Hoogkamer 2018);独立 meta(Healey 2022; Knopp 2023)显示 2-4%
- 睡眠 -3%:区分急性剥夺(Reilly 1993)vs 慢性少睡(Milewski 2014)
- 碳水 1:0.8:Jeukendrup 2020 后更新比例(旧主流 2:1)
- 月经周期段落重写:强调个体差异,Sims 2019 / Elliott-Sale 2021
- 营养克数:从 65kg 假设 → 按 g/kg 算 + 60/70/80kg 三档示例

### 9 处补充

- §9.8 A/B/C 三档目标体系
- §9.9 早晨 GI / 厕所策略
- §9.10 天气四案应对
- §9.11 NSAID 警告
- §9.12 撞墙重启六步法
- §9.13 异地赛事旅行
- §9.14 赛道预习方法
- §9.15 皮肤摩擦与脚部防护
- 附录 A.2 VDOT × 配速大表

### 📚 视觉提升

- 顶部阅读进度条
- Hero 11 张章节预览卡
- 13+ 处文献引用 inline 标注

---

## v1 — 2026-05-21

### 🎉 初版手册

10 章 + 附录,约 2 200 行 HTML / 86 KB。覆盖:

- §1 生理基础
- §2 主流训练理论
- §3 课表机理
- §4 力量与跑姿
- §5 营养水合
- §6 睡眠恢复
- §7 运动心理
- §8 伤病与康复
- §9 比赛日 + Taper
- §10 赛后 + 业内前沿
- ∞ 附录:VDOT × 配速 + 术语表 + 推荐阅读

### 🎨 视觉

- 暗色 editorial 主题(`--bg #0e0e0c` + `--accent #d4a548` 金)
- 衬线大标题(Cormorant Garamond)+ 等宽数字(JetBrains Mono)+ 中文 PingFang
- 10 章节色系
- 5 种 callout(sharp / ops / note / you / formula)
- 15 张 SVG 数据图

---

*维护规则:每次大改动后,在顶部加新版本条目,并把上一版 index.html 复制到 archive/manual-vX.html*
