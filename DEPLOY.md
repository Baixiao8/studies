# 部署指南 · DEPLOY

> 把研究报告项目推到线上,获取永久公开链接。

---

## 推荐方案:GitHub 仓库 + GitHub Pages

**优势**:
- 免费(无限私有/公开仓库,Pages 免费 100GB/月流量)
- 自动部署(push 后 1-2 分钟生效)
- 永久 URL(`https://<user>.github.io/<repo>/...`)
- 版本控制(可回滚任何历史版本)
- 可分享(URL 公开,谁都能打开)

**适合**:你这种长期累积型的研究报告库。

---

## Step 1 · 初始化 Git 仓库

```bash
cd "/Users/baixiao/白笑/claude/运动健康"

# 首次:初始化
git init
git add .
git commit -m "init: 研究报告项目骨架 v1 + 跑步科学报告 v2"
```

---

## Step 2 · 在 GitHub 创建仓库

1. 打开 https://github.com/new
2. **Repository name**:推荐 `research-reports` 或 `sports-science-reports`
3. **Visibility**:Private(私有,只有你能看)或 Public(公开,任何人都能看)
   - 注意:GitHub Pages 在<strong>免费账号下,只有 Public 仓库才能用 Pages</strong>;Pro 账号 ($4/月) 才支持 Private + Pages
   - 如果是个人项目想公开发布,选 Public 即可
4. **不要**勾选 "Initialize this repository"(我们本地已有内容)
5. 点 Create repository

---

## Step 3 · 推到 GitHub

```bash
# 把 <user> 和 <repo> 换成你的实际值
git remote add origin git@github.com:<user>/<repo>.git
git branch -M main
git push -u origin main
```

如果用 HTTPS(默认):
```bash
git remote add origin https://github.com/<user>/<repo>.git
git branch -M main
git push -u origin main
```

---

## Step 4 · 启用 GitHub Pages

1. 进入 GitHub 仓库页面
2. 顶部 **Settings** → 左侧 **Pages**
3. **Source**:Deploy from a branch
4. **Branch**:`main` / `/ (root)` → Save
5. 等 1-2 分钟,Pages 会显示 "Your site is live at https://<user>.github.io/<repo>/"

---

## Step 5 · 访问报告

部署后的 URL 结构:

| 文件 | URL |
|---|---|
| 项目首页(README) | `https://<user>.github.io/<repo>/` |
| 跑步报告 | `https://<user>.github.io/<repo>/reports/2026-05-running-science/index.html` |

把跑步报告的 URL 收藏到浏览器、分享给朋友、贴到飞书索引页。

---

## 日常维护流程

```bash
# 修改/新增内容后
python3 _shared/build.py reports/<slug>     # 重新装配
open reports/<slug>/index.html              # 浏览器验证

# 推到线上(自动部署)
git add .
git commit -m "report: <slug> 内容更新"
git push

# 等 1-2 分钟,线上 URL 就刷新了
```

---

## 在飞书中维护索引页

推荐做法:在飞书云文档新建一个"我的研究报告"长期文档,把每份报告的链接 + 简介集中维护。

```markdown
# 我的研究报告

## 运动健康
- [运动学之内 · 跑步的科学解构 v2](https://<user>.github.io/<repo>/reports/2026-05-running-science/) 
  - 12 章 · 14 万字 · 4.3 小时阅读
  - 力学 · 生理 · 解剖 · 神经 · 代谢 · 训练 · 伤病 · 极限的完整解构

## (后续报告)
- ...
```

可以用 lark-cli 自动同步:
```bash
# 把 README.md 推到飞书云文档(需要先创建一个空文档拿 token)
lark-cli doc +update --token <doc-token> --file README.md --mode replace
```

---

## 备选方案

如果不想用 GitHub:

### Vercel (静态站托管)
- 优势:更快 CDN、自定义域名免费
- 步骤:连接 GitHub 仓库 → Vercel 自动检测 → 1 分钟部署
- URL:`https://<repo>.vercel.app/reports/...`

### Netlify
- 与 Vercel 类似,功能略多
- URL:`https://<repo>.netlify.app/...`

### 飞书云文档(不推荐)
- 长 HTML 渲染不友好
- 失去自定义样式
- 仅适合作为"报告索引页"维护工具

---

## 安全注意

- 报告里如果包含个人数据(训练日志、生理指标等),仓库选 **Private**(需要 Pro 账号才能配合 Pages)
- `.gitignore` 已经排除 `.DS_Store`、`__pycache__`、`_legacy/` 等无关文件
- 不要把 token、密码、API key 提交到仓库

---

## 自定义域名(可选)

如果有自己的域名(如 `whitelaugh.com`):

1. GitHub Pages Settings → Custom domain → 填 `reports.whitelaugh.com`
2. 在域名 DNS 添加 CNAME 记录指向 `<user>.github.io`
3. 等 DNS 生效后,启用 HTTPS

URL 变成:`https://reports.whitelaugh.com/reports/<slug>/`,更专业,可以放简历或博客。
