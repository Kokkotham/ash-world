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

  // 以下页面已有丰富的 HTML 内容，不覆盖 #onto-content
  // 仅保留底部 Ontology 关联区块
  function renderGlossary(data) {}
  function renderNews(data) {}
  function renderArticles(data) {}
  function renderCommunity(data) {}
  function renderMerch(data) {}
  function renderWorks(data) {}

  function renderPageLinks(data, el) {
    // 用户友好的关联内容展示，不再暴露调试信息
    const raceCount = data.races ? data.races.total : 0;
    const deityCount = (data.deities?.pantheons?.length || 0) + (data.deities?.twelve_labors?.length || 0) + (data.deities?.notable_deities?.length || 0);
    const moduleCount = data.modules ? (data.modules.official?.length || 0) + (data.modules.short?.length || 0) : 0;
    const regionCount = data.regions ? data.regions.length : 0;
    const linkCount = data.links ? data.links.length : 0;

    let html = '<h2 class="section-title">相关内容</h2>';
    html += '<div class="card-grid" style="grid-template-columns:repeat(auto-fill,minmax(180px,1fr))">';
    html += '<div class="card"><h3>种族</h3><p class="meta">' + raceCount + ' 个种族设定</p></div>';
    html += '<div class="card"><h3>神系</h3><p class="meta">' + deityCount + ' 位神祇与圣工</p></div>';
    html += '<div class="card"><h3>模组</h3><p class="meta">' + moduleCount + ' 个冒险模组</p></div>';
    html += '<div class="card"><h3>地区</h3><p class="meta">' + regionCount + ' 个地区设定</p></div>';
    html += '</div>';
    html += '<div style="text-align:center;margin-top:20px;font-size:0.8rem;color:var(--ash-gold-dim);opacity:0.6">' +
      '以上内容通过 ' + linkCount + ' 条设定关联相互连接</div>';
    el.innerHTML = html;
  }

  window.PageRender = { init };
})();
