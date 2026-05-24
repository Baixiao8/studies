# 研究报告项目准则 · PRINCIPLES

> 本文件定义在 **运动健康** 这个研究报告项目下做报告的所有约定。
> 后续每份报告应遵守这套准则,以保持视觉一致性、可读性、可维护性。
>
> 版本:v1.0 · 适用范围:本仓库下所有 `reports/*/`

---

## 一、目录结构规范

```
运动健康/                                ← 项目根
├── README.md                            项目说明 + 报告索引
├── PRINCIPLES.md                        本文件 · 项目准则
├── DEPLOY.md                            部署指南
├── .gitignore                           Git 忽略规则
│
├── _shared/                             所有报告共享的资产
│   ├── style.css                        统一样式(设计 tokens + 组件 + 布局)
│   ├── mini-toc.js                      右侧悬浮章节内目录
│   ├── tooltip.js                       术语 hover 浮窗
│   ├── progress.js                      顶部进度条 + sticky-nav 高亮
│   ├── glossary.json                    术语词典(全项目共享)
│   └── build.py                         报告装配脚本
│
├── reports/
│   └── YYYY-MM-<slug>/                  每份报告独立目录
│       ├── index.html                   build 装配的最终页(部署目标)
│       ├── parts/
│       │   ├── 00_hero.html             Hero + Sticky-nav 起头
│       │   ├── 05_intro.html            3 分钟速览页(可选)
│       │   ├── 95_antithesis.html       反共识索引页(可选)
│       │   ├── 99_footer.html           Footer + script 引用
│       │   └── _recaps.json             每章 5 分钟回顾数据
│       ├── chapters/
│       │   └── ch01.html ... chXX.html  各章节内容(纯 section 片段)
│       └── assets/                      报告专属图片(目前未用)
│
└── _legacy/                             旧版本/试验/废弃文件,只读归档
```

**规则:**
- 新报告目录名:`YYYY-MM-<英文 slug>`,如 `2026-08-sleep-science/`
- 章节文件命名:`ch01.html`、`ch02.html`...,两位数字,按顺序
- 报告生成必须通过 `python3 _shared/build.py reports/<slug>` 装配
- 共享资产不复制到报告目录,统一引用 `../../_shared/*`

---

## 二、八条铁律 · 报告必须遵守

| # | 原则 | 含义 |
|---|---|---|
| **1** | 五件套必备 | 每份报告必须有 Hero + Sticky-nav + 章首 TL;DR + 章末 5 分钟回顾 + Footer |
| **2** | 视觉锚点密度 | 每 800 字至少 1 个视觉锚点 (callout/svg/grid/table),避免连续 1500 字纯文本 |
| **3** | 段落呼吸 | 单段 > 6 行必须拆,或加 h4 小节标题 |
| **4** | 字号锚定 | 正文 15.5px / 引导 17.5px / h3 32px / h1 52-84px;行高 1.72-1.78,绝不 < 1.6 |
| **5** | 字体栈固定 | 苹方 PingFang SC (正文) + Cormorant Garamond (衬线标题) + JetBrains Mono (数据/标签) |
| **6** | 配色规则 | 每章一个学科色,顶部 4px border + metric-card 子类一致;颜色统一引用 CSS 变量 |
| **7** | callout 用法 | sharp = 反共识 (≤3/章) · ops = 操作建议 · you = 个人化 · note = 机制注释 · story = 故事钩子 |
| **8** | 引用规则 | 用 `[Author Year]` inline format,不伪造,模糊化年代或泛指 |

---

## 三、组件使用约定

### Callout 系列(关键!)

| Callout | 用途 | 视觉 | 频率限制 |
|---|---|---|---|
| `.callout.sharp` | 反共识洞察 | 红色边 + ✕ | ≤ 3 个/章 |
| `.callout.ops` | 可操作建议 | 绿色边 + ✓ | ≤ 3 个/章 |
| `.callout.you` | 个人化注解 | 紫色边 + ◐ | ≤ 1 个/章 |
| `.callout.note` | 机制注释/数学小结 | 灰色边 + i | ≤ 2 个/章 |
| `.callout.story` | 故事钩子(章首叙事) | 暖橙边 + ◆ + 衬线斜体 | ≤ 1 个/章,放章首 |

**为什么有频率限制**:reader 需要节奏,反共识太多就不再反共识。

### 章节标题层级

