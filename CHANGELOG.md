# Changelog · 项目演进史

> 此文档记录项目的版本演进。每个版本对应一次产品形态的飞跃,而不是小修小补。
> 详细的设计文档放在 `docs/`,部署细节看 [DEPLOY.md](./DEPLOY.md)。

---

## v5.0 · 阅读 + 听书模式(2026-05-23)

> **不是给报告加播放按钮,是把研究报告从「久坐型阅读品」升级为「随身型消费品」。**

引入跨报告的「阅读 + 听书」共享组件。所有当前与未来报告自动获得右下角悬浮 ▶ 按钮,点击进入沉浸阅读模式 + 一键 TTS 听书。

### 新增

- **`_shared/reader.css`**(530 行)三主题 + 桌面/手机响应式 + 全部 UI 视觉
- **`_shared/reader.js`**(750 行)P0-P2 全功能(沉浸阅读 + TTS + 段落高亮 + 进度记忆 + 章末接下章 + 定时关闭 + mini player + Media Session 锁屏控制 + URL 段落分享 + 听书时长估算)
- **`_shared/READER_RULES.md`**(374 行)报告写作约定 —— 未来所有报告遵守这份规范即可零适配兼容
- **`docs/PRD-reader-mode.md`**(1099 行)完整产品需求文档 v0.2

### P0 功能(基础阅读 + TTS)

- F-001 ~ F-013:右下角 ▶ 触发 / overlay 浮层 / 三主题 / 4 档字号 / 3 档行距 / TTS 一键朗读 / 段落高亮 + 自动滚动到中央 / 6 档倍速 / 上下段跳转 / 章节跳转 / localStorage 进度记忆 / 移动端响应式 / SVG 占位提示

### P1 功能(听书化升级)

- F-101 定时关闭:5/10/15/30/60 分钟 + **本章末**(微信读书独家)
- F-102 章末自动接下章(默认开启)
- F-103 mini player:关闭 overlay 后底部常驻浮条,可继续听
- F-104 多音色选择:枚举系统所有中文 TTS 音色
- F-105 Media Session API:锁屏 / 通知栏 ⏯ + 上下段控制
- F-106 9 档倍速:0.5 / 0.75 / 1.0 / 1.25 / 1.5 / 1.75 / 2.0 / 2.5 / 3.0
- F-107 语义朗读强化:反共识 / 协议 / 第二人称剧本朗读时加前缀 + 视觉强调

### P2 功能(独门)

- F-201 段落双向跳转:点击段落即从该段开始朗读
- F-202 URL 段落分享:`#read=xxx` 锚点可直接跳到段落 + 自动朗读
- F-204 听书时长估算:每章标题旁显示「🎧 X 分钟」

### 工程基础设施

- 改 `_shared/build.py`:支持多 CSS / 多 JS 自动 inline
- 更新 `parts/00_hero.html`:引入 reader.css
- 更新 `parts/99_footer.html`:引入 reader.js
- `READER_RULES.md` 写作约定 → 未来报告零适配兼容

### 关键决策依据

- **不上云端 TTS**:GitHub Pages 纯静态站约束 → 用浏览器原生 SpeechSynthesis(免费、零后端、零 API Key)
- **跨设备同步省略**:用 localStorage 单设备 + URL 锚点分享补偿
- **桌面 vs 手机分开设计**:单代码 + 双 CSS 布局规则,不是一套 UI 硬适配两端

### 已知限制

- iOS Safari 锁屏 30 秒后系统会自动暂停 TTS(系统级硬伤,加横幅提示用户"保持屏幕亮")
- 中文音色质量取决于操作系统(Mac/Chrome/Edge 较好,Firefox 一般)
- 不支持词级跟读(Web Speech API boundary 事件不可靠)

详见:[PRD-reader-mode.md](./docs/PRD-reader-mode.md) Section 7.6 兼容性矩阵 + Section 9 风险与开放问题

---

## v4.0 · 可读性嫁接(2026-05-23)

针对「专业但太学术化」反馈,在 12 章学术骨架上**嫁接 5 类追加组件**,让读者从「读不懂」变成「读完知道下周该干啥」。

### 5 类嫁接组件(全 12 章合计)

| 组件 | 数量 | 形态 |
|---|---|---|
| **白话翻译行** `.plain` | 99 个 | 每个公式/缩写后挂一句「翻译成人话」+ 跑步场景代入 |
| **3 件事清单** `.callout.ops` | 69 个 | 每个核心小节末:测什么 / 改什么 / 看什么信号 |
| **第二人称剧本** `.callout.you` | 31 个 | 按时间轴推演(0-700 ms 步态 / 30 km 撞墙 / Kipchoge 破二) |
| **章末协议清单** `.callout.protocol` | 12 个 | 操作手册风,每章 3 个协议 |
| **STOP 警示块** | 36 个 | 每协议必有「何时停训或就医」具体指引 |

