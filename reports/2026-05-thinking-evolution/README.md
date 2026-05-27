# 思考进化

一比一克隆自 [uxlaws.wwei.ai](https://uxlaws.wwei.ai)（《用户体验之书》），作为后续改造为"思考进化"主题手册的起点。

当前是**原版镜像**：文案、数据、视觉全是 UX 主题。主题改造留到下一步。

## 文件结构

```
.
├── index.html              # 单页应用壳：HTML + 内联 CSS + 内联 JS（约 940 行）
├── cards.v0.1.json         # 第一部 · 理论卡片  (162 张)
├── companies.v0.1.json     # 第二部 · 大厂工作流 (22 家)
├── paradigm.json           # 第三部 · AI 范式迁移
├── figures.v0.1.json       # 配图库  (189 个 SVG/图片)
├── unsplash.v0.1.json      # Hero 照片 (50 张)
├── icon.svg                # 站点 icon / 苹果触屏图标 / OG 缩略图
└── README.md
```

## 本地启动

JSON 是用 `fetch()` 加载的，必须走 HTTP，不能直接 `file://` 打开。

```bash
python3 -m http.server 8765 --directory "/Users/baixiao/白笑/claude/思考进化"
# 浏览器打开 http://127.0.0.1:8765/
```

任意 HTTP 服务都行（`npx serve`、`caddy`、Nginx 等等）。

## 改造入口（按改动量从小到大）

| 想改什么 | 改哪里 |
|----------|--------|
| 封面文案、Tab 名、页脚版权 | `index.html` 内 `<header class="cover">`、`<nav class="tabs">`、`<footer>` |
| 配色（藏青/金色） | `index.html` 顶部 `:root { --navy, --gold, --cream ... }` |
| 字体 | `index.html` 第 17-19 行的 Google Fonts `<link>` + body `font-family` |
| 162 张卡片内容 | `cards.v0.1.json`（数组，每条 schema 见原文件首条） |
| 22 家公司内容 | `companies.v0.1.json` |
| 范式迁移 4 节 | `paradigm.json` |
| Tab 数量/字段结构 | `index.html` 内 `renderTheory/renderCorps/renderParadigm` 函数 |
| 卡片抽屉里的 section 图标 | `index.html` 内 `const ICONS = {...}` |

## JSON Schema 速查

完整 schema 直接读 JSON 第 1 条记录最快。常用字段：

**cards.v0.1.json** — 每张卡片
- `id`, `category`, `name_cn`, `name_en`, `aliases`, `originator`, `year`
- `one_liner`, `principle`, `formula`, `key_points[]`, `use_when[]`
- `examples[{context, description}]`, `pitfalls[]`, `related_ids[]`
- `sources[{title, author, url, type}]`, `tags[]`, `in_training`, `difficulty`

**companies.v0.1.json** — 每家公司
- `id`, `company_cn`, `company_en`, `region`, `industry`, `founded`
- `design_system{name, url, version, open_source}`, `summary`
- `design_philosophy[]`, `design_org{size, structure, key_people[]}`
- `classic_workflow{stages[], signature_practice}`
- `ai_era_evolution{process_changes[], internal_ai_tools[], role_changes[], new_artifacts[]}`
- `still_in_use[]`, `deprecated_or_replaced[]`, `signature_projects[]`
- `cultural_motto[]`, `lessons_for_others[]`, `controversies[]`, `must_read[]`

**paradigm.json** — 单 object
- `title`, `subtitle`, `tldr`, `framing{thesis, implication}`
- `sections[{id, title, intro, items[]}]` — `id` 取值：`still-canon` / `upgraded` / `deprecated` / `emerging`
- `matrix[{domain, before_ai, after_ai, verdict}]`
- `key_quotes[]`, `advice_for_chinese_designers[]`, `must_read[]`

## 已做的清理

相对原站删除了一行 `<script src="https://auth.wwei.ai/widget.js">`（原站自己的认证脚本，跟项目无关）。其余文案/字段/版权暂未动。

## 来源

- 原项目：<https://uxlaws.wwei.ai/>
- 编纂：千图网 Wayne
- 抓取时间：2026-05-22
