// 灰烬世界 Ontology 页面渲染引擎
// 所有子页面引用此文件，即可从 data/ 读取内容并显示关联
(function() {

  // 用户可见的错误提示（替代静默 return）
  function showError(msg) {
    var el = document.getElementById('onto-content');
    if (!el) return;
    el.innerHTML = '<div style="text-align:center;padding:60px 20px;color:var(--ash-dim)">' +
      '<h2 style="color:var(--ash-gold);margin-bottom:12px">⚠ 内容加载异常</h2>' +
      '<p style="margin-bottom:8px">' + msg + '</p>' +
      '<p style="font-size:0.78rem;opacity:0.6">请按 Ctrl+F5 强制刷新，或稍后重试</p></div>';
  }

  async function init(pageName) {
    try {
      await window.AshData.loadAll();
    } catch(e) {
      console.error('[PageRender] loadAll failed:', e);
      showError('数据加载异常：' + (e.message || e));
      throw e;
    }
    var data = window.AshData;
    if (!data.loaded) {
      showError('数据未完成加载');
      return;
    }

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

  // ============================================================
  //  规则书阅读器：预渲染所有章节 + 缩略图导航 + IntersectionObserver
  // ============================================================
  function renderRules(data) {
    var el = document.getElementById('onto-content');
    if (!el || !data.chapters) return;
    var chapters = data.chapters.chapters || [];
    var chapterIds = [];

    // 收集所有顶级章节 ID
    chapters.forEach(function(ch) { chapterIds.push(ch.id); });

    // 构建缩略图导航 HTML
    var navHTML = '<div class="reader-nav-title">章 节</div>';
    chapters.forEach(function(ch) {
      var isEmpty = !hasChapterContent(ch, data);
      var cls = 'chapter-thumb' + (isEmpty ? ' empty' : '');
      navHTML += '<div class="' + cls + '" data-target="' + ch.id + '" role="button" tabindex="0">';
      navHTML += '<span class="thumb-number">' + (ch.number || '') + '</span>';
      navHTML += '<span class="thumb-title">' + (ch.title || ch.name || '') + '</span>';
      if (isEmpty) {
        navHTML += '<span class="thumb-hint">整理中</span>';
      }
      navHTML += '</div>';
    });

    // 构建主阅读区 HTML（预渲染所有章节）
    var mainHTML = '';
    chapters.forEach(function(ch, idx) {
      mainHTML += '<section class="reader-chapter" id="reader-' + ch.id + '" data-chapter="' + ch.id + '">';
      mainHTML += renderChapterContent(ch, data, chapters, idx);
      // 下一章按钮（最后一章特殊处理）
      var isLast = idx === chapters.length - 1;
      mainHTML += '<div class="next-chapter-sentinel" data-sentinel="' + ch.id + '"></div>';
      mainHTML += '<button class="next-chapter-btn' + (isLast ? ' last-chapter' : '') + '" ';
      mainHTML += 'data-next="' + (isLast ? '' : chapters[idx + 1].id) + '"';
      if (isLast) { mainHTML += ' disabled'; }
      mainHTML += '>下一章</button>';
      mainHTML += '</section>';
    });

    // 组装布局
    var html = '<div class="reader-layout">';
    html += '<nav class="reader-nav" id="reader-nav">' + navHTML + '</nav>';
    html += '<div class="reader-main" id="reader-main">' + mainHTML + '</div>';
    html += '</div>';
    el.innerHTML = html;

    // ---- 交互绑定 ----
    setupReaderInteractions(chapterIds);
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
    html += '<span class="chapter-num">' + (ch.number || '') + '</span>';
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
            var divineRendered = renderDivineChapter(src, data);
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
      ch.sub_sections.forEach(function(sub) {
        html += '<div class="sub-section">';
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
          html += renderGenericList(catData.abilities, sub);
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
  function renderDivineChapter(src, data) {
    var html = '';
    var hasContent = false;
    var pantheons = src.pantheons || [];

    if (pantheons.length === 0) {
      return { html: '', hasContent: false };
    }

    pantheons.forEach(function(p) {
      html += '<div class="sub-section">';
      html += '<h3>' + (p.name || '') + '</h3>';
      if (p.doctrine && p.doctrine.length > 0) {
        p.doctrine.forEach(function(d) {
          html += '<p>' + d + '</p>';
        });
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

  // ---- ch5: 故事运作章节渲染（带子章节） ----
  function renderStoryChapter(ch, src, data) {
    var html = '';
    var hasContent = false;

    if (ch.sub_sections && ch.sub_sections.length > 0) {
      ch.sub_sections.forEach(function(sub) {
        html += '<div class="sub-section">';
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

  // ---- 交互绑定：缩略图点击、下一章按钮、IntersectionObserver ----
  function setupReaderInteractions(chapterIds) {
    var nav = document.getElementById('reader-nav');
    var main = document.getElementById('reader-main');
    if (!nav || !main) return;

    var thumbs = nav.querySelectorAll('.chapter-thumb');
    var chapters = main.querySelectorAll('.reader-chapter');
    var nextBtns = main.querySelectorAll('.next-chapter-btn');
    var sentinels = main.querySelectorAll('.next-chapter-sentinel');

    // ---- 缩略图点击 → 平滑滚动 ----
    thumbs.forEach(function(thumb) {
      thumb.addEventListener('click', function() {
        var targetId = this.getAttribute('data-target');
        var target = document.getElementById('reader-' + targetId);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });

    // ---- 下一章按钮点击 ----
    nextBtns.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var nextId = this.getAttribute('data-next');
        if (!nextId) return;
        var target = document.getElementById('reader-' + nextId);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });

    // ---- IntersectionObserver：当前章节高亮 + 下一章按钮显隐 ----
    if (typeof IntersectionObserver !== 'undefined') {
      // Observer 1: 章节进入视口 → 更新左侧高亮
      var chapterObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            var chId = entry.target.getAttribute('data-chapter');
            // 移除所有 active
            thumbs.forEach(function(t) { t.classList.remove('active'); });
            // 给当前添加 active
            var activeThumb = nav.querySelector('.chapter-thumb[data-target="' + chId + '"]');
            if (activeThumb) activeThumb.classList.add('active');
          }
        });
      }, {
        root: main,
        rootMargin: '-20% 0px -60% 0px',
        threshold: 0
      });

      chapters.forEach(function(ch) { chapterObserver.observe(ch); });

      // Observer 2: 章节底部 sentinel → 显示/隐藏下一章按钮
      var sentinelObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          var chId = entry.target.getAttribute('data-sentinel');
          var chapterEl = entry.target.closest('.reader-chapter');
          if (!chapterEl) return;
          var btn = chapterEl.querySelector('.next-chapter-btn');
          if (!btn) return;

          if (entry.isIntersecting) {
            btn.style.display = 'block';
          } else {
            btn.style.display = 'none';
          }
        });
      }, {
        root: main,
        rootMargin: '0px 0px -40px 0px',
        threshold: 0
      });

      sentinels.forEach(function(s) { sentinelObserver.observe(s); });
    } else {
      // 降级：所有按钮始终显示，章节高亮用滚动事件
      nextBtns.forEach(function(btn) { btn.style.display = 'block'; });

      // 滚动监听降级
      var scrollTicking = false;
      main.addEventListener('scroll', function() {
        if (!scrollTicking) {
          requestAnimationFrame(function() {
            updateActiveThumbOnScroll(chapters, thumbs, main);
            scrollTicking = false;
          });
          scrollTicking = true;
        }
      });
    }

    // 初始高亮第一个有内容的章节或第一个章节
    var firstActive = thumbs[0];
    for (var i = 0; i < thumbs.length; i++) {
      if (!thumbs[i].classList.contains('empty')) {
        firstActive = thumbs[i];
        break;
      }
    }
    firstActive.classList.add('active');
  }

  // 降级滚动高亮
  function updateActiveThumbOnScroll(chapters, thumbs, main) {
    var scrollTop = main.scrollTop;
    var containerTop = main.getBoundingClientRect().top;
    var activeId = null;

    chapters.forEach(function(ch) {
      var rect = ch.getBoundingClientRect();
      if (rect.top - containerTop < main.clientHeight * 0.4) {
        activeId = ch.getAttribute('data-chapter');
      }
    });

    if (activeId) {
      thumbs.forEach(function(t) { t.classList.remove('active'); });
      var activeThumb = document.querySelector('.chapter-thumb[data-target="' + activeId + '"]');
      if (activeThumb) activeThumb.classList.add('active');
    }
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

  window.PageRender = { init };
})();
