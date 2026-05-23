# Reader Design System v1.0

> 为「阅读 + 听书」共享组件的所有 UI 元素定义统一规范。任何后续修改/扩展都必须遵守这份规范,避免视觉割裂。  
> **建立**:2026-05-23 · v5.2 重构同期  
> **生效范围**:`_shared/reader.{css,js}` 全部元素

---

## 0. 设计原则

```
1. 内容优先     · UI 元素永远不能比正文显眼
2. 一次理解     · 用户看一眼就明白这个按钮是干啥的
3. 三层精简     · 主操作 → 次操作 → 设置(三个层级,不能再多)
4. 跨平台一致   · 桌面 + 手机 共享代码,差异只在尺寸不在结构
5. 可测可量     · 所有尺寸、间距、颜色都有数值,不靠"觉得差不多"
```

---

## 1. 颜色系统(每个主题相同结构,不同变量值)

### 三主题 CSS Variables(对照表)

| 角色 | --r-bg(底) | --r-ink(墨) | --r-accent(强调) | --r-btn-bg(按钮底) |
|---|---|---|---|---|
| paper(米黄) | #f0ebdd | #1a1a1a | #a8423b | rgba(26,26,26,.06) |
| dark(暗灰) | #1f1f1b | #e8e2d0 | #e8a85c | rgba(232,226,208,.08) |
| green(暗绿) | #1c2e1f | #deead3 | #95c878 | rgba(222,234,211,.08) |

### 使用规则

```
正文文字          var(--r-ink)
段落高亮背景      var(--r-highlight-bg) = accent @ 10% alpha
主播放按钮        bg: var(--r-accent), color: var(--r-bg)
次级按钮          bg: var(--r-btn-bg), color: var(--r-ink)
选中态(任何控件)  bg: var(--r-accent), color: var(--r-bg)
边框              1px solid var(--r-line-soft)
分隔线            1px solid var(--r-line)
```

**禁止**:在任何元素上写死颜色值。所有颜色必须通过 `var(--r-*)` 引用。

---

## 2. 尺寸系统(8px 网格)

### 间距 token

```
--space-1: 4px    ── 同组按钮之间
--space-2: 8px    ── 跨组按钮之间
--space-3: 12px   ── 控制条内边距
--space-4: 16px   ── Section 内边距
--space-5: 24px   ── Section 间距
```

### 元素高度

```
按钮 / select       36px         ── 桌面通用
主播放按钮          44px         ── 桌面强调
按钮 / select 移动  38-40px      ── 手机拇指目标
主播放按钮 移动     42px
控制条总高          52px(桌面)/ 56px(移动)
Sheet 弹出最大高    80vh
Mini Player        56px
```

### 圆角 token

```
--radius-1: 4px    ── 内部小元素(如 protocol .stop block)
--radius-2: 6px    ── 一般按钮 / select / 占位卡片
--radius-3: 8px    ── 控制条容器 / Sheet 顶部 (16px)
--radius-4: 18px   ── Pill 按钮(Sheet 里的选项)
--radius-full      ── 圆形按钮(主播放 / 主题色块)
```

**规则**:同一控制条内所有按钮必须用同一档圆角(通常 `--radius-2: 6px`),避免视觉不齐。

---

## 3. 字体系统

```
正文              "PingFang SC", "Hiragino Sans GB", sans-serif
正文中文 fallback  Microsoft YaHei
标题              "Inter Tight", "PingFang SC", sans-serif · 700-900
数字 / 等宽       "JetBrains Mono", monospace
UI 控件           inherit(从父继承)+ font-weight 调节
```

### UI 字号

```
控制条按钮文字    13px(数字) / 14px(汉字)
Sheet 选项        14.5px
Sheet 标签        14px(left-side) / 12-13px(right pill)
Mini Player 标题  12.5px
iOS Toast        12.5px
```

**禁止**:在控件里混用衬线/无衬线/等宽字体。一组按钮内字体必须一致。

---

## 4. 控件规格(按重要性排序)

### A · 主播放按钮(只有 1 个)

```
桌面: 44×44px, --radius-full, bg=accent, color=bg, font-size=16px
移动: 42×42px(同上)
图标: ▶ / ⏸  (Unicode 三角 / 双竖线)
状态: hover 透明度 0.88,active scale 0.96
```

### B · 上下段按钮(2 个,prev/next)

```
所有尺寸: 36×36px(桌面)/ 38×38px(移动)
bg=btn-bg, color=ink, radius=6px
图标: ◀ (Unicode left triangle) / ▶| (right triangle + bar)
```

### C · 倍速 / 章节 / 音色(select dropdown)

```
高度: 36px(桌面)/ 38px(移动)
内边距: 8px 24px 8px 12px (右留 ▾ 指示器空间)
背景: btn-bg
文字: mono 13px
箭头: ▾ 绝对定位右侧 10px 处
固定宽度: 倍速 70px, 章节 180px, 音色 130px
不允许换行
```

### D · 字号 A-/A+ 按钮(各 1 个)

```
尺寸: 36×36px
等宽字体,字号 13px
显示文本: "A-" / "A+"
```

### E · 行距按钮(1 个)

```
尺寸: 36×36px
显示: 三横线图标 ☰(Unicode)
hover/active: 加深 btn-bg
```

### F · 主题切换(三色块容器)

```
容器: padding 3px, bg=btn-bg, radius=6px
单个色块: 28×28px(桌面)/ 32×32px(Sheet 内圆形)
桌面控制条版: 方形 radius-2
Sheet 内版: 圆形 radius-full
选中态: 1.5px solid var(--r-accent) 内边框 + box-shadow 双层环
```

