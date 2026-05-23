# 部署指南 · DEPLOY

> 本项目已部署到 GitHub Pages,本文档记录部署过程 + 日常维护流程 + 新报告发布。

---

## 当前部署状态

✅ **已上线** · v5.0 · 阅读 + 听书模式(三主题 / TTS / mini player / Media Session 锁屏控制)

| 资源 | URL |
|---|---|
| 项目首页 | https://baixiao8.github.io/studies/ |
| 跑步报告 | https://baixiao8.github.io/studies/reports/2026-05-running-science/ |
| GitHub 仓库 | https://github.com/Baixiao8/studies |

每次 `git push` 后,GitHub Pages 自动重建,**1-2 分钟内**线上 URL 刷新。

---

## 日常维护流程 · 修改报告

```bash
cd "/Users/baixiao/白笑/claude/运动健康"

# 1. 修改章节内容(chapters/chXX.html)或添加新数据卡(_shared/inject-hero.py)

# 2. 重新装配
python3 _shared/build.py reports/2026-05-running-science

# 3. 本地预览(打开本地 HTML 文件)
open reports/2026-05-running-science/index.html

# 4. 推送上线
git add .
git commit -m "report: 更新章节内容"
git push

# 5. 等 1-2 分钟,刷新线上 URL
```

---

## 新报告发布流程 · v3 完整工作流

```bash
# Phase 1 · 内容准备 (3-5 天)
# 复制模板
cp -r reports/2026-05-running-science reports/2026-XX-<slug>

# 清空内容,重新写
rm reports/2026-XX-<slug>/chapters/*.html
rm reports/2026-XX-<slug>/parts/_recaps.json

# 写 12 章 ch01.html ~ ch12.html
# 写 _recaps.json(每章 5 分钟回顾)

# Phase 2 · 视觉生成 (1-2 小时)
# 用千图 AI 生成 12 张章首图
# 参考 _shared/inject-hero.py 注释里的 prompt 模板
# 把图保存为 assets/ch01-hero.jpg ~ ch12-hero.jpg

# 修改 _shared/inject-hero.py 的 KEYPOINTS dict,加入新报告的数据卡
# 然后批量注入:
python3 _shared/inject-hero.py

# Phase 3 · 装配 + 测试 (30 分钟)
python3 _shared/build.py reports/2026-XX-<slug>
open reports/2026-XX-<slug>/index.html
# 检查:hero 图 / 数据卡 / 故事钩子 / 反共识 / SVG 颜色

# Phase 4 · 更新元数据
# 编辑 README.md 加入新报告到列表
# 编辑 index.html(根目录首页)加入新报告卡片

# Phase 5 · 上线
git add .
git commit -m "report: 2026-XX-<slug> 首次发布 · v3 风格"
git push
# 等 1-2 分钟,公开链接生效
```

---

## URL 结构

| 资源 | URL 格式 |
|---|---|
| 项目首页 | `https://baixiao8.github.io/studies/` |
| 任意报告 | `https://baixiao8.github.io/studies/reports/<slug>/` |
| 报告内章节锚点 | `.../<slug>/#s1` 到 `#s12` |
| 反共识索引 | `.../<slug>/#antithesis` |
| 3 分钟速览 | `.../<slug>/#intro` |
| AI 章首图直链 | `.../<slug>/assets/chXX-hero.jpg` |

---

## 在飞书中维护索引页

推荐做法:在飞书云文档新建"我的研究报告"文档,集中维护所有报告链接 + 简介。

```markdown
# 我的研究报告库 · Studies

🌐 https://baixiao8.github.io/studies/

## 运动健康

### [运动学之内 · 跑步的科学解构 v3](https://baixiao8.github.io/studies/reports/2026-05-running-science/)
- 12 章 · 100K 字 · 4.8 小时阅读
- 力学 · 生理 · 解剖 · 神经 · 代谢 · 训练 · 伤病 · 极限
- 12 张 AI 章首插画 + 48 个数据卡 + 30+ SVG 数据图
- 30 个反共识洞察 · 12 个真实科学故事 · 19 个角色化场景

## 其他主题(规划中)

- 睡眠科学
- 注意力 / 认知
- 衰老 / 长寿
- ...
```

