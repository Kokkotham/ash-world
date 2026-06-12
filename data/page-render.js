// 灰烬世界 Ontology 页面渲染引擎
// 所有子页面引用此文件，即可从 data/ 读取内容并显示关联
(function() {
  async function init(pageName) {
    await window.AshData.loadAll();
    const data = window.AshData;
    if (!data.loaded) return;

    switch (pageName) {
      case 'modules': renderModules(data); break;
      case 'pantheon': renderPantheon(data); break;
      case 'worldview': break;  // 世界观页以文本为主，底部加关联
      case 'map': break;        // 地图页是 SVG，底部加关联
      case 'rules': break;      // 规则书是交互式，底部加关联
      case 'character-sheet': break;
      case 'glossary': renderGlossary(data); break;
      case 'news': renderNews(data); break;
      case 'articles': renderArticles(data); break;
      case 'art': break;
      case 'discussion': break;
      case 'community': renderCommunity(data); break;
      case 'merch': renderMerch(data); break;
      case 'works': renderWorks(data); break;
    }

    // 底部关联区块
    const linked = document.getElementById('onto-linked');
    if (linked) renderPageLinks(data, linked);
  }

  function renderModules(data) {
    const el = document.getElementById('onto-content');
    if (!el || !data.modules) return;
    let html = '';
    html += cardSection('官方战役模组', data.modules.official, data);
    html += cardSection('短篇模组', data.modules.short, data);
    html += '<h2 class="section-title">主持人工具包</h2><div class="text-block">官方主持人工具包包含以下资源，帮助主持人更轻松地创建自己的灰烬世界冒险：</div>';
    html += '<div class="card-grid">' +
      '<div class="card"><h3>随机事件生成表</h3><p>涵盖旅行、城市、荒野、地下城四大场景的 200+ 条随机事件。</p></div>' +
      '<div class="card"><h3>NPC 快速生成器</h3><p>包含姓名、种族、职业、动机、秘密五维度快速生成表。</p></div>' +
      '<div class="card"><h3>地图素材包</h3><p>20 张可打印的战术地图，涵盖森林、地下城、城市街道、船只等场景。</p></div>' +
      '</div>';
    el.innerHTML = html;
  }

  function cardSection(title, items, data) {
    if (!items || items.length === 0) return '';
    let html = '<h2 class="section-title">' + title + '</h2><div class="card-grid">';
    items.forEach(item => {
      const links = data.resolveLinks('module', item.id);
      let linkedHTML = '';
      if (links.length > 0) {
        linkedHTML = '<div style="margin-top:8px;font-size:0.8rem;color:var(--ash-gold-dim)"><strong>关联：</strong>';
        const seen = new Set();
        links.forEach(l => {
          if (!l.target || !l.target.name) return;
          if (seen.has(l.target.name)) return;
          seen.add(l.target.name);
          linkedHTML += '<span style="margin-right:6px">' + l.target.name + '</span>';
        });
        linkedHTML += '</div>';
      }
      html += '<div class="card"><h3>' + (item.name || '') + '</h3><p>' + (item.desc || '') + '</p>' +
        '<div class="meta">难度：' + (item.difficulty || '') + ' | 时长：' + (item.duration || '') +
        (item.players ? ' | 推荐人数：' + item.players : '') +
        (item.source ? ' | ' + item.source : '') + '</div>';
      if (item.tags) {
        html += '<div class="region-tags" style="margin-top:8px">';
        item.tags.forEach(t => { html += '<span class="tag">' + t + '</span>'; });
        html += '</div>';
      }
      html += linkedHTML + '</div>';
    });
    html += '</div>';
    return html;
  }

  function renderPantheon(data) {
    const el = document.getElementById('onto-content');
    if (!el || !data.deities) return;
    let html = '';

    html += '<h2 class="section-title">三大神系</h2><div class="card-grid">';
    (data.deities.pantheons || []).forEach(p => {
      html += '<div class="card"><h3>' + p.name + '</h3><p>' + (p.desc || '') + '</p></div>';
    });
    html += '</div>';

    html += '<h2 class="section-title">十二圣工（半神英雄）</h2><div class="card-grid">';
    (data.deities.twelve_labors || []).forEach(l => {
      const links = data.resolveLinks('labor', l.id);
      let linkedHTML = '';
      if (links.length > 0) {
        linkedHTML = '<div style="margin-top:6px;font-size:0.8rem;color:var(--ash-gold-dim)">关联：';
        const seen = new Set();
        links.forEach(link => {
          if (!link.target || !link.target.name) return;
          if (seen.has(link.target.name)) return;
          seen.add(link.target.name);
          linkedHTML += '<span style="margin-right:6px">' + link.target.name + '</span>';
        });
        linkedHTML += '</div>';
      }
      html += '<div class="card"><h3>' + l.name + '</h3><p class="meta">' + (l.title || '') + '</p><p>' + (l.desc || '') + '</p>' + linkedHTML + '</div>';
    });
    html += '</div>';

    if (data.deities.notable_deities) {
      html += '<h2 class="section-title">特殊神祇</h2><div class="card-grid">';
      data.deities.notable_deities.forEach(d => {
        html += '<div class="card"><h3>' + d.name + '</h3><p>' + (d.title || '') + '</p><p class="meta">主要信仰区域：' + (d.worshiped_by || '') + '</p></div>';
      });
      html += '</div>';
    }
    el.innerHTML = html;
  }

  function renderGlossary(data) {
    const el = document.getElementById('onto-content');
    if (!el) return;
    el.innerHTML = '<p style="text-align:center;color:var(--ash-gold-dim);padding:40px">术语表数据已迁移至 data/ 层。<br>搜索和分类筛选功能保持可用。</p>';
  }

  function renderNews(data) {
    const el = document.getElementById('onto-content');
    if (!el) return;
    el.innerHTML = '<p style="text-align:center;color:var(--ash-gold-dim);padding:40px">新闻数据已迁移至 data/ 层。<br>时间线展示功能保持可用。</p>';
  }

  function renderArticles(data) {
    const el = document.getElementById('onto-content');
    if (!el) return;
    el.innerHTML = '<p style="text-align:center;color:var(--ash-gold-dim);padding:40px">文章数据已迁移至 data/ 层。<br>深度阅读功能保持可用。</p>';
  }

  function renderCommunity(data) {
    const el = document.getElementById('onto-content');
    if (!el) return;
    el.innerHTML = '<p style="text-align:center;color:var(--ash-gold-dim);padding:40px">共创项目数据已迁移至 data/ 层。</p>';
  }

  function renderMerch(data) {
    const el = document.getElementById('onto-content');
    if (!el) return;
    el.innerHTML = '<p style="text-align:center;color:var(--ash-gold-dim);padding:40px">商品数据已迁移至 data/ 层。</p>';
  }

  function renderWorks(data) {
    const el = document.getElementById('onto-content');
    if (!el) return;
    el.innerHTML = '<p style="text-align:center;color:var(--ash-gold-dim);padding:40px">衍生作品数据已迁移至 data/ 层。</p>';
  }

  function renderPageLinks(data, el) {
    el.innerHTML = '<h2 class="section-title">Ontology 关联一览</h2>' +
      '<div style="font-size:0.85rem;color:var(--ash-gold-dim);line-height:1.8">' +
      '<p>数据来源：<code>data/links.json</code>（共 ' + (data.links ? data.links.length : 0) + ' 条关系链接）</p>' +
      '<p>链接类型：栖息于 · 发生在 · 涉及 · 受信仰于 · 关联事件</p>' +
      '<p>数据实体：' + data.races.total + ' 个种族 · ' +
      (data.deities?.pantheons?.length || 0) + ' 神系 · ' +
      (data.deities?.twelve_labors?.length || 0) + ' 圣工</p>' +
      '</div>';
  }

  window.PageRender = { init };
})();