```html
<section id="s1" style="border-top: 4px solid var(--c-theory);">
<div class="container">
  <div class="section-tag"><span class="num">01</span>KINEMATICS · 力学篇 / 第一章</div>
  <h1 class="section-h">章节标题 <span class="en">English Subtitle</span></h1>
  <p class="section-sub">导语段...</p>

  <div class="tldr">
    <div class="label">▼ ELEVATOR PITCH</div>
    <p>本章核心命题(衬线大字)</p>
  </div>

  <!-- reading-meta + chapter-toc 由 build.py 自动注入 -->

  <h3><span class="pre">1.1</span>子节标题</h3>
  <p class="lead">引导段...</p>
  <p>正文...</p>

  ...
</div>
</section>
```

### 数据展示组件优先级

按密度递增:
1. **inline mention** (`<strong>` `<em>`) — 一两个数字
2. **`.chip`** — 标签型(配速、训练日)
3. **`.number-strip`** — 4 个并列关键数字
4. **`.metric-grid` + `.metric-card`** — 6+ 个有名 KPI
5. **`<table>`** — 结构化对比
6. **`.svg-frame` + inline SVG** — 关系/趋势/分布

---

## 四、内容写作约定

### 基调
- **学术深度但可读**:每章 8-12K 字,密度高,但用 callout / table / svg 切碎
- **反共识立场**:每章主动找 2-3 个被推翻的"常识",用 `.callout.sharp` 标出
- **可操作锚点**:理论 + 至少 1 个 `.callout.ops` 给出"你可以怎么做"
- **不要过渡词**:删掉"重要的是""我们可以看到""值得注意"

### 段落写作
- 一段一个主旨
- 单段 ≤ 6 行;超出必须拆 / 加小标题 / 换列表
- 关键数字带单位、英文术语用 `<em>` 标
- 引用模糊年代:`[Brooks 2018]`、`[Joyner 1991]`,不伪造

### 章首三件套
1. **section-sub**:1-2 句话点题
2. **TL;DR**:衬线大字 1 句话精炼(像电影 logline)
3. **(可选) `.callout.story`**:1 段叙事钩子(人物/实验/历史场景)

### 章末三件套
1. **`.callout.note` 本章核心命题**:重点总结
2. **`.chapter-recap` 5 分钟回顾**:5 条要点(数据写入 `_recaps.json`,build.py 注入)
3. **`<p class="ref">` 主要参考**:`[Author Year]` 列表

---

## 五、SVG 数据图准则

- 用 `viewBox` 而不是固定宽高,确保响应式
- 必有:坐标轴、刻度、单位、图注 `.svg-caption`
- 配色用 CSS 变量(`var(--accent)`、`var(--c-physio)`...),不要硬编码颜色
- 字体 `font-family: var(--ff-mono)`(SVG 全局已设置)
- 复杂图用 `<defs>` 定义渐变、`<g>` 分组、`<text>` 标签
- 图注命名规则:`FIG X.Y · SHORT DESC · [Author Year]`

**典型 SVG 类型(按报告主题挑选):**
- 时序曲线(对比多变量随时间变化)
- 占比/分布(柱状、饼状)
- 散点/相关性
- 解剖示意图(人体侧视、关节角度)
- 流程图/因果链

---

## 六、配色系统

| 学科 | CSS 变量 | 色值 | 用途示例 |
|---|---|---|---|
| 力学/理论 | `--c-theory` | `#b54848` 红 | 步态、动力学 |
| 解剖/力量 | `--c-strength` | `#6a8b3d` 绿 | 肌肉、骨骼 |
| 生理 | `--c-physio` | `#4a6fa5` 蓝 | 心肺、代谢 |
| 训练/课表 | `--c-session` | `#c47f17` 橙 | 周期、课表 |
| 营养 | `--c-nutrition` | `#d97a3c` 暖橙 | 能量、补给 |
| 恢复/免疫 | `--c-recovery` | `#3d8b6e` 青绿 | 睡眠、免疫 |
| 神经/心理 | `--c-psych` | `#9c4bb5` 紫 | 神经、心理 |
| 伤病 | `--c-injury` | `#b56565` 粉红 | 损伤、康复 |
| 比赛/极限 | `--c-race` | `#c93f3f` 正红 | 极限、个体差异 |
| 金色主强调 | `--accent` | `#d4a548` | 全局强调 |

**规则**:
- 每章选一个主色,在 `<section>` 顶部 4px border 体现
- 同章内的 metric-card 也用同色(`.metric-card.physio` 等)
- 一份报告里同色最好只用 1-2 章,避免颜色混乱
- 不要随意创造新色

---

## 七、可读性设计准则