可以用 lark-cli 自动同步:
```bash
lark-cli doc +update --token <doc-token> --file README.md --mode replace
```

---

## 备份策略

GitHub 仓库本身即是云端备份,但建议定期:

```bash
# 1. 本地完整备份(防止 GitHub 出意外)
cp -r /Users/baixiao/白笑/claude/运动健康 ~/Backups/studies-$(date +%Y%m%d)

# 2. 重要积分凭证(如果千图 AI 账户有大量积分余额)
# 截图保存或导出
```

---

## 性能 / 流量

GitHub Pages 限制:
- 仓库大小 ≤ 1 GB
- 月流量 ≤ 100 GB

当前项目状态:
- 仓库大小:~5 MB(图片占大头)
- 单报告:850 KB HTML + 1.9 MB 图片 = ~2.7 MB
- 估算:每月 1 万次访问也只用掉 27 GB,远不到上限

---

## 自定义域名(可选)

如果有自己的域名(如 `whitelaugh.com`),可以让访问 URL 更专业:

1. GitHub 仓库 Settings → Pages → Custom domain
2. 填 `studies.whitelaugh.com`(或任意子域)
3. 域名 DNS 添加 CNAME 记录:`studies` → `baixiao8.github.io`
4. 等 DNS 生效(几分钟到几小时),启用 HTTPS

之后访问 URL 变为:`https://studies.whitelaugh.com/`,可以放简历、博客、名片。

---

## 历史:首次部署记录

2026-05-22 当天完成的部署里程碑:

1. ✅ 装 gh CLI(用 tarball,无需 brew/sudo)
2. ✅ git init + 首次 commit
3. ✅ gh auth login(浏览器一次性码授权)
4. ✅ gh repo create Baixiao8/studies --public
5. ✅ 启用 GitHub Pages(`gh api repos/.../pages -X POST`)
6. ✅ 排除 `_legacy/`(避免泄露 COROS MCP / 训练日志)
7. ✅ 排除 `.claude/`(避免 Claude Code 本地配置外露)
8. ✅ Fix:Jekyll 屏蔽 `_shared/` 加 `.nojekyll`
9. ✅ Fix:浏览器 negative-cache 404,加 cache-busting + inline CSS
10. ✅ Fix:`</script>` 字符串导致 JS SyntaxError,build.py 加转义
11. ✅ Fix:CSS 注释 `reports/*/index.html` 含 `*/` 提前关注释,改 `<slug>`

这些坑在 PRINCIPLES.md 的"反共识"节有详细记录,后续报告别再踩。

---

## 备选方案

如果将来想换托管:

### Vercel
- 优势:更快 CDN + 自定义域名免费 + 私有仓库也能用
- 步骤:连接 GitHub 仓库 → Vercel 自动检测 → 1 分钟部署
- URL:`https://studies.vercel.app/`

### Netlify
- 与 Vercel 类似,功能略多

### Cloudflare Pages
- 全球 CDN 最快 + 免费 SSL + 私有仓库支持
- URL:`https://studies.pages.dev/`

迁移成本低(都是静态站托管,内容文件不变)。

---

## 安全注意

- 仓库是 Public,任何人都能看完整源码
- 报告内容综合自公开文献,无敏感信息
- `.gitignore` 已经排除:
  - `_legacy/`(旧训练数据图、COROS MCP 工具)
  - `.claude/`(Claude Code 本地配置)
  - `__pycache__/`、`.DS_Store` 等
- 未来如果加入个人化数据(如自己的训练日志),先放 `_legacy/` 或本地未提交分支
