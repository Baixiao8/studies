/* ==========================================================================
 * Reader · 阅读 + 听书模式
 * v5.0 · 2026-05-23
 * 浏览器原生 SpeechSynthesis + MediaSession + localStorage
 *
 * 功能覆盖(对照 PRD-reader-mode.md):
 * P0: F-001~F-013 沉浸阅读 / TTS / 段落高亮 / 字号配色 / 进度记忆 / 移动响应
 * P1: F-101~F-107 定时关闭 / 章末接下章 / mini player / 多音色 / Media Session / 9 档倍速 / 语义朗读
 * P2: F-201~F-205 段落点击播放 / URL 分享 / 进度条断点 / 听书时长 / 关键段落标记
 * ========================================================================== */

(function () {
  'use strict';

  /* ============================================================ */
  /* 1. 常量与黑白名单(必须与 READER_RULES.md 完全一致)            */
  /* ============================================================ */

  var EXCLUDE_SELECTORS = [
    'svg', 'svg *',
    '.hero', '.hero-keypoints', '.hero-toc-section',
    '.number-strip', '.section-tag',
    '.sticky-nav', '.mini-toc', '.progress-bar',
    'table',
    'script', 'style', '.ref', '.chip',
    '.svg-frame', '.svg-caption',
    '.reader-trigger', '.reader-overlay', '.reader-mini'
  ];

  var INCLUDE_TAGS = ['h2', 'h3', 'h4', 'p', 'li', 'blockquote'];

  // 字号档位(S / M / L / XL)
  var FONT_SIZES = ['S', 'M', 'L', 'XL'];

  // 行距档位
  var LINE_HEIGHTS = ['tight', 'normal', 'loose'];

  // 主题
  var THEMES = ['paper', 'dark', 'green'];

  // 倍速档位(9 档,微信读书风)
  var RATES = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0];

  // 定时关闭档位(分钟,'chapter' 表示本章末)
  var SLEEP_OPTIONS = [
    { value: null, label: '关闭' },
    { value: 5, label: '5 分钟' },
    { value: 10, label: '10 分钟' },
    { value: 15, label: '15 分钟' },
    { value: 30, label: '30 分钟' },
    { value: 60, label: '60 分钟' },
    { value: 'chapter', label: '本章末' }
  ];

  // 中文 TTS 平均速度(字/分钟)用于估算章节时长
  var CHARS_PER_MIN_AT_1X = 280;

  /* ============================================================ */
  /* 2. 工具函数                                                   */
  /* ============================================================ */

  function $(sel, root) { return (root || document).querySelector(sel); }
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
        else if (k === 'style' && typeof attrs[k] === 'object') {
          for (var s in attrs[k]) n.style[s] = attrs[k][s];
        }
        else n.setAttribute(k, attrs[k]);
      }
    }
    if (children) {
      (Array.isArray(children) ? children : [children]).forEach(function (c) {
        if (c == null) return;
        if (typeof c === 'string') n.appendChild(document.createTextNode(c));
        else n.appendChild(c);
      });
    }
    return n;
  }

  function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  }
  function isMobile() {
    return window.matchMedia('(max-width: 768px)').matches;
  }

  function debounce(fn, ms) {
    var t;
    return function () {
      var args = arguments;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(null, args); }, ms);
    };
  }

  /* ============================================================ */
  /* 3. localStorage 包装(配置 + 进度)                            */
  /* ============================================================ */

  var STORAGE_KEY = 'studies-reader-v1';
  var REPORT_ID = (function () {
    var m = location.pathname.match(/\/reports\/([^\/]+)/);
    return m ? m[1] : 'unknown';
  })();

  var DEFAULT_CONFIG = {
    theme: 'paper',
    fontSize: 'M',
    lineHeight: 'normal',
    rate: 1.0,
    voice: '',
    autoNextChapter: true,
    sleepTimer: null
  };

  function loadStore() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : { config: {}, progress: {} };
    } catch (e) { return { config: {}, progress: {} }; }
  }

  function saveStore(data) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); }
    catch (e) { /* quota exceeded, ignore */ }
  }

  function getConfig() {
    var store = loadStore();
    return Object.assign({}, DEFAULT_CONFIG, store.config || {});
  }

  function setConfig(patch) {
    var store = loadStore();
    store.config = Object.assign({}, store.config || {}, patch);
    saveStore(store);
  }

  function getProgress() {
    var store = loadStore();
    return (store.progress || {})[REPORT_ID] || null;
  }

  var saveProgressDebounced = debounce(function (data) {
    var store = loadStore();
    if (!store.progress) store.progress = {};
    store.progress[REPORT_ID] = Object.assign({}, data, { ts: Date.now() });
    saveStore(store);
  }, 500);

  /* ============================================================ */
  /* 4. 内容提取 · 黑白名单过滤 + 段落 ID                          */
  /* ============================================================ */

  function isExcluded(node) {
    for (var i = 0; i < EXCLUDE_SELECTORS.length; i++) {
      if (node.matches && node.matches(EXCLUDE_SELECTORS[i])) return true;
      if (node.closest && node.closest(EXCLUDE_SELECTORS[i])) return true;
    }
    return false;
  }

  function chunkId(node, fallbackIdx) {
    // 优先用现有 id
    if (node.id) return 'reader-' + node.id;
    var chapter = node.closest('.chapter');
    var chapterId = chapter ? (chapter.id || 'chx') : 'chx';
    // 用 chapter id + 顺序 hash
    return 'reader-' + chapterId + '-' + fallbackIdx;
  }

  function classify(node) {
    if (node.matches('h2')) return 'h2';
    if (node.matches('h3')) return 'h3';
    if (node.matches('h4')) return 'h4';
    if (node.matches('p.lead')) return 'lead';
    if (node.matches('p.plain')) return 'plain';
    var callout = node.closest('.callout');
    if (callout) {
      if (callout.classList.contains('sharp')) return 'sharp';
      if (callout.classList.contains('ops')) return 'ops';
      if (callout.classList.contains('you')) return 'you';
      if (callout.classList.contains('protocol')) return 'protocol';
      if (callout.classList.contains('story')) return 'story';
      if (callout.classList.contains('note')) return 'note';
    }
    if (node.matches('li')) return 'li';
    return 'p';
  }

  // TTS 朗读时的文本增强(加前缀 / 停顿 / 语义化)
  function semanticAugment(node, type) {
    var text = (node.textContent || '').replace(/\s+/g, ' ').trim();
    if (!text) return '';

    // 反共识:加前缀
    var callout = node.closest('.callout');
    if (callout && callout.classList.contains('sharp')) {
      if (node.matches('.label')) return ''; // label 本身略过(避免重复)
      // 第一个段落加前缀
      var firstP = callout.querySelector('p:not(.label)');
      if (node === firstP) return '反共识。' + text;
    }
    // 协议:加前缀
    if (callout && callout.classList.contains('protocol')) {
      if (node.matches('.label')) return '';
      if (node.matches('h4')) return '协议。' + text;
    }
    // 第二人称剧本:加前缀
    if (callout && callout.classList.contains('you')) {
      if (node.matches('.label')) return '';
      var firstPy = callout.querySelector('p:not(.label)');
      if (node === firstPy) return '设身处地。' + text;
    }
    // 3 件事清单:加前缀
    if (callout && callout.classList.contains('ops')) {
      if (node.matches('.label')) return '';
    }
    // 故事钩子
    if (callout && callout.classList.contains('story')) {
      if (node.matches('.label')) return '';
      var firstPs = callout.querySelector('p:not(.label)');
      if (node === firstPs) return '故事。' + text;
    }
    // .stop 块加前缀
    if (node.matches('.stop') || node.closest('.stop')) {
      return '何时停。' + text.replace(/^[⚠\s]*何时停\s*/, '');
    }
    // 章节标题
    if (type === 'h2' || type === 'h3') {
      // 跳过装饰前缀(如 "4.6" 这种 .pre)
      var preEl = node.querySelector('.pre');
      var clean = preEl ? text.replace(preEl.textContent, '').trim() : text;
      var prefix = type === 'h2' ? '本章。' : '小节。';
      return prefix + clean;
    }

    return text;
  }

  function extractChunks(scope) {
    var chunks = [];
    var nodes = $$(INCLUDE_TAGS.join(','), scope);
    var idx = 0;

    nodes.forEach(function (node) {
      if (isExcluded(node)) return;
      // 跳过纯 callout label(没有实际内容)
      if (node.matches('.callout .label')) return;
      // 跳过 callout 外层(只读 callout 内部段落)
      var type = classify(node);
      var text = semanticAugment(node, type);
      if (!text || text.length < 2) return;
      var id = chunkId(node, idx++);
      node.setAttribute('data-reader-id', id);
      chunks.push({
        id: id,
        node: node,
        text: text,
        type: type,
        chars: text.length,
        chapter: node.closest('.chapter')
      });
    });

    return chunks;
  }

  /* ============================================================ */
  /* 5. TTS 引擎封装                                               */
  /* ============================================================ */

  function TTSEngine() {
    this.synth = window.speechSynthesis;
    this.voices = [];
    this.currentUtter = null;
    this.onEndCb = null;
    this.onErrCb = null;
    this._loadVoices();
  }

  TTSEngine.prototype._loadVoices = function () {
    var self = this;
    this.voices = this.synth ? this.synth.getVoices() : [];
    if (this.synth && this.voices.length === 0) {
      this.synth.addEventListener('voiceschanged', function () {
        self.voices = self.synth.getVoices();
      });
    }
  };

  TTSEngine.prototype.getChineseVoices = function () {
    return this.voices.filter(function (v) {
      return /zh|cmn|yue/i.test(v.lang);
    });
  };

  TTSEngine.prototype.speak = function (text, opts) {
    if (!this.synth) return;
    this.cancel();
    var self = this;
    var utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'zh-CN';
    utter.rate = (opts && opts.rate) || 1.0;
    utter.pitch = 1.0;
    utter.volume = 1.0;
    if (opts && opts.voice) {
      var v = this.voices.find(function (x) { return x.name === opts.voice; });
      if (v) utter.voice = v;
    }
    utter.onend = function () {
      if (self.onEndCb) self.onEndCb();
    };
    utter.onerror = function (e) {
      // iOS / 浏览器中断不算异常,只有真正错误才报告
      if (e.error && e.error !== 'interrupted' && e.error !== 'canceled') {
        if (self.onErrCb) self.onErrCb(e);
      }
    };
    this.currentUtter = utter;
    // iOS Safari: 必须在用户手势内调用 speak
    try { this.synth.speak(utter); } catch (e) {}
  };

  TTSEngine.prototype.pause = function () {
    if (this.synth && this.synth.speaking) this.synth.pause();
  };

  TTSEngine.prototype.resume = function () {
    if (this.synth && this.synth.paused) this.synth.resume();
  };

  TTSEngine.prototype.cancel = function () {
    if (this.synth) this.synth.cancel();
    this.currentUtter = null;
  };

  /* ============================================================ */
  /* 6. Reader 主类                                                */
  /* ============================================================ */

  function Reader() {
    this.tts = new TTSEngine();
    this.config = getConfig();
    this.chunks = [];
    this.allChunks = [];      // 全报告所有 chunks(用于跨章衔接)
    this.currentIdx = -1;
    this.isOpen = false;
    this.isPlaying = false;
    this.overlay = null;
    this.mini = null;
    this.sleepDeadline = null;
    this.sleepTicker = null;
    this.scrollLockTop = 0;
    this.miniBeforeScrollY = 0;

    // v6 · 音频模式(高音质 Azure Neural,优先于浏览器原生 TTS)
    this.audioEl = null;
    this.audioMode = false;            // 当前是否使用音频模式
    this.audioAvailable = false;       // 当前章是否有 audio 可用
    this.audioSegments = null;         // 段落 ID → 时间秒数 映射
    this.audioChapterId = null;
    this.audioLastSegIdx = -1;
  }

  Reader.prototype.init = function () {
    var self = this;
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () { self._init(); });
    } else {
      this._init();
    }
  };

  Reader.prototype._init = function () {
    this._injectTrigger();
    this._bindShortcuts();
    this._setupMediaSession();
    this._handleHashSegmentNav();
    // 听书时长估算:遍历 12 章字数有开销,异步到 idle 时间,不阻塞首屏交互
    var self = this;
    if ('requestIdleCallback' in window) {
      window.requestIdleCallback(function () { self._estimateListenTime(); }, { timeout: 3000 });
    } else {
      setTimeout(function () { self._estimateListenTime(); }, 800);
    }
  };

  /* ─── 触发按钮 ────────────────────────────────────────────── */
  Reader.prototype._injectTrigger = function () {
    var self = this;
    var btn = el('button', {
      class: 'reader-trigger',
      title: '阅读 + 听书 (R)',
      'aria-label': '打开阅读模式'
    });
    btn.innerHTML = '<span style="font-size:18px">▶</span>' +
      '<span class="reader-trigger-label">R · 阅读 + 听书</span>';
    btn.addEventListener('click', function () { self.open(); });
    document.body.appendChild(btn);
    this.triggerBtn = btn;
  };

  Reader.prototype._bindShortcuts = function () {
    var self = this;
    document.addEventListener('keydown', function (e) {
      var inField = /input|textarea|select/i.test(e.target.tagName);
      if (inField) return;
      if (e.key === 'r' || e.key === 'R') {
        if (!self.isOpen) { e.preventDefault(); self.open(); }
      }
      if (e.key === 'Escape' && self.isOpen) { e.preventDefault(); self.close(); }
      if (!self.isOpen) return;
      if (e.key === ' ') { e.preventDefault(); self.togglePlay(); }
      if (e.key === 'ArrowRight') { e.preventDefault(); self.next(); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); self.prev(); }
    });
  };

  /* ─── 检测当前章节 ─────────────────────────────────────────── */
  Reader.prototype._detectVisibleChapter = function () {
    var chapters = $$('.chapter');
    if (chapters.length === 0) return document.querySelector('main') || document.body;
    var best = null;
    var bestVisible = -1;
    var vh = window.innerHeight;
    chapters.forEach(function (ch) {
      var r = ch.getBoundingClientRect();
      var visible = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
      if (visible > bestVisible) { bestVisible = visible; best = ch; }
    });
    return best || chapters[0];
  };

  /* ─── 听书时长估算 ─────────────────────────────────────────── */
  Reader.prototype._estimateListenTime = function () {
    var chapters = $$('.chapter');
    chapters.forEach(function (ch) {
      var chunks = extractChunks(ch);
      var totalChars = chunks.reduce(function (s, c) { return s + c.chars; }, 0);
      var mins = Math.ceil(totalChars / CHARS_PER_MIN_AT_1X);
      // 在章节标题旁加听书时长
      var h2 = ch.querySelector('h2');
      if (h2 && !h2.querySelector('.reader-listen-time')) {
        var badge = el('span', {
          class: 'reader-listen-time',
          title: '听书估算 · 1x 倍速'
        }, '🎧 ' + mins + ' 分钟');
        h2.appendChild(document.createTextNode(' '));
        h2.appendChild(badge);
      }
    });
  };

  /* ─── 打开 / 关闭 ──────────────────────────────────────────── */
  // 渐进式打开:① 立即骨架 paint ② 下一帧算 chunks ③ 再下一帧填内容
  // 用户感知"瞬间响应",实际重活分摊到 3 帧(每帧 16ms 内不阻塞)
  Reader.prototype.open = function (opts) {
    if (this.isOpen) return;
    var self = this;
    this.scrollLockTop = window.scrollY;
    var chapter = (opts && opts.chapter) || this._detectVisibleChapter();
    if (!chapter) return;

    // ① 立即:锁滚动 + 显示空骨架(用户感知瞬间响应)
    document.body.classList.add('reader-open');
    document.body.style.top = -this.scrollLockTop + 'px';
    document.body.style.position = 'fixed';
    document.body.style.width = '100%';
    this._renderSkeleton();
    this.isOpen = true;
    this._hideMini();

    // ② 下一帧:计算 chunks + 起始段(让骨架先 paint)
    requestAnimationFrame(function () {
      // extractChunks 给原节点加 data-reader-id —— 必须在 _detectVisibleChunkIdx 之前
      self.chunks = extractChunks(chapter);
      self.allChunks = null;
      if (self.chunks.length === 0) {
        console.warn('[Reader] 当前章节无可读段落');
        self.close();
        return;
      }

      // 异步检测 + 加载音频(不阻塞)· 加载完后启用切换按钮
      var chapterId = chapter.id;
      if (chapterId) {
        self._loadAudio(chapterId).then(function (ok) {
          self.audioAvailable = !!ok;
          // 首次访问默认开启音频(如果可用)
          if (ok && self.config.audioMode !== false) {
            self.audioMode = true;
          }
          self._updateAudioToggle();
          if (self.audioEl) {
            self.audioEl.playbackRate = self.config.rate || 1.0;
          }
        });
      }

      // 计算起始段落 · 优先级:opts.startId > 视口可视段 > localStorage > 0
      var startIdx = -1;
      if (opts && opts.startId) {
        startIdx = self.chunks.findIndex(function (c) { return c.id === opts.startId; });
      }
      if (startIdx < 0) {
        startIdx = self._detectVisibleChunkIdx(chapter);
      }
      if (startIdx < 0) {
        var prog = getProgress();
        if (prog && prog.chapter === chapter.id && (Date.now() - prog.ts) < 86400000) {
          startIdx = self.chunks.findIndex(function (c) { return c.id === prog.chunkId; });
        }
      }
      if (startIdx < 0) startIdx = 0;
      self.currentIdx = startIdx;

      // ③ 再下一帧:填充内容 + 高亮(让 chunks 算完 paint 一次再做重活)
      requestAnimationFrame(function () {
        self._renderOverlay(chapter);
        self._applyConfig();
        requestAnimationFrame(function () {
          self._highlightChunk(startIdx);
        });
      });
    });
  };

  // 立即显示骨架(空 overlay + 控制条)给用户"已响应"反馈
  Reader.prototype._renderSkeleton = function () {
    if (this.overlay) return;
    var overlay = el('div', {
      class: 'reader-overlay',
      'data-theme': this.config.theme,
      'data-size': this.config.fontSize,
      'data-lh': this.config.lineHeight
    });
    // 极简骨架:控制条占位 + 转圈
    overlay.appendChild(el('div', {
      class: 'reader-controls',
      style: { height: '56px' }
    }));
    overlay.appendChild(el('div', {
      class: 'reader-content',
      style: { textAlign: 'center', paddingTop: '120px', opacity: '0.5' }
    }, '正在加载...'));
    document.body.appendChild(overlay);
    this.overlay = overlay;
    requestAnimationFrame(function () { overlay.classList.add('open'); });
  };

  // 检测原始页面视口内最居中的可读段落
  // 注意:必须在 extractChunks() 之后调用(node 才有 data-reader-id)
  Reader.prototype._detectVisibleChunkIdx = function (chapter) {
    var vh = window.innerHeight;
    var center = vh / 2;
    var best = -1;
    var bestDist = Infinity;
    for (var i = 0; i < this.chunks.length; i++) {
      var node = this.chunks[i].node;
      if (!node || !node.getBoundingClientRect) continue;
      var r = node.getBoundingClientRect();
      // 完全在视口外的跳过
      if (r.bottom < 0 || r.top > vh) continue;
      // 太小的元素跳过(如空段)
      if (r.height < 4) continue;
      var nodeCenter = r.top + r.height / 2;
      var dist = Math.abs(nodeCenter - center);
      if (dist < bestDist) {
        bestDist = dist;
        best = i;
      }
    }
    return best;
  };

  // 跨章 chunks · lazy 构建(仅 _onChapterEnd 需要时调用)
  Reader.prototype._buildAllChunks = function () {
    if (this.allChunks) return this.allChunks;
    var all = [];
    $$('.chapter').forEach(function (ch) {
      all = all.concat(extractChunks(ch));
    });
    this.allChunks = all;
    return all;
  };

  Reader.prototype.close = function () {
    if (!this.isOpen) return;
    // 关 sheet
    this._closeSheet();
    // 暂停 TTS,但保留进度(可能用 mini player)
    var wasPlaying = this.isPlaying;
    if (this.tts) this.tts.pause();
    this._removeOverlay();
    document.body.classList.remove('reader-open');
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.width = '';
    window.scrollTo(0, this.scrollLockTop);
    this.isOpen = false;
    if (wasPlaying && this.currentIdx >= 0) {
      // 关闭时如果在播,显示 mini player
      this._showMini();
      // 在 mini 状态恢复播放
      var self = this;
      setTimeout(function () { self._continueMini(); }, 300);
    }
  };

  /* ─── Overlay 渲染 ─────────────────────────────────────────── */
  Reader.prototype._renderOverlay = function (chapter) {
    var self = this;
    var overlay = el('div', {
      class: 'reader-overlay',
      'data-theme': this.config.theme,
      'data-size': this.config.fontSize,
      'data-lh': this.config.lineHeight
    });

    var controls = this._renderControls();
    var content = el('div', { class: 'reader-content' });
    var inner = el('div', { class: 'reader-content-inner' });

    // iOS 锁屏提示:第一次显示 toast,5 秒后自动消失,用户关闭后永久不再
    if (isIOS()) {
      this._showIOSToastIfNeeded();
    }

    // 克隆章节内容到 overlay
    var clone = this._buildReaderContent(chapter);
    inner.appendChild(clone);
    content.appendChild(inner);

    overlay.appendChild(controls);
    overlay.appendChild(content);

    document.body.appendChild(overlay);
    requestAnimationFrame(function () { overlay.classList.add('open'); });
    this.overlay = overlay;
    this.overlayContent = content;
    this.overlayInner = inner;

    // 锚点点击播放(P2: F-201 段落双向跳转)
    inner.addEventListener('click', function (e) {
      var target = e.target.closest('[data-reader-id]');
      if (!target) return;
      var id = target.getAttribute('data-reader-id');
      var idx = self.chunks.findIndex(function (c) { return c.id === id; });
      if (idx >= 0) { self.currentIdx = idx; self.play(); }
    });

    // 段落 hover 提示(桌面)
    if (!isMobile()) {
      $$('[data-reader-id]', inner).forEach(function (n) {
        n.style.cursor = 'pointer';
        n.title = '点击从这里开始朗读';
      });
    }
  };

  Reader.prototype._buildReaderContent = function (chapter) {
    var self = this;
    var frag = document.createDocumentFragment();

    // 标题(h2)+ 副标题
    var h2 = chapter.querySelector('h2');
    if (h2) frag.appendChild(this._cloneFiltered(h2));
    var sub = chapter.querySelector('.subtitle, .chapter-subtitle');
    if (sub) frag.appendChild(this._cloneFiltered(sub));

    // 逐个段落 + 占位
    var nodes = $$(INCLUDE_TAGS.join(',') + ', svg, table, figure', chapter);
    var seenIds = {};
    nodes.forEach(function (node) {
      // SVG / table 占位
      if (node.matches('svg, table')) {
        var label = node.matches('svg') ? '此处有可视化图表' : '此处有数据表格';
        var caption = '';
        // 找邻近的 caption
        var capEl = node.parentElement && node.parentElement.querySelector('.svg-caption, caption');
        if (capEl) caption = capEl.textContent.trim();
        if (caption) label += ' · ' + caption;
        frag.appendChild(el('div', { class: 'reader-placeholder' }, label + '(回原页查看)'));
        return;
      }
      // figure 包含 svg 也跳
      if (node.matches('figure') && node.querySelector('svg, img')) return;
      if (isExcluded(node)) return;
      // h2 已经放过
      if (node.matches('h2')) return;
      // 拿到 reader-id
      var id = node.getAttribute('data-reader-id');
      if (id && seenIds[id]) return;
      if (id) seenIds[id] = true;
      // 复制(保留 reader-id 和必要的 class)
      var clone = self._cloneFiltered(node);
      if (id) clone.setAttribute('data-reader-id', id);
      // callout 需要带外层结构
      var callout = node.closest('.callout');
      if (callout && !frag.contains(callout)) {
        // 第一次遇到这个 callout 的子节点 - 整个克隆 callout
        var calloutDom = node._readerCalloutDone ? null : self._cloneCallout(callout, chapter);
        node._readerCalloutDone = true;
        if (calloutDom) frag.appendChild(calloutDom);
        return;
      }
      // 普通段落
      if (!callout) frag.appendChild(clone);
    });

    // 重置 _readerCalloutDone 标志
    $$('.callout *', chapter).forEach(function (n) { n._readerCalloutDone = false; });

    return frag;
  };

  Reader.prototype._cloneCallout = function (callout, chapter) {
    var self = this;
    var newCallout = el('div', { class: callout.className });
    // label
    var label = callout.querySelector('.label');
    if (label) newCallout.appendChild(el('div', { class: 'label' }, label.textContent));
    // 子段落(p / h4 / ol / ul)
    $$('p, h4, ol, ul', callout).forEach(function (child) {
      // 跳过嵌套的 callout
      if (child.closest('.callout') !== callout) return;
      var c = self._cloneFiltered(child);
      var id = child.getAttribute('data-reader-id');
      if (id) c.setAttribute('data-reader-id', id);
      child._readerCalloutDone = true;
      newCallout.appendChild(c);
    });
    // .stop 块
    var stop = callout.querySelector('.stop');
    if (stop) {
      var stopDiv = el('div', { class: 'stop' }, stop.innerHTML);
      stopDiv.innerHTML = stop.innerHTML;
      var stopId = stop.getAttribute('data-reader-id');
      if (stopId) stopDiv.setAttribute('data-reader-id', stopId);
      newCallout.appendChild(stopDiv);
    }
    return newCallout;
  };

  Reader.prototype._cloneFiltered = function (node) {
    var clone = node.cloneNode(true);
    // 移除内部 SVG 和表格
    EXCLUDE_SELECTORS.forEach(function (sel) {
      $$(sel, clone).forEach(function (n) {
        if (n.parentElement === clone) n.remove();
      });
    });
    return clone;
  };

  Reader.prototype._removeOverlay = function () {
    if (this.overlay) {
      this.overlay.classList.remove('open');
      var o = this.overlay;
      setTimeout(function () { if (o.parentElement) o.remove(); }, 280);
      this.overlay = null;
    }
    // 清理孤立 sleep menu(挂在 body 上,需要手动移除)
    $$('.reader-sleep-menu').forEach(function (n) {
      if (n.parentElement) n.remove();
    });
    // 清理 sheet
    if (this.sheet && this.sheet.parentElement) this.sheet.remove();
    if (this.sheetMask && this.sheetMask.parentElement) this.sheetMask.remove();
    this.sheet = null;
    this.sheetMask = null;
  };

  /* ─── 控制条渲染 ──────────────────────────────────────────── */
  Reader.prototype._renderControls = function () {
    var self = this;

    function btn(label, onclick, opts) {
      opts = opts || {};
      var b = el('button', {
        title: opts.title || '',
        'aria-label': opts.title || label,
        onclick: onclick,
        class: opts.class || ''
      });
      b.innerHTML = label;
      return b;
    }

    // 主播放按钮
    var playBtn = btn('▶', function () { self.togglePlay(); }, {
      title: '播放 / 暂停 (Space)',
      class: 'reader-play'
    });
    this.playBtn = playBtn;

    // 上一段 / 下一段
    var prevBtn = btn('◀', function () { self.prev(); }, {
      title: '上一段 (←)', class: 'reader-prev'
    });
    var nextBtn = btn('▶|', function () { self.next(); }, {
      title: '下一段 (→)', class: 'reader-next'
    });

    // 倍速 select(固定 72px 宽)
    var rateOpts = RATES.map(function (r) {
      return '<option value="' + r + '"' + (self.config.rate === r ? ' selected' : '') + '>' + r + 'x</option>';
    }).join('');
    var rateSel = el('div', { class: 'reader-select-wrap reader-rate-wrap', title: '朗读速度' });
    rateSel.innerHTML = '<select>' + rateOpts + '</select>';
    rateSel.querySelector('select').addEventListener('change', function (e) {
      var v = parseFloat(e.target.value);
      self.config.rate = v;
      setConfig({ rate: v });
      // 音频模式:直接调 playbackRate(无缝切换)
      if (self.audioEl) self.audioEl.playbackRate = v;
      // Web TTS:正在播则重启当前段以新速度
      if (self.isPlaying && !self.audioMode) self._speakCurrent();
    });

    // 章节 select
    var chapters = $$('.chapter');
    var chapterOpts = chapters.map(function (ch, i) {
      var h2 = ch.querySelector('h2');
      var t = h2 ? h2.textContent.replace(/🎧.*/, '').trim() : '章节 ' + (i + 1);
      if (t.length > 18) t = t.slice(0, 18) + '…';
      return '<option value="' + (ch.id || 'chx-' + i) + '">' + (i + 1) + '. ' + t + '</option>';
    }).join('');
    var chSel = el('div', { class: 'reader-select-wrap reader-chapter-wrap', title: '跳转到章节' });
    chSel.innerHTML = '<select>' + chapterOpts + '</select>';
    chSel.querySelector('select').addEventListener('change', function (e) {
      var ch = document.getElementById(e.target.value);
      if (ch) {
        self.close();
        setTimeout(function () { self.open({ chapter: ch }); }, 100);
      }
    });

    // 字号 - / +
    var fontDown = btn('A-', function () {
      var idx = FONT_SIZES.indexOf(self.config.fontSize);
      if (idx > 0) {
        self.config.fontSize = FONT_SIZES[idx - 1];
        setConfig({ fontSize: self.config.fontSize });
        self._applyConfig();
      }
    }, { title: '字号减小' });
    var fontUp = btn('A+', function () {
      var idx = FONT_SIZES.indexOf(self.config.fontSize);
      if (idx < FONT_SIZES.length - 1) {
        self.config.fontSize = FONT_SIZES[idx + 1];
        setConfig({ fontSize: self.config.fontSize });
        self._applyConfig();
      }
    }, { title: '字号增大' });

    // 行距循环
    var lhBtn = btn('☰', function () {
      var idx = LINE_HEIGHTS.indexOf(self.config.lineHeight);
      var next = LINE_HEIGHTS[(idx + 1) % LINE_HEIGHTS.length];
      self.config.lineHeight = next;
      setConfig({ lineHeight: next });
      self._applyConfig();
    }, { title: '切换行距' });

    // 主题 3 件套
    var themeGroup = el('div', { class: 'reader-theme-group' });
    THEMES.forEach(function (t) {
      var tb = el('button', {
        'data-t': t,
        title: '主题 · ' + t,
        class: self.config.theme === t ? 'active' : '',
        onclick: function () {
          self.config.theme = t;
          setConfig({ theme: t });
          self._applyConfig();
        }
      });
      themeGroup.appendChild(tb);
    });

    // 音色 select(P1: F-104)
    var voiceSel = el('div', { class: 'reader-select-wrap', title: '朗读音色' });
    var voices = this.tts.getChineseVoices();
    var voiceOpts = '<option value="">默认</option>' + voices.map(function (v) {
      var sel = self.config.voice === v.name ? ' selected' : '';
      return '<option value="' + v.name + '"' + sel + '>' + v.name.slice(0, 14) + '</option>';
    }).join('');
    voiceSel.innerHTML = '<select>' + voiceOpts + '</select>';
    voiceSel.querySelector('select').addEventListener('change', function (e) {
      self.config.voice = e.target.value;
      setConfig({ voice: e.target.value });
      if (self.isPlaying) self._speakCurrent();
    });
    // 隐藏 if no voices
    if (voices.length === 0) voiceSel.style.display = 'none';

    // 定时关闭按钮 + 菜单(fixed 定位,以 button 位置为锚)
    var sleepBtn = btn('⏱', function (e) {
      e.stopPropagation();
      var isOpen = sleepMenu.classList.contains('open');
      if (isOpen) {
        sleepMenu.classList.remove('open');
      } else {
        // 计算 fixed 定位:菜单在按钮上方 8px
        var rect = sleepBtn.getBoundingClientRect();
        sleepMenu.style.left = Math.max(8, rect.left + rect.width / 2 - 72) + 'px';
        sleepMenu.style.bottom = (window.innerHeight - rect.top + 8) + 'px';
        sleepMenu.style.top = 'auto';
        sleepMenu.classList.add('open');
      }
    }, { title: '定时关闭' });
    var sleepMenu = el('div', { class: 'reader-sleep-menu' });
    SLEEP_OPTIONS.forEach(function (opt) {
      var b = el('button', {
        class: self.config.sleepTimer === opt.value ? 'active' : '',
        onclick: function (ev) {
          ev.stopPropagation();
          self._setSleepTimer(opt.value);
          sleepMenu.classList.remove('open');
          $$('button', sleepMenu).forEach(function (x) { x.classList.remove('active'); });
          b.classList.add('active');
        }
      }, opt.label);
      sleepMenu.appendChild(b);
    });
    document.addEventListener('click', function (e) {
      if (!sleepBtn.contains(e.target) && !sleepMenu.contains(e.target)) {
        sleepMenu.classList.remove('open');
      }
    });
    // sleep menu 直接挂到 body(不在控制条内,避免被 sticky overflow 裁切)
    document.body.appendChild(sleepMenu);
    var sleepWrap = el('div', { class: 'reader-sleep-group' }, [sleepBtn]);

    // 设置按钮(移动端入口,桌面隐藏)
    var settingsBtn = btn('⚙', function () { self._toggleSheet(); }, {
      title: '更多设置', class: 'reader-settings-btn'
    });

    // 音频模式切换(默认隐藏,有音频时显示)
    var audioToggleBtn = btn('🤖 标准', function () { self._toggleAudioMode(); }, {
      title: '切换 Web TTS / 高音质录音', class: 'reader-audio-toggle'
    });
    audioToggleBtn.style.display = 'none';
    this.audioToggleBtn = audioToggleBtn;

    // 关闭按钮
    var closeBtn = btn('✕', function () { self.close(); }, {
      title: '关闭 (ESC)', class: 'reader-close'
    });

    // 给 chSel / fontDown/Up / lhBtn 加 mobile-hidden class(CSS 会处理隐藏)
    chSel.classList.add('reader-chapter-wrap');
    var fontGroup = el('div', { class: 'group reader-font-group' }, [fontDown, fontUp]);
    lhBtn.classList.add('reader-lh-btn');
    voiceSel.classList.add('voice-select-wrap');

    // 组装控制条
    // - 桌面端:全部显示
    // - 移动端:只显示 prev/play/next + speed + 音频切换 + ⚙ + ✕(其他在 sheet 里)
    var controls = el('div', { class: 'reader-controls' }, [
      el('div', { class: 'group' }, [prevBtn, playBtn, nextBtn]),
      el('div', { class: 'group' }, [rateSel]),
      el('div', { class: 'group audio-toggle-group' }, [audioToggleBtn]),
      el('div', { class: 'group mobile-secondary' }, [chSel]),
      fontGroup,
      el('div', { class: 'group mobile-secondary' }, [lhBtn]),
      el('div', { class: 'group mobile-secondary' }, [themeGroup]),
      el('div', { class: 'group mobile-secondary' }, [voiceSel]),
      el('div', { class: 'group mobile-secondary' }, [sleepWrap]),
      el('div', { class: 'spacer' }),
      el('div', { class: 'group' }, [settingsBtn, closeBtn])
    ]);

    return controls;
  };

  /* ─── iOS 提示 Toast(轻量,可关闭,可记忆) ────────────────── */
  Reader.prototype._showIOSToastIfNeeded = function () {
    try {
      if (localStorage.getItem('studies-reader-ios-toast-dismissed') === '1') return;
    } catch (e) {}
    var self = this;
    if (this.iosToast) return;
    var t = el('div', { class: 'reader-ios-toast' }, [
      document.createTextNode('💡 iOS 建议保持屏幕亮,避免朗读中断'),
    ]);
    var closeBtn = el('button', {
      class: 'close-x',
      onclick: function () {
        try { localStorage.setItem('studies-reader-ios-toast-dismissed', '1'); } catch (e) {}
        t.classList.remove('show');
        setTimeout(function () { if (t.parentElement) t.remove(); }, 350);
      }
    }, '✕');
    t.appendChild(closeBtn);
    document.body.appendChild(t);
    this.iosToast = t;
    requestAnimationFrame(function () { t.classList.add('show'); });
    // 5 秒后自动消失(用户没点关闭按钮的话)
    setTimeout(function () {
      if (t.parentElement && t.classList.contains('show')) {
        t.classList.remove('show');
        setTimeout(function () { if (t.parentElement) t.remove(); }, 350);
      }
    }, 5000);
  };

  /* ─── 设置 Sheet(移动端二级菜单) ─────────────────────────── */
  Reader.prototype._toggleSheet = function () {
    if (!this.sheet) {
      this._buildSheet();
    }
    var isOpen = this.sheet.classList.contains('open');
    if (isOpen) this._closeSheet();
    else this._openSheet();
  };

  Reader.prototype._openSheet = function () {
    if (!this.sheet) this._buildSheet();
    this.sheetMask.classList.add('open');
    this.sheet.classList.add('open');
  };

  Reader.prototype._closeSheet = function () {
    if (this.sheet) this.sheet.classList.remove('open');
    if (this.sheetMask) this.sheetMask.classList.remove('open');
  };

  Reader.prototype._buildSheet = function () {
    var self = this;
    var mask = el('div', {
      class: 'reader-sheet-mask',
      onclick: function () { self._closeSheet(); }
    });
    var sheet = el('div', { class: 'reader-sheet' });
    sheet.appendChild(el('div', { class: 'sheet-handle' }));

    // 行 1 · 章节跳转
    var chapters = $$('.chapter');
    var chOpts = chapters.map(function (ch, i) {
      var h2 = ch.querySelector('h2');
      var t = h2 ? h2.textContent.replace(/🎧.*/, '').trim() : '章节 ' + (i + 1);
      if (t.length > 14) t = t.slice(0, 14) + '…';
      return '<option value="' + (ch.id || 'chx-' + i) + '">' + (i + 1) + '. ' + t + '</option>';
    }).join('');
    var chSel2 = el('select');
    chSel2.innerHTML = chOpts;
    var curCh = this.chunks[0] && this.chunks[0].chapter;
    if (curCh && curCh.id) chSel2.value = curCh.id;
    chSel2.addEventListener('change', function (e) {
      var ch = document.getElementById(e.target.value);
      if (ch) {
        self._closeSheet();
        self.close();
        setTimeout(function () { self.open({ chapter: ch }); }, 100);
      }
    });
    sheet.appendChild(el('div', { class: 'sheet-row' }, [
      el('div', { class: 'sheet-row-label' }, '章节'),
      el('div', { class: 'sheet-row-control' }, [chSel2])
    ]));

    // 行 2 · 主题
    var themeRow = el('div', { class: 'sheet-row-control' });
    var pills = el('div', { class: 'sheet-pills' });
    THEMES.forEach(function (t) {
      var b = el('button', {
        class: 'theme-circle' + (self.config.theme === t ? ' active' : ''),
        'data-t': t,
        title: '主题 · ' + t,
        onclick: function () {
          self.config.theme = t;
          setConfig({ theme: t });
          self._applyConfig();
          $$('.theme-circle', sheet).forEach(function (x) { x.classList.remove('active'); });
          b.classList.add('active');
        }
      });
      pills.appendChild(b);
    });
    themeRow.appendChild(pills);
    sheet.appendChild(el('div', { class: 'sheet-row' }, [
      el('div', { class: 'sheet-row-label' }, '主题'),
      themeRow
    ]));

    // 行 3 · 字号
    var fontRow = el('div', { class: 'sheet-row-control' });
    var fontPills = el('div', { class: 'sheet-pills' });
    FONT_SIZES.forEach(function (s) {
      var b = el('button', {
        class: 'sheet-pill' + (self.config.fontSize === s ? ' active' : ''),
        onclick: function () {
          self.config.fontSize = s;
          setConfig({ fontSize: s });
          self._applyConfig();
          $$('.sheet-pill', fontPills).forEach(function (x) { x.classList.remove('active'); });
          b.classList.add('active');
        }
      }, s);
      fontPills.appendChild(b);
    });
    fontRow.appendChild(fontPills);
    sheet.appendChild(el('div', { class: 'sheet-row' }, [
      el('div', { class: 'sheet-row-label' }, '字号'),
      fontRow
    ]));

    // 行 4 · 行距
    var lhRow = el('div', { class: 'sheet-row-control' });
    var lhPills = el('div', { class: 'sheet-pills' });
    var lhLabels = { tight: '紧', normal: '中', loose: '松' };
    LINE_HEIGHTS.forEach(function (lh) {
      var b = el('button', {
        class: 'sheet-pill' + (self.config.lineHeight === lh ? ' active' : ''),
        onclick: function () {
          self.config.lineHeight = lh;
          setConfig({ lineHeight: lh });
          self._applyConfig();
          $$('.sheet-pill', lhPills).forEach(function (x) { x.classList.remove('active'); });
          b.classList.add('active');
        }
      }, lhLabels[lh]);
      lhPills.appendChild(b);
    });
    lhRow.appendChild(lhPills);
    sheet.appendChild(el('div', { class: 'sheet-row' }, [
      el('div', { class: 'sheet-row-label' }, '行距'),
      lhRow
    ]));

    // 行 5 · 音色(如有)
    var voices = this.tts.getChineseVoices();
    if (voices.length > 0) {
      var vSel = el('select');
      var vOpts = '<option value="">系统默认</option>' + voices.map(function (v) {
        var sel = self.config.voice === v.name ? ' selected' : '';
        return '<option value="' + v.name + '"' + sel + '>' + v.name.slice(0, 18) + '</option>';
      }).join('');
      vSel.innerHTML = vOpts;
      vSel.addEventListener('change', function (e) {
        self.config.voice = e.target.value;
        setConfig({ voice: e.target.value });
        if (self.isPlaying) self._speakCurrent();
      });
      sheet.appendChild(el('div', { class: 'sheet-row' }, [
        el('div', { class: 'sheet-row-label' }, '音色'),
        el('div', { class: 'sheet-row-control' }, [vSel])
      ]));
    }

    // 行 6 · 定时关闭
    var sleepRow = el('div', { class: 'sheet-row-control' });
    var sleepPills = el('div', { class: 'sheet-pills' });
    SLEEP_OPTIONS.forEach(function (opt) {
      var b = el('button', {
        class: 'sheet-pill' + (self.config.sleepTimer === opt.value ? ' active' : ''),
        onclick: function () {
          self._setSleepTimer(opt.value);
          $$('.sheet-pill', sleepPills).forEach(function (x) { x.classList.remove('active'); });
          b.classList.add('active');
        }
      }, opt.label);
      sleepPills.appendChild(b);
    });
    sleepRow.appendChild(sleepPills);
    sheet.appendChild(el('div', { class: 'sheet-row' }, [
      el('div', { class: 'sheet-row-label' }, '定时'),
      sleepRow
    ]));

    // 行 7 · 自动接下章 toggle
    var autoRow = el('div', { class: 'sheet-row-control' });
    var autoBtn = el('button', {
      class: 'sheet-pill' + (this.config.autoNextChapter ? ' active' : ''),
      onclick: function () {
        self.config.autoNextChapter = !self.config.autoNextChapter;
        setConfig({ autoNextChapter: self.config.autoNextChapter });
        autoBtn.classList.toggle('active', self.config.autoNextChapter);
        autoBtn.textContent = self.config.autoNextChapter ? '开启' : '关闭';
      }
    }, this.config.autoNextChapter ? '开启' : '关闭');
    autoRow.appendChild(autoBtn);
    sheet.appendChild(el('div', { class: 'sheet-row' }, [
      el('div', { class: 'sheet-row-label' }, '章末自动接下章'),
      autoRow
    ]));

    document.body.appendChild(mask);
    document.body.appendChild(sheet);
    this.sheet = sheet;
    this.sheetMask = mask;
  };

  /* ─── 应用配置 ────────────────────────────────────────────── */
  Reader.prototype._applyConfig = function () {
    if (!this.overlay) return;
    this.overlay.setAttribute('data-theme', this.config.theme);
    this.overlay.setAttribute('data-size', this.config.fontSize);
    this.overlay.setAttribute('data-lh', this.config.lineHeight);
    // 更新主题按钮
    if (this.overlay) {
      $$('.reader-theme-group button', this.overlay).forEach(function (b) {
        b.classList.toggle('active', b.getAttribute('data-t') === this.config.theme);
      }.bind(this));
    }
  };

  /* ─── 播放控制 ────────────────────────────────────────────── */
  Reader.prototype.togglePlay = function () {
    if (this.isPlaying) this.pause();
    else this.play();
  };

  Reader.prototype.play = function () {
    if (this.currentIdx < 0) this.currentIdx = 0;
    // 音频模式:走 <audio> 元素
    if (this.audioMode && this.audioEl && this.audioSegments) {
      var chunk = this.chunks[this.currentIdx];
      if (chunk) {
        this._playAudioFromSegment(chunk.id);
        this.isPlaying = true;
        this._updatePlayBtn();
        this._updateMediaSession(chunk);
        return;
      }
    }
    // Web TTS 模式
    this._speakCurrent();
  };

  Reader.prototype._speakCurrent = function () {
    var self = this;
    if (this.currentIdx >= this.chunks.length) {
      this._onChapterEnd();
      return;
    }
    var chunk = this.chunks[this.currentIdx];
    if (!chunk) return;
    this._highlightChunk(this.currentIdx);
    // 音频模式分支
    if (this.audioMode && this.audioEl && this.audioSegments) {
      this._playAudioFromSegment(chunk.id);
      this.isPlaying = true;
      this._updatePlayBtn();
      this._updateMediaSession(chunk);
      saveProgressDebounced({
        chunkId: chunk.id,
        idx: this.currentIdx,
        chapter: chunk.chapter && chunk.chapter.id
      });
      return;
    }
    // Web TTS 默认分支
    this.tts.onEndCb = function () { self._onChunkEnd(); };
    this.tts.onErrCb = function (e) {
      console.warn('[Reader TTS error]', e);
      self.isPlaying = false;
      self._updatePlayBtn();
    };
    this.tts.speak(chunk.text, {
      rate: this.config.rate,
      voice: this.config.voice
    });
    this.isPlaying = true;
    this._updatePlayBtn();
    this._updateMediaSession(chunk);
    saveProgressDebounced({
      chunkId: chunk.id,
      idx: this.currentIdx,
      chapter: chunk.chapter && chunk.chapter.id
    });
  };

  Reader.prototype._onChunkEnd = function () {
    if (!this.isPlaying) return;
    // 定时检查
    if (this.sleepDeadline && Date.now() >= this.sleepDeadline) {
      this._sleepFire();
      return;
    }
    var nextIdx = this.currentIdx + 1;
    if (nextIdx >= this.chunks.length) {
      this._onChapterEnd();
    } else {
      this.currentIdx = nextIdx;
      this._speakCurrent();
    }
  };

  Reader.prototype._onChapterEnd = function () {
    // 本章末定时:停
    if (this.config.sleepTimer === 'chapter') {
      this._sleepFire();
      return;
    }
    if (!this.config.autoNextChapter) {
      this.pause();
      return;
    }
    // 找下一章
    var current = this.chunks[this.chunks.length - 1];
    var currentCh = current && current.chapter;
    if (!currentCh) { this.pause(); return; }
    var chapters = $$('.chapter');
    var idx = chapters.indexOf(currentCh);
    if (idx < 0 || idx >= chapters.length - 1) { this.pause(); return; }
    var nextCh = chapters[idx + 1];
    var self = this;
    // 切到下一章
    this.close();
    setTimeout(function () {
      self.open({ chapter: nextCh });
      setTimeout(function () { self.play(); }, 200);
    }, 300);
  };

  Reader.prototype.pause = function () {
    if (this.audioMode && this.audioEl) {
      this.audioEl.pause();
    }
    this.tts.cancel();
    this.isPlaying = false;
    this._updatePlayBtn();
    this._updateMediaSession(null, 'paused');
  };

  Reader.prototype.next = function () {
    if (this.currentIdx < this.chunks.length - 1) {
      this.currentIdx++;
      if (this.isPlaying) this._speakCurrent();
      else this._highlightChunk(this.currentIdx);
    }
  };

  Reader.prototype.prev = function () {
    if (this.currentIdx > 0) {
      this.currentIdx--;
      if (this.isPlaying) this._speakCurrent();
      else this._highlightChunk(this.currentIdx);
    }
  };

  Reader.prototype._highlightChunk = function (idx) {
    if (!this.overlayInner) return;
    $$('[data-current="true"]', this.overlayInner).forEach(function (n) {
      n.removeAttribute('data-current');
    });
    var c = this.chunks[idx];
    if (!c) return;
    var target = $('[data-reader-id="' + c.id + '"]', this.overlayInner);
    if (target) {
      target.setAttribute('data-current', 'true');
      this._scrollToChunk(idx, true, target);
    }
  };

  Reader.prototype._scrollToChunk = function (idx, smooth, target) {
    target = target || (this.overlayInner && $('[data-reader-id="' + this.chunks[idx].id + '"]', this.overlayInner));
    if (!target) return;
    target.scrollIntoView({
      behavior: smooth ? 'smooth' : 'auto',
      block: 'center'
    });
  };

  Reader.prototype._updatePlayBtn = function () {
    if (this.playBtn) this.playBtn.innerHTML = this.isPlaying ? '⏸' : '▶';
    if (this.miniPlayBtn) this.miniPlayBtn.innerHTML = this.isPlaying ? '⏸' : '▶';
  };

  /* ─── Sleep Timer ──────────────────────────────────────────── */
  Reader.prototype._setSleepTimer = function (value) {
    this.config.sleepTimer = value;
    setConfig({ sleepTimer: value });
    if (this.sleepTicker) { clearInterval(this.sleepTicker); this.sleepTicker = null; }
    if (value === null) { this.sleepDeadline = null; return; }
    if (value === 'chapter') { this.sleepDeadline = 'chapter'; return; }
    // 数字分钟
    var ms = value * 60 * 1000;
    this.sleepDeadline = Date.now() + ms;
    var self = this;
    this.sleepTicker = setInterval(function () {
      if (Date.now() >= self.sleepDeadline) self._sleepFire();
    }, 5000);
  };

  Reader.prototype._sleepFire = function () {
    this.pause();
    this.sleepDeadline = null;
    if (this.sleepTicker) { clearInterval(this.sleepTicker); this.sleepTicker = null; }
    // 视觉提示
    this._toast('已按定时关闭');
  };

  Reader.prototype._toast = function (msg) {
    var t = el('div', {
      style: {
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        background: 'rgba(0,0,0,0.86)',
        color: '#fff',
        padding: '14px 22px',
        borderRadius: '8px',
        zIndex: '100000',
        fontSize: '14px',
        fontFamily: 'PingFang SC, sans-serif'
      }
    }, msg);
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 2000);
  };

  /* ─── Mini Player ──────────────────────────────────────────── */
  Reader.prototype._showMini = function () {
    var self = this;
    if (!this.mini) {
      this.mini = el('div', { class: 'reader-mini' });
      this.miniPlayBtn = el('button', {
        class: 'reader-mini-play',
        onclick: function () { self.togglePlay(); }
      }, '⏸');
      var info = el('div', { class: 'reader-mini-info' });
      this.miniTitle = el('div', { class: 'reader-mini-title' }, '');
      this.miniSub = el('div', { class: 'reader-mini-sub' }, '');
      info.appendChild(this.miniTitle);
      info.appendChild(this.miniSub);
      var expandBtn = el('button', {
        onclick: function () {
          self._hideMini();
          var chunk = self.chunks[self.currentIdx];
          var ch = chunk && chunk.chapter;
          self.open({ chapter: ch });
        }
      }, '⌃');
      var closeMini = el('button', {
        onclick: function () { self._stopMini(); }
      }, '✕');
      this.mini.appendChild(this.miniPlayBtn);
      this.mini.appendChild(info);
      this.mini.appendChild(expandBtn);
      this.mini.appendChild(closeMini);
      document.body.appendChild(this.mini);
    }
    var chunk = this.chunks[this.currentIdx];
    if (chunk) {
      var ch = chunk.chapter;
      var t = ch && ch.querySelector('h2') ? ch.querySelector('h2').textContent.replace(/🎧.*/, '').trim() : '';
      this.miniTitle.textContent = t.slice(0, 30);
      this.miniSub.textContent = (this.currentIdx + 1) + ' / ' + this.chunks.length + ' · ' + this.config.rate + 'x';
    }
    this.mini.classList.add('open');
  };

  Reader.prototype._hideMini = function () {
    if (this.mini) this.mini.classList.remove('open');
  };

  Reader.prototype._stopMini = function () {
    this.pause();
    this._hideMini();
  };

  Reader.prototype._continueMini = function () {
    // 关 overlay 时还在播放,mini 状态启动播放
    if (this.currentIdx >= 0) this._speakCurrent();
  };

  /* ─── Media Session API(锁屏控制) ────────────────────────── */
  Reader.prototype._setupMediaSession = function () {
    if (!('mediaSession' in navigator)) return;
    var self = this;
    navigator.mediaSession.setActionHandler('play', function () { self.play(); });
    navigator.mediaSession.setActionHandler('pause', function () { self.pause(); });
    navigator.mediaSession.setActionHandler('previoustrack', function () { self.prev(); });
    navigator.mediaSession.setActionHandler('nexttrack', function () { self.next(); });
  };

  Reader.prototype._updateMediaSession = function (chunk, state) {
    if (!('mediaSession' in navigator)) return;
    if (chunk) {
      var ch = chunk.chapter;
      var title = ch && ch.querySelector('h2') ? ch.querySelector('h2').textContent.replace(/🎧.*/, '').trim() : '研究报告';
      var artist = REPORT_ID;
      navigator.mediaSession.metadata = new MediaMetadata({
        title: title,
        artist: '段落 ' + (this.currentIdx + 1) + ' / ' + this.chunks.length,
        album: artist
      });
    }
    if (state) {
      try { navigator.mediaSession.playbackState = state; } catch (e) {}
    }
  };

  /* ─── URL Hash 分享(P2: F-202) ──────────────────────────── */
  Reader.prototype._handleHashSegmentNav = function () {
    var hash = location.hash;
    if (!hash) return;
    var m = hash.match(/^#read=([\w-]+)/);
    if (!m) return;
    var id = m[1];
    var self = this;
    setTimeout(function () {
      // 找到对应 reader-id 的元素的章节
      self._buildAllChunks();
      var target = $$('[data-reader-id="' + id + '"]')[0];
      if (target) {
        var ch = target.closest('.chapter');
        self.open({ chapter: ch });
        setTimeout(function () {
          var idx = self.chunks.findIndex(function (c) { return c.id === id; });
          if (idx >= 0) {
            self.currentIdx = idx;
            self._highlightChunk(idx);
            self.play();
          }
        }, 200);
      }
    }, 500);
  };

  /* ============================================================ */
  /* 6.5 · 音频模式(v6:高音质 Azure Neural 预录音频)             */
  /* ============================================================ */

  // 检测当前章是否有可用音频
  Reader.prototype._checkAudioAvailable = function (chapterId) {
    if (!chapterId) return Promise.resolve(false);
    var self = this;
    var audioUrl = 'audio/' + chapterId + '.mp3';
    var jsonUrl = 'audio/' + chapterId + '.json';
    return fetch(jsonUrl, { method: 'HEAD' })
      .then(function (res) { return res.ok; })
      .catch(function () { return false; });
  };

  // 加载某章音频 + 段落映射
  Reader.prototype._loadAudio = function (chapterId) {
    var self = this;
    if (this.audioChapterId === chapterId && this.audioEl) {
      return Promise.resolve(true);
    }
    var audioUrl = 'audio/' + chapterId + '.mp3';
    var jsonUrl = 'audio/' + chapterId + '.json';
    return fetch(jsonUrl)
      .then(function (res) { return res.ok ? res.json() : null; })
      .then(function (data) {
        if (!data || !data.segments) return false;
        self.audioSegments = data.segments;
        self.audioChapterId = chapterId;
        // 创建或重用 audio element
        if (!self.audioEl) {
          self.audioEl = new Audio();
          self.audioEl.preload = 'metadata';
          self._setupAudioListeners();
        }
        self.audioEl.src = audioUrl;
        return true;
      })
      .catch(function () { return false; });
  };

  Reader.prototype._setupAudioListeners = function () {
    var self = this;
    var a = this.audioEl;
    a.addEventListener('timeupdate', function () {
      if (!self.audioMode || !self.audioSegments) return;
      self._syncAudioSegmentHighlight();
    });
    a.addEventListener('ended', function () {
      self.isPlaying = false;
      self._updatePlayBtn();
      self._onChapterEnd();
    });
    a.addEventListener('play', function () {
      self.isPlaying = true;
      self._updatePlayBtn();
    });
    a.addEventListener('pause', function () {
      self.isPlaying = false;
      self._updatePlayBtn();
    });
  };

  // 根据 audio.currentTime 找到对应段落并高亮
  Reader.prototype._syncAudioSegmentHighlight = function () {
    if (!this.audioSegments || !this.audioEl) return;
    var t = this.audioEl.currentTime;
    // 二分查找最大的 start <= t 的 segment
    var lo = 0, hi = this.audioSegments.length - 1, found = 0;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      if (this.audioSegments[mid].start <= t) {
        found = mid;
        lo = mid + 1;
      } else {
        hi = mid - 1;
      }
    }
    if (found === this.audioLastSegIdx) return;
    this.audioLastSegIdx = found;
    var segId = this.audioSegments[found].id;
    // 找到 chunks 里相同 ID 的 chunk,高亮
    var chunkIdx = this.chunks.findIndex(function (c) { return c.id === segId; });
    if (chunkIdx >= 0) {
      this.currentIdx = chunkIdx;
      this._highlightChunk(chunkIdx);
      saveProgressDebounced({
        chunkId: segId,
        idx: chunkIdx,
        chapter: this.audioChapterId
      });
    }
  };

  // 用音频模式从指定段开始播放
  Reader.prototype._playAudioFromSegment = function (segId) {
    if (!this.audioEl || !this.audioSegments) return;
    var seg = this.audioSegments.find(function (s) { return s.id === segId; });
    if (seg) {
      this.audioEl.currentTime = seg.start;
    }
    var self = this;
    var p = this.audioEl.play();
    if (p && p.catch) {
      p.catch(function (err) {
        console.warn('[Reader audio] play failed:', err);
        // 自动降级到 Web TTS
        self.audioMode = false;
        self._updateAudioToggle();
        self._speakCurrent();
      });
    }
  };

  Reader.prototype._pauseAudio = function () {
    if (this.audioEl) this.audioEl.pause();
  };

  // 切换 Web TTS / 音频模式
  Reader.prototype._toggleAudioMode = function () {
    if (!this.audioAvailable) return;
    var wasPlaying = this.isPlaying;
    // 停止当前播放
    if (this.audioMode) {
      this._pauseAudio();
    } else {
      this.tts.cancel();
    }
    this.audioMode = !this.audioMode;
    setConfig({ audioMode: this.audioMode });
    this._updateAudioToggle();
    if (wasPlaying) {
      // 用新模式继续播
      this.isPlaying = false;
      this.play();
    }
  };

  Reader.prototype._updateAudioToggle = function () {
    if (!this.audioToggleBtn) return;
    if (this.audioMode) {
      this.audioToggleBtn.textContent = '🎙 高音质';
      this.audioToggleBtn.classList.add('active');
      this.audioToggleBtn.title = '当前:Azure Neural 录音 · 点切回 Web TTS';
    } else {
      this.audioToggleBtn.textContent = '🤖 标准';
      this.audioToggleBtn.classList.remove('active');
      this.audioToggleBtn.title = '当前:Web TTS · 点切高音质录音';
    }
    this.audioToggleBtn.style.display = this.audioAvailable ? '' : 'none';
  };

  /* ============================================================ */
  /* 7. 初始化                                                     */
  /* ============================================================ */

  // 只在报告页激活
  function shouldActivate() {
    return $$('.chapter').length > 0 || $$('main').length > 0;
  }

  if (shouldActivate()) {
    window.__reader = new Reader();
    window.__reader.init();
  }

})();
