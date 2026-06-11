/**
 * Ash World — 页面过渡动画系统
 *
 * 提供两个核心函数：
 *   transition.out(url)    → 火星爆散 → 黑屏 → 跳转
 *   transition.in()        → 页面加载后灰烬消散 → 内容淡入
 *
 * 所有子页面自动调用 transition.in()
 * 首页骰子点击调用 transition.out(url)
 */

(function () {
  'use strict';

  const TRANSITION_DURATION = 800; // 过渡总时长(ms)，与 CSS 保持同步

  // ============================================================
  // 在首页：退出动画（火星爆散 → 跳转）
  // ============================================================
  function out(targetUrl) {
    // 防止重复触发
    if (document.getElementById('ash-transition-overlay')) return;

    // 1. 创建全屏覆盖层
    const overlay = document.createElement('div');
    overlay.id = 'ash-transition-overlay';
    Object.assign(overlay.style, {
      position: 'fixed', inset: '0', zIndex: '9999',
      pointerEvents: 'none',
      background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 0%, rgba(0,0,0,0.3) 40%, rgba(0,0,0,0.95) 100%)',
      opacity: '0',
      transition: 'opacity 0.3s ease-in',
    });
    document.body.appendChild(overlay);

    // 2. 创建 Canvas 粒子层（火星爆散）
    const canvas = document.createElement('canvas');
    canvas.id = 'ash-transition-canvas';
    Object.assign(canvas.style, {
      position: 'fixed', inset: '0', zIndex: '10000',
      pointerEvents: 'none', display: 'block',
      width: '100%', height: '100%',
    });
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');

    // 粒子参数
    const cx = window.innerWidth / 2;
    const cy = window.innerHeight / 2;
    const PARTICLE_COUNT = 300;

    const particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 1.5 + Math.random() * 6;
      const dist = 20 + Math.random() * 60; // 初始偏移（从骰子区域散开）
      particles.push({
        x: cx + Math.cos(angle) * dist,
        y: cy + Math.sin(angle) * dist,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - Math.random() * 2,
        life: 1,
        decay: 0.006 + Math.random() * 0.014,
        size: 1 + Math.random() * 3,
        hue: Math.random() < 0.6 ? 15 + Math.random() * 20 : 30 + Math.random() * 30,
      });
    }

    const startTime = performance.now();
    let fadeDone = false;

    function animate(now) {
      const elapsed = now - startTime;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      let alive = 0;
      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.02; // 微重力
        p.life -= p.decay;

        if (p.life > 0) {
          alive++;
          const alpha = p.life * 0.9;
          ctx.globalAlpha = alpha;
          ctx.fillStyle = `hsl(${p.hue}, 80%, ${50 + p.life * 40}%)`;
          ctx.shadowColor = `hsl(${p.hue}, 90%, 50%)`;
          ctx.shadowBlur = 4;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      ctx.shadowBlur = 0;
      ctx.globalAlpha = 1;

      // 0.35s 后开始淡出 overlay
      if (elapsed > 350 && !fadeDone) {
        fadeDone = true;
        overlay.style.opacity = '1';
      }

      if (elapsed > TRANSITION_DURATION || alive < 3) {
        // 动画结束 → 跳转
        document.body.style.background = '#030508';
        window.location.href = targetUrl;
        return;
      }

      requestAnimationFrame(animate);
    }

    // 启动
    requestAnimationFrame(animate);

    // 同时让主页骰子/标题快速淡出
    const header = document.querySelector('.header');
    const diceWrap = document.querySelector('.dice-wrap');
    if (header) header.style.opacity = '0';
    if (diceWrap) diceWrap.style.opacity = '0';
  }

  // ============================================================
  // 在子页面：入场动画（灰烬消散 → 内容淡入）
  // ============================================================
  function in_() {
    // 防止在首页触发
    if (window.location.pathname === '/' || window.location.pathname.endsWith('index.html')) return;

    const overlay = document.createElement('div');
    overlay.id = 'ash-enter-overlay';
    Object.assign(overlay.style, {
      position: 'fixed', inset: '0', zIndex: '9998',
      pointerEvents: 'none',
      background: 'radial-gradient(ellipse at center, rgba(3,5,8,0.3) 0%, rgba(3,5,8,0.95) 70%, rgba(3,5,8,1) 100%)',
      opacity: '1',
      transition: 'opacity 0.6s ease-out',
    });
    document.body.appendChild(overlay);

    // 入场粒子（几个从中心散开的火星）
    const canvas = document.createElement('canvas');
    Object.assign(canvas.style, {
      position: 'fixed', inset: '0', zIndex: '9999',
      pointerEvents: 'none', display: 'block',
    });
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    const enterParticles = [];
    const cx = window.innerWidth / 2;
    const cy = window.innerHeight / 2;
    for (let i = 0; i < 60; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 1 + Math.random() * 3;
      enterParticles.push({
        x: cx, y: cy,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 1,
        decay: 0.01 + Math.random() * 0.02,
        size: 0.5 + Math.random() * 2,
      });
    }

    const startTime = performance.now();
    function animEnter(now) {
      const elapsed = now - startTime;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      let alive = 0;
      for (const p of enterParticles) {
        p.x += p.vx;
        p.y += p.vy;
        p.life -= p.decay;
        if (p.life > 0) {
          alive++;
          ctx.globalAlpha = p.life * 0.6;
          ctx.fillStyle = '#c9943a';
          ctx.shadowColor = '#a06020';
          ctx.shadowBlur = 3;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      ctx.shadowBlur = 0;
      ctx.globalAlpha = 1;

      if (elapsed > 300) {
        overlay.style.opacity = '0';
      }
      if (elapsed > 800 || alive < 2) {
        if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
        if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
        return;
      }
      requestAnimationFrame(animEnter);
    }
    requestAnimationFrame(animEnter);
  }

  // ============================================================
  // 导出
  // ============================================================
  window.ashTransition = {
    out: out,
    in: in_,
  };

  // 子页面自动调用入场动画
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', in_);
  } else {
    in_();
  }

})();