### 36 个可落地训练协议

Cooper 12 min 测试 / 30 min LT2 推算 / 晨脉 7 天基线 / HRV 监测 / HRmax 实测 / Alfredson 跟腱 12 周 / 北欧腘绳 / Borg RPE 校准 / 脑耐力训练 BET / 14 天热适应 / REDs 自检三件套 / 长跑 GI 6 周渐进 / 比赛日营养清单 / 铁蛋白季度 / CTL-PMC(intervals.icu) / 12 周半马骨架 / Taper 14 天 / **ACWR Strava 自计算** / **0-30-50-70-90-100 伤后回归** / **绿黄红区伤病分级** / 40+ 抗衰退周菜单 / VDOT 配速换算 / Pfitzinger 马拉松 等。

### 数据变化

- 字数 101K → **137K**(+35K, +35%)
- 阅读时间 4.8h → **6.5h**
- 文件大小 853KB → 1.04MB

### 工程基础设施

- 新增 `_shared/v4_insertions/apply_v4.py` 装配脚本(支持 dry-run)
- 5 个生成 sub-agent + 4 个装配 sub-agent 并行协作
- 新增 `.plain` 「人话」徽章 CSS 样式
- 新增 `.callout.protocol` 等宽字体 + STOP 警示块样式

---

## v3.0 · Newsprint 报刊风 + AI 章首图(2026-05-22)

从暗色主题转向米黄报刊纸风,加入 12 张 AI 生成的章首插图。

### 视觉重塑

- 背景 #F0EBDD 米黄纸张
- 正文 PingFang SC 苹方
- 标题 Inter Tight 700-900
- 报刊红 #A8423B 强调色
- 3px double border 章节分隔

### 内容增强

- 12 张 AI 章首图(千图 AI 即梦5.0 生成)
- 48 个 HTML 数据卡(每章 4 个 keypoints)
- 30+ SVG 数据图全部从暗色重映射到米黄主题

### 工程基础设施

- 新增 `_shared/inject-hero.py` 批量注入脚本
- SVG_COLOR_MAP 32 色映射(暗色 → Newsprint 浅色)
- 全站 CSS 变量主题化(`:root --bg/--ink/--accent`)

---

## v2.0 · 阅读辅助(2026-05-21)

加入术语词典 / 章末回顾 / 速览页 / 反共识索引等阅读辅助功能。

### 新增

- `_shared/glossary.json`:80+ 术语词典 hover 弹出解释
- `_shared/tooltip.js`:术语 hover 浮窗
- `_shared/mini-toc.js`:章节内悬浮 mini-TOC(桌面 1280px+)
- `parts/05_intro.html`:3 分钟速览页
- `parts/95_antithesis.html`:反共识索引(30+ 反直觉洞察集中页)
- 每章末「5 分钟回顾」卡片
- 每章阅读时间标记

### 工程基础设施

- 重组 `_shared/` 共享资产
- `build.py` inline 模式(单文件 HTML,无外部依赖)
- 解决 GitHub Pages Jekyll 屏蔽 `_shared/` 问题(`.nojekyll`)
- 解决浏览器 negative-cache 404 问题(cache-busting + inline 全部资源)

---

## v1.0 · 内容深度(2026-05-20)

12 章跑步深度研究报告首版上线。

### 内容

- 12 章学术骨架:力学 / 生理 / 解剖 / 神经 / 代谢 / 训练 / 伤病 / 极限
- 100K 字 / 4.8h 阅读
- 30+ SVG 数据图(原创手绘)
- Bassett & Howley / Wilmore & Costill / Brooks & Fahey 等教材参考
- IOC / ACSM 共识声明引用

### 工程基础设施

- 项目骨架建立:`reports/<slug>/chapters/*.html` + `parts/*.html` + `_shared/`
- `build.py` 装配脚本
- GitHub Pages 部署(`https://baixiao8.github.io/studies/`)

---

## 路线图(规划中)

### v5.1 · 阅读+听书反馈迭代

- 收集 4 周使用数据(打开率 / 完成率 / 移动端占比)
- 根据反馈决定是否加 L3 功能(段落双向跳转完善 / 进度条断点 / 关键段落标记)
- 修复 iOS Safari 锁屏 TTS 中断的兜底方案

### v6.0 · 新报告(主题 TBD)

候选主题:睡眠科学 / 注意力 / 衰老 / 营养 / ……
新报告从写作第一行就遵循 `READER_RULES.md`,零适配兼容阅读+听书模式。

### v7.0+ 长期愿景

- 报告族横向连接(跨报告交叉引用 / 概念链接)
- 用户笔记 + 朗读标记联动(如果有真实需求)
- 多语言版本(英文报告 + 中文报告并存)

---

**更新规则**:每次发布版本时,在此文档顶部追加新版本条目。不直接修改历史版本(只追加 "errata / 修正" 注释)。