| 元素 | 准则 |
|---|---|
| Mini-TOC | 桌面 1280px+ 自动启用,移动端隐藏 |
| Tooltip | 鼠标停靠 < 250ms 出现,术语来自 `glossary.json` |
| 阅读时间 | 按中文字符数 ÷ 350 字/分钟自动计算 |
| 章节内目录 | < 3 个小节不显示,3+ 个显示在 section 头部 |
| 5 分钟回顾 | 5 条结构化要点(不是段落),从 `_recaps.json` 注入 |
| 反共识索引 | 全报告 sharp callout 汇总到末尾独立 section |

---

## 八、Build & Deploy

```bash
# 1. 装配单份报告
python3 _shared/build.py reports/<slug>

# 2. 打开浏览器预览
open reports/<slug>/index.html

# 3. 推 Git
git add . && git commit -m "report: <slug> v1.0" && git push

# 4. GitHub Pages 自动部署
# 配置见 DEPLOY.md
```

---

## 九、新报告 checklist

- [ ] 新建 `reports/YYYY-MM-<slug>/` 目录
- [ ] 复制 `parts/00_hero.html`、`99_footer.html` 作为骨架
- [ ] 在 chapters/ 下写各章 ch01.html ... chXX.html
- [ ] 写 `parts/_recaps.json`(每章 5 点回顾)
- [ ] (可选) 写 `parts/05_intro.html`(3 分钟速览)
- [ ] (可选) 写 `parts/95_antithesis.html`(反共识索引)
- [ ] 跑 `build.py`,浏览器验证
- [ ] 更新 `README.md` 报告索引
- [ ] git commit + push,自动部署

---

## 九-bis · Footer 范式(v8.6+ 锁定,以后照抄)

每份报告底部的 `parts/99_footer.html` 用**同一套五块结构 + 单行署名**,不再重新发明。

### 结构(~200 字 · 不要超)

```
1. 引语 .lede          · 一句研究观,可两行,英文 em 词点缀
2. 关于这份调研          · 一段 · 干什么 + 不干什么(明确否定一种)
3. 内容来源            · 一段 · 教材 / 期刊 / 共识 / 学者(列名,不展开)
4. 使用边界            · 一段 · 不构成医疗建议(医学相关报告加红区清单)
5. credit             · mono 大写一行 · 学科 · DEEP RESEARCH · vX.X · CHAPTERS 1–12 · 月份 年份
6. signature          · "白笑 · YYYY 年 M 月" · 与 credit 同视觉,作为最底部
```

### HTML 模板(直接复制)

```html
</main>

<!-- ============= FOOTER ============= -->
<footer>
  <div class="container">
    <p class="lede">
      "<<引语句 1>><br>
      <<引语句 2,含 <em>英文词</em>>>"
    </p>

    <div class="colophon">
      <h4>关于这份调研</h4>
      <p>一份基于公开<<学科>>文献综合编撰的<strong><<学科>>多学科调研</strong>。
         从<<第一性原理>>出发,把<<研究对象>>当作研究对象解构——<<关键词列表>>。
         <em>不是<<否定的体裁,如训练手册/诊疗手册>></em>,是一份回答"<<核心问题>>"的报告。</p>

      <h4>内容来源</h4>
      <p>综合自<<教材短列>>、<em>期刊1</em> / <em>期刊2</em> / <em>期刊3</em> 等核心期刊代表性研究、
         <<共识机构短列>> 共识声明、以及 <<学者短列>> 等学者的工作。
         具体引用为示例性使用,优先精度而非来源覆盖。</p>

      <h4>使用边界</h4>
      <p>本报告不构成医疗建议或<<学科相关处方>>。涉及<<决策类型>>时,
         请咨询<<专业人士>>。生物学的核心规律是<em>个体差异</em>。
         <<医学报告追加:出现<strong>红区信号</strong>(...)请立即就医。>></p>
    </div>

    <p class="credit"><<学科名英文>> · DEEP RESEARCH · vX.X · CHAPTERS 1–12 · <<MONTH>> <<YEAR>></p>
    <p class="signature">白笑 · <<YYYY>> 年 <<M>> 月</p>
  </div>
</footer>

<!-- ============= SHARED SCRIPTS ============= -->
<script src="../../_shared/progress.js?v=YYYYMMDD" defer></script>
<script src="../../_shared/mini-toc.js?v=YYYYMMDD" defer></script>
<script src="../../_shared/tooltip.js?v=YYYYMMDD" defer></script>
<script src="../../_shared/reader-bootstrap.js?v=YYYYMMDD" defer></script>

</body>
</html>
```

