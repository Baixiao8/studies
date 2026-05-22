# 运动健康 · 深度研究报告库

> 一个持续扩张的运动科学研究报告项目。每份报告都是<strong>知识性视角</strong>下对某个具体主题的深度解构——不是手册,不是清单,是研究对象式的全景调查。

---

## 报告列表

| 报告 | 主题 | 状态 | 字数 | 阅读时间 | 链接 |
|---|---|---|---|---|---|
| **2026-05** | 运动学之内 · 跑步的科学解构 | v2 已发布 | ~150K | 4.3h | [reports/2026-05-running-science/index.html](reports/2026-05-running-science/index.html) |
| 2026-06 | (待定) | 规划中 | — | — | — |

---

## 项目结构

```
运动健康/
├── README.md                                ← 你在这里
├── PRINCIPLES.md                            项目准则(必读,新增报告前先看)
├── DEPLOY.md                                GitHub Pages 部署指南
├── .gitignore
│
├── _shared/                                 共享资产 · 所有报告复用
│   ├── style.css                            统一样式
│   ├── glossary.json                        术语词典(80+ 术语)
│   ├── mini-toc.js                          右侧悬浮章节内目录
│   ├── tooltip.js                           术语 hover 浮窗
│   ├── progress.js                          顶部进度条
│   └── build.py                             报告装配脚本
│
├── reports/
│   └── 2026-05-running-science/             第一份报告:跑步科学
│       ├── index.html                       装配后的最终页(部署用)
│       ├── parts/                           Hero/Intro/Antithesis/Footer 各部分
│       ├── chapters/                        12 章原始内容
│       └── assets/                          (待用)
│
└── _legacy/                                 旧版本/试验文件,只读归档
```

详细规范见 [PRINCIPLES.md](PRINCIPLES.md)。

---

## 设计语言

- **暗色主题**:#0e0e0c 主背 + 金色 `#d4a548` 强调 + 学科多色辅助
- **字体栈**:正文 PingFang SC 苹方 · 标题 Cormorant Garamond · 数据 JetBrains Mono
- **可读性组件**:章节内 mini-TOC + 术语 hover tooltip + 阅读进度条 + 章末 5 分钟回顾
- **学科色板**:力学红 / 解剖绿 / 生理蓝 / 代谢橙 / 神经紫 / 心肺青 / 伤病粉红 / 极限正红

---

## 新增一份报告

```bash
# 1. 看准则
cat PRINCIPLES.md

# 2. 复制模板
cp -r reports/2026-05-running-science reports/2026-XX-<slug>
# 然后清空 chapters/ 和 parts/_recaps.json,重新写

# 3. 装配
python3 _shared/build.py reports/2026-XX-<slug>

# 4. 预览
open reports/2026-XX-<slug>/index.html

# 5. 更新本 README 的报告列表
```

---

## 部署到线上

详见 [DEPLOY.md](DEPLOY.md)。推荐方案:

1. **GitHub 仓库 + GitHub Pages**:免费、自动、永久链接
2. 部署后每份报告都拥有 `https://<user>.github.io/<repo>/reports/<slug>/index.html` 的固定地址
3. **飞书云文档维护索引页**:把这个 README 的报告列表同步到飞书,作为日常入口

---

## 项目目标

- 建立一个**长期可累积**的深度研究报告库
- 把每份报告做成**视觉一致、可读性高、信息密度大**的产品
- 通过共享样式 + 装配脚本 + 设计准则,让每份新报告的"建立成本"从一天降到一小时
- 报告之间术语互通(共享 glossary),知识互相强化

---

## 命名约定

- 报告目录:`YYYY-MM-<英文 slug>`,如 `2026-08-sleep-science`
- 章节文件:`ch01.html`、`ch02.html` ...
- 共享资产:`_shared/` 下划线开头表示"非内容"
- 旧版本:统一放 `_legacy/`,不删除以保留历史

---

## 版本与变更

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-05-22 | v1 | 跑步报告 v1 发布(12 章,单文件 HTML,内联样式) |
| 2026-05-22 | v2 | 项目化重组:抽离 `_shared/`、加 mini-TOC / tooltip / 速览页 / 反共识索引 / 章末回顾 |

---

## License & 使用边界

报告内容综合自公开运动科学文献,不构成医疗建议或训练处方。具体决策请咨询专业人士。

仅供个人学习使用。