### G · 设置 / 关闭(各 1 个)

```
尺寸: 36×36px
设置 ⚙: 桌面 display: none(永久),仅移动端入口
关闭 ✕: 透明背景,hover 加 btn-bg
图标用 Unicode 字符,字号 16px
```

### H · 闹钟/Sleep(桌面控制条,移动端进 Sheet)

```
桌面: 36×36px 按钮 + 点击弹出菜单
菜单: position: fixed,以按钮位置为锚点用 JS 计算
菜单内选项: 36px 高,8px 12px 内边距,hover bg-btn,选中态 accent bg
移动端: 不在控制条出现,只在 Sheet 内的"定时"行
```

**重要**: 桌面控制条上的 ⏰ 必须用 fixed 定位的菜单,不能用 absolute(会被 sticky 控制条的 overflow 裁切)。

---

## 5. 布局规格

### 桌面控制条(viewport ≥ 769px)

```
高度: 52px
横向布局,从左到右:
  [组1] prev | play | next       ── 主操作
  [组2] 倍速                      ── 速度
  [组3] 章节 select               ── 内容跳转
  [组4] A- | A+ | 行距            ── 字号 / 行距
  [组5] 主题色块容器              ── 主题
  [组6] 音色 select               ── 音色
  [组7] 闹钟                      ── 定时
  [spacer 1fr]
  [组8] 关闭                      ── 退出

组内 gap: 4px
跨组 gap: 6px(由 group + spacer 自然产生)
不允许换行,横向滚动 hidden
```

### 移动控制条(viewport ≤ 768px)

```
高度: 56px (含 safe-area-inset-bottom)
固定底部,只显示 4 个核心控件:
  prev | play | next       ── 主操作
  倍速                     ── 速度
  设置 ⚙                  ── 进入 Sheet 看其他
  关闭 ✕                  ── 退出

其他控件全部移到 Sheet 内
Sheet 弹出从底部,圆角 16px 顶部
```

### Sheet 内容(只在移动端使用)

```
顶部:小拖动 handle(纯装饰)
然后是行,每行:
  左:标签(14.5px)
  右:控件(pill 按钮组 / select / theme circles)
  
行间分隔: 1px solid var(--r-line-soft)
行内边距: 14px 22px

顺序:
1. 章节(select)
2. 主题(3 个圆环)
3. 字号(S/M/L/XL pill)
4. 行距(紧/中/松 pill)
5. 音色(select,可隐藏 if 无系统中文 TTS)
6. 定时(关闭/5/10/15/30/60/本章末 pill)
7. 章末自动接下章(开启/关闭 pill toggle)
```

---

## 6. 选中态规范

### 通用规则

```
所有"被选中"的按钮:
  background: var(--r-accent)
  color: var(--r-bg)
  font-weight: 600(数字字体保持原 weight)
  无边框,无阴影
```

### 例外:主题色块圆环

```
主题色块的"选中态"是特殊的,因为它本身就显示颜色:
  border: 2.5px solid var(--r-accent)
  box-shadow: 0 0 0 2px var(--r-bg), 0 0 0 4px var(--r-accent)
  双层环视觉
```

---

## 7. 图标规则

### 必须用 Unicode 字符(不用 emoji)

| 含义 | 字符 | 备注 |
|---|---|---|
| 播放 | ▶ | U+25B6 |
| 暂停 | ⏸ | U+23F8 |
| 上一段 | ◀ | U+25C0 |
| 下一段 | ▶\| | 三角 + 竖线 |
| 字号减 | A- | 字母组合 |
| 字号加 | A+ | 字母组合 |
| 行距 | ☰ | U+2630 |
| 关闭 | ✕ | U+2715(不用 × 乘号) |
| 设置 | ⚙ | U+2699(只移动端) |
| 闹钟/定时 | ⏱ | U+23F1 秒表(不用 ⏰ 闹钟,更克制) |
| 主题色 | (色块) | 无图标,色显示 |
| Mini Player ⌃ | ⌃ | U+2303 上箭头(展开) |

**禁止**:🎧 ⏰ 这类颜色 emoji,因为它们在不同系统字体下渲染差异巨大。

---

## 8. 动效规则

```
过渡时长:
  快速(按钮 hover / active):150-180ms
  中等(主题切换 / 主题色变化):220ms
  慢速(Sheet 弹起 / Overlay fade):280-320ms

缓动函数:
  通用: ease(默认)
  弹出: cubic-bezier(.22, .61, .36, 1)
  退场: ease-out

不允许:
  spring / overshoot 动效(过于 playful,不符合阅读器调性)
  > 320ms 的过渡(感觉慢)
```

---

## 9. 焦点状态(键盘可访问)

```
所有 button / select / [tabindex]:
  outline: 2px solid var(--r-accent)
  outline-offset: 2px
  outline-style: dashed(避免与选中态混淆)
```

---

## 10. 验收清单

任何新加 / 修改的 UI 元素,必须通过以下检查:

```
□ 颜色是否全部用 var(--r-*),没有硬编码值?
□ 圆角是否符合该控件应用的 --radius-* token?
□ 高度是否是 36/38/42/44px 之一(主播放按钮才能 44)?
□ 字体是否符合 §3 规则,没混用?
□ 选中态是否用 §6 规范?
□ 图标是否用 Unicode 字符(§7)?
□ 桌面 / 移动 / Sheet 三种容器都测试过?
□ 三主题(paper/dark/green)都视觉 OK?
□ 键盘 Tab 焦点态有效?
□ Sheet 弹出不挡核心内容?
```

---

**End of Reader Design System v1.0**
