# Reader Rules · 报告写作强制约定

> **作用**:本仓库下所有研究报告写作时**必须**遵守的语义约定。报告通过共享组件 `_shared/reader.{js,css}` 提供「阅读 + 听书」模式;只有遵守本规则的内容才能被正确过滤、朗读与朗读高亮。  
> **目标读者**:撰写新报告的作者(Claude 或人类)  
> **关联**:[PRD-reader-mode.md](../docs/PRD-reader-mode.md) · 重点 Section 7.4 / 7.5  
> **修订**:每次新增 callout / 块级容器 / 装饰元素,必须同步更新本文件

---

## 0. 一句话核心约定

> **正文用语义化 HTML 写,装饰用 `<svg>` / `<table>` / `.hero` / `.sticky-nav` 隔离,callout 走指定 class 系列。其余结构都不会被朗读,不需自己实现"听书友好版"。**

记住三件事:

1. **阅读模式只朗读"白名单"里的东西**(`h2`/`h3`/`h4`/`p`/`li`/`blockquote` + 指定 callout)。其它一律不读、不显示。
2. **装饰、导航、表格、SVG 默认全部隐藏**,你不需要做任何额外标注就能跳过 —— 但前提是你**用对了标签**。
3. **关键数字 / 反共识 / 协议**必须冗余写一份在 `<p>` 里。SVG 文字、表格行不会进朗读队列,听众只能听到 `<p>` 那份。

---

## 1. 阅读模式 EXCLUDE 黑名单(权威清单)

以下 selector 在阅读模式下**不显示 + 不朗读**。写报告时,任何不希望被朗读的内容都应该归到这些容器里:

```js
// 来源:_shared/reader.js · 7.4
EXCLUDE_SELECTORS = [
  // 视觉装饰
  'svg', 'svg *',                                  // SVG 及其内部 <text>/<tspan> 全部隐藏
  '.hero', '.hero-keypoints', '.hero-toc-section', // 章首封面与要点条
  '.number-strip', '.section-tag',                  // 数据条 / 章节标签

  // 导航 / 控制
  '.sticky-nav', '.mini-toc', '.progress-bar',

  // 表格(自动占位,提示"此处有表格,点击查看原文")
  'table',

  // 元信息
  'script', 'style',
  '.ref',                                          // 参考文献行
  '.chip',                                         // 标签芯片

  // SVG 容器(含 caption)
  '.svg-frame', '.svg-caption',
];
```

**含义**:写新组件时,如果它属于"装饰"或"元信息",**必须**用上述 class 之一(或包在 `.svg-frame` / `<svg>` / `<table>` 里)。否则它会进入朗读队列,造成"读出 FIG 4.2 三大供能系统功率峰值"这类断裂体验。

---

## 2. 阅读模式 INCLUDE 白名单(会被朗读)

```js
INCLUDE_TAGS = ['h2', 'h3', 'h4', 'p', 'li', 'blockquote'];

INCLUDE_CALLOUT_TYPES = [
  'plain',     // 白话翻译  → TTS 直接朗读三段式
  'sharp',     // 反共识    → TTS 加前缀"反共识。"
  'ops',       // 实操含义  → TTS 加前缀"实操含义。"
  'you',       // 第二人称剧本
  'protocol',  // 章末协议  → TTS 编号化朗读
  'story',     // 章首故事
  'note',      // 旁注
];
```

正文里**任何**想被听到的内容,都必须长在这些标签 / 容器里。挂在其它容器(`<div>`、`<span>`、`<aside>`、`<figure>` 的 caption 等)里的文字,听众听不到。

---

## 3. 五条核心写作规则

### 规则 1 · 章节层级统一用 `h3` / `h4`,不要跳级

阅读模式靠 `h3` 切章节,靠 `h4` 切小节;跳级会让"章节跳转"下拉乱、TTS 在错误位置加停顿。

GOOD:
```html
<h3><span class="pre">4.4</span>乳酸真相——把它当燃料,不要当废物</h3>
<p class="lead">...</p>
<h4>乳酸穿梭 Lactate Shuttle</h4>
<p>...</p>
```

BAD:
```html
<h2>乳酸真相</h2>          <!-- ❌ 跳级:章节级别错位 -->
<h5>乳酸穿梭</h5>           <!-- ❌ 跳级:无法被识别为子小节 -->
<p class="big-title">乳酸真相</p>   <!-- ❌ 用样式假装标题 -->
```

### 规则 2 · 装饰性图表**必须**包在 `<svg>` 或 `.svg-frame` 里

