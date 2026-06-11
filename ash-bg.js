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
  // 返回骰子按钮（所有子页面统一）
  // ============================================================
  function createReturnBtn() {
    if (document.getElementById('ash-return-btn')) return;

    // 注入样式
    if (!document.getElementById('ash-return-style')) {
      const s = document.createElement('style');
      s.id = 'ash-return-style';
      s.textContent = `
        #ash-return-btn {
          position: fixed; bottom: 28px; right: 28px; z-index: 999;
          width: 48px; height: 48px;
          background: rgba(10,14,18,0.85);
          border: 1px solid rgba(201,168,76,0.3);
          border-radius: 6px;
          display: flex; align-items: center; justify-content: center;
          cursor: pointer; transition: all 0.3s;
          color: rgba(201,168,76,0.7);
          font-size: 1.2rem; text-decoration: none;
          box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        #ash-return-btn:hover {
          border-color: var(--ash-gold, #c9a84c);
          color: var(--ash-gold, #c9a84c);
          box-shadow: 0 4px 28px rgba(184,146,58,0.2);
          transform: translateY(-2px);
        }
        #ash-return-btn .dice-icon {
          font-family: 'Cinzel', serif;
          font-size: 1.3rem;
          line-height: 1;
        }
        #ash-return-btn .return-tip {
          position: absolute; right: 58px; top: 50%; transform: translateY(-50%);
          background: rgba(10,14,18,0.9);
          color: var(--ash-gold, #c9a84c);
          font-size: 0.72rem; padding: 4px 12px; border-radius: 3px;
          white-space: nowrap; opacity: 0; pointer-events: none;
          transition: opacity 0.3s; letter-spacing: 0.06em;
          border: 1px solid rgba(201,168,76,0.15);
        }
        #ash-return-btn:hover .return-tip { opacity: 1; }
        @media (max-width: 768px) {
          #ash-return-btn { bottom: 16px; right: 16px; width: 40px; height: 40px; }
        }
      `;
      document.head.appendChild(s);
    }

    const btn = document.createElement('a');
    btn.id = 'ash-return-btn';
    btn.href = '../index.html';
    btn.title = '返回灰烬骰子';
    btn.innerHTML =
      '<span class="dice-icon">&#x2684;</span>' +
      '<span class="return-tip">返回骰子</span>';

    // 点击时触发过渡动画
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      if (window.ashTransition && window.ashTransition.out) {
        ashTransition.out('../index.html');
      } else {
        window.location.href = '../index.html';
      }
    });

    document.body.appendChild(btn);
  }

  // DOM ready 后挂载
  function mount() {
    if (!document.getElementById('ash-bg-particles-mount')) {
      container.id = 'ash-bg-particles-mount';
      document.body.insertBefore(container, document.body.firstChild);
    }
    createReturnBtn();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }

})();
