# Marathon Manual 架构设计

> 本文档记录已确立的设计决策、视觉系统、命名约定。新增内容前必须对照检查。

---

## 一、为什么需要这些规则

这份手册是**单文件 HTML**(`index.html`),没有框架、没有编译检查,所有 CSS / SVG / 内容都在一个文件里。随着 10 章 + 附录的累积,最容易出问题的是:

1. **视觉风格漂移**：颜色 / 字号 / 间距各章自行其是,文档失去整体感
2. **章节结构不一致**：有的章有 TL;DR 有的没有,有的 h3 用「数字+点」有的用 emoji 前缀
3. **资产命名混乱**：`hero1.jpg` vs `s1_hero.jpg` vs `chapter1.jpeg`,引用时找不着
4. **静默文字泄露**：AI 生成图时 prompt 里的 hex code / ALL CAPS 被渲染成画面文字（v2 → v3 的教训）

下面规则从根本上消灭这些问题。

---

## 二、章节结构铁律

### 标准模板

每章 `<section id="sN">` 内必须依次包含:

```
<section id="sN" style="border-top: 4px solid var(--c-XXX);">
  <div class="container">
    <div class="ch-hero">                    ← AI 扉页
      <img src="images/sN_hero.jpg" alt="" loading="lazy">
    </div>
    <div class="section-tag">                ← 章号 + 英文标签
      <span class="num">0N</span>EN-NAME
    </div>
    <h1 class="section-h">                   ← 中文主标 + 英文副标
      章节中文名 <span class="en">English Subtitle</span>
    </h1>
    <p class="section-sub">章节一句话定位</p>
    <div class="tldr">                       ← 全章核心一句话
      <div class="label">TL;DR</div>
      <p>核心论点</p>
    </div>
    <!-- 各 h3 子章节按 X.Y 编号 -->
  </div>
</section>
```

### h3 子章节模板

```
<h3><span class="pre">X.Y</span>子章节中文名</h3>
<p class="lead">子章节开场一句话（可选）</p>
<!-- 内容: param-card / metric-grid / svg-frame / callout / compare-2 等 -->
```

**🚫 禁止**:
- 跳过任意一个标准块（hero / section-tag / section-h / section-sub / tldr）
- h3 用 emoji 前缀代替 `.pre` span
- 同章内编号断号（必须 X.1 / X.2 / X.3 连续）

---

## 三、视觉系统

### 字体（v3.2 后全部苹方）

```css
:root {
  --font-sans: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
               "Source Han Sans SC", "Noto Sans SC", system-ui, sans-serif;
}
```

所有文本(标题、TL;DR、数字、label、code)统一苹方,**用字重 + 字号 + 字距**建立层级,不再用衬线 / 等宽建立差异。

- 大标题: weight 600 · letter-spacing -0.025em
- h3: weight 600 · letter-spacing -0.015em
- 数字 (.num / .m-value): weight 600 · `font-feature-settings: "tnum" 1`（等宽数字）
- Label: weight 500 · letter-spacing 0.18em（用字距营造「tech 标签」感）

### 章节色系（不变）

| 变量 | 色值 | 章节 |
|---|---|---|
| `--c-physio` | `#4a6fa5` 蓝 | §1 生理 |
| `--c-theory` | `#b54848` 红 | §2 训练理论 |
| `--c-session` | `#c47f17` 橙 | §3 课表 |
| `--c-strength` | `#6a8b3d` 绿 | §4 力量 |
| `--c-nutrition` | `#d97a3c` 橙红 | §5 营养 |
| `--c-recovery` | `#3d8b6e` 青 | §6 恢复 |
| `--c-psych` | `#9c4bb5` 紫 | §7 心理 |
| `--c-injury` | `#b56565` 暗红 | §8 伤病 |
| `--c-race` | `#c93f3f` 红 | §9 比赛 |
| `--c-post` | `#5a7fa5` 蓝 | §10 赛后 |

强调色: `--accent` `#d4a548` 金 —— 全文唯一的"重点色"。

### 垂直节奏（v3.1 spacing pass）

8px 网格基准:

- `section` padding: 112px / 80px (mobile)
- `h3` margin-top: 72px (子章节大间距)
- `h4` margin-top: 36px
- `callout` margin: 36px;连排时收紧到 20px
- `svg-frame` margin: 48px

---

## 四、组件库（v3 + v3.3 引入）

### 基础组件
- `.tldr` · 章节核心一句话
- `.callout` 的 5 个变体: `sharp` 红色尖锐结论 / `ops` 绿色操作建议 / `note` 灰色补丁 / `you` 紫色个人数据 / `formula` 灰色公式
- `.zone-bar` · 颜色分段条
- `.svg-frame` + `.svg-caption` · SVG 图容器

