# Embers World — 项目上下文

> **文档级别**: 必读 (AI 接手前第一个阅读)
> **最后更新**: 2026-07-04
> **维护者**: 林鹏 (DM / Project Owner)

---

## 1. 项目定位

**Embers World** 是一款原创 TRPG（桌面角色扮演游戏）的官方数字平台。

- **项目英文名**: Embers World
- **项目中文名**: 灰烬世界
- **GitHub 仓库名**: ash-world (历史命名，勿改)
- **自定义域名**: https://ember-world.site
- **GitHub 仓库**: https://github.com/Kokkotham/ash-world

### 这个网站是什么

| 维度 | 说明 |
|------|------|
| 展示世界观 | 种族、神系、地理、历史、势力 |
| 查询游戏规则 | 专修、神术、故事运作、状态词缀 |
| 查询规则词条 | 术语表 500+ 条，支持关联跳转 |
| 保存玩家角色卡 | 角色创建、属性分配、云端存储 |
| 提供官方更新日志 | 版本管理、改动记录 |
| 维护规则数据库 | 后台可编辑的实体化管理 |

### 这个网站不是什么

| 不是 | 原因 |
|------|------|
| 商业官网 | 不卖产品，不做营销 |
| D&D Beyond | 不兼容 D&D 5e 或其他第三方规则 |
| 开放社区 | 不做 UGC，不做论坛（现阶段） |
| VTT（虚拟桌面） | 不做地图标注、骰子滚动、实时同步 |
| 战役管理工具 | 不做战役模组编辑、时间线管理 |
| 在线跑团平台 | 不做语音/视频/即时聊天 |

> 以上功能以后可以扩展，但**不是当前目标**。

---

## 2. 目标用户

| 角色 | 需求 | 优先级 |
|------|------|--------|
| **玩家 (Player)** | 查规则、查词条、建角色卡、看世界观 | P0 |
| **GM (主持人)** | 以上全部 + 快速检索规则、管理多张角色卡 | P0 |
| **开发组 (Dev)** | 后台编辑规则、管理版本、审核内容 | P1 |
| **管理员 (Admin)** | 用户管理、权限分配、全站配置 | P2 |

---

## 3. 技术架构

### 3.1 当前状态 (Phase 0 — 原型)

| 层 | 技术 | 说明 |
|----|------|------|
| 前端 | 静态 HTML + Vanilla JS | 数据驱动渲染，零框架依赖 |
| 数据 | JSON 文件 + CloudBase NoSQL | `data/*.json` 为数据源，CloudBase 存用户/角色卡 |
| 认证 | CloudBase v2 Auth | 手机号验证码 + 邮箱注册 |
| 部署 | CloudBase 静态托管 + GitHub Pages | 双部署通道 |
| 域名 | ember-world.site | DNS → GitHub Pages |

### 3.2 目标架构 (Phase 1+ — 正式版)

```
Vue 3 (SPA)
    ↓ REST API (Axios)
Django + DRF (后端)
    ↓ ORM
MySQL (关系型数据库)
    ↓
SimpleUI (Django Admin 后台)
```

| 层 | 技术 | 版本目标 | 理由 |
|----|------|----------|------|
| 前端框架 | Vue 3 | 3.4+ | 组件化、响应式、生态成熟 |
| UI 组件库 | 自研 (黑金风格) | — | 不用 Element/Ant Design，保持暗黑幻想视觉 |
| HTTP 客户端 | Axios | 1.6+ | 拦截器、错误处理 |
| 后端框架 | Django | 5.0+ | Admin 成熟、ORM 强大 |
| API 框架 | Django REST Framework | 3.14+ | 序列化、视图集、权限 |
| 数据库 | MySQL | 8.0+ | 关系型，适合复杂关联 |
| 后台管理 | SimpleUI | latest | Django Admin 美化层 |
| 部署 | Docker + Nginx | — | 容器化部署 |

### 3.3 迁移路径

```
Phase 0 (当前)                Phase 1 (目标)               Phase 2+
─────────────────             ─────────────────            ─────────────────
静态 HTML + JSON              Vue 3 SPA 上线               角色系统完整
CloudBase 认证          →     Django 后端上线         →    搜索/收藏/历史
CloudBase NoSQL               MySQL 数据库                 版本管理
GitHub Pages                  Docker 部署                  开放 API
```

> **迁移原则**: 不破坏现有数据。JSON 文件数据将编写迁移脚本导入 MySQL。

---

## 4. 项目文件结构

### 4.1 当前结构

