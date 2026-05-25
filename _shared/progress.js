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

        // v8.7.3 · 强制 instant scroll · sticky-nav 高 80px,留出标题不被遮挡
        // ⚠️ MDN spec 陷阱(v8.7→v8.7.1→v8.7.2→v8.7.3 反复 4 次才搞清楚):
        //   CSS html { scroll-behavior: smooth } 影响所有 JS scroll API:
        //   - scrollTo(x, y) 老 API form  → 仍受 CSS smooth 影响(以前以为不会)
        //   - scrollTo({ behavior: 'auto' }) → 读 CSS = smooth
        //   - scrollTo({ behavior: 'instant' }) → 强制 instant,**唯一可靠的写法**
        //   - document.documentElement.style.scrollBehavior = 'auto' 临时禁用不可靠
        // 已用 MCP browser 在浏览器实测过 3 种方法,只有显式 'instant' 立即生效。
        const targetTop = target.getBoundingClientRect().top + window.pageYOffset - 80;
        window.scrollTo({ top: targetTop, behavior: 'instant' });
        // 手动更新 URL hash(因为 preventDefault 阻止了浏览器原生 hash change)
        history.pushState(null, '', '#' + targetId);

        // 兜底:scrollend 不支持的浏览器(Safari < 17.4),0.6s 后强制解锁
        // instant scroll 比 smooth 快很多,所以等待时间从 1200 降到 600
        if (programmaticScrollTimer) clearTimeout(programmaticScrollTimer);
        programmaticScrollTimer = setTimeout(() => {
          isProgrammaticScroll = false;
          programmaticScrollTimer = null;
        }, 600);
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
