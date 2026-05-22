/* =========================================================
 * TERM TOOLTIP · 术语 hover 浮窗
 *
 * 行为:
 *   - 加载 glossary.json (同目录),建立术语→定义映射
 *   - 自动扫描全文匹配术语(精确匹配,大小写敏感),包成
 *     <span class="term" data-term="...">...</span>
 *   - hover/click 时弹出浮窗显示定义 + 跳转到首次定义章节
 *   - 移动端 tap 显示,再次 tap 外关闭
 *
 * 注意:
 *   - 已经在 HTML 里手工标注的 <span class="term"> 会被尊重
 *   - 不在 callout 标题、表头、SVG text 内做替换(避免破坏样式)
 *   - 一段中同一术语只标第一次出现
 *
 * 用法:
 *   <script src="../../_shared/tooltip.js" defer></script>
 *   glossary.json 必须与 tooltip.js 同目录
 * ========================================================= */

(function() {
  'use strict';

  // 浮窗 DOM
  let tooltipEl = null;
  let glossary = {};
  let activeTerm = null;
  let hideTimer = null;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  async function init() {
    // 1) 加载 glossary
    // 优先用 embed 模式 inline 的 window.__EMBEDDED_GLOSSARY__,否则 fetch glossary.json
    if (window.__EMBEDDED_GLOSSARY__) {
      glossary = window.__EMBEDDED_GLOSSARY__;
    } else {
      try {
        // 智能路径:相对于当前页面,glossary 在 ../../_shared/
        const scriptEl = document.querySelector('script[src*="tooltip.js"]');
        const scriptSrc = scriptEl ? scriptEl.src : '';
        const glossaryUrl = scriptSrc.replace(/tooltip\.js.*$/, 'glossary.json');
        const res = await fetch(glossaryUrl);
        glossary = await res.json();
      } catch (e) {
        console.warn('[tooltip] glossary.json 加载失败,术语 hover 禁用', e);
        return;
      }
    }

    // 2) 创建 tooltip 浮窗
    tooltipEl = document.createElement('div');
    tooltipEl.className = 'term-tooltip';
    document.body.appendChild(tooltipEl);

    // 3) 自动扫描 + 包裹术语
    autoWrapTerms();

    // 4) 给所有 .term 绑定事件(手工的 + 自动的)
    bindEvents();

    // 5) 点击外部关闭
    document.addEventListener('click', (e) => {
      if (!tooltipEl.contains(e.target) && !e.target.classList.contains('term')) {
        hideTooltip();
      }
    });
  }

  function autoWrapTerms() {
    // 收集所有 glossary key,按长度倒序(优先匹配长术语,避免 "VO2max" 被截成 "VO2")
    const terms = Object.keys(glossary).sort((a, b) => b.length - a.length);
    if (terms.length === 0) return;

    // 转义 regex 特殊字符
    const escape = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const termPattern = new RegExp(
      '\\b(' + terms.map(escape).join('|') + ')\\b',
      'g'
    );

    // 哪些容器不扫描(避免破坏)
    const skipSelectors = [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',  // 标题不替换
      'th', 'td.mono-cell',                  // 表头/mono 单元格
      'code', 'pre',                         // 代码
      '.term', '.chip', '.mono', '.ref',     // 已标记或不应该改的
      '.callout .label', '.section-tag',     // 标签
      '.mini-toc', '.term-tooltip',          // 自己
      'svg',                                 // SVG 内部
      '.svg-caption',
      '.reading-meta',
    ];

    // 在每个 <p> / <li> / .card p 等内容容器里替换文本节点
    const contentSelectors = 'p, li, .card .desc, .number-strip .sub, .metric-card .m-desc, .callout p';
    document.querySelectorAll(contentSelectors).forEach(container => {
      // 跳过被排除的祖先
      if (skipSelectors.some(sel => container.closest(sel))) return;

      // 每个容器内只标记每个术语第一次出现
      const seenInContainer = new Set();

      walkTextNodes(container, (textNode) => {
        const text = textNode.nodeValue;
        if (!text || !text.trim()) return;
        // 跳过术语容器内部
        if (textNode.parentElement.closest('.term, .chip, .mono, .ref, code, svg')) return;

        let lastIdx = 0;
        let frag = null;
        let match;
        termPattern.lastIndex = 0;

        while ((match = termPattern.exec(text)) !== null) {
          const term = match[1];
          if (seenInContainer.has(term)) continue;
          seenInContainer.add(term);

          if (!frag) frag = document.createDocumentFragment();
          // 之前的纯文本
          if (match.index > lastIdx) {
            frag.appendChild(document.createTextNode(text.slice(lastIdx, match.index)));
          }
          // 包成 .term
          const span = document.createElement('span');
          span.className = 'term';
          span.dataset.term = term;
          span.textContent = term;
          frag.appendChild(span);
          lastIdx = match.index + term.length;
        }

        if (frag) {
          if (lastIdx < text.length) frag.appendChild(document.createTextNode(text.slice(lastIdx)));
          textNode.parentNode.replaceChild(frag, textNode);
        }
      });
    });
  }

  function walkTextNodes(node, callback) {
    const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, null);
    const nodes = [];
    let n;
    while (n = walker.nextNode()) nodes.push(n);
    nodes.forEach(callback);
  }

  function bindEvents() {
    document.body.addEventListener('mouseover', onEnter);
    document.body.addEventListener('mouseout', onLeave);
    document.body.addEventListener('click', onClick);
  }

  function onEnter(e) {
    const t = e.target.closest('.term');
    if (!t) return;
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
    showTooltip(t);
  }

  function onLeave(e) {
    const t = e.target.closest('.term');
    if (!t) return;
    hideTimer = setTimeout(hideTooltip, 250);
  }

  function onClick(e) {
    const t = e.target.closest('.term');
    if (!t) return;
    e.preventDefault();
    showTooltip(t);
  }

  function showTooltip(termEl) {
    const term = termEl.dataset.term || termEl.textContent.trim();
    const entry = glossary[term];
    if (!entry) return;
    activeTerm = termEl;

    const linkHtml = entry.chapter
      ? `<a href="#${entry.anchor || ('s' + entry.chapter.split('.')[0])}" class="tt-link">→ 详见 Ch ${entry.chapter}</a>`
      : '';

    tooltipEl.innerHTML = `
      <div class="tt-name">${term}</div>
      <div class="tt-cn">${entry.cn || ''}</div>
      <div class="tt-def">${entry.def || ''}</div>
      ${linkHtml}
    `;

    // 定位:在术语下方,如果超出窗口则放上方
    const rect = termEl.getBoundingClientRect();
    const tipRect = tooltipEl.getBoundingClientRect();
    let top = rect.bottom + window.scrollY + 8;
    let left = rect.left + window.scrollX;

    // 防止右侧出界
    if (left + 320 > window.innerWidth - 16) {
      left = window.innerWidth - 336;
    }
    if (left < 16) left = 16;

    // 防止下方出界(放上方)
    if (rect.bottom + 220 > window.innerHeight) {
      top = rect.top + window.scrollY - 8 - tooltipEl.offsetHeight;
    }

    tooltipEl.style.top = top + 'px';
    tooltipEl.style.left = left + 'px';
    tooltipEl.classList.add('visible');

    // tooltip 内 hover 时不关闭
    tooltipEl.onmouseenter = () => { if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; } };
    tooltipEl.onmouseleave = () => { hideTimer = setTimeout(hideTooltip, 200); };
  }

  function hideTooltip() {
    tooltipEl.classList.remove('visible');
    activeTerm = null;
  }
})();