✅ 鼓励:用 inline `<svg>` 画一切可视化(供能曲线、Crossover Concept、心率-配速对照)。  
⚠️ 注意:`<svg>` 内的 `<text>` 也会被一起过滤,所以 SVG 上的关键数字必须在正文 `<p>` 里再写一份。  
❌ 避免:用 `<img alt="...">` 装关键文字 —— TTS 不会读 alt;用 `<div class="chart">...文字...</div>` 假装图表 —— 这些文字会被朗读出来,变成数字洪流。

GOOD:
```html
<div class="svg-frame">
  <svg viewBox="0 0 1080 380" xmlns="http://www.w3.org/2000/svg">
    <text x="540" y="200">50% VO2max</text>   <!-- 装饰,会被跳过 -->
  </svg>
  <div class="svg-caption">FIG 4.2 · SUBSTRATE UTILIZATION × INTENSITY</div>
</div>
<p>Crossover 点约在 <strong>50% VO2max</strong>——这是脂肪和糖供能反转的临界。</p>
<!-- 听众只听到上面这一段;SVG 里的标签都被跳过 -->
```

BAD:
```html
<div class="chart-card">
  <div class="big-number">50%</div>          <!-- ❌ 会被朗读为"百分之五十" -->
  <div class="label">VO2max</div>             <!-- ❌ 会读"VO2max" -->
</div>
<!-- 数字脱离上下文,听众一头雾水 -->
```

### 规则 3 · 数据表用 `<table>`,关键洞察**冗余**写一段 `<p>`

阅读模式会把整张 `<table>` 隐藏并替换为"▸ 此处有表格,点击查看原文"占位。听众**不会**听到任何表格内容 —— 包括表头、表格行。

✅ 鼓励:用 `<table>` 表达结构化对照数据(底物 × 储量 × 能量密度)。  
⚠️ 注意:如果表里有不可替代的关键发现,必须在表前后写一段 `<p>` 把核心结论说出来。  
❌ 避免:把唯一的关键洞察藏在表里,正文不提。

GOOD:
```html
<p class="lead">把"三系统耦合"翻译成具体配速,你会看到:<strong>5K 以上 90% 以上靠有氧氧化,马拉松更是 98%。</strong></p>
<table>
  <thead><tr><th>项目</th><th>磷酸原</th><th>糖酵解</th><th>有氧</th></tr></thead>
  <tbody><tr><td>100m</td><td>80%</td><td>15%</td><td>5%</td></tr>...</tbody>
</table>
<p>留意 5K 这一行:你已经几乎不在烧糖酵解了——所以训练 5K 的核心是<em>有氧上限</em>,不是冲刺。</p>
```

BAD:
```html
<h4>各项目供能分布</h4>
<table>...12 行数据...</table>     <!-- ❌ 表格被隐藏后,听众只听到"此处有表格" -->
<h3>4.4 下一节</h3>
```

### 规则 4 · 公式 / 缩写 / 希腊字母**必须**配 `.plain` 白话翻译

`.plain` 是 v4 报告的招牌组件;它本身就是"对听觉友好的人类语言版"。阅读模式不做额外处理,但你写得规范,TTS 就能正确读出三段式("原理-翻译-放在跑步场景")。

✅ 鼓励:任何公式、英文缩写、希腊字母、生僻术语首次出现,都补一个 `<p class="plain">原理...<strong>翻译:</strong>...<em>放在跑步场景:</em>...</p>`。  
⚠️ 注意:中文里如果有 `α-actinin-3` 这类拉丁化术语,在 `.plain` 里给它一个中文音译加描述。  
❌ 避免:留一堆 `VO2max`、`MCT1`、`LT2` 不解释 —— TTS 会逐字母念出"V-O-2-max",听感极差。

GOOD:
```html
<p>Fick 方程是耐力科学的总公式:VO2 = Q × (a-vO2 diff)。</p>
<p class="plain">原理:Fick 方程 VO2 = Q × (a-vO2 diff) = SV × HR × (a-vO2 diff)。<strong>翻译:</strong>身体一分钟用多少氧 = 心脏一分钟泵多少血(Q)× 每升血肌肉能扒走多少氧。Q 又拆成"每次跳泵多少血"(SV)× "每分钟跳多少下"(HR)。<em>放在跑步场景:</em>HIIT 把 SV 撑大,Z2 跑把"扒氧能力"撑大,两种练法各管一半。</p>
```

