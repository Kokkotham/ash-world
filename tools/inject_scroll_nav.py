"""
在 page-render.js 末尾（window.PageRender = { init } 之前）
注入横向拖拽滑动 + 箭头翻页交互逻辑
"""
import re

JS_PATH = r"C:\ProgramData\WorkBuddy\chromium-env\13613ht\WorkBuddy\2026-06-07-11-51-51\data\page-render.js"

with open(JS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 要注入的代码
scroll_code = r'''
  /* ═══════════════════════════════════════════
   * 横向滚动条增强：鼠标拖拽 + 左右箭头翻页
   * 适用: .sub-nav-bar 和 .detail-nav-bar
   * ═══════════════════════════════════════════ */
  (function initScrollableNav() {
    var SCROLL_AMOUNT = 280; // 每次箭头点击滚动像素

    function makeScrollable(bar) {
      if (!bar) return;
      bar.classList.add('scroll-enhanced');
      var isDown = false;
      var startX, scrollLeft;
      var arrowsContainer;

      // ---- 鼠标/触摸 拖拽滑动 ----
      bar.addEventListener('mousedown', function(e) {
        isDown = true;
        bar.style.cursor = 'grabbing';
        startX = e.pageX - bar.offsetLeft;
        scrollLeft = bar.scrollLeft;
        e.preventDefault();
      });
      bar.addEventListener('mouseleave', function() { isDown = false; bar.style.cursor = 'grab'; });
      bar.addEventListener('mouseup', function() { isDown = false; bar.style.cursor = 'grab'; });
      bar.addEventListener('mousemove', function(e) {
        if (!isDown) return;
        e.preventDefault();
        var x = e.pageX - bar.offsetLeft;
        var walk = (x - startX) * 1.2; // 拖拽灵敏度
        bar.scrollLeft = scrollLeft - walk;
        updateArrows();
      });

      // 触摸支持（原生已支持overflow-x auto，这里只做箭头更新）
      bar.addEventListener('scroll', function() { updateArrows(); }, { passive: true });

      // ---- 左右箭头按钮 ----
      arrowsContainer = document.createElement('div');
      arrowsContainer.className = 'scroll-arrows';

      var leftBtn = document.createElement('button');
      leftBtn.className = 'scroll-arrow-btn left';
      leftBtn.innerHTML = '&#8249;'; // ‹
      leftBtn.setAttribute('type', 'button');
      leftBtn.setAttribute('aria-label', '向左滚动');

      var rightBtn = document.createElement('button');
      rightBtn.className = 'scroll-arrow-btn right';
      rightBtn.innerHTML = '&#8250;'; // ›
      rightBtn.setAttribute('type', 'button');
      rightBtn.setAttribute('aria-label', '向右滚动');

      leftBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        smoothScrollBy(bar, -SCROLL_AMOUNT);
      });
      rightBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        smoothScrollBy(bar, SCROLL_AMOUNT);
      });

      arrowsContainer.appendChild(leftBtn);
      arrowsContainer.appendChild(rightBtn);
      bar.appendChild(arrowsContainer);

      // 初始状态（延迟到bar visible后检测）
      setTimeout(updateArrows, 350);
      bar._scrollLeftBtn = leftBtn;
      bar._scrollRightBtn = rightBtn;

      function updateArrows() {
        var canScrollLeft = bar.scrollLeft > 3;
        var canScrollRight = bar.scrollLeft < bar.scrollWidth - bar.clientWidth - 3;
        if (leftBtn) leftBtn.classList.toggle('visible', canScrollLeft);
        if (rightBtn) rightBtn.classList.toggle('visible', canScrollRight);
      }
    }

    function smoothScrollBy(el, amount) {
      el.scrollTo({
        left: el.scrollLeft + amount,
        behavior: 'smooth'
      });
    }

    // 用 MutationObserver 监听 nav-bar 变为 visible 时初始化
    var observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(m) {
        if (m.target.classList.contains('sub-nav-bar') || m.target.classList.contains('detail-nav-bar')) {
          if (m.target.classList.contains('visible') && !m.target.classList.contains('scroll-enhanced')) {
            makeScrollable(m.target);
          }
        }
      });
    });

    // 观察已有的nav-bar（DOM ready后）
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(function() {
        document.querySelectorAll('.sub-nav-bar.visible, .detail-nav-bar.visible').forEach(function(el) {
          if (!el.classList.contains('scroll-enhanced')) makeScrollable(el);
        });
        // 监听尚未visible的nav-bar
        document.querySelectorAll('.sub-nav-bar, .detail-nav-bar').forEach(function(el) {
          observer.observe(el, { attributes: true, attributeFilter: ['class'] });
        });
      }, 200);
    });

    // 全局暴露，供动态创建的nav-bar调用
    window.initScrollableNav = makeScrollable;
  })();

'''

# 在 "window.PageRender = { init };" 之前注入
marker = "  window.PageRender = { init };"
if marker in content:
    content = content.replace(marker, scroll_code + marker)
    with open(JS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 注入成功！在 window.PageRender 之前添加了横向滚动增强代码")
else:
    print("❌ 未找到注入点 marker")
