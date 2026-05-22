# Studies · 深度研究报告库

> 一个持续累积的研究报告项目,从运动科学起步。每份报告都是 **知识性视角** 下对某个具体主题的深度解构——不是手册,不是清单,是研究对象式的全景调查。
>
> 🌐 **公开访问:** https://baixiao8.github.io/studies/
> 📦 **仓库:** https://github.com/Baixiao8/studies
> 🏷️ **当前版本:** v3.0 · Newsprint 报刊风 + AI 章首图

---

## 报告列表

| # | 主题 | 字数 | 阅读 | AI 图 | 公开链接 |
|---|---|---|---|---|---|
| **2026-05** | 运动学之内 · 跑步的科学解构 | ~100K | 4.8h | 12 张 | [🔗 在线阅读](https://baixiao8.github.io/studies/reports/2026-05-running-science/) |
| 2026-06 | (规划中) | — | — | — | — |

---

## 设计语言 · v3 Newsprint 报刊风

```
背景:    米黄纸张 #F0EBDD  (印刷品千年验证的长文背景)
正文:    深灰墨色 #2C2C2C  (高对比度,长时阅读不疲劳)
强调:    报刊红 #A8423B    (kicker、反共识、强调点)
分隔:    3px double border  (报刊式章节分隔)
字体栈:
  - 标题  Inter Tight 700-900 (无衬线粗体大字)
  - 正文  PingFang SC 苹方   (中文可读性最优)
  - 数据  JetBrains Mono     (等宽数字、dateline)
学科色板(印刷低饱和):
  力学 红 / 解剖 绿 / 生理 蓝 / 代谢 棕 / 神经 紫 / 心肺 青
```

## 每章信息架构

```
┌──────────────────────────────────────┐
│  [AI Hero 跑者剪影 · 米黄底]            │  ← 视觉钩子(5 秒)
│  FIG 0 · 章节主题                       │
└──────────────────────────────────────┘
┌──────┬──────┬──────┬──────┐
│ 数据卡│ 数据卡│ 数据卡│ 数据卡│           ← 信息密度(1 分钟)
└──────┴──────┴──────┴──────┘

CHAPTER · 力学篇 / 第 X 章
章节大标题
副标题

▼ ELEVATOR PITCH (TL;DR)
[一句话精炼概括]

◆ 故事 · 年代 · 地点
[真实科学场景开篇]

[章节正文 + 6-8 张 Newsprint 浅色 SVG 图]
[内嵌反共识 / 操作建议 / 角色化注解 / 机制注释]

★ 5-MINUTE RECAP · 五分钟回顾
[5 条核心要点]
```

---

## 可读性组件

- **章首 AI Hero 图** · 千图 AI 即梦5.0 生成,统一报刊风
- **HTML 数据卡片** · 每章 4 个关键数据点,前端文本(避免 AI 中文乱码)
- **章节内 mini-TOC** · 右侧悬浮目录,滚动高亮当前小节
- **术语 hover tooltip** · 80+ 词条悬停浮窗解释(VO2max/LT2/ACWR/SSC...)
- **阅读进度条** · 顶部金色进度条
- **章末 5 分钟回顾** · 每章末尾 5 条核心要点卡片
- **3 分钟速览页** · Hero 后的"全书速览"
- **反共识索引** · 报告末尾 30+ 个反直觉洞察的一页汇总

---

## 项目结构

```
运动健康/
├── README.md                           ← 你在这里
├── PRINCIPLES.md                       项目准则(8 条铁律)
├── DEPLOY.md                           部署指南
├── index.html                          项目首页 Newsprint 风
├── preview-newsprint.html              首页历史参考
├── preview-newsprint-ch1.html          Ch1 单章预览(历史试点)
├── .gitignore
│
├── _shared/                            共享资产 · 所有报告复用
│   ├── style.css                       Newsprint 浅色样式
│   ├── glossary.json                   术语词典(80+ 术语)
│   ├── mini-toc.js                     右侧悬浮章节内目录
│   ├── tooltip.js                      术语 hover 浮窗
│   ├── progress.js                     顶部进度条
│   ├── build.py                        报告装配脚本(SVG 颜色反色)
│   ├── build-newsprint.py              单章 Newsprint 预览生成器
│   └── inject-hero.py                  AI hero + 数据卡批量注入
│
└── reports/
    └── 2026-05-running-science/        第一份报告:跑步科学
        ├── index.html                  装配后的最终页(部署用)
        ├── parts/
        │   ├── 00_hero.html            Hero + Sticky-nav
        │   ├── 05_intro.html           3 分钟速览页
        │   ├── 95_antithesis.html      反共识索引
        │   ├── 99_footer.html          Footer + 共享 JS
        │   └── _recaps.json            每章 5 分钟回顾数据
        ├── chapters/
        │   ├── ch01.html ~ ch12.html   12 章原始内容
        └── assets/                     AI 生成的章首图
            └── ch01-hero.jpg ~ ch12-hero.jpg
```

详细规范见 [PRINCIPLES.md](PRINCIPLES.md)。

---

## 新增一份报告 · v3 工作流

```bash
# 1. 看准则
cat PRINCIPLES.md

# 2. 复制模板
cp -r reports/2026-05-running-science reports/2026-XX-<slug>
# 清空 chapters/ 和 parts/_recaps.json,重新写

# 3. 写 12 章内容 + _recaps.json

# 4. 生成 AI 章首图(可选,大幅提升视觉)
#    用千图 AI 即梦5.0,prompt 模板见 _shared/inject-hero.py 注释
#    每章 ~2 积分,12 张约 24 积分
#    下载到 reports/<slug>/assets/ch01-hero.jpg ~ ch12-hero.jpg

# 5. 配置每章 4 个数据卡(KEYPOINTS dict in inject-hero.py)
#    然后批量注入:
python3 _shared/inject-hero.py

# 6. 装配
python3 _shared/build.py reports/2026-XX-<slug>

# 7. 预览
open reports/2026-XX-<slug>/index.html

# 8. 更新 README 报告列表 + push
git add . && git commit -m "report: <slug> v1" && git push
```

---

## AI 配图工作流(v3 新增)

**用千图 AI 平台生成 Newsprint 风格章首图。**

通用 prompt 模板:
```
极简编辑插画风格,横向构图。
[主体描述:跑者侧面剪影 + 章节特定元素]
米黄色纸张背景 #F0EBDD。深炭灰身体轮廓。
深红色 #A8423B 用于[强调元素]。
Apple Keynote 极简美学,Kinfolk 留白感,vector clean illustration。
无任何文字。
```

模型推荐:**即梦5.0(model_id: 4739)**,16:9 横向,2K 分辨率。

12 张图风格统一,组合起来形成"跑步科学连环画"的视觉系列。

---

## 部署状态

✅ **已部署到 GitHub Pages** · 每次 `git push` 后 1-2 分钟自动重新发布

- 仓库:https://github.com/Baixiao8/studies
- 站点根:https://baixiao8.github.io/studies/
- 跑步报告:https://baixiao8.github.io/studies/reports/2026-05-running-science/

完整部署指南见 [DEPLOY.md](DEPLOY.md)。

---

## 项目目标

- 建立一个**长期可累积**的深度研究报告库
- 把每份报告做成**视觉一致、可读性高、信息密度大**的产品
- 通过共享样式 + 装配脚本 + AI 配图,让每份新报告从"白板"到"上线"控制在 8-12 小时内
- 报告之间术语互通(共享 glossary),知识互相强化
- 视觉语言统一(Newsprint 报刊风),整套库像一本持续出版的杂志

---

## 命名约定

- 报告目录:`YYYY-MM-<英文 slug>`,如 `2026-08-sleep-science`
- 章节文件:`ch01.html` ~ `ch12.html`(必须 0 填充)
- AI 章首图:`assets/ch01-hero.jpg` ~ `assets/ch12-hero.jpg`(必须 0 填充)
- 共享资产:`_shared/` 下划线开头表示"非内容"

---

## 版本与变更

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-05-22 | v1 | 跑步报告 v1 发布(12 章,单文件 HTML,内联样式) |
| 2026-05-22 | v2 | 项目化重组:抽离 `_shared/`、加 mini-TOC / tooltip / 速览页 / 反共识索引 / 章末回顾 |
| 2026-05-22 | **v3** | **Newsprint 报刊风全站换肤 + 12 张 AI 章首图 + 48 个 HTML 数据卡 + SVG 颜色自动反色** |

---

## License & 使用边界

报告内容综合自公开运动科学文献,不构成医疗建议或训练处方。具体决策请咨询专业人士。

仅供个人学习使用。
