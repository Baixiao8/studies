/* ==========================================================================
 * Reader · 极简听书组件
 * v7.0 · 2026-05-24 · 通用化重写
 *
 * 设计原则:
 *   - 只做一件事:把当前章节的可朗读文本读出来
 *   - 只有 3 个控件:播放/暂停 · 速度 · 关闭
 *   - 无主题切换 / 无字号调节 / 无章节跳转 / 无定时关闭 / 无音频文件
 *   - 用浏览器原生 SpeechSynthesis,零依赖、零成本
 *
 * 触发(任一即可):
 *   - URL ?listen=1 或 ?reader=1
 *   - 键盘 R 键
 *   - window.activateReader()
 *
 * 作为「公共组件」,不为任何特定报告专门定制。
 * ========================================================================== */

(function () {
  'use strict';

  // 黑名单:这些元素的文本不朗读
  var EXCLUDE_SELECTORS = [
    'svg', 'svg *', 'table',
    '.hero', '.hero-keypoints', '.hero-toc-section',
    '.number-strip', '.section-tag',
    '.sticky-nav', '.mini-toc', '.progress-bar',
    '.svg-frame', '.svg-caption',
    'script', 'style', '.ref', '.chip',
    '.reader-overlay'
  ];
  var INCLUDE_TAGS = 'h2,h3,h4,p,li,blockquote';
  var RATES = [0.75, 1.0, 1.5];

  // ──────────────────────────────────────────────────────────────
  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (k === 'class') n.className = attrs[k];
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

  // 当前视口里占比最大的章节
  function getVisibleChapter() {
    var chapters = $$('section.chapter');
    if (chapters.length === 0) return document.body;
    var best = chapters[0];
    var bestVis = -1;
    var vh = window.innerHeight;
    chapters.forEach(function (ch) {
      var r = ch.getBoundingClientRect();
      var vis = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
      if (vis > bestVis) {
        bestVis = vis;
        best = ch;
      }
    });
    return best;
  }

  function extractText(scope) {
    return $$(INCLUDE_TAGS, scope)
      .filter(function (n) { return !isExcluded(n); })
      .map(function (n) {
        return (n.textContent || '').replace(/\s+/g, ' ').trim();
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
  }

  Reader.prototype.open = function () {
    if (this.overlay) return;
    var self = this;

    var chapter = getVisibleChapter();
    this.text = extractText(chapter);
    if (!this.text) {
      console.warn('[Reader] 当前章节没有可朗读文本');
      return;
    }

    // === 控件构建 ===
    this.playBtn = el('button', {
      class: 'reader-play',
      title: '播放 / 暂停 (Space)',
      onclick: function () { self.toggle(); }
    }, '▶');

    var rateSel = el('select', {
      class: 'reader-rate',
      title: '朗读速度',
      onchange: function (e) {
        self.rate = parseFloat(e.target.value);
        if (self.isPlaying) self._speak();
      }
    });
    RATES.forEach(function (r) {
      var opt = el('option', { value: r }, r + 'x');
      if (r === self.rate) opt.selected = true;
      rateSel.appendChild(opt);
    });

    var closeBtn = el('button', {
      class: 'reader-close',
      title: '关闭 (ESC)',
      onclick: function () { self.close(); }
    }, '✕');

    var controls = el('div', { class: 'reader-controls' }, [
      this.playBtn,
      rateSel,
      closeBtn
    ]);

    var contentInner = el('div', { class: 'reader-content-inner' });
    // 用纯文本显示,保留段落分隔
    this.text.split('\n\n').forEach(function (para) {
      contentInner.appendChild(el('p', null, para));
    });

    var content = el('div', { class: 'reader-content' }, contentInner);

    this.overlay = el('div', { class: 'reader-overlay open' }, [controls, content]);
    document.body.appendChild(this.overlay);
    document.body.style.overflow = 'hidden';

    // === 键盘 ===
    this._escHandler = function (e) {
      if (e.key === 'Escape') {
        e.preventDefault();
        self.close();
      } else if (e.key === ' ') {
        var inField = /input|textarea|select/i.test(e.target.tagName);
        if (!inField) {
          e.preventDefault();
          self.toggle();
        }
      }
    };
    document.addEventListener('keydown', this._escHandler);
  };

  Reader.prototype.toggle = function () {
    if (this.isPlaying) this.pause();
    else this.play();
  };

  Reader.prototype.play = function () {
    if (this.synth.paused && this.utter) {
      this.synth.resume();
    } else {
      this._speak();
    }
    this.isPlaying = true;
    if (this.playBtn) this.playBtn.textContent = '⏸';
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
      self.isPlaying = false;
      if (self.playBtn) self.playBtn.textContent = '▶';
    };
    this.utter.onerror = function (e) {
      if (e.error !== 'interrupted' && e.error !== 'canceled') {
        console.warn('[Reader] TTS error:', e);
      }
    };
    this.synth.speak(this.utter);
  };

  Reader.prototype.pause = function () {
    if (this.synth.speaking && !this.synth.paused) {
      this.synth.pause();
    }
    this.isPlaying = false;
    if (this.playBtn) this.playBtn.textContent = '▶';
  };

  Reader.prototype.close = function () {
    this.synth.cancel();
    this.isPlaying = false;
    if (this.overlay) {
      this.overlay.remove();
      this.overlay = null;
    }
    document.body.style.overflow = '';
    if (this._escHandler) {
      document.removeEventListener('keydown', this._escHandler);
      this._escHandler = null;
    }
  };

  // ──────────────────────────────────────────────────────────────
  // 启动:bootstrap 加载本脚本时,通常用户已经触发了听书
  // 自动打开 overlay 并提示用户点 ▶ 开始(浏览器策略要求用户手势触发 TTS)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  function boot() {
    var r = new Reader();
    window.__reader = r;
    r.open();
  }
})();