### 禁区(写新报告时不要再加这些)

- ❌ **"设计与排版"段落** — 字体/配色这种工程内省,读者不关心
- ❌ **"vX.X 升级亮点"段落** — CHANGELOG 该负责的事不该塞进每份报告
- ❌ **长篇致谢段落** — 感谢太满会变自我感动
- ❌ **GitHub 链接、邮件、社交账号** — 读者不需要,有兴趣的人会找到
- ❌ **署名块的视觉突出**(衬线大字 / 头像 / 多行 vCard)— 与 credit 同视觉,一行即可
- ❌ **二维码、版权符号、ISO 日期格式** — 印刷感来自留白,不来自符号堆砌

### 唯一变量

每份新报告下面这些**必须改**,其他都照抄:

| 位置 | 变量 |
|---|---|
| `.lede` | 引语两句(学科核心观) |
| `关于这份调研` | 学科 / 第一性原理 / 关键词 / 否定的体裁 / 核心问题 |
| `内容来源` | 教材列表 / 期刊列表 / 共识机构 / 学者列表 |
| `使用边界` | 决策类型 / 专业人士;医学报告追加红区信号 |
| `.credit` | 学科名英文 / 版本号 / 章数 / 月份年份 |
| `.signature` | **不变**:始终 `白笑 · YYYY 年 M 月` |

---

## 十、未来扩展(待决)

- [ ] 在线搜索(Lunr.js 全文索引)
- [ ] 暗色/亮色主题切换
- [ ] PDF 导出脚本(用 `weasyprint` 或 `pagedjs`)
- [ ] 分享卡片自动生成(社交媒体的 Open Graph)
- [ ] 跨报告术语索引页
- [ ] 数据图的 D3.js 化(目前是手画 SVG,未来交互化)

---

## 📖 听书组件接入指南(v8.3+)

`_shared/reader-bootstrap.{js,css}` + `_shared/reader.{js,css}` 是**所有报告通用**的听书组件。

### 新报告接入(只需 2 行)

```html
<!-- parts/00_hero.html · head 内 -->
<link rel="stylesheet" href="../../_shared/reader-bootstrap.css?v=20260524c">

<!-- parts/99_footer.html · body 末 -->
<script src="../../_shared/reader-bootstrap.js?v=20260524c" defer></script>
```

`build.py` inline 模式会自动把这两个文件内联进 index.html。完整 reader.js / reader.css 按需加载(用户点入口时才下载)。

### 触发方式(用户视角)

1. 点击章节标题旁的 **"🎧 听这章"** pill 按钮(每章)
2. 点击小节标题旁的 **🎧** mini 按钮(每节,从该节起播)
3. URL 加 `?listen=1`
4. 键盘按 R 键
5. 任意 JS 调用 `window.activateReader()`

### 报告写作约定(让朗读自然)

- **章节大标题用 `<h1 class="section-h">` 或 `<h2>`** — 自动获得"听这章"入口
- **小节标题用 `<h3>`** — 自动获得 mini "听此节"入口
- **section 加 `class="chapter"`**(build.py 自动加)
- **图表 / 装饰加合适 class**(`.hero`, `.svg-frame`, `.kp-*` 等)— 自动从朗读中排除
- **不要把可朗读的纯文本藏在 SVG 内部** — SVG 整体被跳过

### 听书功能边界(诚实告诉用户做不到什么)

| 能力 | 状态 |
|---|---|
| Web Speech API 朗读 | ✅ |
| 段落起播(任意小节) | ✅ |
| 倍速 0.75 / 1.0 / 1.25 / 1.5x | ✅ |
| 章末自动接下章 | ✅ |
| 防屏幕自动息屏(Wake Lock) | ✅ |
| iOS Safari 主动锁屏继续播 | ❌ 平台硬伤(30s 系统停 JS) |
| 预录 MP3 / 多音色 / 段落高亮同步 | ❌ 主动不做(过度叠加) |

### 修改约定

任何 reader 修改在 `_shared/` 一处完成,然后**所有报告 rebuild + 验证**(防止某个报告改了某个没改的不一致)。

---

## 🧠 加功能"三问"(v6.3 反思,长期约束)

每加新功能前**必答**:

1. 用户**明确说要**了吗?(不是一句话引申)
2. 强化核心 还是 叠加新场景?
3. 失败的代价是什么?

v5-v6 没认真问 → 1850+ 行听书代码 + 227MB 音频 → 最终砍掉。
v8.x 每次都先问再做(小节入口 / 自动接下章 / Wake Lock 都过了三问)。
