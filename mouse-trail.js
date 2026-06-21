/**
 * mouse-trail.js — 灰烬世界子页面鼠标火光拖尾效果
 * 用法：在子页面 </body> 前加 <script src="../mouse-trail.js"></script>
 * 效果：暖橙色鼠标光晕 + 火星粒子拖尾，无 Three.js 背景粒子
 * 开关：自动在右下角创建按钮；也可通过 window.__setMouseTrail(on) 控制
 */
(function () {
    'use strict';

    // ── 全局开关状态（默认开启，读取 localStorage）──
    let trailOn = localStorage.getItem('ash_trail_on') !== 'false';
    window.__mouseTrailOn = trailOn;
    window.__setMouseTrail = function (on) {
        trailOn = !!on;
        window.__mouseTrailOn = trailOn;
        localStorage.setItem('ash_trail_on', trailOn ? '1' : '0');
        updateToggleBtn();
        if (!trailOn) {
            // 关闭时立刻清画布
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    };

    // ── 创建 canvas 元素 ──
    const canvas = document.createElement('canvas');
    canvas.id = 'cursor-trail';
    canvas.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;z-index:9999;pointer-events:none;';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // ── 状态 ──
    const trailPoints = [];
    const MAX_TRAIL = 90;
    let lastMouseX = -1000, lastMouseY = -1000;
    let mouseActive = false;
    let mouseInactiveTimer = 0;
    let glowFade = 0;       // 光晕淡出系数 0~1，1=完全亮，0=完全灭
    const FADE_SPEED = 1.8; // 淡出速度（越大越快，1.8 约 0.55 秒消完）

    // ── 鼠标追踪 ──
    window.addEventListener('mousemove', function (e) {
        if (!trailOn) return; // 关闭状态不记录
        mouseActive = true;
        mouseInactiveTimer = 0;
        glowFade = 1.0; // 移动时立刻全亮
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;

        // 每次移动生成 2~4 个带随机偏移的粒子
        const spawnCount = Math.floor(Math.random() * 3) + 2;
        for (let s = 0; s < spawnCount; s++) {
            const offsetX = (Math.random() - 0.5) * 14;
            const offsetY = (Math.random() - 0.5) * 14;
            trailPoints.push({
                x: e.clientX + offsetX,
                y: e.clientY + offsetY,
                life: 0.7 + Math.random() * 0.3,
                size: Math.random() * 1.8 + 0.6,
            });
        }
        while (trailPoints.length > MAX_TRAIL) trailPoints.shift();
    });

    // ── 动画循环 ──
    let lastTime = performance.now();

    function animate(now) {
        window.requestAnimationFrame(animate);

        // 关闭状态：不绘制任何内容，清空画布后直接返回
        if (!trailOn) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            return;
        }

        const dt = Math.min((now - lastTime) / 1000, 0.05);
        lastTime = now;

        // 鼠标静止超时 — 标记停止，glowFade 缓慢衰减
        mouseInactiveTimer += dt;
        if (mouseInactiveTimer > 0.4) {
            mouseActive = false;
            glowFade = Math.max(0, glowFade - FADE_SPEED * dt);
        }

        // 清空画布
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // ── 绘制鼠标光晕（用 glowFade 淡出）──
        if (glowFade > 0.01 && lastMouseX > -100) {
            const f = glowFade;
            // 大范围热源光晕
            const lightGrad = ctx.createRadialGradient(
                lastMouseX, lastMouseY, 0,
                lastMouseX, lastMouseY, 220
            );
            lightGrad.addColorStop(0, 'rgba(255, 180, 80, ' + (0.07 * f) + ')');
            lightGrad.addColorStop(0.2, 'rgba(255, 160, 60, ' + (0.045 * f) + ')');
            lightGrad.addColorStop(0.5, 'rgba(240, 130, 40, ' + (0.018 * f) + ')');
            lightGrad.addColorStop(1, 'rgba(220, 100, 20, 0)');
            ctx.fillStyle = lightGrad;
            ctx.beginPath();
            ctx.arc(lastMouseX, lastMouseY, 220, 0, Math.PI * 2);
            ctx.fill();

            // 核心聚焦热源
            const coreGrad = ctx.createRadialGradient(
                lastMouseX, lastMouseY, 0,
                lastMouseX, lastMouseY, 60
            );
            coreGrad.addColorStop(0, 'rgba(255, 230, 180, ' + (0.12 * f) + ')');
            coreGrad.addColorStop(0.4, 'rgba(255, 200, 120, ' + (0.06 * f) + ')');
            coreGrad.addColorStop(1, 'rgba(255, 170, 80, 0)');
            ctx.fillStyle = coreGrad;
            ctx.beginPath();
            ctx.arc(lastMouseX, lastMouseY, 60, 0, Math.PI * 2);
            ctx.fill();
        }

        // ── 绘制拖尾粒子 ──
        if (trailPoints.length > 0) {
            ctx.globalCompositeOperation = 'lighter';
            for (let i = trailPoints.length - 1; i >= 0; i--) {
                const p = trailPoints[i];
                const progress = i / trailPoints.length;
                const alpha = p.life * (0.15 + progress * 0.85);
                const r = p.size * p.life * (0.4 + progress * 0.6);

                // 外发光
                const g1 = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 4);
                g1.addColorStop(0, 'rgba(255, 180, 60, ' + (alpha * 0.6) + ')');
                g1.addColorStop(0.3, 'rgba(255, 150, 40, ' + (alpha * 0.3) + ')');
                g1.addColorStop(1, 'rgba(255, 120, 20, 0)');
                ctx.fillStyle = g1;
                ctx.beginPath();
                ctx.arc(p.x, p.y, r * 4, 0, Math.PI * 2);
                ctx.fill();

                // 核心亮点
                ctx.fillStyle = 'rgba(255, 245, 220, ' + alpha + ')';
                ctx.beginPath();
                ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.globalCompositeOperation = 'source-over';

            // 衰减 life
            for (let i = trailPoints.length - 1; i >= 0; i--) {
                trailPoints[i].life -= 0.022;
                if (trailPoints[i].life <= 0) trailPoints.splice(i, 1);
            }
        }
    }

    window.requestAnimationFrame(animate);

    // ==================== 开关按钮 ====================
    function createToggleBtn() {
        // 避免重复创建
        if (document.getElementById('mouse-trail-toggle')) return;

        const btn = document.createElement('button');
        btn.id = 'mouse-trail-toggle';
        btn.className = 'mouse-trail-toggle';
        btn.setAttribute('aria-label', '切换鼠标火光拖尾效果');
        btn.innerHTML = '<span class="trail-icon">✦</span><span class="trail-label">火光拖尾</span>';
        document.body.appendChild(btn);

        btn.addEventListener('click', function () {
            window.__setMouseTrail(!trailOn);
        });

        // 同步初始状态
        updateToggleBtn();
    }

    function updateToggleBtn() {
        const btn = document.getElementById('mouse-trail-toggle');
        if (!btn) return;
        if (trailOn) {
            btn.classList.remove('off');
            btn.title = '关闭鼠标火光拖尾';
        } else {
            btn.classList.add('off');
            btn.title = '开启鼠标火光拖尾';
        }
    }

    // ── 注入按钮样式 ──
    function injectStyle() {
        if (document.getElementById('mouse-trail-style')) return;
        const style = document.createElement('style');
        style.id = 'mouse-trail-style';
        style.textContent = `
/* 鼠标火光拖尾开关按钮 */
.mouse-trail-toggle {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 10000;
    pointer-events: auto;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: rgba(3, 5, 8, 0.65);
    border: 1px solid rgba(184, 146, 58, 0.25);
    border-radius: 2px;
    color: var(--ash-gold-dim, #8a7340);
    font-family: 'Noto Serif SC', serif;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    cursor: pointer;
    transition: all 0.3s;
    backdrop-filter: blur(4px);
    user-select: none;
}
.mouse-trail-toggle:hover {
    border-color: rgba(184, 146, 58, 0.55);
    color: var(--ash-gold, #c9a84c);
}
.mouse-trail-toggle.off {
    border-color: rgba(60, 60, 60, 0.3);
    color: rgba(100, 100, 100, 0.5);
}
.mouse-trail-toggle .trail-icon {
    font-size: 0.85rem;
    line-height: 1;
    transition: opacity 0.3s;
}
.mouse-trail-toggle.off .trail-icon {
    opacity: 0.4;
}
.mouse-trail-toggle .trail-label {
    font-size: 0.68rem;
}

/* 拖尾按钮在返回按钮下方 */
.mouse-trail-toggle {
    bottom: 6px;
}
#ash-return-btn ~ .mouse-trail-toggle,
.mouse-trail-toggle {
    bottom: 6px;
}
@media (max-width: 768px) {
    .mouse-trail-toggle {
        bottom: 16px;
        right: 12px;
        padding: 8px 12px;
        font-size: 0.68rem;
    }
    .mouse-trail-toggle {
        bottom: 4px;
    }
    #ash-return-btn ~ .mouse-trail-toggle,
    .particle-toggle ~ .mouse-trail-toggle {
        bottom: 4px;
    }
}
`;
        document.head.appendChild(style);
    }

    // ── 初始化按钮 ──
    injectStyle();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createToggleBtn);
    } else {
        createToggleBtn();
    }

})();
