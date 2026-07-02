/**
 * Ash World — 共享灰烬粒子背景
 *
 * 为所有子页面提供与首页一致的浮动灰烬粒子 + 余烬光晕。
 * 自动挂载，无需额外调用。
 */

(function () {
  'use strict';

  // 防止重复加载
  if (window.__ashBgLoaded) return;
  window.__ashBgLoaded = true;

  const PARTICLE_COUNT = 80;

  // 创建容器
  const container = document.createElement('div');
  container.className = 'ash-bg-particles';
  container.style.cssText =
    'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;';

  // 创建余烬光晕（bottom glow）
  const glow = document.createElement('div');
  glow.className = 'ash-bottom-glow';
  glow.style.cssText =
    'position:fixed;bottom:-40%;left:50%;transform:translateX(-50%);' +
    'width:120vw;height:80vh;z-index:0;pointer-events:none;' +
    'background:radial-gradient(ellipse at center,rgba(92,26,26,0.10) 0%,transparent 70%);' +
    'filter:blur(60px);';
  container.appendChild(glow);

  // 生成粒子元素
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const p = document.createElement('div');
    p.className = 'ash-particle';
    const size = 1 + Math.random() * 2.5;
    const hue = Math.random() < 0.7 ? '20' : '200';
    const sat = 30 + Math.random() * 40;
    p.style.cssText =
      `position:absolute;width:${size}px;height:${size}px;` +
      `background:hsl(${hue},${sat}%,${50 + Math.random() * 40}%);` +
      `border-radius:50%;opacity:${0.15 + Math.random() * 0.35};` +
      `left:${Math.random() * 100}%;top:${40 + Math.random() * 60}%;` +
      `animation:ash-drift ${8 + Math.random() * 16}s linear infinite;` +
      `animation-delay:-${Math.random() * 16}s;`;
    container.appendChild(p);
  }

  // 注入动画关键帧（仅一次）
  if (!document.getElementById('ash-bg-style')) {
    const style = document.createElement('style');
    style.id = 'ash-bg-style';
    style.textContent = `
      @keyframes ash-drift {
        0%   { transform: translateY(0) translateX(0) scale(1); opacity: 0.3; }
        25%  { transform: translateY(-25vh) translateX(15px) scale(0.8); }
        50%  { transform: translateY(-50vh) translateX(-10px) scale(1.2); opacity: 0.15; }
        75%  { transform: translateY(-75vh) translateX(8px) scale(0.6); }
        100% { transform: translateY(-105vh) translateX(-5px) scale(0.3); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }

  // ============================================================
  // 返回骰子按钮 — 已移除（用户不再需要）
  // ============================================================
  function createReturnBtn() {
    /* no-op: 返回按钮已禁用 */
  }

  // DOM ready 后挂载
  function mount() {
    if (!document.getElementById('ash-bg-particles-mount')) {
      container.id = 'ash-bg-particles-mount';
      document.body.insertBefore(container, document.body.firstChild);
    }
    createReturnBtn();
    highlightCurrentPage();
  }

  // ============================================================
  // 当前页面高亮
  // ============================================================
  function highlightCurrentPage() {
    if (window.location.pathname === '/' || window.location.pathname.endsWith('index.html')) return;
    var path = window.location.pathname.split('/').pop();
    if (!path) return;

    // 高亮顶部导航的一级菜单项
    var navItems = document.querySelectorAll('.top-nav .nav-item > a, .top-nav .nav-item > span');
    navItems.forEach(function(item) { item.classList.remove('active'); });

    // 高亮下拉菜单中的对应二级链接
    var dropdownLinks = document.querySelectorAll('.top-nav .nav-dropdown a');
    dropdownLinks.forEach(function(a) {
      a.classList.remove('active');
      if (a.getAttribute('href') === path) {
        a.classList.add('active');
        // 也高亮其父级 nav-item
        var navItem = a.closest('.nav-item');
        if (navItem) {
          var trigger = navItem.querySelector(':scope > a, :scope > span');
          if (trigger) trigger.classList.add('active');
        }
      }
    });

    // 高亮一级扁平链接
    var flatLinks = document.querySelectorAll('.top-nav .nav-item > a');
    flatLinks.forEach(function(a) {
      if (a.getAttribute('href') === path) {
        a.classList.add('active');
        a.closest('.nav-item').classList.add('active');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }

})();
