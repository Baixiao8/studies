/* ==========================================================================
 * Reader Bootstrap · 通用公共组件 v8.3
 * 2026-05-24
 *
 * 职责:
 *   1. 在每个章节(h1.section-h / h2)旁注入"听这章"pill 按钮
 *   2. 在每个小节(h3)旁注入纯图标 mini 入口
 *   3. 监听 URL ?listen=1 / 键盘 R / window.activateReader() 触发
 *   4. 触发时动态加载完整 _shared/reader.{css,js}
 *
 * 不做:
 *   - 不做 TTS(完整 reader.js 才做)
 *   - 不做 overlay 渲染(reader.js 做)
 *   - 不做任何"重活"
 *
 * 通用化:所有报告通用,无报告专属逻辑。
 *   <link rel="stylesheet" href="../../_shared/reader-bootstrap.css">
 *   <script src="../../_shared/reader-bootstrap.js" defer></script>
 * 即接入。build.py 会在 inline 模式自动把两文件内联进 index.html。
 * ========================================================================== */

(function () {
  'use strict';

  // SF Symbols / Lucide 风格 · headphones(描边 1.75,跨平台一致)
  var ICON_HEADPHONES = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 14a9 9 0 0 1 18 0"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>';

  var loaded = false;

  function loadReader(opts) {
    window.__readerOpts = opts || {};
    if (loaded) {
      // 已加载过:直接调用 open(可能是关了再开)
      if (window.__reader) window.__reader.open(window.__readerOpts);
      return;
    }
    loaded = true;
    var ver = '20260524c';
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = '../../_shared/reader.css?v=' + ver;
    document.head.appendChild(l);
    var s = document.createElement('script');
    s.src = '../../_shared/reader.js?v=' + ver;
    s.defer = true;
    document.body.appendChild(s);
  }

  // 注入章节入口
  // 大章节(h1.section-h / h2):full pill 带文字 "听这章"
  // 小节(h3):mini 纯图标,从该小节起播
  function injectEntries() {
    document.querySelectorAll('section.chapter h2, section.chapter h1.section-h').forEach(function (h) {
      if (h.querySelector('.reader-entry-btn')) return;
      var chapter = h.closest('section.chapter') || h.closest('section');
      var btn = document.createElement('button');
      btn.className = 'reader-entry-btn';
      btn.type = 'button';
      btn.title = '从这一章开始听';
      btn.setAttribute('aria-label', '听这一章');
      btn.innerHTML = ICON_HEADPHONES + '<span>听这章</span>';
      btn.addEventListener('click', function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        loadReader({ chapter: chapter });
      });
      h.appendChild(document.createTextNode(' '));
      h.appendChild(btn);
    });

    document.querySelectorAll('section.chapter h3').forEach(function (h) {
      if (h.querySelector('.reader-entry-btn')) return;
      var chapter = h.closest('section.chapter');
      if (!chapter) return;
      var btn = document.createElement('button');
      btn.className = 'reader-entry-btn mini';
      btn.type = 'button';
      btn.title = '从这一小节开始听';
      btn.setAttribute('aria-label', '从此小节听');
      btn.innerHTML = ICON_HEADPHONES + '<span>听此节</span>';
      btn.addEventListener('click', function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        loadReader({ chapter: chapter, startNode: h });
      });
      h.appendChild(document.createTextNode(' '));
      h.appendChild(btn);
    });
  }

  // URL / 键盘自动触发
  function attachAutoTriggers() {
    if (location.search.indexOf('listen=1') >= 0 ||
        location.search.indexOf('reader=1') >= 0 ||
        location.hash.indexOf('#read=') >= 0) {
      loadReader();
    }
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'r' && e.key !== 'R') return;
      if (/input|textarea|select/i.test(e.target.tagName)) return;
      loadReader();
    });
  }

  // 全局 API(任何外部触发)
  window.activateReader = function (opts) { loadReader(opts); };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      injectEntries();
      attachAutoTriggers();
    });
  } else {
    injectEntries();
    attachAutoTriggers();
  }
})();