```
ash-world/                     # GitHub 仓库名
├── index.html                 # 首页（含登录弹窗、导航栏）
├── pages/                     # 子页面
│   ├── common.css             # 共享样式（导航栏、卡片、表格、tooltip）
│   ├── rules.html             # 规则书阅读器
│   ├── rules.css              # 规则书专用样式
│   ├── races-ontology.html    # 种族页
│   ├── glossary.html          # 术语表
│   ├── character-sheet.html   # 角色创建页
│   ├── profile.html           # 个人主页
│   ├── pantheon.html          # 神系页
│   ├── worldview.html         # 世界观
│   ├── news.html              # 公告/更新日志
│   └── ...                    # 其他页面
├── js/                        # 脚本
│   ├── tcb-sdk.js             # CloudBase JS SDK
│   ├── ash-init.js            # 共享初始化（app/auth 导出）
│   ├── ash-db.js              # 数据库操作（users/characters/sessions）
│   └── ash-nav.js             # 共享导航栏组件
├── data/                      # JSON 数据源
│   ├── races.json             # 种族（远古+玩家）
│   ├── professions.json       # 专修（11大类）
│   ├── divine-arts.json       # 神术
│   ├── story-rules.json       # 故事运作规则
│   ├── glossary.json          # 术语表
│   ├── chapters.json          # 章节树
│   ├── links.json             # 交叉关联
│   ├── ew_raw/                # docx 原始提取（65个）
│   └── ...
├── tools/                     # 工具脚本
│   ├── docx2json.py           # docx → JSON 批量转换
│   └── build_glossary.py      # 术语表生成
├── docs/                      # ← 本文档目录
├── _deploy_live/              # CloudBase 部署镜像
├── CNAME                      # GitHub Pages 自定义域名
└── .nojekyll                  # 禁用 Jekyll
```

### 4.2 目标结构 (Phase 1+)

```
ash-world/
├── docs/                      # 项目文档（本目录）
├── frontend/                  # Vue 3 SPA
│   ├── src/
│   │   ├── components/        # 公共组件
│   │   ├── views/             # 页面视图
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── api/               # API 请求层
│   │   ├── router/            # Vue Router
│   │   └── assets/            # 静态资源
│   ├── public/
│   └── package.json
├── backend/                   # Django 后端
│   ├── config/                # Django 配置
│   ├── apps/
│   │   ├── rules/             # 规则模块
│   │   ├── lore/              # 世界观模块
│   │   ├── characters/        # 角色卡模块
│   │   ├── accounts/          # 用户模块
│   │   └── glossary/          # 术语表模块
│   ├── manage.py
│   └── requirements.txt
├── data/                      # 迁移用原始 JSON（保留）
└── docker-compose.yml         # 容器编排
```

---

## 5. 关键约束

1. **项目英文名是 Embers World**，不是 Ash World。仓库名 `ash-world` 是历史遗留，文档中统一使用 Embers World。
2. **视觉风格是黑金暗黑幻想**，永远不要改成科技蓝、玻璃拟态、Material Design 或苹果风。详见 `04_UI_UX_GUIDE.md`。
3. **当前原型用静态 HTML**，但目标是 Vue3 + Django。新功能如果复杂度高，应直接用目标架构开发，而非继续在静态 HTML 上堆叠。
4. **数据是核心资产**。67 个 docx 规则书已转为 JSON，这些数据迁移到 MySQL 时不能丢失。
5. **用户系统使用 CloudBase 认证**（当前），迁移到 Django 后需要做认证迁移，保留已有用户。

---

## 6. 外部服务

| 服务 | 用途 | 状态 |
|------|------|------|
| 腾讯云 CloudBase | 静态托管 + 认证 + NoSQL | 运行中 |
| GitHub Pages | 备用部署通道 | 运行中 |
| 腾讯云 DNS | ember-world.site 域名解析 | 运行中 |
| CloudBase 环境 | `ew-prod-d0gciqy00757cc7dc` | ap-shanghai |

### CloudBase 集合

| 集合名 | 用途 | 安全规则 |
|--------|------|----------|
| `users` | 用户资料 | `{"read":"auth != null","write":"auth != null"}` |
| `characters` | 角色卡 | 同上 |
| `sessions` | 游戏记录 | 同上 |

> **注意**: CloudBase 不会自动创建集合，必须手动在控制台创建。

---

## 7. 文档阅读顺序

任何 AI 或开发者接手项目，请按以下顺序阅读：

1. `00_PROJECT_CONTEXT.md` ← 你在这里
2. `01_DEVELOPMENT_RULES.md`
3. `02_PRODUCT_ROADMAP.md`
4. `03_DATABASE_DESIGN.md`
5. `04_UI_UX_GUIDE.md`
6. `05_AI_HANDOFF.md`
7. `06_DECISION_LOG.md`
8. 按需阅读: `07_PRD.md` ~ `11_GIT_CONVENTIONS.md`
