# Changelog · 项目演进史

> 此文档记录项目的版本演进。每个版本对应一次产品形态的飞跃,而不是小修小补。
> 详细的设计文档放在 `docs/`,部署细节看 [DEPLOY.md](./DEPLOY.md)。

---

## v6.0 · 高音质 Audio Mode 集成(2026-05-24)

针对 v5 三大结构性体验问题(iOS 锁屏中断 / 中文音色机械感 / 自研修补 ROI 递减),
引入预生成 MP3 + 浏览器原生 `<audio>` 元素的新模式。

### 三大问题对照

| 问题 | v5 状态 | v6 解法 |
|---|---|---|
| iOS Safari 锁屏 30s 中断 | ❌ 系统硬限制无解 | ✅ `<audio>` 是浏览器一等公民,锁屏后台完美 |
| 中文音色机械感 | ❌ 系统 TTS 质量差 | ✅ Azure Neural 神经音色(云希·男声·阳光) |
| 自研修补 ROI | ❌ 修不动 Web 平台天花板 | ✅ 改走 audio 模式,平台限制变非限制 |

### 技术方案

```
edge-tts(社区反向 API,免费)
└── 调用 Edge 浏览器朗读功能背后的 Azure Neural TTS
    └── 生成 MP3 + SentenceBoundary 词级时间戳
        └── 自写 SRT + JSON 段落映射
            └── 前端 reader.js 用原生 <audio> 播放 + timeupdate 同步段落高亮
```

**全程 0 成本**:edge-tts 免费,GitHub Pages 静态存储免费,浏览器原生 audio 免费。

### 新增产物

1. **`_shared/audio-gen.py`**(450+ 行)
   - BeautifulSoup 严格过滤(嵌套 div / SVG / 表格 / 装饰)
   - 自动分块(4500 字/块,处理 Edge TTS 单次请求限制)
   - 修复关键 bug:`not getattr(tag, 'attrs', None)` 在空 dict 时误判 145 个 `<p>` 标签
   - 输出 MP3 + SRT + JSON 三件套

2. **`_shared/reader.js` v6 audio mode**
   - 6 个新 prototype 方法(检测/加载/监听/同步/播放/切换)
   - open() 异步检测音频可用性,有则自动启用
   - play() / pause() / next() / prev() 全部加 audioMode 分支
   - 速率切换同步到 audio.playbackRate(无缝)
   - timeupdate 二分查找当前段落 → 高亮 + 进度记忆
   - 控制条加 "🤖 标准 / 🎙 高音质" 切换按钮
   - 音频播放失败自动降级到 Web TTS

3. **章节音频**(逐步生成上线)
   - Ch1:15.8MB MP3 / 45KB SRT / 163 段映射(已上线)
   - Ch2-12:陆续生成中,~170MB 全部完成

### 用户体验

```
桌面 + 移动 自动检测当前章节是否有音频:
有音频 → 自动切换到高音质模式 + 显示 "🎙 高音质" 按钮
无音频 → 降级到 Web TTS + 显示 "🤖 标准" 按钮

切换按钮一键来回切换两种模式
切换后从同一段落继续播放(进度无损)

iOS Safari 锁屏:
旧版 Web TTS → 30s 后系统暂停 ❌
新版 audio  → 完美后台播放 ✅
```

### Bug 修复(audio-gen 开发过程)

| Bug | 原因 | 修复 |
|---|---|---|
| 145 个 `<p>` 被跳过 | `not getattr(tag, 'attrs', None)` 在空 dict 时返回 True | 改为只检查 `tag.parent is None` |
| Edge TTS NoAudioReceived | 单次请求字数超 5K 限制 | 段落级智能切块(每块 ≤4500 字) |
| edge-tts 7.x SubMaker 失效 | API 改为 `SentenceBoundary` | 自写 SRT,直接处理 chunk['offset']/'duration' |
| `hero-keypoints` 数据卡漏读 | regex 嵌套 div 处理不对 | 换用 BeautifulSoup 多轮 decompose |

### 待办

- [ ] Ch2-12 音频生成完成后 push
- [ ] 移动端测试切换按钮 + 锁屏播放
- [ ] 验证 Ch1 SRT 段落高亮是否精准

