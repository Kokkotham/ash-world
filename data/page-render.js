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
      case 'rules': renderRules(data); break;
      case 'character-sheet': break;
      case 'races': renderPlayerRaces(data); break;
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

  // 术语表页面：卡片网格，按 categories 分组过滤
  function renderGlossary(data) {
    var el = document.getElementById('onto-content');
    if (!el || !data.glossary) return;
    var entries = data.glossary.entries || [];
    var categories = {};
    entries.forEach(function(e) {
      var cat = e.category || '未分类';
      if (!categories[cat]) categories[cat] = [];
      categories[cat].push(e);
    });
    var html = '';
    var catNames = Object.keys(categories).sort();
    catNames.forEach(function(cat) {
      html += '<h2 class="section-title">' + cat + '</h2><div class="card-grid">';
      categories[cat].forEach(function(entry) {
        html += '<div class="card"><h3>' + (entry.term || entry.name || '') + '</h3>';
        if (entry.aliases && entry.aliases.length) {
          html += '<p class="meta">别称：' + entry.aliases.join('、') + '</p>';
        }
        html += '<p>' + (entry.definition || entry.desc || '') + '</p></div>';
      });
      html += '</div>';
    });
    el.innerHTML = html;
  }

  // 规则书页面：左侧折叠树 + 右侧内容面板
  function renderRules(data) {
    var el = document.getElementById('onto-content');
    if (!el || !data.chapters) return;
    var chapters = data.chapters || [];

    function buildTree(nodes) {
      if (!nodes || !nodes.length) return '';
      var html = '<ul>';
      nodes.forEach(function(node) {
        if (node.children && node.children.length) {
          html += '<li><details><summary>' + (node.title || node.name || '') + '</summary>';
          html += buildTree(node.children);
          html += '</details></li>';
        } else {
          html += '<li><a href="#" class="rules-nav-link" data-chapter="' + (node.id || '') + '">' + (node.title || node.name || '') + '</a></li>';
        }
      });
      html += '</ul>';
      return html;
    }

    var html = '<div class="rules-layout">';
    html += '<nav class="rules-sidebar" id="rules-sidebar">' + buildTree(chapters) + '</nav>';
    html += '<div id="rules-content" class="rules-content"><p style="color:var(--ash-gold-dim);text-align:center;padding:40px">请从左侧选择一个章节</p></div>';
    html += '</div>';
    el.innerHTML = html;

    // 点击叶子节点加载内容
    var links = el.querySelectorAll('.rules-nav-link');
    links.forEach(function(link) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        var chapterId = this.getAttribute('data-chapter');
        loadChapterContent(chapterId, data);
      });
    });
  }

  function loadChapterContent(chapterId, data) {
    var contentEl = document.getElementById('rules-content');
    if (!contentEl) return;
    // 在 chapters 树中递归查找节点
    function findNode(nodes, id) {
      for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].id === id) return nodes[i];
        if (nodes[i].children) {
          var found = findNode(nodes[i].children, id);
          if (found) return found;
        }
      }
      return null;
    }
    var node = findNode(data.chapters, chapterId);
    if (!node) {
      contentEl.innerHTML = '<p style="color:var(--ash-danger)">未找到章节：' + chapterId + '</p>';
      return;
    }
    // 根据 data_source + data_path 查找内容
    var sourceData = null;
    if (node.data_source) {
      sourceData = data[node.data_source];
    }
    var content = node.content || '';
    var html = '<h2>' + (node.title || node.name || '') + '</h2>';
    if (content) {
      html += '<div class="text-block">' + content + '</div>';
    }
    // 渲染关联表格
    if (node.tables && node.tables.length) {
      node.tables.forEach(function(t) {
        html += '<h3>' + (t.title || '表格') + '</h3>';
        html += renderLevelTable(t.rows || t.data || []);
      });
    }
    // 如果 node 包含 level_table 直接渲染
    if (node.level_table) {
      html += renderLevelTable(node.level_table);
    }
    contentEl.innerHTML = html;
  }

  // 渲染等级/数据表格
  function renderLevelTable(table) {
    if (!table || !table.length) return '';
    var headers = Object.keys(table[0]);
    var html = '<table class="level-table"><thead><tr>';
    headers.forEach(function(h) { html += '<th>' + h + '</th>'; });
    html += '</tr></thead><tbody>';
    table.forEach(function(row) {
      html += '<tr>';
      headers.forEach(function(h) { html += '<td>' + (row[h] != null ? row[h] : '') + '</td>'; });
      html += '</tr>';
    });
    html += '</tbody></table>';
    return html;
  }

  // 玩家种族页面：属性条 + 特质列表
  function renderPlayerRaces(data) {
    var el = document.getElementById('onto-content');
    if (!el || !data.races || !data.races.players) return;
    var players = data.races.players;
    var attrNames = [
      { key: 'strength', label: '躯魄' },
      { key: 'agility', label: '敏韧' },
      { key: 'constitution', label: '体质' },
      { key: 'intelligence', label: '心智' },
      { key: 'wisdom', label: '洞识' },
      { key: 'charisma', label: '魅力' }
    ];
    var html = '<h2 class="section-title">玩家种族</h2><div class="card-grid">';
    players.forEach(function(player) {
      var vsTag = '';
      if (player.version_status) {
        var vsClass = player.version_status === '新' ? 'tag-new' : 'tag-modified';
        vsTag = ' <span class="' + vsClass + '" style="font-size:0.7rem;padding:1px 6px;border-radius:8px;vertical-align:middle;margin-left:6px">' + player.version_status + '</span>';
      }
      html += '<div class="card"><h3>' + player.name + vsTag + '</h3>';
      // 属性条形图
      html += '<div class="attr-bars" style="margin:8px 0">';
      var mods = player.attribute_mods || {};
      attrNames.forEach(function(a) {
        var val = mods[a.key] || 0;
        var barColor = val > 0 ? 'var(--ash-gold)' : val < 0 ? 'var(--ash-danger)' : '#555';
        var barWidth = Math.abs(val) * 20;
        html += '<div style="display:flex;align-items:center;margin:2px 0;font-size:0.75rem">';
        html += '<span style="width:32px;text-align:right;margin-right:4px;color:var(--ash-gold-dim)">' + a.label + '</span>';
        html += '<span style="display:inline-block;width:' + barWidth + 'px;height:8px;background:' + barColor + ';border-radius:4px;min-width:4px"></span>';
        html += '<span style="margin-left:4px;color:' + (val >= 0 ? 'var(--ash-gold)' : 'var(--ash-danger)') + '">' + (val >= 0 ? '+' : '') + val + '</span>';
        html += '</div>';
      });
      html += '</div>';
      // 描述
      if (player.desc && player.desc.length) {
        html += '<p style="font-size:0.85rem;color:var(--ash-gold-dim)">' + player.desc.slice(0, 2).join(' ') + '</p>';
      }
      // 特质列表
      if (player.traits && player.traits.length) {
        html += '<div style="margin-top:6px"><strong style="font-size:0.8rem;color:var(--ash-gold)">种族特质：</strong>';
        html += '<ul style="margin:4px 0 0 16px;font-size:0.78rem;color:var(--ash-gold-dim)">';
        var shownTraits = player.traits.slice(0, 4);
        shownTraits.forEach(function(t) {
          html += '<li><strong>' + t.name + '</strong>：' + t.desc.substring(0, 80) + (t.desc.length > 80 ? '...' : '') + '</li>';
        });
        if (player.traits.length > 4) {
          html += '<li style="list-style:none;color:var(--ash-gold)">...还有 ' + (player.traits.length - 4) + ' 个特质</li>';
        }
        html += '</ul></div>';
      }
      // 玩法提示
      if (player.gameplay_notes) {
        html += '<div class="meta" style="margin-top:6px">' + player.gameplay_notes + '</div>';
      }
      // 关键词
      if (player.related_keywords && player.related_keywords.length) {
        html += '<div class="region-tags" style="margin-top:6px">';
        player.related_keywords.forEach(function(kw) {
          html += '<span class="tag">' + kw + '</span>';
        });
        html += '</div>';
      }
      html += '</div>';
    });
    html += '</div>';
    el.innerHTML = html;
  }

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
