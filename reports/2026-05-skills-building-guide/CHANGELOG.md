# Changelog · Skills Building Guide

> 记录中文化笔记的版本演进。版本号规则见 [../../CONVENTIONS.md](../../CONVENTIONS.md)。

---

## v0.3 · 单文件 SPA · 全 7 章 + 3 附录补齐（2026-05-27）

### 重构：从多文件改为单文件 SPA

**动因**：v0.2 是「首页 + 每章一个 HTML」的多文件结构，加上 6 章 + 3 附录后会有 8~10 个文件，管理负担太重。

**做法**：
- 所有 7 个 section（首页 + 6 章）合并到单一 `index.html`
- 每个 section 一个 `data-route` 属性，JS 根据 `location.hash` 控制显示
- 首页章节卡链接 `<a href="#chN" target="_blank">` → 浏览器新开标签页打开对应章节
- 子锚点（如 `#ch1-progressive`）也支持，自动定位到该小节
- `<title>` 根据当前 section 自动更新
- 旧的 `ch1-fundamentals.html` 改为自动重定向页面，可手动 rm 删除（sandbox 无权限）

### 新增：ch2 ~ ch6 五章 + 三个附录完整对照

按 v0.2 确定的 C 路线（英文原文 + 中文导读）写完：

- **ch2 · Planning and Design** · 8 小节：用例先行、三大类别（文档创作 / 流程自动化 / MCP 增强）、成功指标、技术规范、YAML frontmatter 全字段、description 好坏例对照、主指令结构模板、写指令 4 条原则
- **ch3 · Testing and Iteration** · 7 小节：三层测试方法、Pro Tip、触发/功能/性能对比测试、skill-creator 用法、迭代信号反馈（欠触发/过触发/执行问题）
- **ch4 · Distribution and Sharing** · 5 小节：现行分发模型、Agent Skills 开放标准、API 用法对照表、GitHub 推荐做法、定位话术原则
- **ch5 · Patterns and Troubleshooting** · 11 小节：Problem-first vs Tool-first、5 种 Pattern 完整代码骨架、5 类排错（上传/触发/MCP/指令/上下文）
- **ch6 · Resources + 3 Appendices** · 官方文档/博客/仓库索引 + Appendix A 自检表 + Appendix B YAML 完整字段 + Appendix C 完整示例 Skill 索引

### 技术细节

- 总行数 3500+，单文件 ~157KB
- SPA 路由用纯 JS（无依赖）
- 视觉组件复用 v0.2：`.en-orig` / `.cn-gloss` / `.parallel` / `.layer` / `.kitchen` / `.compare-table` / `.pull-quote`
- 每章独立 TOC + 章末 prev/next 跳转

---

## v0.2 · 风格切换到 C 路线 · 英中对照（2026-05-27）

### 重构：从「中文重写」改为「英文原文保留 + 中文注释对照」

**动因**：v0.1 全文中文意译，丢失了原始术语和官方表述。改为 C 路线后：
- 概念性段落、原理说明 → 仍中文导读
- 官方原句、定义、对照表、bullet 列表 → 保留英文原文，加中文注释

**视觉新增**（沿用同一 newsprint 主题）：
- `.en-orig` 英文原文卡（米色底 + 蓝色左边条 + `Original · Anthropic` 小标签）
- `.cn-gloss` 紧跟其后的中文导读（红色左边条 + `中文导读` 小标签）
- `.parallel` 短句英中并列卡
- `.pull-quote` 升级为英文原句 + 中文翻译并列
- 章首新增「阅读约定」三栏说明，让读者一眼区分原文 / 导读 / code

**改动文件**：
- `ch1-fundamentals.html` 完整返工
- `index.html` Hero deck + Introduction + bullet 列表 + Pull quote 全部改对照式

---

## v0.1 · 首页 + 第 1 章样本（2026-05-27）

### 新增：项目初始化

- 归档原英文 PDF 为 `source.pdf`
- **index.html** — 首页索引：报头 + Introduction 精华 + 7 章导航卡片
- **ch1-fundamentals.html** — 第 1 章 · 基础概念中文重写：什么是 Skill / 三层渐进披露 / 可组合性 / 可移植性 / Skills 与 MCP 的关系

### 下一步

等首页和第 1 章风格确认后，继续推进 ch2 ~ ch6。
