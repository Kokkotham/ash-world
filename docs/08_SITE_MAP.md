# Embers World — 站点地图

> **文档级别**: 信息架构
> **最后更新**: 2026-07-04

---

## 1. 导航结构

```
Embers World
├── 首页 (/)
├── 规则 (/rules)
│   ├── 专修 (/rules/professions)
│   │   ├── 本能 (/rules/professions/instinct)
│   │   ├── 知识 (/rules/professions/knowledge)
│   │   ├── 交流 (/rules/professions/communication)
│   │   ├── 艺术 (/rules/professions/art)
│   │   ├── 生存 (/rules/professions/survival)
│   │   ├── 特殊 (/rules/professions/special)
│   │   ├── 制造 (/rules/professions/craft)
│   │   ├── 武器 (/rules/professions/weapon)
│   │   ├── 战斗 (/rules/professions/combat)
│   │   ├── 武术 (/rules/professions/martial)
│   │   └── 秘法 (/rules/professions/arcane)
│   ├── 神术 (/rules/divine-arts)
│   │   ├── 父神系 (/rules/divine-arts/father)
│   │   └── 母神系 (/rules/divine-arts/mother)
│   ├── 故事运作 (/rules/story)
│   │   ├── 战斗 (/rules/story/combat)
│   │   ├── 交流 (/rules/story/social)
│   │   ├── 经营 (/rules/story/management)
│   │   └── 状态词缀 (/rules/story/status)
│   └── 属性系统 (/rules/attributes)
├── 世界观 (/lore)
│   ├── 种族 (/lore/races)
│   │   ├── 远古种族 (/lore/races/ancient)
│   │   ├── 玩家种族 (/lore/races/players)
│   │   └── NPC种族 (/lore/races/npc)
│   ├── 神系 (/lore/deities)
│   ├── 地理 (/lore/regions)
│   ├── 历史 (/lore/history)
│   └── 势力 (/lore/factions)
├── 词条 (/glossary)
│   ├── 核心系统 (/glossary?cat=core)
│   ├── 种族 (/glossary?cat=race)
│   ├── 神术 (/glossary?cat=divine)
│   └── 全部 (/glossary?cat=all)
├── 角色 (/characters)
│   ├── 创建 (/characters/new)
│   ├── 列表 (/characters/list)
│   └── 详情 (/characters/:id)
├── 个人中心 (/profile)
│   ├── 资料编辑 (/profile/edit)
│   ├── 我的角色卡 (/profile/characters)
│   ├── 游戏记录 (/profile/sessions)
│   └── 账号安全 (/profile/security)
├── 公告 (/news)
│   ├── 更新日志 (/news/changelog)
│   └── 公告列表 (/news/list)
└── 关于 (/about)
```

---

## 2. 页面清单

### 当前已有页面 (Phase 0)

| 路径 | 文件 | 说明 |
|------|------|------|
| `/` | `index.html` | 首页 + 登录弹窗 |
| `/pages/rules.html` | 规则书阅读器 | 分章滚动 |
| `/pages/races-ontology.html` | 种族页 | 远古 + 玩家种族 |
| `/pages/glossary.html` | 术语表 | 动态渲染 |
| `/pages/character-sheet.html` | 角色卡 | 属性分配 |
| `/pages/profile.html` | 个人主页 | 资料编辑 |
| `/pages/pantheon.html` | 神系页 | 骨架 |
| `/pages/worldview.html` | 世界观 | 骨架 |
| `/pages/news.html` | 公告 | 骨架 |
| `/pages/map.html` | 地图 | 骨架 (未来) |

### 目标页面 (Phase 1+)

| 路径 | Vue 组件 | 说明 |
|------|----------|------|
| `/` | `views/Home.vue` | 首页 |
| `/rules` | `views/RuleList.vue` | 规则分类列表 |
| `/rules/:slug` | `views/RuleDetail.vue` | 规则详情 |
| `/lore` | `views/LoreIndex.vue` | 世界观入口 |
| `/lore/races` | `views/RaceList.vue` | 种族列表 |
| `/lore/races/:slug` | `views/RaceDetail.vue` | 种族详情 |
| `/glossary` | `views/Glossary.vue` | 术语表 |
| `/characters` | `views/CharacterList.vue` | 角色卡列表 |
| `/characters/new` | `views/CharacterCreate.vue` | 角色创建 |
| `/characters/:id` | `views/CharacterDetail.vue` | 角色详情 |
| `/profile` | `views/Profile.vue` | 个人中心 |
| `/login` | `views/Login.vue` | 登录页 |
| `/register` | `views/Register.vue` | 注册页 |
| `/news` | `views/News.vue` | 公告 |

---

## 3. URL 规范

| 规则 | 说明 | 示例 |
|------|------|------|
| 小写 | 全部小写 | `/rules/divine-arts` |
| 连字符 | 多词用连字符 | `/lore/races/player-races` |
| 复数 | 列表页用复数 | `/rules`, `/characters` |
| Slug | 详情页用 slug | `/rules/instinct` |
| 查询参数 | 筛选用 query | `/glossary?cat=core` |

---

## 4. 导航栏菜单

```
[Logo] Embers World    规则  世界观  词条  角色              [用户区]
```

| 菜单项 | 下拉 | 链接 |
|--------|------|------|
| 规则 | 专修 / 神术 / 故事运作 / 属性 | `/rules` |
| 世界观 | 种族 / 神系 / 地理 / 历史 | `/lore` |
| 词条 | 核心系统 / 种族 / 神术 / 全部 | `/glossary` |
| 角色 | — | `/characters` |
| 用户区 | 个人中心 / 我的角色卡 / 退出 | `/profile` |
