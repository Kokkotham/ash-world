# Embers World — AI 交接文档

> **文档级别**: 每次换 AI 时第一个让它读的文件
> **最后更新**: 2026-07-04

---

## 接手流程

如果你是接手本项目的 AI（WorkBuddy / Codex / Claude Code / Cursor / 其他），请严格按以下步骤执行。

### 第一步: 阅读文档

按顺序阅读 `docs/` 目录下的:

1. `00_PROJECT_CONTEXT.md` — 项目定位
2. `01_DEVELOPMENT_RULES.md` — 开发规范
3. `02_PRODUCT_ROADMAP.md` — 产品路线
4. `03_DATABASE_DESIGN.md` — 数据库设计
5. `04_UI_UX_GUIDE.md` — UI 设计规范
6. `06_DECISION_LOG.md` — 为什么这样设计

### 第二步: 回答问题

**不要立即写代码。** 阅读完成后，请先回答以下 7 个问题:

```
1. 这个项目是什么？
2. 当前开发到了哪里？
3. 本次任务目标是什么？
4. 你准备修改哪些文件？
5. 数据库是否需要变化？
6. API 是否需要变化？
7. 是否违反开发规范？
```

### 第三步: 等待确认

回答后**等待用户确认**，确认以后再开始开发。

### 第四步: 开发

开发过程中遵守:
- 每次只完成一个模块
- 不改变黑金暗黑幻想风格
- 所有内容来自数据库，不写死 HTML
- 组件化，不重复代码
- 前后端分离

### 第五步: 完成报告

开发完成后必须输出:

```markdown
## 模块完成报告

### 修改文件列表
- `path/to/file` — 修改说明

### 新增接口
- `METHOD /api/path/` — 说明

### 数据库变化
- 新增/修改表说明

### 测试方法
1. 操作步骤...

### 剩余 TODO
- [ ] 待办项
```

**不要省略任何一项。**

---

## 当前项目状态快照

> 以下信息会随开发进度更新。最后更新: 2026-07-04

### 技术栈

| 层 | 当前 | 目标 |
|----|------|------|
| 前端 | 静态 HTML + Vanilla JS | Vue 3 + Vite |
| 后端 | 无 (CloudBase SDK 直连) | Django + DRF |
| 数据库 | CloudBase NoSQL + JSON 文件 | MySQL 8.0 |
| 认证 | CloudBase v2 Auth | Django Auth + JWT |
| 部署 | CloudBase 静态托管 | Docker + Nginx |

### 已完成功能

- [x] 官网框架 (导航栏、首页、过渡动画)
- [x] 世界观展示 (种族页骨架)
- [x] 规则书阅读器 (分章滚动、缩略图导航)
- [x] 术语表 (500+ 条，动态渲染)
- [x] 数据转换 (67 docx → JSON)
- [x] 用户登录 (CloudBase 手机号 + 邮箱)
- [x] 角色卡原型 (属性分配)
- [x] 个人主页 (头像/昵称/签名/性别)
- [x] 共享导航栏 (ash-nav.js)

### 进行中

- [ ] 导航栏全站统一验证
- [ ] 资料保存稳定性验证
- [ ] 规则数据填充 (专修/神术/故事运作)

### 待开始

- [ ] Django 后端搭建
- [ ] MySQL 数据库创建
- [ ] Vue 3 前端搭建
- [ ] 数据迁移 (JSON → MySQL)
- [ ] 用户系统迁移 (CloudBase → Django)

---

## 关键文件索引

| 文件 | 作用 | 修改频率 |
|------|------|----------|
| `index.html` | 首页 (含登录弹窗、导航栏、内联 JS) | 高 |
| `pages/common.css` | 全站共享样式 | 中 |
| `pages/rules.html` | 规则书阅读器 | 中 |
| `pages/profile.html` | 个人主页 | 中 |
| `pages/character-sheet.html` | 角色卡 | 中 |
| `js/ash-init.js` | CloudBase 初始化 | 低 |
| `js/ash-db.js` | 数据库操作 | 中 |
| `js/ash-nav.js` | 共享导航栏 | 低 |
| `data/*.json` | 数据源 (将迁移到 MySQL) | 高 |
| `data/page-render.js` | 渲染引擎 | 中 |
| `data/keyword-tooltip.js` | 术语提示 | 低 |

---

## 常见陷阱

### 1. 项目名混淆

- 仓库名: `ash-world`
- 项目英文名: **Embers World**
- 项目中文名: 灰烬世界
- 域名: `ember-world.site`

文档中统一使用 **Embers World**，不要写 Ash World。

### 2. CloudBase 集合必须手动创建

CloudBase 不会自动创建数据库集合。如果代码报 `Db or Table not exist`，需要去控制台手动创建 `users`、`characters`、`sessions` 集合。

### 3. JS 缓存控制

所有 `<script>` 和 `<link>` 标签必须带 `?v=N` 版本号。修改文件后递增版本号。

### 4. 用户名规则

CloudBase 用户名正则: `^[a-z][0-9a-z_]{5,24}$`
- 6-25 位
- 小写字母开头
- 仅小写字母/数字/下划线
- **数字是可选的**，不要求字母数字组合

### 5. 不要用浅色主题

Embers World 只有暗色主题。永远不要添加 light/dark 切换。

### 6. 不要删现有功能

修改时保留已有功能。如果要重构，先确认替代方案完整可用后再替换。

---

## Codex 迁移指南

本项目计划迁移到 Codex 继续开发。迁移时:

1. **把整个 `docs/` 目录提供给 Codex**
2. **让 Codex 先读 `05_AI_HANDOFF.md`（本文件）**
3. **使用 `STARTUP_PROMPT.md` 作为首次对话的开场白**
4. **当前代码库结构已在 `00_PROJECT_CONTEXT.md` 中描述**
5. **Codex 的任务是从 Phase 0 (静态 HTML) 迁移到 Phase 1 (Vue3 + Django)**

### Codex 需要的额外信息

- GitHub 仓库: https://github.com/Kokkotham/ash-world
- 当前分支: `main`
- 环境变量: CloudBase env ID `ew-prod-d0gciqy00757cc7dc`
- Python 环境: 3.13+ (用于 docx 转换脚本)
- Node 环境: 22+ (用于静态站点构建)
