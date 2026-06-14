/**
 * 灰烬世界关键词 Tooltip 子系统
 * IIFE — 零依赖。扫描 DOM 中 [data-keyword] 元素，hover 时显示术语释义。
 * 支持 glossary.json 动态加载、别名匹配、200ms 延迟、视口边界检测。
 */
(function() {
  'use strict';

  var tooltip = null;
  var glossaryMap = new Map();
  var hoverTimer = null;
  var initDone = false;

  /**
   * 初始化：加载 glossary.json → 构建 Map → 创建 Tooltip DOM → 扫描关键词
   */
  async function init() {
    if (initDone) return;
    initDone = true;

    try {
      var resp = await fetch('../data/glossary.json');
      if (!resp.ok) return;
      var data = await resp.json();
      var entries = data.entries || [];
      entries.forEach(function(e) {
        var key = e.term || e.name || '';
        if (key) {
          glossaryMap.set(key, e);
          glossaryMap.set(key.toLowerCase(), e);
        }
        if (e.aliases && e.aliases.length) {
          e.aliases.forEach(function(a) {
            glossaryMap.set(a, e);
            glossaryMap.set(a.toLowerCase(), e);
          });
        }
      });
    } catch (_) {
      // glossary.json 加载失败时静默降级，不影响页面功能
      return;
    }

    if (glossaryMap.size === 0) return;

    createTooltip();
    scanKeywords();
  }

  /**
   * 创建全局 tooltip 元素并附加到 body
   */
  function createTooltip() {
    tooltip = document.createElement('div');
    tooltip.id = 'ash-tooltip';
    tooltip.className = 'tt-hidden';
    document.body.appendChild(tooltip);
  }

  /**
   * 扫描当前 DOM 中所有 [data-keyword] 元素并绑定 hover 事件
   */
  function scanKeywords() {
    var elements = document.querySelectorAll('[data-keyword]');
    elements.forEach(function(el) {
      // 避免重复绑定
      if (el.dataset.keywordBound === '1') return;
      el.dataset.keywordBound = '1';

      el.addEventListener('mouseenter', function(e) {
        var key = el.getAttribute('data-keyword');
        if (!key) return;
        var entry = glossaryMap.get(key) || glossaryMap.get(key.toLowerCase());
        if (!entry) return;

        clearTimeout(hoverTimer);
        hoverTimer = setTimeout(function() {
          showTooltip(e, entry);
        }, 200);
      });

      el.addEventListener('mouseleave', function() {
        clearTimeout(hoverTimer);
        hoverTimer = null;
        hideTooltip();
      });
    });
  }

  /**
   * 显示 tooltip 并渲染内容
   * @param {MouseEvent} e - 鼠标事件
   * @param {Object} entry - 术语条目
   */
  function showTooltip(e, entry) {
    if (!tooltip) return;

    var termName = entry.term || entry.name || '';
    var category = entry.category || '';
    var definition = entry.definition || entry.desc || '';

    var html = '<div class="tt-term">' + escapeHtml(termName) + '</div>';
    if (category) {
      html += '<div class="tt-category">' + escapeHtml(category) + '</div>';
    }
    html += '<div class="tt-def">' + escapeHtml(definition) + '</div>';

    tooltip.innerHTML = html;
    tooltip.classList.remove('tt-hidden');
    positionTooltip(e);
  }

  /**
   * 隐藏 tooltip
   */
  function hideTooltip() {
    if (tooltip) {
      tooltip.classList.add('tt-hidden');
    }
  }

  /**
   * tooltip 定位：跟随鼠标 + 视口边界检测
   * @param {MouseEvent} e - 鼠标事件
   */
  function positionTooltip(e) {
    if (!tooltip) return;

    var offset = 14;
    var margin = 10;
    var x = e.clientX + offset;
    var y = e.clientY + offset;

    // 先设置位置再读取尺寸，确保 getBoundingClientRect 准确
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';

    var rect = tooltip.getBoundingClientRect();
    var winW = window.innerWidth;
    var winH = window.innerHeight;

    // 右边界溢出 → 翻转到左侧
    if (x + rect.width > winW - margin) {
      x = e.clientX - rect.width - offset;
      if (x < margin) x = margin;
      tooltip.style.left = x + 'px';
    }

    // 下边界溢出 → 翻转到上方
    if (y + rect.height > winH - margin) {
      y = e.clientY - rect.height - offset;
      if (y < margin) y = margin;
      tooltip.style.top = y + 'px';
    }
  }

  /**
   * HTML 转义，防止 XSS
   * @param {string} str
   * @returns {string}
   */
  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ========== 启动 ==========
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
