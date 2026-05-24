/* ==========================================================================
 * Reader · 极简听书组件 v8.0
 * 2026-05-24
 *
 * v8 改动:
 *   - 全部 emoji 换为 inline SVG(Lucide 风格 / 跨平台一致 / 描边粗细统一 1.75)
 *   - 章节 h2 旁注入"听这章" pill 入口(移动端必备 / Apple 风格胶囊)
 *   - 起播位置 = 视口里第一个完整可见的可读段(不再从章首)
 *
 * 公共组件原则:
 *   - 只做一件事:把当前章节(从你看到的段落起)读出来
 *   - 只有 3 个控件:⏵ 播放/暂停 · 速度 · 关闭
 *   - 无主题、无字号、无章节跳转、无定时
 *   - 浏览器原生 SpeechSynthesis,零依赖
 * ========================================================================== */

(function () {
  'use strict';

  var EXCLUDE_SELECTORS = [
    'svg', 'svg *', 'table',
    '.hero', '.hero-keypoints', '.hero-toc-section',
    '.number-strip', '.section-tag',
    '.sticky-nav', '.mini-toc', '.progress-bar',
    '.svg-frame', '.svg-caption',
    'script', 'style', '.ref', '.chip',
    '.reader-overlay', '.reader-entry-btn'
  ];
  var INCLUDE_TAGS = 'h2,h3,h4,p,li,blockquote';
  var RATES = [0.75, 1.0, 1.25, 1.5];

  // ─── SVG Icons(Lucide 风格,统一描边 1.75 / viewBox 24×24)──
  var ICON = {
    play:  '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.14v13.72a1 1 0 0 0 1.51.86l11.04-6.86a1 1 0 0 0 0-1.72L9.51 4.28A1 1 0 0 0 8 5.14z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="4.5" width="4" height="15" rx="1"/><rect x="14" y="4.5" width="4" height="15" rx="1"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>',
    headphones: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 14a9 9 0 0 1 18 0"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>'
  };

  // ──────────────────────────────────────────────────────────────
  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (k === 'class') n.className = attrs[k];
        else if (k === 'html') n.innerHTML = attrs[k];
        else if (k === 'text') n.textContent = attrs[k];
        else if (k.indexOf('on') === 0) n.addEventListener(k.slice(2), attrs[k]);
        else n.setAttribute(k, attrs[k]);
      }
    }
    if (children) {
      (Array.isArray(children) ? children : [children]).forEach(function (c) {
        if (c == null) return;
        n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
      });
    }
    return n;
  }

  function isExcluded(node) {
    for (var i = 0; i < EXCLUDE_SELECTORS.length; i++) {
      if (node.matches && node.matches(EXCLUDE_SELECTORS[i])) return true;
      if (node.closest && node.closest(EXCLUDE_SELECTORS[i])) return true;
    }
    return false;
  }

  // ─── 定位 · 视口中的章节 + 段落 ───────────────────────────
  function getVisibleChapter() {
    var chapters = $$('section.chapter');
    if (chapters.length === 0) return document.body;
    var best = chapters[0], bestVis = -1, vh = window.innerHeight;
    chapters.forEach(function (ch) {
      var r = ch.getBoundingClientRect();
      var vis = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
      if (vis > bestVis) { bestVis = vis; best = ch; }
    });
    return best;
  }

  // 在章节里找视口里第一个完整可见的可读段(从这里起播)
  function getStartNode(chapter, preferred) {
    var nodes = $$(INCLUDE_TAGS, chapter).filter(function (n) { return !isExcluded(n); });
    if (nodes.length === 0) return null;
    if (preferred && nodes.indexOf(preferred) >= 0) return preferred;
    var vh = window.innerHeight;
    for (var i = 0; i < nodes.length; i++) {
      var r = nodes[i].getBoundingClientRect();
      // 节点顶部在视口内(0~vh)的第一个就用它
      if (r.top >= -20 && r.top < vh * 0.7) return nodes[i];
    }
    // 视口里没找到,选第一个底部 > 0 的(已经滚过去的也算)
    for (var j = 0; j < nodes.length; j++) {
      var r2 = nodes[j].getBoundingClientRect();
      if (r2.bottom > 0) return nodes[j];
    }
    return nodes[0];
  }

  function extractText(scope, startNode) {
    var all = $$(INCLUDE_TAGS, scope).filter(function (n) { return !isExcluded(n); });
    var startIdx = startNode ? all.indexOf(startNode) : 0;
    if (startIdx < 0) startIdx = 0;
    return all.slice(startIdx)
      .map(function (n) {
        // clone + 移除入口按钮 → 朗读时不读"听这章""听此节"等按钮文字
        var c = n.cloneNode(true);
        c.querySelectorAll('.reader-entry-btn').forEach(function (b) { b.remove(); });
        return (c.textContent || '').replace(/\s+/g, ' ').trim();
      })
      .filter(function (t) { return t.length > 1; })
      .join('\n\n');
  }

  // ──────────────────────────────────────────────────────────────
  function Reader() {
    this.synth = window.speechSynthesis;
    this.utter = null;
    this.rate = 1.0;
    this.isPlaying = false;
    this.text = '';
    this.overlay = null;
    this.playBtn = null;
    this.chapter = null;        // v8.1 · 记录当前章节用于自动接下章
    this._userPaused = false;   // v8.1 · 用户主动暂停标记
    this._wakeLock = null;      // v8.2 · Wake Lock 防屏幕自动息屏
  }

  // v8.2 · Wake Lock(防屏幕自动息屏 / 部分缓解 iOS 锁屏停播)
  // 注意:仅防"系统自动息屏",用户主动锁屏仍会停 — 这是 Web 平台硬限制
  Reader.prototype._requestWakeLock = function () {
    var self = this;
    if (!('wakeLock' in navigator) || this._wakeLock) return;
    navigator.wakeLock.request('screen')
      .then(function (lock) {
        self._wakeLock = lock;
        lock.addEventListener('release', function () { self._wakeLock = null; });
      })
      .catch(function (e) { /* 用户拒绝或不支持,静默 */ });
  };
  Reader.prototype._releaseWakeLock = function () {
    if (this._wakeLock) {
      try { this._wakeLock.release(); } catch (e) {}
      this._wakeLock = null;
    }
  };

  Reader.prototype.open = function (opts) {
    if (this.overlay) return;
    var self = this;

    var chapter = (opts && opts.chapter) || getVisibleChapter();
    var startNode = (opts && opts.startNode) || getStartNode(chapter);
    this.chapter = chapter;
    this.text = extractText(chapter, startNode);
    if (!this.text) {
      console.warn('[Reader] 当前位置没有可朗读文本');
      return;
    }

    this.playBtn = el('button', {
      class: 'reader-play',
      title: '播放 / 暂停 (空格)',
      'aria-label': '播放',
      html: ICON.play,
      onclick: function () { self.toggle(); }
    });

    var rateSel = el('select', {
      class: 'reader-rate',
      title: '朗读速度',
      onchange: function (e) {
        self.rate = parseFloat(e.target.value);
        if (self.isPlaying) self._speak();
      }
    });
    RATES.forEach(function (r) {
      var opt = el('option', { value: r }, r + '×');
      if (r === self.rate) opt.selected = true;
      rateSel.appendChild(opt);
    });

    var closeBtn = el('button', {
      class: 'reader-close',
      title: '关闭 (Esc)',
      'aria-label': '关闭',
      html: ICON.close,
      onclick: function () { self.close(); }
    });

    var controls = el('div', { class: 'reader-controls' }, [
      this.playBtn, rateSel, closeBtn
    ]);

    var inner = el('div', { class: 'reader-content-inner' });
    this.text.split('\n\n').forEach(function (para) {
      inner.appendChild(el('p', null, para));
    });
    var content = el('div', { class: 'reader-content' }, inner);

    this.overlay = el('div', { class: 'reader-overlay open' }, [controls, content]);
    document.body.appendChild(this.overlay);
    document.body.style.overflow = 'hidden';

    this._keyHandler = function (e) {
      if (e.key === 'Escape') { e.preventDefault(); self.close(); }
      else if (e.key === ' ' && !/input|textarea|select/i.test(e.target.tagName)) {
        e.preventDefault();
        self.toggle();
      }
    };
    document.addEventListener('keydown', this._keyHandler);

    // v8.2 · 切到后台再回前台时,wake lock 自动失效,需要重新请求
    this._visHandler = function () {
      if (document.visibilityState === 'visible' && self.isPlaying) {
        self._requestWakeLock();
      }
    };
    document.addEventListener('visibilitychange', this._visHandler);
  };

  Reader.prototype.toggle = function () {
    if (this.isPlaying) this.pause(); else this.play();
  };

  Reader.prototype.play = function () {
    this._userPaused = false;
    this._requestWakeLock();  // v8.2 · 播放时请求 wake lock
    if (this.synth.paused && this.utter) {
      this.synth.resume();
    } else {
      this._speak();
    }
    this._setPlaying(true);
  };

  Reader.prototype._speak = function () {
    this.synth.cancel();
    this.utter = new SpeechSynthesisUtterance(this.text);
    this.utter.lang = 'zh-CN';
    this.utter.rate = this.rate;
    this.utter.pitch = 1.0;
    this.utter.volume = 1.0;
    var self = this;
    this.utter.onend = function () {
      self._setPlaying(false);
      // v8.1 · 章末自动接下一章(除非用户主动暂停)
      if (!self._userPaused) self._autoNext();
    };
    this.utter.onerror = function (e) {
      if (e.error !== 'interrupted' && e.error !== 'canceled') {
        console.warn('[Reader] TTS error:', e);
      }
    };
    this.synth.speak(this.utter);
  };

  // v8.1 · 自动接下一章 · 章末停顿 800ms,从下一章首开始读
  Reader.prototype._autoNext = function () {
    if (!this.chapter) return;
    var chapters = $$('section.chapter');
    var idx = chapters.indexOf(this.chapter);
    if (idx < 0 || idx >= chapters.length - 1) return;
    var nextCh = chapters[idx + 1];
    var nextText = extractText(nextCh, null);
    if (!nextText) return;
    this.chapter = nextCh;
    this.text = nextText;
    this._updateContent();
    var self = this;
    setTimeout(function () {
      if (!self._userPaused) {
        self._speak();
        self._setPlaying(true);
      }
    }, 800);
  };

  // v8.1 · 更新 overlay 内容(自动接下章时重填新章节文本)
  Reader.prototype._updateContent = function () {
    if (!this.overlay) return;
    var inner = this.overlay.querySelector('.reader-content-inner');
    if (!inner) return;
    inner.innerHTML = '';
    this.text.split('\n\n').forEach(function (para) {
      var p = document.createElement('p');
      p.textContent = para;
      inner.appendChild(p);
    });
    var content = this.overlay.querySelector('.reader-content');
    if (content) content.scrollTop = 0;
  };

  Reader.prototype.pause = function () {
    if (this.synth.speaking && !this.synth.paused) this.synth.pause();
    this._userPaused = true;  // v8.1 · 标记主动暂停 → 章末不自动接下章
    this._releaseWakeLock();  // v8.2 · 暂停时释放 wake lock
    this._setPlaying(false);
  };

  Reader.prototype._setPlaying = function (playing) {
    this.isPlaying = playing;
    if (this.playBtn) {
      this.playBtn.innerHTML = playing ? ICON.pause : ICON.play;
      this.playBtn.setAttribute('aria-label', playing ? '暂停' : '播放');
    }
  };

  Reader.prototype.close = function () {
    this.synth.cancel();
    this.isPlaying = false;
    this._releaseWakeLock();  // v8.2 · 关闭释放 wake lock
    if (this.overlay) {
      this.overlay.remove();
      this.overlay = null;
    }
    document.body.style.overflow = '';
    if (this._keyHandler) {
      document.removeEventListener('keydown', this._keyHandler);
      this._keyHandler = null;
    }
    if (this._visHandler) {
      document.removeEventListener('visibilitychange', this._visHandler);
      this._visHandler = null;
    }
  };

  // ─── 启动 · 按需加载的 reader 自动 open ────────────────────
  // bootstrap(99_footer.html 内联)负责入口注入 + URL/R 键触发
  // 这里只在 reader.js 真正被加载后,读取 __readerOpts 自动 open
  function boot() {
    var r = new Reader();
    window.__reader = r;
    r.open(window.__readerOpts || {});
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
