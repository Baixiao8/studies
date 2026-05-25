/* =========================================================
 * READING PROGRESS · 顶部金色进度条
 *
 * 用法:页面顶部插入 <div class="progress-bar" id="progressBar"></div>
 * 然后 <script src="../../_shared/progress.js" defer></script>
 * ========================================================= */

(function() {
  'use strict';

  function init() {
    let bar = document.getElementById('progressBar');
    if (!bar) {
      // 如果 HTML 没插,自动插
      bar = document.createElement('div');
      bar.className = 'progress-bar';
      bar.id = 'progressBar';
      document.body.insertBefore(bar, document.body.firstChild);
    }

    function update() {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const pct = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
      bar.style.width = pct + '%';
    }

    window.addEventListener('scroll', update, { passive: true });
    update();

    // 同步:点击 sticky-nav 链接时,高亮当前 active
    const navLinks = document.querySelectorAll('.sticky-nav .nav-inner a[href^="#"]');
    if (navLinks.length === 0) return;

    const sectionMap = new Map();
    navLinks.forEach(link => {
      const id = link.getAttribute('href').slice(1);
      const sec = document.getElementById(id);
      if (sec) sectionMap.set(sec, link);
    });

    // v8.7 · 区分"用户主动滚动" vs "代码触发滚动"
    // 修复:点击 nav 后 scroll 过程中,IO 监听到一闪而过的 sections 会乱跳 active
    // 根因:多事件源(点击 / 滚动)写共享状态(active),没有协调层
    let isProgrammaticScroll = false;
    let programmaticScrollTimer = null;

    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        const targetId = link.getAttribute('href').slice(1);
        const target = document.getElementById(targetId);
        if (!target) return;  // 不存在的锚点,让浏览器默认处理

        // v8.7.1 · 阻止浏览器原生 smooth scroll
        // 根因:_shared/style.css 设了 html { scroll-behavior: smooth }
        // 跨长距离(s1→s9 约 10 万 px)smooth 要 30+ 秒,体验上像卡住
        e.preventDefault();

        isProgrammaticScroll = true;
        // 立即把 active 设到目标 link(给用户即时反馈,不等 IO)
        navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        // v8.7.4 · 强制 instant scroll + retry-on-layout-shift
        // 真根因(MCP browser 实测发现 — 反复 5 次:v8.7→v8.7.1→v8.7.2→v8.7.3→v8.7.4):
        //   1. CSS html { scroll-behavior: smooth } 影响所有 JS scroll API,
        //      唯一可靠的强制 instant 写法是 scrollTo({ behavior: 'instant' })
        //   2. 章节 hero 图片 lazy load 加载完后 layout 持续 shift,
        //      导致 click 瞬间的 target 位置过几秒后不再准确。
        //      实测:点 #s9,click 时 s9 在 docPos 26220,scroll 到 26140 (= 26220-80);
        //      接着 hero 图片加载,s9 实际位置变成 47060,viewport 仍停在 26140,
        //      用户看到的是 s7/s8 内容,以为 scroll 没生效。
        // 修复:click 立即 instant-scroll,然后多次 retry catch image-load 引起的 layout shifts。
        //      用户主动 wheel/touchmove/keydown 时,取消 retry(尊重用户意图)。
        const doScroll = () => {
          const tt = target.getBoundingClientRect().top + window.pageYOffset - 80;
          window.scrollTo({ top: tt, behavior: 'instant' });
        };

        doScroll();
        // 手动更新 URL hash(因为 preventDefault 阻止了浏览器原生 hash change)
        history.pushState(null, '', '#' + targetId);

        // 用户主动 scroll/key 取消后续 retry
        let userCancelled = false;
        const onUserInput = () => { userCancelled = true; };
        window.addEventListener('wheel', onUserInput, { passive: true, once: true });
        window.addEventListener('touchmove', onUserInput, { passive: true, once: true });
        window.addEventListener('keydown', onUserInput, { passive: true, once: true });

        // 定时 retry(catch 非 image 的 layout shift / async DOM mutation)
        [50, 150, 400, 1000].forEach(delay => {
          setTimeout(() => { if (!userCancelled) doScroll(); }, delay);
        });

        // image load retry(catch image-induced layout shift,主要场景)
        document.querySelectorAll('img').forEach(img => {
          if (!img.complete) {
            img.addEventListener('load', () => {
              if (!userCancelled) doScroll();
            }, { once: true });
            img.addEventListener('error', () => {
              if (!userCancelled) doScroll();
            }, { once: true });
          }
        });

        // 1.5s 后清理 listeners(超过这时间 layout 应该稳定了)
        setTimeout(() => {
          window.removeEventListener('wheel', onUserInput);
          window.removeEventListener('touchmove', onUserInput);
          window.removeEventListener('keydown', onUserInput);
        }, 1500);

        // 兜底:scrollend 不支持的浏览器,1.2s 后解锁 scroll spy
        if (programmaticScrollTimer) clearTimeout(programmaticScrollTimer);
        programmaticScrollTimer = setTimeout(() => {
          isProgrammaticScroll = false;
          programmaticScrollTimer = null;
        }, 1200);
      });
    });

    // 现代浏览器优先用 scrollend(Chrome 114+ / Firefox 109+ / Safari 17.4+)
    window.addEventListener('scrollend', () => {
      isProgrammaticScroll = false;
      if (programmaticScrollTimer) {
        clearTimeout(programmaticScrollTimer);
        programmaticScrollTimer = null;
      }
    });

    const navObserver = new IntersectionObserver((entries) => {
      // v8.7 · 代码触发滚动期间,scroll spy 不更新 active
      if (isProgrammaticScroll) return;
      entries.forEach(entry => {
        const link = sectionMap.get(entry.target);
        if (!link) return;
        if (entry.isIntersecting) {
          navLinks.forEach(l => l.classList.remove('active'));
          link.classList.add('active');
        }
      });
    }, {
      rootMargin: '-30% 0px -60% 0px',
      threshold: 0
    });
    sectionMap.forEach((link, sec) => navObserver.observe(sec));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
