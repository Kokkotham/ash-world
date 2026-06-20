// 灰烬世界 Ontology 数据加载器
// 所有页面引用此文件，即可从统一数据层读取

(function() {
  var DATA_PATH = '../data/';

  // 安全fetch：单个文件失败不阻断其他
  function safeFetch(name) {
    return fetch(DATA_PATH + name)
      .then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status + ' ' + name);
        return r.json();
      })
      .catch(function(err) {
        console.error('[AshData] 加载失败: ' + name, err);
        return null;
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
    loadErrors: [], // 记录哪些文件失败了

    async loadAll() {
      if (this.loaded) return;
      var results = await Promise.all([
        safeFetch('races.json'),
        safeFetch('deities.json'),
        safeFetch('regions.json'),
        safeFetch('modules.json'),
        safeFetch('links.json'),
        safeFetch('professions.json'),
        safeFetch('divine-arts.json'),
        safeFetch('story-rules.json'),
        safeFetch('glossary.json'),
        safeFetch('chapters.json')
      ]);
      var names = ['races','deities','regions','modules','links','professions','divineArts','storyRules','glossary','chapters'];
      this.loadErrors = [];
      for (var i = 0; i < names.length; i++) {
        if (results[i]) {
          this[names[i]] = results[i];
        } else {
          this.loadErrors.push(names[i]);
        }
      }
      this.loaded = true;
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
