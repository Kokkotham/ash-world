# Embers World — 文档索引

> **仓库**: https://github.com/Kokkotham/ash-world
> **域名**: https://ember-world.site
> **最后更新**: 2026-07-04

---

## 文档阅读顺序

### 必读 (AI 接手前)

| 序号 | 文件 | 内容 | 读者 |
|------|------|------|------|
| 00 | `00_PROJECT_CONTEXT.md` | 项目定位、技术架构、文件结构 | AI + 开发者 |
| 01 | `01_DEVELOPMENT_RULES.md` | 开发规范、八大原则 | AI + 开发者 |
| 02 | `02_PRODUCT_ROADMAP.md` | 产品路线、里程碑 | AI + 开发者 + PM |
| 03 | `03_DATABASE_DESIGN.md` | 数据库 ER 图、表结构、迁移计划 | AI + 开发者 |
| 04 | `04_UI_UX_GUIDE.md` | 色板、字体、布局、组件规范 | AI + 开发者 + 设计 |
| 05 | `05_AI_HANDOFF.md` | AI 交接流程、当前状态、常见陷阱 | AI (必读) |
| 06 | `06_DECISION_LOG.md` | 架构决策记录 (为什么这样设计) | AI + 开发者 |

### 扩展 (按需阅读)

| 序号 | 文件 | 内容 | 读者 |
|------|------|------|------|
| 07 | `07_PRD.md` | 产品需求文档、用户故事、验收标准 | PM + 开发者 |
| 08 | `08_SITE_MAP.md` | 站点地图、URL 规范、导航结构 | 开发者 |
| 09 | `09_API_SPEC.md` | REST API 接口规范 | 后端开发者 |
| 10 | `10_COMPONENT_SPEC.md` | Vue 组件规范、目录结构、模板 | 前端开发者 |
| 11 | `11_GIT_CONVENTIONS.md` | Git 分支、Commit、PR 规范 | 所有贡献者 |
| 12 | `12_USER_FLOWS.md` | 用户流程图 (注册/登录/角色/资料) | 设计 + 开发者 |

### 启动

| 文件 | 用途 |
|------|------|
| `STARTUP_PROMPT.md` | 每次新对话的开场白 (复制粘贴) |

---

## 快速导航

### 我是 AI，刚接手项目

1. 读 `05_AI_HANDOFF.md`
2. 用 `STARTUP_PROMPT.md` 的内容作为开场白
3. 按必读顺序阅读 00-06
4. 回答 7 个问题，等待确认

### 我是新开发者

1. 读 `00_PROJECT_CONTEXT.md` 了解项目
2. 读 `01_DEVELOPMENT_RULES.md` 了解规范
3. 读 `04_UI_UX_GUIDE.md` 了解视觉风格
4. 读 `11_GIT_CONVENTIONS.md` 了解协作流程
5. 找 PM 确认任务

### 我要开发后端 API

1. 读 `03_DATABASE_DESIGN.md` 了解表结构
2. 读 `09_API_SPEC.md` 了解接口规范
3. 读 `06_DECISION_LOG.md` 了解为什么选 Django

### 我要开发前端页面

1. 读 `04_UI_UX_GUIDE.md` 了解色板和组件
2. 读 `10_COMPONENT_SPEC.md` 了解 Vue 组件规范
3. 读 `08_SITE_MAP.md` 了解页面结构
4. 读 `12_USER_FLOWS.md` 了解交互流程

### 我要了解产品规划

1. 读 `02_PRODUCT_ROADMAP.md` 了解路线
2. 读 `07_PRD.md` 了解需求
3. 读 `06_DECISION_LOG.md` 了解决策

---

## 文档维护规则

1. **每次重大变更后更新** — 修改架构、新增模块、变更技术栈时同步更新对应文档
2. **保持单一真相来源** — 同一信息只在一个地方定义，其他地方引用
3. **标注更新日期** — 每个文件头部有 `最后更新` 字段
4. **决策必须记录** — 任何架构决策写入 `06_DECISION_LOG.md`
5. **AI 交接时更新** — 每次换 AI 时更新 `05_AI_HANDOFF.md` 的状态快照

---

## 旧文档归档

| 文件 | 状态 | 说明 |
|------|------|------|
| `system_design.md` | 已归档 | Phase 0 系统设计，被 03/09/10 替代 |
| `class-diagram.mermaid` | 已归档 | Phase 0 类图，被 03_DATABASE_DESIGN.md 替代 |
| `sequence-diagram.mermaid` | 保留 | 交互序列图，仍有参考价值 |

> 旧文档不删除，但以新文档为准。