BAD:
```html
<p>Fick: VO2 = Q × (a-vO2 diff) = SV × HR × ΔaO2.</p>
<p>因此 HIIT 提高 SV,Z2 提高 ΔaO2,两者协同推 VO2max。</p>
<!-- ❌ TTS 读"V-O-2 等于 Q 乘以 a-v-O-2 差",听众完全听不懂 -->
```

### 规则 5 · 反共识用 `.callout.sharp`,协议清单用 `.callout.protocol`

TTS 会对这两类 callout 做语义增强 —— `.sharp` 自动加"反共识。"前缀 + 0.4s 停顿,`.protocol` 会把内部 `<ol>` 编号化朗读(协议一、第一步…),这是 Chrome 阅读模式做不到的差异化。

✅ 鼓励:每章 1-3 个 `.sharp` 标注反共识 / 误区纠正;章末固定 1 个 `.protocol` 收尾可落地训练方案。  
⚠️ 注意:`.sharp` 内不要嵌套图表 / 表格 —— callout 只走"标题 + 段落"结构,嵌套会破坏 TTS 节奏。  
❌ 避免:用 `<blockquote>` 或 `<aside>` 假装反共识;阅读模式不会给它们加语义前缀。

GOOD:
```html
<div class="callout sharp">
  <div class="label">反共识 / 乳酸不是疲劳元凶</div>
  <p>George Brooks 在 1980–2000 年代连续多项同位素示踪研究证实:<em>乳酸是糖酵解的正常中间产物</em>。心肌摄取乳酸为燃料的比例占其总底物的 25–40%——它是燃料,不是废物。</p>
</div>
<!-- TTS 朗读为:"反共识。乳酸不是疲劳元凶。George Brooks 在..." -->

<div class="callout protocol">
  <div class="label">PROTOCOL · 本章关键操作清单</div>
  <h4>协议 1 · Cooper 12 分钟测试推 VO2max</h4>
  <ol>
    <li><strong>测什么:</strong>12 分钟全力跑的距离</li>
    <li><strong>工具:</strong>跑表 + 400m 跑道</li>
    <li><strong>步骤:</strong>热身 10 min → 全力均速 12 分钟 → 记录距离</li>
  </ol>
</div>
<!-- TTS 朗读为:"协议清单。协议一,Cooper 12 分钟测试推 VO2max。第一步,测什么:..." -->
```

BAD:
```html
<blockquote>
  <p><strong>反共识:</strong>乳酸不是疲劳元凶。</p>
</blockquote>
<!-- ❌ TTS 不会加"反共识。"前缀,听感与普通段落无区别 -->

<div class="callout">                <!-- ❌ 缺 type class -->
  <ol><li>测什么:...</li></ol>
</div>
```

---

## 4. SVG / 表格 / 图片 等特殊元素处理指南

| 元素 | 阅读模式行为 | 写作要点 |
|---|---|---|
| `<svg>` (inline) | 完全隐藏,内部 `<text>`/`<tspan>` 一并跳过 | 关键数字必须在正文 `<p>` 冗余一份;不要把唯一来源放 SVG |
| `<svg>` 包在 `.svg-frame` | 同上 + `.svg-caption` 也隐藏 | 推荐用法,视觉上更整齐 |
| `<table>` | 替换为占位"▸ 此处有表格,点击查看原文",原表不朗读 | 关键发现必须在表前/表后用 `<p>` 复述 |
| `<table>` + `data-summary="..."` | 占位提示 + 把 `data-summary` 内容朗读 | 可选;1-2 句话总结表的核心结论 |
| `<img>` | 完全隐藏,`alt` **不**朗读 | 不要把任何可读文字放 `<img alt>` 里 |
| `<figure><figcaption>` | `<figure>` 内的 `<svg>` 隐藏,`<figcaption>` 走 `<p>` 规则会被朗读 | 想跳过 caption,把它包成 `.svg-caption` |
| `.hero` / `.hero-keypoints` | 完全隐藏(章首封面、数据条) | 关键数字另外在第一段 `<p>` 写出 |
| `.sticky-nav` / `.mini-toc` / `.progress-bar` | 完全隐藏 | 这些是阅读时的导航辅助,听书时无意义 |
| `.ref`(参考文献行) | 完全隐藏 | 写作时就用 `<p class="ref">[Brooks 2018]...</p>` 包起来,自动跳过 |
| `.chip`(标签芯片) | 完全隐藏 | 装饰性标签放这里 |
| `<code>` / `<pre>` | 当前默认朗读,但实测听感差 | 短代码段建议放 `.svg-frame` 视觉容器或单独成 `<pre class="no-tts">`(预留 hook) |

