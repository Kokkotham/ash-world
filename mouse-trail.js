/**
 * mouse-trail.js — 灰烬世界子页面鼠标火光拖尾效果
 * 用法：在子页面 </body> 前加 <script src="../mouse-trail.js"></script>
 * 效果：暖橙色鼠标光晕 + 火星粒子拖尾，无 Three.js 背景粒子
 */
(function () {
    'use strict';

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
})();
