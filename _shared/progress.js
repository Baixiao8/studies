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

    const navObserver = new IntersectionObserver((entries) => {
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
