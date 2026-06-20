// 灰烬世界 Ontology 数据加载器
// 所有页面引用此文件，即可从统一数据层读取

(function() {
  var DATA_PATH = '../data/';

  // 通用加载函数：优先用 fetch，失败时自动回退到 XHR
  // XHR 在 file:// 协议下的兼容性比 fetch 更好
  function loadJSON(name) {
    var url = DATA_PATH + name;

    // 方式1：fetch（现代浏览器首选）
    if (typeof fetch === 'function') {
      return fetch(url)
        .then(function(r) {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          return r.json();
        })
        .catch(function(err) {
          console.warn('[AshData] fetch 失败，尝试 XHR 回退:', name, err.message || err);
          return loadJSON_XHR(name);  // 回退到 XHR
        });
    }

    // 方式2：直接用 XHR
    return loadJSON_XHR(name);
  }

  // XHR 回退加载器
  function loadJSON_XHR(name) {
    return new Promise(function(resolve, reject) {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', DATA_PATH + name, true);
      xhr.responseType = 'json';
      xhr.onload = function() {
        if (xhr.status === 200 && xhr.response) {
          resolve(xhr.response);
        } else {
          reject(new Error('XHR 状态 ' + xhr.status + ': ' + name));
        }
      };
      xhr.onerror = function() { reject(new Error('XHR 网络错误: ' + name)); };
      xhr.send();
    });
  }

  window.AshData = {
    races: null,
    deities: null,
    regions: null,
    modules: null,
    links: null,
    professions: null,
    divineArts: null,
    storyRules: null,
    glossary: null,
    chapters: null,
    loaded: false,
    loadErrors: [],

    async loadAll() {
      if (this.loaded) return;
      var results = await Promise.all([
        loadJSON('races.json').catch(null),
        loadJSON('deities.json').catch(null),
        loadJSON('regions.json').catch(null),
        loadJSON('modules.json').catch(null),
        loadJSON('links.json').catch(null),
        loadJSON('professions.json').catch(null),
        loadJSON('divine-arts.json').catch(null),
        loadJSON('story-rules.json').catch(null),
        loadJSON('glossary.json').catch(null),
        loadJSON('chapters.json').catch(null)
      ]);
      var names = ['races','deities','regions','modules','links','professions','divineArts','storyRules','glossary','chapters'];
      this.loadErrors = [];
      var successCount = 0;
      for (var i = 0; i < names.length; i++) {
        if (results[i]) {
          this[names[i]] = results[i];
          successCount++;
        } else {
          this.loadErrors.push(names[i]);
        }
      }
      // 不再抛出错误 —— 即使全部失败也标记 loaded=true
      // 由各页面自行决定如何处理缺失数据
      this.loaded = true;
      console.log('[AshData] 加载完成: ' + successCount + '/' + names.length + ' 个文件成功');
      if (this.loadErrors.length > 0) {
        console.warn('[AshData] 部分文件加载失败:', this.loadErrors);
      }
    },

    // 查所有关联：给一个对象的 type+id，返回所有关联内容
    getLinked(entityType, entityId) {
      if (!this.links) return [];
      return this.links.filter(l =>
        (l.from_type === entityType && l.from_id === entityId) ||
        (l.to_type === entityType && l.to_id === entityId)
      );
    },

    // 查关联并解析为可阅读的对象
    resolveLinks(entityType, entityId) {
      const raw = this.getLinked(entityType, entityId);
      return raw.map(l => {
        let target = null;
        if (l.to_type === 'region') {
          target = this.findAll(this.regions, l.to_id);
        } else if (l.to_type === 'race') {
          target = this.findAll(this.races, l.to_id);
        } else if (l.to_type === 'deity') {
          target = this.deities?.pantheons?.find(d => d.id === l.to_id)
            || this.deities?.twelve_labors?.find(d => d.id === l.to_id)
            || this.deities?.notable_deities?.find(d => d.id === l.to_id);
        } else if (l.to_type === 'profession') {
          target = this.findAll(this.professions, l.to_id);
        } else if (l.to_type === 'divine_art') {
          target = this.findAll(this.divineArts, l.to_id);
        } else if (l.to_type === 'story_rule') {
          target = this.findAll(this.storyRules, l.to_id);
        } else if (l.to_type === 'glossary') {
          target = this.findAll(this.glossary, l.to_id);
        } else if (l.to_type === 'player_race') {
          target = this.races?.players?.find(r => r.id === l.to_id) || null;
        }
        return { link: l.link, target, targetType: l.to_type };
      }).filter(r => r.target);
    },

    // 泛用查找
    findAll(data, id) {
      if (!data) return null;
      if (Array.isArray(data)) return data.find(d => d.id === id);
      const keys = ['ancient', 'spirit_mixed', 'nature_psionic', 'human_branches', 'players',
        'regions', 'seas', 'passes', 'official', 'short',
        'categories', 'pantheons', 'sections', 'entries'];
      for (const key of keys) {
        if (data[key]) {
          if (Array.isArray(data[key])) {
            const found = data[key].find(d => d.id === id);
            if (found) return found;
          }
        }
      }
      for (const key of keys) {
        if (data[key]) {
          for (const item of (Array.isArray(data[key]) ? data[key] : [])) {
            if (item.kingdoms) {
              const found = item.kingdoms.find(k => k.id === id);
              if (found) return found;
            }
          }
        }
      }
      return null;
    }
  };
})();
