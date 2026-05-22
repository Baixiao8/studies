/* =========================================================
 * MINI-TOC · 右侧悬浮章节内目录
 *
 * 行为:
 *   - 检测当前可视章节,在屏幕右侧显示该章的 h3 列表
 *   - 滚动时根据 IntersectionObserver 高亮当前 h3
 *   - 离开任何 section 时(在 hero / footer 区)隐藏
 *   - 移动端 (<1280px) CSS 直接 display:none
 *
 * 用法:
 *   <script src="../../_shared/mini-toc.js" defer></script>
 *   不需要任何 HTML,会自动扫描 section[id^="s"] 下的 h3
 * ========================================================= */

(function() {
  'use strict';

  // 等 DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    // 1) 创建 mini-toc DOM
    const tocEl = document.createElement('aside');
    tocEl.className = 'mini-toc';
    tocEl.innerHTML = `
      <div class="mini-toc-label">CHAPTER NAV · 本章导航</div>
      <div class="mini-toc-chapter"></div>
      <ul></ul>
    `;
    document.body.appendChild(tocEl);

    const chapterLabel = tocEl.querySelector('.mini-toc-chapter');
    const tocList = tocEl.querySelector('ul');

    // 2) 收集所有章节信息
    // 报告结构:每个章节是 <section id="s1"...><h1 class="section-h">...</h1><h3 class="...">...</h3></section>
    const sections = Array.from(document.querySelectorAll('section[id^="s"]'));
    if (sections.length === 0) return;

    const chapters = sections.map((sec) => {
      const id = sec.id;
      const heading = sec.querySelector('h1.section-h');
      const title = heading ? heading.firstChild.textContent.trim() : id;
      const tag = sec.querySelector('.section-tag');
      const tagText = tag ? tag.textContent.replace(/\s+/g, ' ').trim() : '';
      const h3s = Array.from(sec.querySelectorAll('h3')).map((h3, idx) => {
        // 给 h3 加 id 如果没有
        if (!h3.id) h3.id = `${id}-h3-${idx + 1}`;
        // 提取标题文字(去掉 .pre 前缀编号)
        let text = h3.textContent.trim();
        const pre = h3.querySelector('.pre');
        let numText = '';
        if (pre) {
          numText = pre.textContent.trim();
          text = text.replace(numText, '').trim();
        }
        return { id: h3.id, text, num: numText };
      });
      return { id, title, tag: tagText, h3s };
    });

    // 3) 用 IntersectionObserver 追踪当前 section 和 h3
    let currentSectionId = null;
    let currentH3Id = null;

    function renderForSection(chapter) {
      if (!chapter) return;
      chapterLabel.textContent = chapter.title;
      tocList.innerHTML = chapter.h3s.map(h3 => `
        <li data-h3-id="${h3.id}">
          <a href="#${h3.id}">
            <span class="num">${h3.num || ''}</span>
            <span class="text">${h3.text}</span>
          </a>
        </li>
      `).join('');
      // 重新绑定 h3 高亮(因为列表重建了)
      updateActiveH3(currentH3Id);
    }

    function updateActiveH3(h3Id) {
      tocList.querySelectorAll('li').forEach(li => {
        if (li.dataset.h3Id === h3Id) {
          li.classList.add('active');
        } else {
          li.classList.remove('active');
        }
      });
    }

    function showToc() { tocEl.classList.add('visible'); }
    function hideToc() { tocEl.classList.remove('visible'); }

    // section 进入视口 → 切换 mini-toc 内容
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const sec = entry.target;
          const chapter = chapters.find(c => c.id === sec.id);
          if (chapter && chapter.id !== currentSectionId) {
            currentSectionId = chapter.id;
            renderForSection(chapter);
            showToc();
          }
        }
      });
    }, {
      rootMargin: '-30% 0px -40% 0px',
      threshold: 0
    });
    sections.forEach(sec => sectionObserver.observe(sec));

    // h3 进入视口 → 高亮 mini-toc 中对应项
    const h3Observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          currentH3Id = entry.target.id;
          updateActiveH3(currentH3Id);
        }
      });
    }, {
      rootMargin: '-20% 0px -70% 0px',
      threshold: 0
    });
    document.querySelectorAll('section[id^="s"] h3').forEach(h3 => h3Observer.observe(h3));

    // 检测 hero / footer 区域,隐藏 mini-toc
    const hero = document.querySelector('header.hero, .hero');
    const footer = document.querySelector('footer');
    if (hero) {
      const heroObs = new IntersectionObserver((entries) => {
        entries.forEach(e => { if (e.isIntersecting) hideToc(); });
      }, { rootMargin: '0px 0px -40% 0px' });
      heroObs.observe(hero);
    }
    if (footer) {
      const footObs = new IntersectionObserver((entries) => {
        entries.forEach(e => { if (e.isIntersecting) hideToc(); });
      }, { rootMargin: '-30% 0px 0px 0px' });
      footObs.observe(footer);
    }
  }
})();
