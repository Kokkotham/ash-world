/**
 * Ash World — 页面过渡动画系统（轻量版）
 *
 *   transition.out(url)    → 快速淡出 → 跳转
 *   transition.in()        → 快速淡入
 */

(function () {
  'use strict';

  // ============================================================
  // 退出动画：快速暗幕 → 跳转
  // ============================================================
  function out(targetUrl) {
    if (document.getElementById('ash-transition-overlay')) return;

    // 暗幕覆盖层
    const overlay = document.createElement('div');
    overlay.id = 'ash-transition-overlay';
    Object.assign(overlay.style, {
      position: 'fixed', inset: '0', zIndex: '9999',
      pointerEvents: 'none',
      background: '#030508',
      opacity: '0',
      transition: 'opacity 0.15s ease-in',
    });
    document.body.appendChild(overlay);

    // 隐藏主页 UI
    const header = document.querySelector('.header');
    const diceWrap = document.querySelector('.dice-wrap');
    if (header) header.style.opacity = '0';
    if (diceWrap) diceWrap.style.opacity = '0';

    requestAnimationFrame(() => {
      overlay.style.opacity = '1';
      setTimeout(() => { window.location.href = targetUrl; }, 180);
    });
  }

  // ============================================================
  // 入场动画：暗幕消散 → 显示内容
  // ============================================================
  function in_() {
    if (window.location.pathname === '/' || window.location.pathname.endsWith('index.html')) return;

    const overlay = document.createElement('div');
    overlay.id = 'ash-enter-overlay';
    Object.assign(overlay.style, {
      position: 'fixed', inset: '0', zIndex: '9998',
      pointerEvents: 'none',
      background: '#030508',
      opacity: '1',
      transition: 'opacity 0.25s ease-out',
    });
    document.body.appendChild(overlay);

    requestAnimationFrame(() => {
      overlay.style.opacity = '0';
      setTimeout(() => {
        if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
      }, 300);
    });
  }

  // ============================================================
  // 导出
  // ============================================================
  window.ashTransition = { out, in };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', in_);
  } else {
    in_();
  }

})();
