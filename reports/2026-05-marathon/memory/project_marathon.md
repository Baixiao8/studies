# Project Memory — Marathon Manual

## 用户身份
- baixiao(Baixiao8)· 业余跑者
- 当前实力:全马 PR 3:20 / 10K 39:00 (VDOT 48)
- 目标:2026 上海马拉松 sub-3:00 (10/25 比赛日)
- 训练数据来源:Coros 手表 6 个月数据(RHR / HRV / 周量 / 越野活动)
- 当前训练计划:23 周备战,5/25 启动,已导入 Coros 训练日历(133 个 W## 工作)

## 项目本质

不是产品,是**学习沉淀作品**:
- 把"备战上马"过程中的学习浓缩成一份可分享的技术手册
- 给团队 / 跑友看,作为入门 sub-3 的知识图谱
- 同时给自己的 23 周训练做参考

## 关键决策

### 内容范围
- **覆盖 10 个领域**:生理 / 训练理论 / 课表 / 力量与跑姿 / 营养 / 睡眠 / 心理 / 伤病 / 比赛 / 赛后前沿
- 每章配:TL;DR + 多个 h3 子章节 + 多种可视化 + 至少 1 个 SHARP TAKE + 真实文献引用

### 风格
- **诚恳尖锐**:每章带 1-3 个 "尖锐共识" callout,敢说反主流观点
- **数据驱动**:33 张 SVG + VDOT 大表 + ACWR 仪表盘
- **苹方字体**(v3.2 后统一)
- **暗色 editorial**:`#0e0e0c` 底 + `#d4a548` 金 + 10 章节色系

### 视觉决策
- v1-v2 单纯 SVG → 太干瘪
- v3 加 33 张 SVG + 21 个新组件 → 数据图密度上去了,但"图表呆"
- v4 加 10 张 AI 章节扉页(即梦 4.5)→ 解决"图表呆"问题,带来情绪 + 氛围
- 试过让模型在 prompt 里塞 hex code / ALL CAPS / "NO TEXT" → 反而触发文字渲染。
   v3 prompt 改用纯描述性自然语言,问题解决。

### 部署
- 仓库 `Baixiao8/study`(原 `learning-thinking`,5/21 改名为短链)
- GitHub Pages 部署 main 分支 root
- 短链: https://baixiao8.github.io/study/marathon/

## 与团队相关

- 用户提过"分享给队友" → 所以需要短链 + Public repo + 队友视角友好
- README 的"分享提示横幅"明确告诉队友:紫色 ◐ "你的数据" callout 是个人样本,可跳过
- 6 处"你的数据"用紫色 .callout.you 标识

## 工具链熟悉度
- 用户接触过 58pic CLI(千图 AI 开放平台,即梦 4.5)
- 有 GitHub Personal Access Token,osxkeychain 已存
- Chrome MCP + 飞书生态熟练
- macOS 14+,Python 3.11
- Coros 手表(MCP 集成,sync 数据已可)

## 与其他项目的关联

- 这是 `~/白笑/claude/学习思考/` 仓库的第一个项目
- 后续会加其他学习项目(同样模式:子目录 + index.html + 短链)
- 工程兄弟:`miniapps/Tech Words/` 是个产品迭代项目,structure 借鉴它(README/ARCHITECTURE/CHANGELOG/archive/knowledge/memory)
- `运动健康/` 是项目工作目录(coros-mcp / 训练计划脚本 / 数据图),不在 `study/` 仓库里

## 推进风格

- 用户喜欢"先 pilot 再批量"模式
- 倾向 "我做不到的让用户做" 透明沟通(比如 sudo 验证、密钥这种敏感事)
- 偏向用 Chrome MCP / 计算机控制驱动 UI,减少用户手动操作
- 多 agent 并行习惯:大任务拆成 3-4 个 sub-agent 并行,主 agent 装配

## 持续维护

- 比赛后(10/25)需要写复盘章节,作为 v5
- knowledge/ 当前是空骨架,后续补充
- archive/ 留底 v3 / v3.3 / v4-pre-hero,以后每次大改前必备份
