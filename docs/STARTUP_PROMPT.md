# Embers World — AI 启动 Prompt

> **用法**: 每次开启新对话（WorkBuddy / Codex / Claude Code / Cursor），把以下内容作为第一条消息发送。

---

## 启动 Prompt (复制以下全部内容)

---

你现在正式接手 Embers World 项目。

这是一个长期维护项目。

请不要立即生成代码。

**第一步:**

完整阅读仓库 `docs/` 文件夹中的所有文档:

- `00_PROJECT_CONTEXT.md` — 项目定位
- `01_DEVELOPMENT_RULES.md` — 开发规范
- `02_PRODUCT_ROADMAP.md` — 产品路线
- `03_DATABASE_DESIGN.md` — 数据库设计
- `04_UI_UX_GUIDE.md` — UI 设计规范
- `05_AI_HANDOFF.md` — AI 交接文档
- `06_DECISION_LOG.md` — 决策日志

阅读完成以后，请回答以下 7 个问题:

1. 这个项目是什么？
2. 当前开发到了哪里？
3. 本次任务目标是什么？
4. 你准备修改哪些文件？
5. 数据库是否需要变化？
6. API 是否需要变化？
7. 是否违反已有开发规范？

**等待我确认以后再开始开发。**

整个项目遵循:

- 技术栈: Vue 3 + Django + DRF + MySQL + SimpleUI (目标架构)
- 当前原型: 静态 HTML + JSON + CloudBase
- 视觉风格: 黑金暗黑幻想 (Dark Fantasy)
- 项目英文名: Embers World (仓库名 ash-world 是历史遗留)

**绝对禁止:**

- ❌ 不要改变黑金暗黑幻想风格
- ❌ 不要删除已有功能
- ❌ 不要写死 HTML 内容 (所有内容来自数据库/JSON)
- ❌ 不要一次性开发多个模块
- ❌ 不要使用蓝色科技风/玻璃拟态/Material Design/苹果风
- ❌ 不要添加浅色主题

**开发完成后必须输出:**

- 修改文件列表
- 新增接口 (如有)
- 数据库变化 (如有)
- 测试步骤
- 剩余 TODO

---

## 补充说明 (给 AI 看的)

### 项目名说明

- 项目英文名: **Embers World**
- 项目中文名: 灰烬世界
- GitHub 仓库名: `ash-world` (历史命名，勿改)
- 自定义域名: `ember-world.site`

### 当前进度

项目处于 **Phase 0 (原型) → Phase 1 (正式架构) 的过渡期**。

Phase 0 已完成:
- 静态 HTML 网站，数据驱动渲染
- CloudBase 认证 (手机号 + 邮箱)
- 规则书/术语表/种族/角色卡/个人主页

Phase 1 待开始:
- Vue 3 前端搭建
- Django + DRF 后端搭建
- MySQL 数据库创建
- 数据迁移 (JSON → MySQL)
- 用户系统迁移 (CloudBase → Django)

### 关键约束

1. 视觉风格永远是黑金暗黑幻想，只有暗色主题
2. 所有内容数据库驱动，不写死 HTML
3. 前后端完全分离，Vue 不直接操作数据库
4. 每次只完成一个模块，完成后输出报告等待确认
5. 组件化，不重复代码