### v3 升级组件
- `.chip` · 彩色标签（easy/tempo/interval/long/strength/recovery/race 7 种变体）
- `.status-list` · ✓ ✗ ⚠ 状态列表
- `.metric-grid` + `.metric-card` · 关键数据卡（顶部 3px 章节色条）
- `.compare-2` · 双栏对比矩阵
- `.bar-row` + `.bar` · 进度条
- `.timeline` + `.step` · 时间线
- `.workout-card` · 课表 sparkline 卡

### v3.3 引入（§1.2 样例后批量推广）
- `.param-grid` + `.param-card` · 概念卡（顶部色条 + 缩写 + 中文名 + 定义 + 嵌套数据块 + tip）
- `.formula-box` · 公式可视化（变量分色 .f-var .f-pct .f-num .f-result）
- `.pitfall-grid` + `.pitfall` · 编号坑点卡（错→对对照）

### v4 引入
- `.ch-hero` · 章节顶部 16:9 AI 扉页容器（含底部渐变过渡）

**🚫 禁止**:
- 引入未在 README 列出的新组件类（保持组件库稳定）
- 在 `style="..."` 里写死颜色,必须用 `var(--c-XXX)` / `var(--accent)`

---

## 五、文献引用约定

每个尖锐结论 / 反主流观点后必须有引用:

```html
<span class="ref">(Author Year)</span>
```

约定:
- 单作者: `(Brooks 2018)`
- 双作者: `(Joyner & Coyle 2008)`（用 `&amp;` 转义）
- 多作者: `(Elliott-Sale et al. 2021)`
- 多文献: `(Roberts 2015; Fyfe 2019)`(分号分隔)

`.ref` 自动:
- `font-size: 10.5px` · 灰色 · 等宽数字
- `white-space: nowrap`（不换行）

**🚫 禁止**:
- 编造文献（每条引用必须对应真实存在的研究）
- 不带引用的"研究表明"

---

## 六、AI 图生成约定（v4 引入后定型）

### 风格指令模板（hero_v3.py 之后）

```python
STYLE = (
    "A single cinematic frame. The entire canvas is one continuous visual image, "
    "not a printed page, not a book spread, not a magazine layout, not framed art. "
    "Dark almost-black background fills the frame. The subject is rendered with "
    "thin precise gold line work, with subtle warm crimson accents only where useful. "
    "Minimal and restrained composition, abundant negative space, art-house cinematic atmosphere, "
    "purely visual imagery without written characters anywhere in the scene."
)
```

### 🚫 禁止写进 prompt 的内容

1. **Hex 色号** (`#0e0e0c`, `#d4a548`) → 会被当成画面文字渲染
2. **ALL CAPS 短语** (`EDGE-TO-EDGE`, `NO TEXT`) → 模型把它们当成图中标题
3. **负面命令** (`NO TEXT`, `NO LABELS`, `NO BORDERS`) → 反而触发文字生成
4. **「book / magazine / editorial illustration」** → 模型理解成印刷页面,生成假段落和页码
5. **章节具体英文标题** (`PHYSIOLOGY`, `RACE DAY`) → 会写到画面

### ✅ 正确做法
- 用自然描述: "dark almost-black background" 而不是 "#0e0e0c"
- 用肯定句: "purely visual imagery" 而不是 "no text"
- 用 "single cinematic frame" 而不是 "editorial illustration"

### 命名 + 比例

- 文件名: `sN_hero.jpg` (N = 章号 1-10)
- 比例: 16:9 (model 4714 即梦4.5,`Aspect: 2`)
- 输出尺寸: 经 sips 压缩到长边 1280px / quality normal
- 平均大小: ~70 KB / 张

---

## 七、版本管理

每次大改动后:
1. 当前 `index.html` 先复制到 `archive/manual-vX.html` 留底
2. 改完测试,然后 `git commit -m "vX → vX+1: <改了什么>"`
3. 在 `CHANGELOG.md` 顶部添加版本条目

archive/ 文件命名: `manual-v3.html` / `manual-v3.3.html` / `manual-v4-pre-hero.html`

---

## 八、内容增删铁律

### 增

- 新章节: 必须包含完整的标准块结构（hero / tag / h1 / sub / tldr / 多个 h3）
- 新 h3 子章节: 同章内编号必须连续
- 新组件: 先在本文档 §4 登记,再使用

### 删

- 删整章 → 同时删 `images/sN_hero.jpg`、CSS 里 `--c-XXX` 引用、所有跨章 anchor
- 删 h3 → 同章后续编号顺移

### 改

- 颜色 → 改 `:root` 变量,不在元素 style 里硬编码
- 字号字距 → 改 v3.2 字体 pass 的 :root 定义,不在元素 style 里覆盖

---

*Last updated: 2026-05-21*