### `data-summary` 用法(给 TTS 一句话表格摘要,可选)

```html
<table data-summary="底物对照:碳水 4 kcal/g 但储量小,脂肪 9 kcal/g 储量近无限,酮体应急,蛋白质少量参与。">
  <thead>...</thead>
  <tbody>...</tbody>
</table>
<!-- 阅读模式:占位提示"▸ 此处有表格,点击查看原文" + 朗读 data-summary 内容 -->
```

不写 `data-summary` 时,占位文字依然显示,只是 TTS 跳过该位置。

---

## 5. TTS 友好的内容写作技巧

### 5.1 段落分隔 · 给 TTS 自然停顿

✅ 鼓励:一段一个意思,80-200 字;数字密集段拆短句、加句号。  
⚠️ 注意:中文逗号 `,` 触发短停顿,句号 `。` 触发长停顿,破折号 `——` 几乎不停顿。  
❌ 避免:一句话 300 字、十个分号串起来 —— TTS 会一口气念完,听众喘不过气。

GOOD:
```html
<p>VO2max 是发动机大小,LT2 是发动机能用多大比例,RE 是发动机的油耗。三个变量都可训练。HIIT 拉 VO2max。LSD 拉 LT2。力量训练拉 RE。</p>
```

BAD:
```html
<p>VO2max 是发动机大小 LT2 是发动机能用多大比例 RE 是发动机的油耗 三个变量都可训练而 HIIT 拉 VO2max 而 LSD 拉 LT2 而力量训练拉 RE.</p>
<!-- ❌ 没有句号,TTS 一口气读完,听众无法捕捉关键 -->
```

### 5.2 数字读法 · 写成 TTS 能正确朗读的形式

| 写法 | TTS 朗读 | 建议 |
|---|---|---|
| `VO2max` | "V O 二 max" | ✅ 业内通用,首次配 `.plain` 解释 |
| `LT2` | "L T 二" | ✅ 同上 |
| `5K` | "五 K" | ⚠️ 改写为 "5 公里" 更清晰 |
| `2 mmol/L` | "二 毫摩尔每升"(部分浏览器读字符) | ✅ 可接受 |
| `9 mmol/kg/s` | 易读错为"九毫摩尔克秒" | ✅ 建议 `<p class="plain">` 里改写为"每公斤每秒 9 毫摩尔" |
| `30.5 kJ/mol` | "三十点五 千焦每摩尔" | ✅ 可接受 |
| `pH 7.0` | "P H 七点零" | ✅ 业内通用 |
| `α-actinin-3` | "阿尔法 actinin 三"(Safari 读不出 α) | ⚠️ 首次配中文 "阿尔法肌动蛋白3" |

### 5.3 英文缩写 · 首次出现配中文全称

GOOD:
```html
<p>VO2max(最大摄氧量)反映心肺供氧上限。LT2(乳酸阈)反映糖酵解贡献上限。RE(跑步经济性)反映同样耗氧能跑多快。</p>
```

BAD:
```html
<p>VO2max 反映心肺,LT2 反映糖酵解,RE 反映经济性。</p>
<!-- ❌ 缩写没解释,听众只能听到一串字母 -->
```

### 5.4 希腊字母 / 特殊符号 · 配文字描述

| 符号 | 直接朗读 | 建议写法 |
|---|---|---|
| `α` | "alpha" 或读不出 | "阿尔法 (α)" |
| `β` | "beta" 或读不出 | "贝塔 (β)" |
| `Δ` | "delta" 或读不出 | "delta(Δ,变化量)" |
| `μ` | "mu" 或读不出 | "微 (μ)" |
| `O₂` | "O 二" 或 "O 下标二" | "氧气 O₂" |
| `H⁺` | "H 加" | "氢离子 H⁺" |
| `→` | 部分浏览器读"指向" | 改写为"产生"或"转化为" |

### 5.5 反共识 / 协议 · 用 callout 让 TTS 加语义提示

`.callout.sharp` → TTS 朗读时自动加 **"反共识。"** 前缀 + 0.4s 停顿  
`.callout.protocol` → 内部 `<ol>` 编号化朗读("第一步…第二步…")  
`.callout.ops` → 自动加 **"实操含义。"** 前缀  
`.callout.you` → 自动加 **"第二人称剧本。"** 前缀  

这是听书模式相对于 Chrome 阅读模式的核心差异化 —— **写作时就要把语义打包好**,让 TTS 引擎自动用。

---

## 6. 兼容性自检清单 · 写完报告跑一遍