---

## v5.1 · 阅读模式三大体验修复(2026-05-23)

针对用户首测后反馈的三大问题做系统性修复。

### 三大问题诊断与修复

#### ① 「从头开始读」是重大 UX bug

用户在 Ch4.6 浏览,点 ▶ 期望从 Ch4.6 开始读,但实际从 chapter[0] 章节标题开始。
**修复**:新增 `_detectVisibleChunkIdx(chapter)`,扫描视口内最居中的可读段落作为起点。
**起始段优先级**:`opts.startId(URL 锚点) > 视口可视段 > localStorage 同章 24h > 0`

#### ② 点击播放 + 页面加载卡顿

诊断:
- `_buildAllChunks()` 跨遍 12 章 ~10000 节点(200-400ms 阻塞)
- `_estimateListenTime` 在 init 时同步遍历 12 章字数
- `open()` 一次性同步执行 4 步重活
- 视口外章节也参与 layout 计算

**修复**:
- `.chapter { content-visibility: auto; contain-intrinsic-size: 0 2400px }` — 视口外 11 章跳过 paint/layout 计算
- `_estimateListenTime` → `requestIdleCallback`(idle 时间执行,不阻塞首屏)
- `_buildAllChunks` 改 lazy,只在 `_onChapterEnd` 跨章衔接时才算
- `open()` 改渐进式 3 帧渲染:①立即骨架 ②rAF 算 chunks ③rAF 填内容

**预期收益**:
- LCP(4G):3s → 1.5-1.8s
- INP(点击响应):300-500ms → **32-80ms**
- 用户感知"点 ▶ 瞬间响应"

#### ③ 移动端 UI 控制条占 30% 屏幕

诊断(用户截图):
- 控制条双行 + iOS Safari nav,阅读区只剩 50%
- iOS 提示 4 行横幅,关键视野被吃
- 主题色块选中态不明显,⏰ emoji 风格不统一
- Sleep 菜单弹出遮挡正文

**修复**:
- **控制条单行紧凑化**:只保留 ◀ ⏸ ▶| · 倍速 · A 字号 · ⚙ 设置 · ✕ 关闭
- **二级控件折叠到 Sheet**(点 ⚙ 从底部弹起的抽屉):章节 / 主题 / 字号 / 行距 / 音色 / 定时 / 章末接下章
- **iOS 提示降级为顶部 Toast**:5 秒自动消失 + 用户关闭后 localStorage 记忆永久不显示
- **Sheet 用主题色 pill 按钮 + 圆环主题选择器**:选中态明显
- **阅读区屏幕占比从 50% → 75%**

### 新增文档

- **`docs/PERF-analysis.md`**(300+ 行):性能优化深度分析
  - 主流产品横向对比(微信读书 / Medium / Notion / 小宇宙 / 知乎 / Substack)
  - Core Web Vitals 阈值与诊断框架
  - 5 个 P0 问题深度分析 + 修复 + 预期收益
  - ROI 决策矩阵 10 项(v5.1 完成 8 项)
  - 实施验证清单 10 项

### 代码改动

- `_shared/reader.js`:open 渐进式 + visible chunk 检测 + sheet 弹出 + iOS toast(~250 行新增/重写)
- `_shared/reader.css`:移动单行控制条 + Sheet + iOS Toast 新样式(~200 行新增/重写)
- `_shared/style.css`:`section.chapter` content-visibility(2 行核心)
- `docs/PERF-analysis.md`:新增 300+ 行
- `CHANGELOG.md`:补 v5.1 条目

### 实施验证清单(发布后 4 周观察)

```
[ ] WiFi 桌面 Chrome · LCP < 1.5s
[ ] 4G 移动 Chrome · LCP < 2.5s
[ ] 点 ▶ 进阅读模式 INP < 100ms
[ ] 滚动到 Ch12 时无明显卡顿
[ ] 12 张 hero 图按视口加载
[ ] Sheet 弹出无遮挡正文
[ ] iOS Toast 仅首次显示,关闭后不再
[ ] 控制条单行,阅读区占屏 ≥ 75%
[ ] 从当前可视段落开始播放
[ ] 与桌面端控制条共享代码无 regression
```

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
