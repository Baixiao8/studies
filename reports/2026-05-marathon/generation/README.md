# Generation Toolkit

> 内容生成相关的脚本与 prompt 模板。

---

## 目录

```
generation/
├── README.md          ← 你在看的
├── scripts/           ← Python 工具链
│   ├── img_pipeline.py
│   ├── embed_heroes.py
│   ├── integrate_v2.py
│   ├── integrate_v3.py
│   ├── integrate_v4.py
│   └── charts.py
└── prompts/           ← AI 图 prompt 演化
    ├── hero_v1.py    ← ❌ 含 hex + ALL CAPS,触发文字串扰
    ├── hero_v2.py    ← ⚠️  无 hex 但用 "book/magazine" 导致假书页
    └── hero_v3.py    ← ✅ 最终版,text-safe
```

---

## scripts/ 工具说明

### `img_pipeline.py` — 图片下载 + 压缩 CLI

通用工具,封装了"58pic CLI 提交 → 轮询 → 下载 → sips 压缩"完整流程。

```bash
# 生成单张图
python3 generation/scripts/img_pipeline.py gen \
  --model 4714 \
  --prompt "..." \
  --out my_image.jpg \
  --max-dim 1280 \
  --quality normal

# 仅下载 + 压缩已有 oss URL
python3 generation/scripts/img_pipeline.py download <url> --out filename.jpg

# 仅压缩本地图(原地覆盖)
python3 generation/scripts/img_pipeline.py compress *.jpg --max-dim 1280
```

### `embed_heroes.py` — 把 10 张 hero 嵌入 HTML

在每个 `<section id="sN">` 容器开头插入 `.ch-hero` 块,同时把 `.ch-hero` CSS 追加到 style。

```bash
python3 generation/scripts/embed_heroes.py
# 直接修改 index.html
```

### `integrate_vN.py` — 章节集成脚本

各版本迭代的批量集成工具:

- `integrate_v2.py` — v1 → v2:14 个章节修复 + 视觉添加
- `integrate_v3.py` — v2 → v3:13 个视觉组件批量插入
- `integrate_v4.py` — v3 → v4:spacing + 字体 pass

### `charts.py` — 趋势图绘制

用 matplotlib 绘制 RHR / HRV / 周量趋势图(基于 Coros 6 个月数据)。

```bash
python3 generation/scripts/charts.py
# 输出 trend_hrv.png / trend_rhr.png / trend_weekly_km.png
```

⚠️ 此脚本依赖 `~/.config/coros-mcp/cache.db` 本地数据库,如果换电脑用需先跑 `coros-mcp sync`。

---

## prompts/ 演化教训

### 为什么有三个版本

最初的 `hero_v1` 生成了 6/10 张带假文字(色号、"RACE DAY TAPER"、"POST-BIACH RECOVERY" 等)。
原因和修复:

| 问题 | v1 错误写法 | v3 修复 |
|---|---|---|
| Hex 色号 | `#0e0e0c` / `#d4a548` | "dark almost-black" / "warm gold" |
| ALL CAPS 短语 | `EDGE-TO-EDGE FULL-BLEED` | "fills the entire canvas" |
| 否定指令 | `NO TEXT, NO LABELS, NO WORDS` | "purely visual imagery without written characters" |
| 印刷物术语 | `editorial illustration for a high-end sports science book` | "A single cinematic frame, not a book spread" |
| 章节英文名 | `HUMAN PHYSIOLOGY` / `RACE DAY` | 改用自然语言描述场景 |

**总规则**:模型会把 prompt 里出现的英文 ALL CAPS、hex code、和"book/magazine"类印刷物术语当成"画面应有的文字",反向触发文字渲染。

### v3 模板(text-safe)

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

每章再加 100-150 字的 semantic content(描述主体内容)即可。详见 hero_v3.py。

---

## 重生 / 扩展

想重新生成 10 张 hero(比如换个调性)?

1. 拷贝 `prompts/hero_v3.py` → `prompts/hero_v4.py`
2. 改 `STYLE` 字符串(注意不要碰 v3 的禁词规则)
3. 改 `WORK` 列表里每章的 semantic content
4. 跑:`python3 prompts/hero_v4.py`
5. 输出到 `marathon/images/`
6. 再跑 `scripts/embed_heroes.py` 重嵌入

成本参考:即梦 4.5 一张 8 积分,10 张约 80 积分。