每写完一份新报告,**逐项**对照:

```
结构层
[ ] 所有装饰图都包在 <svg> 标签或 .svg-frame 容器里(自动隐藏)
[ ] 所有数据表都用 <table>(自动隐藏 → 占位提示)
[ ] 表格如有关键洞察,前后有 <p> 复述
[ ] 没有用 <div class="..."> 或 <span class="..."> 把正文藏进 SVG 容器
[ ] 没有用 <img alt="..."> 装关键文字
[ ] 章节标题统一用 h3,小节用 h4,正文用 p
[ ] 章首封面包在 .hero / .hero-keypoints 里(自动隐藏)
[ ] 参考文献用 <p class="ref">...</p>(自动隐藏)
[ ] 没有 .sticky-nav / .mini-toc / .progress-bar 之外的导航元素混入正文

语义层
[ ] 每个公式 / 英文缩写 / 希腊字母 首次出现都配 .plain 白话翻译
[ ] 反共识用 .callout.sharp(不是 blockquote / aside)
[ ] 实操含义用 .callout.ops
[ ] 第二人称剧本用 .callout.you
[ ] 章末协议用 .callout.protocol,内部用 <ol> 列步骤
[ ] 旁注用 .callout.note
[ ] 章首故事用 .callout.story

冗余层
[ ] 关键数字同时出现在 <svg> 和正文 <p> 里
[ ] 表格关键发现在表前或表后 <p> 里复述了
[ ] 缩写第一次配中文全称
[ ] 希腊字母配文字描述

实测层
[ ] 在桌面 Chrome 打开报告,点右下角 ▶ 进入阅读模式,无 SVG/表格/导航
[ ] 点 ⏸ 朗读 5-10 段:无奇怪字符乱读 / 无英文字母堆 / 无数字洪流
[ ] 滚到 callout.sharp,TTS 听到 "反共识。"前缀
[ ] 滚到 callout.protocol,TTS 听到 "第一步…第二步…"编号
[ ] 手机 Safari 打开,全屏阅读模式正常,无横向滚动
```

---

## 7. 常见陷阱 · 失败案例集

| 陷阱 | 表现 | 修复 |
|---|---|---|
| SVG 里写文字,正文不复述 | 听众听到下一段时没有上下文,关键数字丢失 | 关键数字在 SVG 之前/之后的 `<p>` 写一份 |
| 用 `<div class="big-number">42</div>` 做装饰数字 | TTS 朗读为"四十二",脱离上下文 | 包在 `<svg>` 或 `.hero` 里;数字在正文段落里写完整句 |
| 章末协议用 `<ul>` 而非 `<ol>` | TTS 不会编号化朗读 | 改成 `<ol>`,TTS 自动读"第一步" |
| 反共识用 `<p><strong>反共识:</strong>...</p>` | 没有语义前缀,TTS 听感与普通段落无区别 | 改成 `<div class="callout sharp">` |
| 大量参考文献塞在正文 `<p>` 里 | TTS 念出一长串作者名年份,体验崩 | 包成 `<p class="ref">...</p>`,自动隐藏 |
| 在 `<table>` 里放唯一的反共识洞察 | 听众完全听不到 —— 表格被隐藏 | 同时在 `<p>` 写一段,或 `.callout.sharp` 包一份 |
| 用 `<h2>` 当小节标题 | 章节级别错位 → "章节跳转"下拉异常 | 章用 `h3`,小节用 `h4`,内部点用 `<p><strong>`  |
| 用 `<img src="formula.png">` 显示公式 | TTS 无法朗读,听众完全错过 | 公式用 LaTeX 数学符号 / 文本写出,配 `.plain` 翻译 |
| 在 callout 内嵌套表格或 SVG | TTS 节奏被打断,callout 半截截断 | callout 只放 `<h4>` + `<p>` + `<ol>` / `<ul>`;图表放 callout 之外 |
| 中文用全角弯引号 `"..."` 包关键术语 | 部分 TTS 引擎读"引号 XXX 引号" | 用书名号《》或直角引号「」,或直接去掉引号 |

---

## 8. 一句话总结

> **写报告就像写听众也在场的脚本。任何只在 SVG / 表格 / 装饰里出现的内容,默认听众听不到;关键内容必须冗余进 `<p>` 或指定 callout。**

剩下的过滤、增强、朗读节奏,共享组件 `_shared/reader.{js,css}` 全部自动处理 —— 你只需要遵守上面 5 条规则 + 跑通自检清单。

---

**End of READER_RULES v1.0**
