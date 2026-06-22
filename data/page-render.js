// 灰烬世界 Ontology 页面渲染引擎
// 所有子页面引用此文件，即可从 data/ 读取内容并显示关联
(function() {

  // 用户可见的错误提示（仅在需要数据的页面上显示）
  function showError(msg) {
    var el = document.getElementById('onto-content');
    if (!el) return;
    // 如果内容区已经有实质内容（如"敬请期待"），不要覆盖它
    if (el.children.length > 0 && el.innerText.trim().length > 20) {
      console.warn('[PageRender] 数据加载失败但页面有静态内容，跳过错误覆盖:', msg);
      return;
    }
    el.innerHTML = '<div style="text-align:center;padding:60px 20px;color:var(--ash-dim)">' +
      '<h2 style="color:var(--ash-gold);margin-bottom:12px">⚠ 内容加载异常</h2>' +
      '<p style="margin-bottom:8px">' + msg + '</p>' +
      '<p style="font-size:0.78rem;opacity:0.6">请按 Ctrl+F5 强制刷新，或稍后重试</p></div>';
  }

  // 需要动态数据渲染的页面列表（这些页面缺失数据时才显示错误）
  var DATA_REQUIRED_PAGES = ['rules', 'races', 'pantheon', 'glossary', 'modules'];

  async function init(pageName) {
    try {
      await window.AshData.loadAll();
    } catch(e) {
      console.error('[PageRender] loadAll failed:', e);
      // 只在需要数据的页面才显示错误
      if (DATA_REQUIRED_PAGES.indexOf(pageName) >= 0) {
        showError('数据加载异常：' + (e.message || e));
      }
      return;
    }
    var data = window.AshData;
    if (!data.loaded) return;

    // 检查关键文件是否缺失
    if (data.loadErrors && data.loadErrors.length > 0) {
      console.warn('[PageRender] 缺失文件:', data.loadErrors);
      // 不阻断渲染，但记录缺失
    }

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

  // 检测中英混合标题（如"灰烬世界Ember world"、"灵涅Soul Nirvana"）
  // 规则：同时含中文字符和英文字母、不以句号等标点结尾、长度适中
  function isMixedTitle(text) {
    if (!text || text.length > 80) return false;
    var hasCJK = /[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]/.test(text);
    var hasLatin = /[A-Za-z]/.test(text);
    if (!hasCJK && !hasLatin) return false;
    // 纯中文短标题（如"灵涅与我"）：不长且不带句末标点
    if (hasCJK && !hasLatin) {
      if (text.length > 30) return false;
      if (/[。！？.!?,;；，：]$/.test(text.trim())) return false;
      return true;
    }
    // 中英混合：不以句子标点结尾
    if (/[。！？.!?,;；]$/.test(text)) return false;
    // 不是纯数字+单位（如"1.5米——1.9米"）
    if (/^[\d\s\-—–.]+$/.test(text)) return false;
    return true;
  }

  // ============================================================
  //  规则书速查版：Tab 切换面板（非滚动阅读器）
  //  点击章节标签 → 切换内容区 | 点击子章节 pill → 切换子内容
  // ============================================================
  function renderRules(data) {
    var el = document.getElementById('onto-content');
    if (!el) return;
    if (!data.chapters) {
      el.innerHTML = '<div style="text-align:center;padding:60px 20px;color:var(--ash-dim)">' +
        '<h2 style="color:var(--ash-gold);margin-bottom:12px">⚠ 规则书数据不可用</h2>' +
        '<p style="margin-bottom:8px">章节索引文件（chapters.json）未能加载。</p>' +
        (data.loadErrors && data.loadErrors.length > 0 ?
          '<p style="font-size:0.82rem;opacity:0.7">缺失文件：' + data.loadErrors.join('、') + '</p>' : '') +
        '<p style="font-size:0.78rem;margin-top:16px;opacity:0.5">请尝试 Ctrl+F5 强制刷新</p></div>';
      return;
    }
    var chapters = data.chapters.chapters || [];

    // 构建横向章节标签导航 HTML
    var navHTML = '';
    chapters.forEach(function(ch) {
      var isEmpty = !hasChapterContent(ch, data);
      var cls = 'chapter-tab' + (isEmpty ? ' empty' : '');
      navHTML += '<div class="' + cls + '" data-target="' + ch.id + '" role="button" tabindex="0">';
      // 只显示章节名，不再显示"第X章"编号
      navHTML += '<span class="tab-title">' + (ch.title || ch.name || '') + '</span>';
      navHTML += '</div>';
    });

    // 构建子章节导航条 HTML（每个有 sub_sections 的章节对应一组 pills）
    var subNavHTML = '<div class="sub-nav-bar" id="sub-nav-bar">';
    chapters.forEach(function(ch) {
      if (ch.sub_sections && ch.sub_sections.length > 0) {
        subNavHTML += '<div class="sub-pills-group" data-chapter="' + ch.id + '" style="display:none">';
        ch.sub_sections.forEach(function(sub, sidx) {
          var subId = 'reader-' + (sub.id || (ch.id + '-sub-' + sidx));
          subNavHTML += '<span class="sub-pill" data-target="' + subId + '" role="button" tabindex="0">' + (sub.title || sub.name || '子章节') + '</span>';
        });
        subNavHTML += '</div>';
      }
    });
    subNavHTML += '</div>';
    // 第三层导航：技能条目 pills（动态填充）
    var detailNavHTML = '<div class="detail-nav-bar" id="detail-nav-bar"></div>';

    // 组装布局：导航区 + 空内容区（由 switchChapter 填充）
    var html = '<div class="reader-layout">';
    html += '<div class="reader-nav-wrapper">';
    html += '<nav class="reader-nav" id="reader-nav">' + navHTML + '</nav>';
    html += subNavHTML;
    html += detailNavHTML;
    html += '</div>';
    html += '<div class="reader-main" id="reader-main"></div>';
    html += '</div>';
    el.innerHTML = html;

    // ---- 交互绑定（Tab 切换，非滚动） ----
    setupLookupInteractions(chapters, data);
  }

  // ---- 切换到大章节 ----
  function switchChapter(chId, chapters, data) {
    var main = document.getElementById('reader-main');
    if (!main) return;

    var ch = null;
    var chIdx = 0;
    for (var i = 0; i < chapters.length; i++) {
      if (chapters[i].id === chId) { ch = chapters[i]; chIdx = i; break; }
    }
    if (!ch) return;

    // 渲染内容
    var contentHTML = '';
    contentHTML += '<section class="reader-chapter" data-chapter="' + ch.id + '">';

    // 如果有章节概述文字，展示概述后自动进入第一个子分类（无中间目录页）
    if (ch.content && ch.content.length > 0) {
      contentHTML += '<div class="chapter-heading">';
      contentHTML += '<h2>' + (ch.title || ch.name || '') + '</h2>';
      contentHTML += '<div class="heading-divider"></div>';
      contentHTML += '</div>';
      contentHTML += '<div class="chapter-body">';
      contentHTML += '<div class="chapter-overview">';
      ch.content.forEach(function(p) {
        var pt = p.trim();
        // 以 "XXX专修（X）" 格式的是小标题
        if (/^[^\s]+（[ABCL]）$/.test(pt) || /^[^\s]+\([ABCL]\)$/.test(pt)) {
          contentHTML += '<h4 class="overview-subtitle">' + p + '</h4>';
        // 中文开头+冒号：属性名小标题（如"躯魄："、"核心躯魄："）
        } else if (/^[一-鿿].*[:：]/.test(pt)) {
          contentHTML += '<h4 class="content-subheading">' + p + '</h4>';
        } else if (p.match(/^[A-Za-z]/)) {
          // 纯英文开头的行作为副标题
          contentHTML += '<h3 class="overview-title">' + p + '</h3>';
        } else if (isMixedTitle(pt)) {
          // 中英混合短文本（如"灰烬世界Ember world"、"灵涅Soul Nirvana"）作为章节小标题
          contentHTML += '<h3 class="overview-title">' + p + '</h3>';
        } else {
          contentHTML += '<p>' + p + '</p>';
        }
      });
      contentHTML += '</div>';
      contentHTML += '</div>'; // end .chapter-body
    } else {
      // 无概述文字：直接渲染完整内容（原有的 renderChapterContent 逻辑）
      contentHTML += renderChapterContent(ch, data, chapters, chIdx);
    }

    contentHTML += '</section>';

    main.innerHTML = contentHTML;
    // 不滚动到顶部，保持当前阅读位置

    // 更新标签激活状态
    var nav = document.getElementById('reader-nav');
    if (nav) {
      nav.querySelectorAll('.chapter-tab').forEach(function(t) { t.classList.remove('active'); });
      var activeTab = nav.querySelector('.chapter-tab[data-target="' + chId + '"]');
      if (activeTab) activeTab.classList.add('active');
    }

    // 更新子章节导航条显示
    updateSubNavVisibility(chId);

    // 清除第三层导航（切换大章节时重置）
    var detailBar = document.getElementById('detail-nav-bar');
    if (detailBar) { detailBar.classList.remove('visible'); detailBar.innerHTML = ''; }
    window.__currentAbilities = null;

    // 记录当前状态（不自动进入子分类，停在章节前言页）
    window.__rulesCurrentChapter = chId;
    window.__rulesCurrentSub = null;
    window.__rulesCurrentSubData = null; // 存储当前子分类引用，用于反选时重绘前言
  }

  // ---- 切换到子章节（显示子分类前言，不自动选技能） ----
  function switchSubSection(subId, chapters, data) {
    var main = document.getElementById('reader-main');
    if (!main) return;

    // 反选检测：如果点击的是当前已激活的子pill → 回退到章节前言
    if (window.__rulesCurrentSub === subId) {
      window.__rulesCurrentSub = null;
      window.__rulesCurrentSubData = null;
      // 重新渲染当前章节的前言
      var currentCh = null;
      for (var ci = 0; ci < chapters.length; ci++) {
        if (chapters[ci].id === window.__rulesCurrentChapter) { currentCh = chapters[ci]; break; }
      }
      if (currentCh) {
        // 复用 switchChapter 的内容渲染逻辑（只更新内容区，不重置导航）
        renderChapterPreface(currentCh);
      }
      // 去除所有sub-pill激活态
      var subNavBar = document.getElementById('sub-nav-bar');
      if (subNavBar) subNavBar.querySelectorAll('.sub-pill').forEach(function(p) { p.classList.remove('active'); });
      // 隐藏第三层导航
      var detailBar = document.getElementById('detail-nav-bar');
      if (detailBar) { detailBar.classList.remove('visible'); detailBar.innerHTML = ''; }
      return;
    }

    // 从 subId 解析出所属章节和子索引：格式 "reader-ch3_instinct"
    var targetSub = null;
    var parentCh = null;

    for (var ci = 0; ci < chapters.length; ci++) {
      var ch = chapters[ci];
      if (!ch.sub_sections) continue;
      for (var si = 0; si < ch.sub_sections.length; si++) {
        var sub = ch.sub_sections[si];
        var expectedId = 'reader-' + (sub.id || (ch.id + '-sub-' + si));
        if (expectedId === subId) {
          targetSub = sub;
          parentCh = ch;
          break;
        }
      }
      if (targetSub) break;
    }

    if (!targetSub || !parentCh) return;

    // 存储当前子分类引用（用于反选时重绘前言）
    window.__rulesCurrentSubData = { sub: targetSub, parent: parentCh };

    // 渲染子分类前言视图
    var contentHTML = '';
    contentHTML += '<section class="reader-chapter" data-chapter="' + parentCh.id + '">';

    // 章节标题头
    contentHTML += '<div class="chapter-heading">';
    contentHTML += '<h2>' + (parentCh.title || parentCh.name || '') + '</h2>';
    contentHTML += '<div class="heading-divider"></div>';
    contentHTML += '</div>';

    contentHTML += '<div class="chapter-body">';

    // 如果子分类有前言文字 → 显示子分类前言
    if (targetSub.content && targetSub.content.length > 0) {
      contentHTML += '<div class="sub-section-preface" id="sub-section-preface">';
      contentHTML += '<h3 class="sub-preface-title">' + (targetSub.title || targetSub.name || '') + '</h3>';
      targetSub.content.forEach(function(p) {
        var pt = p.trim();
        if (/^[A-Za-z]/.test(pt) && !/[\u4e00-\u9fff]/.test(pt)) {
          contentHTML += '<h4 class="overview-title">' + p + '</h4>';
        } else if (isMixedTitle(pt)) {
          // 中英混合标题
          contentHTML += '<h4 class="overview-title">' + p + '</h4>';
        } else {
          contentHTML += '<p>' + p + '</p>';
        }
      });
      contentHTML += '</div>';
    }

    // 技能详情占位容器（由 switchAbility 填充，或保持空白等待用户选择）
    contentHTML += '<div class="ability-detail" id="ability-detail"></div>';

    contentHTML += '</div></section>';

    main.innerHTML = contentHTML;
    // 不滚动到顶部，保持当前阅读位置

    // 确保父章节 tab 高亮
    var nav = document.getElementById('reader-nav');
    if (nav) {
      nav.querySelectorAll('.chapter-tab').forEach(function(t) { t.classList.remove('active'); });
      var activeTab = nav.querySelector('.chapter-tab[data-target="' + parentCh.id + '"]');
      if (activeTab) activeTab.classList.add('active');
    }

    // 高亮当前 pill
    var subNavBar = document.getElementById('sub-nav-bar');
    if (subNavBar) {
      subNavBar.querySelectorAll('.sub-pill').forEach(function(p) { p.classList.remove('active'); });
      var activePill = subNavBar.querySelector('.sub-pill[data-target="' + subId + '"]');
      if (activePill) activePill.classList.add('active');
    }

    window.__rulesCurrentChapter = parentCh.id;
    window.__rulesCurrentSub = subId;

    // ---- ch2 特殊处理：直接子分类（种族）点击后直接显示详情 ----
    if (parentCh.id === 'ch2' && targetSub.type === 'data' && targetSub.data_path && data) {
      // 解析种族数据并直接显示详情
      var src = resolveDataSource(data, targetSub.data_source);
      if (src) {
        var race = resolveDataPath(src, targetSub.data_path);
        if (race && typeof race === 'object') {
          switchRace(race, data);
          // 不隐藏第三层导航 — 种族分支将使用 detail-nav-bar 展示（与专修同款）
          return; // 直接返回，不执行后续的第三层导航初始化
        }
      }
    }

    // ---- 第三层导航：按章节类型初始化 ----
    if (parentCh.id === 'ch3' && targetSub.data_path && data) {
      initThirdLevelNav(targetSub, parentCh, data);
    } else if (parentCh.id === 'ch2' && targetSub.data_path && data && targetSub.type !== 'data') {
      // 保留旧逻辑：如果ch2的子分类不是data类型，调用initRaceNav（分类→种族列表）
      initRaceNav(targetSub, parentCh, data);
    } else {
      // 非 ch2/ch3：隐藏第三层导航
      var detailBar = document.getElementById('detail-nav-bar');
      if (detailBar) { detailBar.classList.remove('visible'); detailBar.innerHTML = ''; }
    }
  }

  // ---- 渲染章节前言（反选子pill时调用，只更新内容区） ----
  function renderChapterPreface(ch) {
    var main = document.getElementById('reader-main');
    if (!main || !ch) return;

    var contentHTML = '';
    contentHTML += '<section class="reader-chapter" data-chapter="' + ch.id + '">';

    if (ch.content && ch.content.length > 0) {
      contentHTML += '<div class="chapter-heading">';
      contentHTML += '<h2>' + (ch.title || ch.name || '') + '</h2>';
      contentHTML += '<div class="heading-divider"></div>';
      contentHTML += '</div>';
      contentHTML += '<div class="chapter-body">';
      contentHTML += '<div class="chapter-overview">';
      ch.content.forEach(function(p) {
        var pt = p.trim();
        // 以 "XXX专修（X）" 格式的是小标题
        if (/^[^\s]+（[ABCL]）$/.test(pt) || /^[^\s]+\([ABCL]\)$/.test(pt)) {
          contentHTML += '<h4 class="overview-subtitle">' + p + '</h4>';
        // 中文开头+冒号：属性名小标题（如"躯魄："、"核心躯魄："）
        } else if (/^[一-鿿].*[:：]/.test(pt)) {
          contentHTML += '<h4 class="content-subheading">' + p + '</h4>';
        } else if (p.match(/^[A-Za-z]/)) {
          // 纯英文开头的行作为副标题
          contentHTML += '<h3 class="overview-title">' + p + '</h3>';
        } else if (isMixedTitle(pt)) {
          // 中英混合短文本作为章节小标题
          contentHTML += '<h3 class="overview-title">' + p + '</h3>';
        } else {
          contentHTML += '<p>' + p + '</p>';
        }
      });
      contentHTML += '</div>';
      contentHTML += '</div>';
    }

    contentHTML += '</section>';
    main.innerHTML = contentHTML;
    // 不滚动到顶部，保持当前阅读位置
  }

  // 初始化第三层导航（技能条目 pills），不自动选中任何一个
  function initThirdLevelNav(sub, parentCh, data) {
    var src = resolveDataSource(data, parentCh.data_source);
    if (!src || !src.categories) return;

    var catData = null;
    for (var i = 0; i < src.categories.length; i++) {
      if (src.categories[i].id === sub.data_path) {
        catData = src.categories[i];
        break;
      }
    }

    var abilities = (catData && catData.abilities) ? catData.abilities : [];

    // 存储当前技能列表供第三层导航使用
    window.__currentAbilities = abilities;
    window.__rulesCurrentAbilityName = null; // 记录当前选中的技能名（用于反选检测）

    // 填充第三层导航条（不预选中任何一项）
    updateDetailNav(abilities, null);
  }

  // ---- 渲染单个子章节的内容 ----
  function renderSingleSubSection(sub, parentCh, data) {
    var html = '';
    html += '<div class="sub-section">';
    html += '<h3>' + (sub.title || sub.name || '') + '</h3>';

    // 根据父章节数据源类型查找数据
    if (parentCh.data_source && data) {
      var src = resolveDataSource(data, parentCh.data_source);
      if (src) {

        // ch3 专修：从 categories 数组查找 → 渲染为可点击技能列表
        if (parentCh.id === 'ch3' && src.categories) {
          var catData = null;
          for (var i = 0; i < src.categories.length; i++) {
            if (src.categories[i].id === sub.data_path) {
              catData = src.categories[i];
              break;
            }
          }
          if (catData && catData.abilities && catData.abilities.length > 0) {
            html += renderAbilityList(catData.abilities);
          } else {
            html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
          }
        }
        // ch4 神术：从 pantheons 查找
        else if (parentCh.id === 'ch4') {
          var pantheon = null;
          if (sub.data_path && src) {
            try { pantheon = resolveDataPath(src, sub.data_path); } catch(e) {}
          }
          // fallback: 按 pantheons 数组索引或 name 匹配
          if (!pantheon && src.pantheons) {
            for (var pi = 0; pi < src.pantheons.length; pi++) {
              if (src.pantheons[pi].name === sub.data_path || src.pantheons[pi].id === sub.data_path) {
                pantheon = src.pantheons[pi];
                break;
              }
            }
          }
          if (pantheon) {
            if (pantheon.doctrine) {
              pantheon.doctrine.forEach(function(d) { html += '<p>' + d + '</p>'; });
            }
            if (pantheon.divine_spells && pantheon.divine_spells.length > 0) {
              html += '<h4>神术列表</h4>';
              html += renderGenericList(pantheon.divine_spells, pantheon);
            }
          } else {
            html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
          }
        }
        // ch5 故事运作：从 sections 查找
        else if (parentCh.id === 'ch5' && src.sections) {
          var secData = null;
          for (var j = 0; j < src.sections.length; j++) {
            if (src.sections[j].name === sub.data_path || src.sections[j].id === sub.data_path) {
              secData = src.sections[j];
              break;
            }
          }
          if (secData && secData.rules && secData.rules.length > 0) {
            html += renderGenericList(secData.rules, sub);
          } else {
            html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
          }
        }
        else {
          html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
        }
      } else {
        html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
      }
    } else {
      html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
    }

    html += '</div>';
    return html;
  }

  // 判断章节是否有实质内容
  function hasChapterContent(ch, data) {
    // 文本类章节：有 content 文本数组且非空
    if (ch.type === 'text' && ch.content && ch.content.length > 0) {
      // content 可能是字符串数组或对象数组
      for (var i = 0; i < ch.content.length; i++) {
        var c = ch.content[i];
        if (typeof c === 'string' && c.trim()) return true;
        if (typeof c === 'object' && c.content && c.content.length) return true;
      }
    }
    // 数据类章节：检查数据源是否有内容
    if (ch.type === 'data' && ch.data_source && data) {
      var src = resolveDataSource(data, ch.data_source);
      if (!src) return false;
      if (ch.data_path) {
        var pathVal = resolveDataPath(src, ch.data_path);
        if (pathVal && Array.isArray(pathVal) && pathVal.length > 0) return true;
      }
      // 检查 sub_sections 是否有内容
      if (ch.sub_sections && ch.sub_sections.length > 0) {
        for (var j = 0; j < ch.sub_sections.length; j++) {
          if (hasChapterContent(ch.sub_sections[j], data)) return true;
        }
      }
    }
    if (ch.sub_sections && ch.sub_sections.length > 0) {
      for (var k = 0; k < ch.sub_sections.length; k++) {
        if (hasChapterContent(ch.sub_sections[k], data)) return true;
      }
    }
    return false;
  }

  // 解析数据源名称（kebab-case → camelCase 兼容）
  function resolveDataSource(data, sourceName) {
    var key = sourceName.replace('.json', '');
    // 直接匹配
    if (data[key] !== undefined) return data[key];
    // kebab-case → camelCase（divine-arts → divineArts, story-rules → storyRules）
    var camelKey = key.replace(/-([a-z])/g, function(m, c) { return c.toUpperCase(); });
    if (data[camelKey] !== undefined) return data[camelKey];
    return null;
  }

  // 解析 data_path（如 "players" 或 "sections[0]"）
  function resolveDataPath(src, path) {
    if (!src || !path) return src;
    var val = src;
    var parts = path.split(/\.|\[|\]/).filter(function(p) { return p.length > 0; });
    for (var i = 0; i < parts.length; i++) {
      if (val == null) return null;
      var key = parts[i];
      if (/^\d+$/.test(key)) {
        val = val[parseInt(key, 10)];
      } else {
        val = val[key];
      }
    }
    return val;
  }

  // 渲染单个章节的内容
  function renderChapterContent(ch, data, allChapters, index) {
    var html = '';

    // 章节标题
    html += '<div class="chapter-heading">';
    html += '<h2>' + (ch.title || ch.name || '') + '</h2>';
    html += '<div class="heading-divider"></div>';
    html += '</div>';

    // 章节正文
    html += '<div class="chapter-body">';

    var hasContent = false;

    // 文本类内容
    if (ch.content && ch.content.length > 0) {
      for (var i = 0; i < ch.content.length; i++) {
        var c = ch.content[i];
        if (typeof c === 'string') {
          // 检测段落是否为标题
          if (isHeadingLine(c)) {
            html += '<h3>' + c + '</h3>';
          } else if (isSubHeadingLine(c)) {
            html += '<h4>' + c + '</h4>';
          } else {
            html += '<p>' + c + '</p>';
          }
          hasContent = true;
        } else if (typeof c === 'object') {
          html += '<div class="sub-section">';
          html += '<h3>' + (c.title || '') + '</h3>';
          if (c.content && c.content.length) {
            for (var j = 0; j < c.content.length; j++) {
              html += '<p>' + c.content[j] + '</p>';
            }
            hasContent = true;
          }
          html += '</div>';
        }
      }
    }

    // 数据类内容
    if (ch.type === 'data' && ch.data_source && data) {
      var src = resolveDataSource(data, ch.data_source);
      if (src) {
        // 根据章节 ID 分发渲染器
        switch (ch.id) {
          case 'ch2':
            var rendered = renderRaceChapter(src, data);
            html += rendered.html;
            hasContent = rendered.hasContent || hasContent;
            break;
          case 'ch3':
            var profRendered = renderProfessionChapter(ch, src, data);
            html += profRendered.html;
            hasContent = profRendered.hasContent || hasContent;
            break;
          case 'ch4':
            var divineRendered = renderDivineChapter(ch, src, data);
            html += divineRendered.html;
            hasContent = divineRendered.hasContent || hasContent;
            break;
          case 'ch5':
            var storyRendered = renderStoryChapter(ch, src, data);
            html += storyRendered.html;
            hasContent = storyRendered.hasContent || hasContent;
            break;
          default:
            var pathVal = resolveDataPath(src, ch.data_path);
            if (pathVal && Array.isArray(pathVal) && pathVal.length > 0) {
              html += renderGenericList(pathVal, ch);
              hasContent = true;
            }
        }
      }
    }

    // 如果没有任何内容，显示占位
    if (!hasContent) {
      html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
    }

    html += '</div>'; // .chapter-body

    return html;
  }

  // ---- ch2: 种族章节渲染 ----
  function renderRaceChapter(src, data) {
    var html = '';
    var hasContent = false;
    var players = src.players || [];

    if (players.length === 0) {
      return { html: '', hasContent: false };
    }

    var attrNames = [
      { key: 'strength', label: '躯魄' },
      { key: 'agility', label: '敏韧' },
      { key: 'constitution', label: '体质' },
      { key: 'intelligence', label: '心智' },
      { key: 'wisdom', label: '洞识' },
      { key: 'charisma', label: '魅力' }
    ];

    html += '<h3>可选玩家种族（' + players.length + '）</h3>';

    players.forEach(function(player) {
      var vsTag = '';
      if (player.version_status) {
        var vsClass = player.version_status === '新' ? 'new' : 'modified';
        vsTag = ' <span class="version-tag ' + vsClass + '">' + player.version_status + '</span>';
      }

      html += '<div class="race-card">';
      html += '<div class="race-header"><h4>' + player.name + vsTag + '</h4></div>';

      // 属性条
      var mods = player.attribute_mods || {};
      html += '<div class="attr-bars-mini">';
      attrNames.forEach(function(a) {
        var val = mods[a.key] || 0;
        var barColor = val > 0 ? 'var(--ash-gold)' : val < 0 ? 'var(--ash-red)' : '#444';
        var barWidth = Math.abs(val) * 18;
        var valCls = val > 0 ? 'pos' : val < 0 ? 'neg' : 'zero';
        html += '<div class="attr-item">';
        html += '<span class="attr-label">' + a.label + '</span>';
        html += '<span class="attr-bar" style="width:' + barWidth + 'px;background:' + barColor + '"></span>';
        html += '<span class="attr-val ' + valCls + '">' + (val >= 0 ? '+' : '') + val + '</span>';
        html += '</div>';
      });
      html += '</div>';

      // 描述截取
      if (player.desc && player.desc.length) {
        html += '<div class="race-desc">' + player.desc[0].substring(0, 200) + (player.desc[0].length > 200 ? '…' : '') + '</div>';
      }

      // 特质标签
      if (player.traits && player.traits.length) {
        html += '<div class="trait-tags">';
        player.traits.slice(0, 4).forEach(function(t) {
          html += '<span class="trait-tag" title="' + t.desc.substring(0, 80) + '…">' + t.name + '</span>';
        });
        if (player.traits.length > 4) {
          html += '<span class="trait-tag" style="opacity:0.5">+' + (player.traits.length - 4) + '</span>';
        }
        html += '</div>';
      }

      html += '</div>';
    });

    hasContent = players.length > 0;
    return { html: html, hasContent: hasContent };
  }

  // ---- ch3: 专修章节渲染（带子章节） ----
  function renderProfessionChapter(ch, src, data) {
    var html = '';
    var hasContent = false;

    if (ch.sub_sections && ch.sub_sections.length > 0) {
      ch.sub_sections.forEach(function(sub, sidx) {
        html += '<div class="sub-section" id="reader-' + (sub.id || (ch.id + '-sub-' + sidx)) + '">';
        html += '<h3>' + (sub.title || sub.name || '') + '</h3>';
        // 从 src.categories 数组里按 id 查找分类数据
        var catData = null;
        if (src && src.categories && Array.isArray(src.categories)) {
          for (var i = 0; i < src.categories.length; i++) {
            if (src.categories[i].id === sub.data_path) {
              catData = src.categories[i];
              break;
            }
          }
        }
        if (catData && catData.abilities && catData.abilities.length > 0) {
          html += renderAbilityList(catData.abilities);
          hasContent = true;
        } else if (catData && catData.name) {
          html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
        } else {
          html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
        }
        html += '</div>';
      });
    } else {
      html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
    }

    return { html: html, hasContent: hasContent };
  }

  // ---- ch4: 神术章节渲染 ----
  function renderDivineChapter(ch, src, data) {
    var html = '';
    var hasContent = false;
    var sections = (ch && ch.sub_sections) || [];
    if (sections.length === 0) {
      // fallback：直接渲染 pantheons
      var pantheons = (src && src.pantheons) || [];
      if (pantheons.length === 0) return { html: '', hasContent: false };
      pantheons.forEach(function(p, idx) {
        html += '<div class="sub-section" id="reader-' + (ch ? ch.id : 'ch4') + '-sub-' + idx + '">';
        html += '<h3>' + (p.name || '') + '</h3>';
        if (p.doctrine && p.doctrine.length > 0) {
          p.doctrine.forEach(function(d) { html += '<p>' + d + '</p>'; });
          hasContent = true;
        }
        if (p.divine_spells && p.divine_spells.length > 0) {
          html += '<h4>神术列表</h4>';
          html += renderGenericList(p.divine_spells, p);
          hasContent = true;
        }
        if (!hasContent) {
          html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
        }
        html += '</div>';
      });
      return { html: html, hasContent: hasContent };
    }
    // 按 sub_sections 渲染
    sections.forEach(function(sub, sidx) {
      html += '<div class="sub-section" id="reader-' + sub.id + '">';
      html += '<h3>' + (sub.title || sub.name || '') + '</h3>';
      var pantheon = null;
      if (sub.data_path && src) {
        try { pantheon = resolveDataPath(src, sub.data_path); } catch(e) {}
      }
      if (pantheon && pantheon.doctrine) {
        pantheon.doctrine.forEach(function(d) { html += '<p>' + d + '</p>'; });
        hasContent = true;
      }
      if (pantheon && pantheon.divine_spells && pantheon.divine_spells.length > 0) {
        html += '<h4>神术列表</h4>';
        html += renderGenericList(pantheon.divine_spells, pantheon);
        hasContent = true;
      }
      if (!hasContent) {
        html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
      }
      html += '</div>';
    });
    return { html: html, hasContent: hasContent };
  }

  // ---- ch5: 故事运作章节渲染（带子章节） ----
  function renderStoryChapter(ch, src, data) {
    var html = '';
    var hasContent = false;

    if (ch.sub_sections && ch.sub_sections.length > 0) {
      ch.sub_sections.forEach(function(sub, sidx) {
        html += '<div class="sub-section" id="reader-' + (sub.id || (ch.id + '-sub-' + sidx)) + '">';
        html += '<h3>' + (sub.title || sub.name || '') + '</h3>';
        // 从 src.sections 数组里按 name 或 id 查找章节数据
        var secData = null;
        if (src && src.sections && Array.isArray(src.sections)) {
          for (var i = 0; i < src.sections.length; i++) {
            if (src.sections[i].name === sub.data_path || src.sections[i].id === sub.data_path) {
              secData = src.sections[i];
              break;
            }
          }
        }
        if (secData && secData.rules && secData.rules.length > 0) {
          html += renderGenericList(secData.rules, sub);
          hasContent = true;
        } else {
          html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
        }
        html += '</div>';
      });
    } else {
      html += '<div class="chapter-placeholder">本章内容整理中，敬请期待</div>';
    }

    return { html: html, hasContent: hasContent };
  }

  // 通用列表渲染（简单键值对）
  function renderGenericList(items, parent) {
    var html = '';
    if (!items || !items.length) return html;
    items.forEach(function(item) {
      if (typeof item === 'string') {
        html += '<p>' + item + '</p>';
      } else if (typeof item === 'object') {
        html += '<div class="race-card"><h4>' + (item.name || item.title || '') + '</h4>';
        if (item.desc) html += '<p>' + item.desc + '</p>';
        html += '</div>';
      }
    });
    return html;
  }

  // ---- 技能条目列表渲染（ch3 专用，可点击卡片） ----
  // 渲染技能列表（仅输出详情容器，不再渲染卡片网格——与 detail-pills 重复）
  function renderAbilityList(abilities) {
    var html = '';
    if (!abilities || !abilities.length) return html;
    // 详情占位容器（由 switchAbility 填充）
    html += '<div class="ability-detail" id="ability-detail"></div>';
    return html;
  }

  // ---- 切换到具体技能条目（展示完整详情） ----
  function switchAbility(ability, abilities) {
    var detailEl = document.getElementById('ability-detail');
    if (!detailEl) return;

    // 记录当前选中的技能（用于反选检测）
    window.__rulesCurrentAbilityName = ability.name || ability.id || null;

    // 隐藏子分类前言（选了技能详情后不再显示前言，避免拥挤）
    var prefaceEl = document.getElementById('sub-section-preface');
    if (prefaceEl) prefaceEl.style.display = 'none';

    // 隐藏章节大标题头（"第3章 专修"），用技能名替换
    var chHeading = document.querySelector('.reader-chapter .chapter-heading');
    if (chHeading) chHeading.style.display = 'none';

    // 确保详情容器可见
    detailEl.style.display = '';

    var html = '';

    // 解析名称和EB
    var ebMatch = null;
    if (ability.name && /（(\d*EB)/.test(ability.name)) {
      ebMatch = ability.name.match(/（(\d+EB)/);
    }
    var displayName = ability.name ? ability.name.replace(/（[^）]+）/g, '').trim() : (ability.id || '');

    // ---- 技能主标题（替代原章节标题位置） ----
    html += '<div class="ability-main-title">';
    html += '<h2>' + displayName + '</h2>';
    if (ebMatch) {
      html += '<span class="detail-eb">（' + ebMatch[1] + '）</span>';
    }
    html += '<div class="heading-divider"></div>';
    html += '</div>';

    // ---- 关键词标签 ----
    if (ability.keywords && ability.keywords.length > 0) {
      html += '<div class="ability-keywords">';
      ability.keywords.forEach(function(kw) {
        html += '<span class="kw-tag">' + kw + '</span>';
      });
      html += '</div>';
    }

    // ---- 完整描述 ----
    if (ability.desc && ability.desc.length > 0) {
      html += '<div class="detail-desc">';
      ability.desc.forEach(function(d) {
        if (d) html += '<p>' + d + '</p>';
      });
      html += '</div>';
    }

    // ---- 等级表格 ----
    if (ability.level_table && ability.level_table.length > 0) {
      html += '<table class="level-table">';
      html += '<thead><tr>';
      // 动态列头
      var firstRow = ability.level_table[0];
      var colOrder = ['level', 'bonus', 'cost', 'effect'];
      var colLabels = { level: '等级', bonus: '加值', cost: '消耗', effect: '额外增益' };
      colOrder.forEach(function(key) {
        if (firstRow.hasOwnProperty(key)) {
          html += '<th>' + (colLabels[key] || key) + '</th>';
        }
      });
      html += '</tr></thead><tbody>';
      ability.level_table.forEach(function(row) {
        html += '<tr>';
        colOrder.forEach(function(key) {
          if (row.hasOwnProperty(key)) {
            html += '<td>' + (row[key] || '') + '</td>';
          }
        });
        html += '</tr>';
      });
      html += '</tbody></table>';
    }

    detailEl.innerHTML = html;

    // 更新列表中 active 状态
    var listEl = detailEl.closest('.sub-section');
    if (listEl) {
      listEl.querySelectorAll('.ability-item').forEach(function(item) { item.classList.remove('active'); });
      var nameToFind = ability.name || ability.id || '';
      var activeItem = listEl.querySelector('.ability-item[data-ab-name="' + nameToFind + '"]');
      if (activeItem) activeItem.classList.add('active');
    }

    // 更新第三层导航 pill 激活状态
    updateDetailNavActive(ability);

    window.__rulesCurrentAbility = ability;
  }

  // 更新第三层导航激活状态
  function updateDetailNavActive(ability) {
    var detailBar = document.getElementById('detail-nav-bar');
    if (!detailBar || !ability) return;
    detailBar.querySelectorAll('.detail-pill').forEach(function(p) { p.classList.remove('active'); });
    var nameToFind = ability.name || ability.id || '';
    var activePill = detailBar.querySelector('.detail-pill[data-ab-name="' + nameToFind + '"]');
    if (activePill) activePill.classList.add('active');
  }

  // 填充/更新第三层导航条的 pills
  function updateDetailNav(abilities, selectedName) {
    var detailBar = document.getElementById('detail-nav-bar');
    if (!detailBar) return;

    if (!abilities || abilities.length === 0) {
      detailBar.classList.remove('visible');
      detailBar.innerHTML = '';
      return;
    }

    var pillsHTML = '';
    abilities.forEach(function(ab) {
      var activeCls = (ab.name === selectedName) ? ' active' : '';
      pillsHTML += '<span class="detail-pill' + activeCls + '" data-ab-name="' + (ab.name || ab.id || '') + '" role="button" tabindex="0">' + (ab.name || ab.id || '') + '</span>';
    });

    detailBar.innerHTML = pillsHTML;
    detailBar.classList.add('visible');

    // 绑定点击事件（支持反选：再点一次回到子分类前言）
    detailBar.querySelectorAll('.detail-pill').forEach(function(pill) {
      pill.addEventListener('click', function() {
        var targetName = this.getAttribute('data-ab-name');

        // 反选检测：点击已激活的detail-pill → 回到子分类前言
        if (window.__rulesCurrentAbilityName === targetName) {
          window.__rulesCurrentAbilityName = null;
          // 去除所有detail-pill激活态
          detailBar.querySelectorAll('.detail-pill').forEach(function(p) { p.classList.remove('active'); });
          // 清空技能详情区
          var detailEl = document.getElementById('ability-detail');
          if (detailEl) { detailEl.innerHTML = ''; detailEl.style.display = 'none'; }
          // 恢复子分类前言显示
          var prefaceEl = document.getElementById('sub-section-preface');
          if (prefaceEl) prefaceEl.style.display = '';
          // 恢复章节大标题头
          var chHeading = document.querySelector('.reader-chapter .chapter-heading');
          if (chHeading) chHeading.style.display = '';
          return;
        }

        // 正常选择技能
        if (window.__currentAbilities) {
          for (var i = 0; i < window.__currentAbilities.length; i++) {
            if (window.__currentAbilities[i].name === targetName ||
                window.__currentAbilities[i].id === targetName) {
              window.__rulesCurrentAbilityName = targetName;
              switchAbility(window.__currentAbilities[i], window.__currentAbilities);
              break;
            }
          }
        }
      });
      pill.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.click(); }
      });
    });
  }

  // ---- 速查版交互绑定：Tab 切换 + 子章节 Pill 切换 ----
  function setupLookupInteractions(chapters, data) {
    var nav = document.getElementById('reader-nav');
    var subNavBar = document.getElementById('sub-nav-bar');
    if (!nav) return;

    var tabs = nav.querySelectorAll('.chapter-tab');

    // 找到第一个有内容的章节作为默认显示
    var firstChId = chapters[0] ? chapters[0].id : null;
    for (var i = 0; i < tabs.length; i++) {
      if (!tabs[i].classList.contains('empty')) {
        firstChId = tabs[i].getAttribute('data-target');
        break;
      }
    }

    // ---- 章节标签点击 → 切换内容 ----
    tabs.forEach(function(tab) {
      tab.addEventListener('click', function() {
        var targetId = this.getAttribute('data-target');
        if (targetId) switchChapter(targetId, chapters, data);
      });
      // 键盘支持
      tab.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.click(); }
      });
    });

    // ---- 子章节 pill 点击 → 切换子内容 ----
    if (subNavBar) {
      subNavBar.querySelectorAll('.sub-pill').forEach(function(pill) {
        pill.addEventListener('click', function() {
          var targetId = this.getAttribute('data-target');
          if (targetId) switchSubSection(targetId, chapters, data);
        });
        pill.addEventListener('keydown', function(e) {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.click(); }
        });
      });
    }

    // ---- 技能卡片委托点击（第三层：能力条目） ----
    var main = document.getElementById('reader-main');
    if (main) {
      main.addEventListener('click', function(e) {
        var abilityItem = e.target.closest ? e.target.closest('.ability-item') : null;
        if (!abilityItem) return;
        var idx = parseInt(abilityItem.getAttribute('data-ab-index'), 10);
        if (isNaN(idx) || !window.__currentAbilities || !window.__currentAbilities[idx]) return;
        switchAbility(window.__currentAbilities[idx], window.__currentAbilities);
      });
    }

    // ---- 初始加载：显示第一个有内容的章节 ----
    if (firstChId) {
      switchChapter(firstChId, chapters, data);
    }

    // 高亮第一个标签
    var firstActive = nav.querySelector('.chapter-tab[data-target="' + firstChId + '"]');
    if (firstActive) firstActive.classList.add('active');
  }

  // ---- 更新子章节导航条可见性 ----
  function updateSubNavVisibility(chId) {
    var subNavBar = document.getElementById('sub-nav-bar');
    if (!subNavBar) return;

    // 隐藏所有 pill 组
    var allGroups = subNavBar.querySelectorAll('.sub-pills-group');
    allGroups.forEach(function(g) { g.style.display = 'none'; });

    // 显示当前章节的 pill 组
    var activeGroup = subNavBar.querySelector('.sub-pills-group[data-chapter="' + chId + '"]');
    if (activeGroup) {
      activeGroup.style.display = 'flex';
      subNavBar.classList.add('visible');
    } else {
      subNavBar.classList.remove('visible');
    }

    // 清除所有 pill 激活状态
    subNavBar.querySelectorAll('.sub-pill').forEach(function(p) { p.classList.remove('active'); });
  }

  // 检测标题行：数字+点开头、纯英文标题、以"教条"开头等
  function isHeadingLine(text) {
    if (!text) return false;
    // 章节标题格式："1.选择种族"、"教条1：顺流"
    if (/^\d+[\.\．]\s*\S/.test(text)) return true;
    if (/^教条\d+/.test(text)) return true;
    if (/^[A-Z][a-z]+ [A-Za-z]/.test(text) && text.length < 60) return true;
    // 种族章节的二级标题
    if (/^(古老种族|灵魔混血种族|自然灵能种族|其他人类分支|玩家种族)/.test(text)) return true;
    return false;
  }

  // 检测子标题行：英文+中文混合标题、引言行等
  function isSubHeadingLine(text) {
    if (!text) return false;
    if (text.length > 80) return false;
    // 如 "灵涅Soul Nirvana"、"空洞浩劫Hollow Catastrophe"
    if (/^[\u4e00-\u9fff]{2,8}[A-Z][a-z]/.test(text)) return true;
    // 如 "序言："、"战斗准则"
    if (/^(序言|前言|战斗准则|耐力行动|施法行动)/.test(text)) return true;
    return false;
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

  // ---- ch2 种族：初始化第三层种族导航 ----
  function initRaceNav(sub, parentCh, data) {
    var src = resolveDataSource(data, parentCh.data_source);
    if (!src) return;
    var raceList = src[sub.data_path] || [];
    if (!Array.isArray(raceList)) return;
    window.__currentRaces = raceList;
    window.__rulesCurrentRaceName = null;
    updateRaceNav(raceList, null);
  }

  function updateRaceNav(races, selectedName) {
    var detailBar = document.getElementById('detail-nav-bar');
    if (!detailBar) return;
    detailBar.classList.add('visible');
    detailBar.innerHTML = '';
    if (!races || races.length === 0) return;
    races.forEach(function(race) {
      var name = race.name || race.id || '';
      var active = (name === selectedName) ? ' active' : '';
      var pill = document.createElement('span');
      pill.className = 'detail-pill' + active;
      pill.setAttribute('data-race-name', name);
      pill.textContent = name;
      pill.addEventListener('click', function() {
        var targetName = this.getAttribute('data-race-name');
        if (window.__rulesCurrentRaceName === targetName) {
          window.__rulesCurrentRaceName = null;
          detailBar.querySelectorAll('.detail-pill').forEach(function(p) { p.classList.remove('active'); });
          var detailEl = document.getElementById('ability-detail');
          if (detailEl) { detailEl.innerHTML = ''; detailEl.style.display = 'none'; }
          var prefaceEl = document.getElementById('sub-section-preface');
          if (prefaceEl) prefaceEl.style.display = '';
          return;
        }
        var targetRace = null;
        if (window.__currentRaces) {
          for (var i = 0; i < window.__currentRaces.length; i++) {
            if ((window.__currentRaces[i].name || window.__currentRaces[i].id) === targetName) {
              targetRace = window.__currentRaces[i];
              break;
            }
          }
        }
        if (targetRace) switchRace(targetRace, data);
      });
      detailBar.appendChild(pill);
    });
  }

  function switchRace(race, dataObj) {
    var detailEl = document.getElementById('ability-detail');
    if (!detailEl) return;
    window.__rulesCurrentRaceName = race.name || race.id || null;
    var prefaceEl = document.getElementById('sub-section-preface');
    if (prefaceEl) prefaceEl.style.display = 'none';
    detailEl.style.display = '';
    var html = '';
    html += '<div class="race-detail">';
    html += '<div class="detail-header"><h2>' + (race.name || '') + '</h2>';
    if (race.version_status) {
      var vsCls = race.version_status === '新' ? 'new' : 'modified';
      html += ' <span class="version-tag ' + vsCls + '">' + race.version_status + '</span>';
    }
    html += '</div>';
    if (race.attribute_mods) {
      var attrNames = [
        { key: 'strength', label: '躯魄' },
        { key: 'agility', label: '敏韧' },
        { key: 'constitution', label: '体质' },
        { key: 'intelligence', label: '心智' },
        { key: 'wisdom', label: '洞识' },
        { key: 'charisma', label: '魅力' }
      ];
      html += '<div class="attr-bars-mini">';
      attrNames.forEach(function(a) {
        var val = race.attribute_mods[a.key] || 0;
        var barColor = val > 0 ? 'var(--ash-gold)' : val < 0 ? 'var(--ash-red)' : '#444';
        var barWidth = Math.abs(val) * 18;
        var valCls = val > 0 ? 'pos' : val < 0 ? 'neg' : 'zero';
        html += '<div class="attr-item">';
        html += '<span class="attr-label">' + a.label + '</span>';
        html += '<span class="attr-bar" style="width:' + barWidth + 'px;background:' + barColor + '"></span>';
        html += '<span class="attr-val ' + valCls + '">' + (val >= 0 ? '+' : '') + val + '</span>';
        html += '</div>';
      });
      html += '</div>';
    }

    // ---- 查找分支数据 ----
    var branchData = null;
    if (dataObj && dataObj.races) {
      branchData = findRaceBranchData(dataObj.races, race);
    }

    // ---- 渲染详情内容 ----
    var detailContent = (branchData && branchData.detail) ? branchData.detail : (race.detail || []);
    var parsedBranches = null;
    if (detailContent.length > 0) {
      parsedBranches = parseBranchSections(detailContent);
    }

    // ---- 如果有分支 → 填充第3档导航（与专修同款 detail-pill）----
    if (parsedBranches && parsedBranches.branches.length > 0) {
      window.__currentRaceBranches = parsedBranches;
      window.__currentRaceOverview = race; // 保存种族概述数据
      window.__rulesCurrentBranchName = null;

      // 用 detail-nav-bar 展示分支 pills（复用专修的3档导航条）
      updateDetailNavForBranches(parsedBranches.branches, null);

      // 初始视图：显示种族概述（第一个分支标题之前的内容）
      html += '<div class="race-detail-body" id="race-branch-content">';
      var overviewShown = false;
      parsedBranches.sections.forEach(function(sec, si) {
        if (sec.type === 'branch-header') return; // 跳过分支标题，初始不显示
        overviewShown = true;
        if (sec.type === 'section-header') {
          html += '<h4 class="content-subheading">' + escapeHtml(sec.text) + '</h4>';
        } else if (isMixedTitle(sec.text)) {
          html += '<h3 class="overview-title">' + escapeHtml(sec.text) + '</h3>';
        } else if (/^[A-Za-z]/.test(sec.text.trim()) && !/[\u4e00-\u9fff]/.test(sec.text)) {
          html += '<h4 class="overview-title">' + escapeHtml(sec.text) + '</h4>';
        } else {
          html += '<p>' + escapeHtml(sec.text) + '</p>';
        }
      });
      // 如果没有概述内容，显示提示文字
      if (!overviewShown) {
        html += '<p style="color:var(--ash-text-dim);font-style:italic;">选择下方分支查看详细信息</p>';
      }
      html += '</div>';
    } else {
        // 无分支：平铺渲染（支持混合标题检测）
        html += '<div class="race-detail-body">';
        detailContent.forEach(function(p) {
          var pt = p.trim();
          if (isMixedTitle(pt)) {
            html += '<h3 class="overview-title">' + escapeHtml(p) + '</h3>';
          } else if (/^[A-Za-z]/.test(pt) && !/[\u4e00-\u9fff]/.test(pt)) {
            html += '<h4 class="overview-title">' + escapeHtml(p) + '</h4>';
          } else {
            html += '<p>' + escapeHtml(p) + '</p>';
          }
        });
        html += '</div>';
      }

    // 种族特质（traits）单独展示
    if (race.traits && race.traits.length > 0) {
      html += '<div class="race-traits-section"><h4 class="content-subheading">种族灵涅特质</h4>';
      race.traits.forEach(function(t) {
        html += '<div class="trait-item">';
        html += '<strong class="trait-name">' + escapeHtml(t.name) + '</strong>';
        html += '<p class="trait-desc">' + escapeHtml(t.desc) + '</p>';
        html += '</div>';
      });
      html += '</div>';
    }

    html += '</div>';
    detailEl.innerHTML = html;
  }

  // 在 races 数据中查找匹配的分支数据
  function findRaceBranchData(racesData, race) {
    if (!racesData || !race) return null;
    var raceId = race.id || '';
    var raceName = race.name || '';
    var branchKeys = ['human_branches', 'spirit_mixed', 'nature_psionic', 'ancient'];
    for (var k = 0; k < branchKeys.length; k++) {
      var arr = racesData[branchKeys[k]];
      if (!arr || !Array.isArray(arr)) continue;
      for (var i = 0; i < arr.length; i++) {
        var b = arr[i];
        if (b.id === raceId ||
            b.name === raceName ||
            b.name === raceName.replace(/人类$/, '') ||
            raceId.indexOf(b.id) >= 0 ||
            b.id.indexOf(raceId.replace(/_human$/, '')) >= 0) {
          return b;
        }
      }
    }
    return null;
  }

  // 解析 detail 数组，识别分支段落结构
  function parseBranchSections(detailArr) {
    var sections = [];
    var branches = [];
    for (var i = 0; i < detailArr.length; i++) {
      var text = String(detailArr[i]).trim();
      var secType = 'paragraph';
      if (isBranchTitle(text, detailArr, i)) {
        secType = 'branch-header';
        branches.push({ title: text, idx: branches.length });
      } else if (/^[一-鿿].*[:：\s]*$/.test(text) && text.length < 50 && !/^来源|备注|参考/.test(text) && !/^(肤色|瞳色|发色|根源属地)/.test(text)) {
        secType = 'section-header';
      }
      sections.push({ type: secType, text: text, branchIdx: branches.length - 1 });
    }
    return { sections: sections, branches: branches };
  }

  // 判断一行文本是否是分支标题
  function isBranchTitle(text, arr, idx) {
    var pt = text.trim();
    if (!pt || pt.length > 20 || pt.length < 2) return false;
    if (/[。！？.!?,;；]$/.test(pt)) return false;
    if (/[:：]$/.test(pt)) return false;
    if (/^[\d\s\-—–.]+$/.test(pt)) return false;
    if (/^["「『【]/.test(pt)) return false;
    if (/^(肤色|瞳色|发色|根源属地|根源种族能力|特征|语言|平均身高|生育率|种族体型|成年岁数|种族抗性|基础主属性加成|种族能力|备注|来源)/.test(pt)) return false;
    var mostlyCJK = /[\u4e00-\u9fff]/.test(pt);
    if (!mostlyCJK) return false;
    // 排除纯属性标签（如"躯魄+1"）
    if (/^[^\s]*[+-]\d/.test(pt)) return false;
    return true;
  }

  // ============================================================
  //  种族分支第3档导航（与专修同款 detail-pill 风格）
  // ============================================================

  /**
   * 用 detail-nav-bar 展示种族分支 pills，点击切换内容
   * @param {Array} branches - [{ title: '精灵Elf', idx: 0 }, ...]
   * @param {string|null} selectedTitle - 当前选中的分支标题
   */
  function updateDetailNavForBranches(branches, selectedTitle) {
    var detailBar = document.getElementById('detail-nav-bar');
    if (!detailBar) return;

    if (!branches || branches.length === 0) {
      detailBar.classList.remove('visible');
      detailBar.innerHTML = '';
      return;
    }

    var pillsHTML = '';
    branches.forEach(function(b) {
      var activeCls = (b.title === selectedTitle) ? ' active' : '';
      pillsHTML += '<span class="detail-pill' + activeCls + '"'
                 + ' data-branch-name="' + escapeAttr(b.title) + '"'
                 + ' data-branch-idx="' + b.idx + '"'
                 + ' role="button" tabindex="0">'
                 + escapeHtml(b.title) + '</span>';
    });

    detailBar.innerHTML = pillsHTML;
    detailBar.classList.add('visible');

    // ---- 点击事件：切换内容（非滚动）----
    detailBar.querySelectorAll('.detail-pill').forEach(function(pill) {
      pill.addEventListener('click', function() {
        var targetName = this.getAttribute('data-branch-name');
        var targetIdx = parseInt(this.getAttribute('data-branch-idx'), 10);

        // 反选：再点已激活的 → 回到概述
        if (window.__rulesCurrentBranchName === targetName) {
          window.__rulesCurrentBranchName = null;
          detailBar.querySelectorAll('.detail-pill').forEach(function(p) { p.classList.remove('active'); });
          renderRaceOverviewContent();
          return;
        }

        // 正常选择：渲染该分支的内容段落
        window.__rulesCurrentBranchName = targetName;
        detailBar.querySelectorAll('.detail-pill').forEach(function(p) { p.classList.remove('active'); });
        this.classList.add('active');
        renderRaceBranchContent(targetIdx);
      });
      pill.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.click(); }
      });
    });
  }

  /** 渲染种族概述（所有分支标题之前的内容） */
  function renderRaceOverviewContent() {
    var container = document.getElementById('race-branch-content');
    if (!container || !window.__currentRaceBranches) return;

    var html = '';
    var shown = false;
    window.__currentRaceBranches.sections.forEach(function(sec) {
      if (sec.type === 'branch-header') return; // 跳过所有分支标题及之后的内容
      shown = true;
      if (sec.type === 'section-header') {
        html += '<h4 class="content-subheading">' + escapeHtml(sec.text) + '</h4>';
      } else if (isMixedTitle(sec.text)) {
        html += '<h3 class="overview-title">' + escapeHtml(sec.text) + '</h3>';
      } else if (/^[A-Za-z]/.test(sec.text.trim()) && !/[\u4e00-\u9fff]/.test(sec.text)) {
        html += '<h4 class="overview-title">' + escapeHtml(sec.text) + '</h4>';
      } else {
        html += '<p>' + escapeHtml(sec.text) + '</p>';
      }
    });
    if (!shown) {
      html += '<p style="color:var(--ash-text-dim);font-style:italic;">选择上方分支查看详细信息</p>';
    }
    container.innerHTML = html;
  }

  /** 渲染指定分支的完整内容 */
  function renderRaceBranchContent(branchIdx) {
    var container = document.getElementById('race-branch-content');
    if (!container || !window.__currentRaceBranches) return;

    var html = '';
    var inTargetBranch = false;
    window.__currentRaceBranches.sections.forEach(function(sec) {
      // 进入目标分支区域
      if (sec.type === 'branch-header' && sec.branchIdx === branchIdx) {
        inTargetBranch = true;
        html += '<h4 class="content-subheading" style="color:var(--ash-gold);margin-top:16px;">' + escapeHtml(sec.text) + '</h4>';
        return;
      }
      // 到达下一个分支标题 → 停止
      if (sec.type === 'branch-header' && inTargetBranch) return;
      // 只渲染目标分支内的内容
      if (inTargetBranch) {
        if (sec.type === 'section-header') {
          html += '<h4 class="content-subheading">' + escapeHtml(sec.text) + '</h4>';
        } else if (isMixedTitle(sec.text)) {
          html += '<h3 class="overview-title">' + escapeHtml(sec.text) + '</h3>';
        } else if (/^[A-Za-z]/.test(sec.text.trim()) && !/[\u4e00-\u9fff]/.test(sec.text)) {
          html += '<h4 class="overview-title">' + escapeHtml(sec.text) + '</h4>';
        } else {
          html += '<p>' + escapeHtml(sec.text) + '</p>';
        }
      }
    });
    container.innerHTML = html;
  }

  /** HTML 属性转义 */
  function escapeAttr(s) {
    return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  function escapeHtml(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }


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

      // ---- 左右箭头按钮（已移除，用户不需要） ----

      // 初始化完成（保留拖拽和触摸滚动功能）
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

  window.PageRender = { init };
})();
