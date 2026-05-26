# _shared/epub_templates/ · EPUB 内部资源模板

> EPUB 文件本质是个 zip 包(`.epub` 后缀),内部按 EPUB 3 spec 组织。
> 这里是组装 EPUB 用的模板和资源文件。

## EPUB 内部结构(每份报告生成时的目标)

```
<slug>.epub (zip)
├── mimetype                           ← 第一个文件,不压缩,值 "application/epub+zip"
├── META-INF/
│   └── container.xml                  ← 指向 content.opf 入口
└── OEBPS/
    ├── content.opf                    ← Manifest + Spine(资源清单 + 阅读顺序)
    ├── nav.xhtml                      ← 多级 TOC(章 + 节,听书 APP 识别这个)
    ├── styles/
    │   └── main.css                   ← EPUB 内部样式
    ├── chapter01.xhtml ... chapter12.xhtml  ← 各章内容
    └── images/
        ├── ch01-hero.jpg              ← 章节封面图
        ├── ch01-fig-01.png            ← 章节里的 SVG/table 渲染图
        └── ...
```

## 本目录文件

| 文件 | 用途 |
|---|---|
| `container.xml` | META-INF/container.xml 内容,固定值(指向 content.opf)|
| `content.opf.tmpl` | OPF 模板,带 `{{ var }}` 占位,由 build_epub.py 填充 metadata / manifest / spine |
| `nav.xhtml.tmpl` | 多级 TOC 模板,关键 — 子标题节点放这里 |
| `chapter.xhtml.tmpl` | 单个章节 xhtml 模板 |
| `stylesheet.css` | EPUB 内部样式(简化 Newsprint 风格,适配各 reader) |

## EPUB 3 reader 兼容

按 EPUB 3 spec 写,目标 reader:
- 微信读书(主要场景:听书)
- Apple Books / iBooks
- ReadEra / Moon+ Reader / Lithium(Android)
- Calibre(桌面)

## 模板变量(content.opf.tmpl)

| 变量 | 含义 |
|---|---|
| `{{ identifier }}` | EPUB 唯一标识符(UUID 或 URL) |
| `{{ title }}` | 报告标题 |
| `{{ date }}` | 出版日期 |
| `{{ description }}` | 描述 |
| `{{ modified }}` | 修改日期(ISO 8601) |
| `{{ chapter_items }}` | 章节 manifest 条目 |
| `{{ image_items }}` | 图片 manifest 条目 |
| `{{ spine_items }}` | spine 阅读顺序 |
