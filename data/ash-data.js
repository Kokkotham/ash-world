// 灰烬世界 Ontology 数据加载器
// 所有页面引用此文件，即可从统一数据层读取

(function() {
  const DATA_PATH = '../data/';

  window.AshData = {
    races: null,
    deities: null,
    regions: null,
    modules: null,
    links: null,
    loaded: false,

    async loadAll() {
      if (this.loaded) return;
      const [races, deities, regions, modules, links] = await Promise.all([
        fetch(DATA_PATH + 'races.json').then(r => r.json()),
        fetch(DATA_PATH + 'deities.json').then(r => r.json()),
        fetch(DATA_PATH + 'regions.json').then(r => r.json()),
        fetch(DATA_PATH + 'modules.json').then(r => r.json()),
        fetch(DATA_PATH + 'links.json').then(r => r.json())
      ]);
      this.races = races;
      this.deities = deities;
      this.regions = regions;
      this.modules = modules;
      this.links = links;
      this.loaded = true;
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
        }
        return { link: l.link, target, targetType: l.to_type };
      }).filter(r => r.target);
    },

    // 泛用查找
    findAll(data, id) {
      if (!data) return null;
      if (Array.isArray(data)) return data.find(d => d.id === id);
      const keys = ['ancient', 'spirit_mixed', 'nature_psionic', 'human_branches',
        'regions', 'seas', 'passes', 'official', 'short'];
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
