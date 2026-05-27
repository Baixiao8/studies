# Skills Building Guide · 中文化对照笔记

> Anthropic 官方《The Complete Guide to Building Skills for Claude》的中文化对照本。
> **不是直译**——概念段用中文重写，官方原句保留，专业名词带中文注释。

- **当前版本**：v0.3
- **最近更新**：2026-05-27
- **入口**：[index.html](./index.html)
- **翻译策略**：C 路线 · 概念中文重写 + 官方原句保留 + 中文注释对照
- **架构**：单文件 SPA + hash 路由（点章节卡新开标签页）

---

## 这个项目是什么

把英文版 33 页指南转成"我能真正读懂"的中文化对照本。

**不是直译，也不是纯重写**——采用 C 路线：
- 概念性段落、原理解释、类比 → 用中文重新组织
- 官方原句、定义、字段表、对照清单 → 保留英文原文，紧跟中文导读
- 代码块、YAML 示例、命令、错误消息 → 保留原文，行内注释中文化

设计风格沿用「运动健康」项目的 newsprint 报纸版式（泛黄纸张 / Inter Tight 大标题 / 朱砂红强调），针对教程体裁做了适配。读者一眼能区分「英文原文」「中文导读」「code 命令」三种内容。

## 架构（v0.3 关键变化）

**所有 7 个章节（首页 + 6 章）现在都在一个 `index.html` 里**。点击首页的章节卡，浏览器会**新开一个标签页**到对应章节（URL 走 `#ch1` `#ch2` 这种 hash）。好处：

- 维护只管一个文件
- 每章一个标签页，互不干扰
- URL 可分享、可加书签
- 刷新不丢位置

## 文件结构

```
skills-building-guide/
├── README.md         # 本文件
├── CHANGELOG.md      # 版本演进
├── source.pdf        # 原始英文 PDF（33 页）
├── index.html        # 全部 7 章的单文件 SPA（首页 + ch1~ch6 + 3 个附录）
└── ch1-fundamentals.html  # ⚠ 已废弃，自动跳转到 index.html#ch1，可手动 rm
```

## 内容覆盖

| Hash | 章节 | 主题 |
|---|---|---|
| `#home` | 首页 | Introduction + 数据带 + 章节导航 + 12 条术语速查 |
| `#ch1` | 第 1 章 · Fundamentals | Skill 是什么、三层渐进披露、可组合可移植、Skills + MCP |
| `#ch2` | 第 2 章 · Planning & Design | 用例先行、三大类别、成功指标、技术规范、YAML frontmatter、description 怎么写、主指令结构、4 条原则 |
| `#ch3` | 第 3 章 · Testing & Iteration | 三层测试方法、Pro Tip、触发/功能/性能对比测试、skill-creator、迭代信号 |
| `#ch4` | 第 4 章 · Distribution & Sharing | 分发模型、Agent Skills 开放标准、API 通路、GitHub 托管、定位话术 |
| `#ch5` | 第 5 章 · Patterns & Troubleshooting | 问题/工具先行、5 种模式、5 类排错 |
| `#ch6` | 第 6 章 · Resources + 附录 | 官方文档/博客/示例仓库/社区 + Appendix A 自检表 + Appendix B YAML 完整字段 + Appendix C 示例 Skill 索引 |

## 本地预览

```bash
cd ~/白笑/claude/报告库/学习思考/skills-building-guide
python3 -m http.server 8765
# 浏览器打开 http://127.0.0.1:8765/
```

也可以直接在 Finder 里双击 `index.html`——所有样式内联、不依赖后端。

## 接下来要做什么

v0.3 已完成全部 7 章 + 3 附录。可能的后续：

- 真实使用中发现表述不清的地方迭代
- 加一个"全文搜索"小工具（Ctrl+F 在单文件里跨 section 不工作）
- 等 Anthropic 出更新版 PDF 后做差异更新
