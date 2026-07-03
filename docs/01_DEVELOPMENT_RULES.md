# Embers World — 开发规范

> **文档级别**: 强制遵守
> **最后更新**: 2026-07-04

---

## 第一原则: 数据库驱动

**不要开发静态页面。所有内容必须来自数据库。**

包括但不限于:
- 规则文本
- 世界观条目
- 角色卡数据
- 公告/更新日志
- 版本记录
- 术语表

**全部后台可编辑。** 前端只负责渲染，不负责存储内容。

```
正确做法:
  数据库 → API → Vue 组件渲染

错误做法:
  Vue 组件里写死 <p>纳露安人类是...</p>
```

> 当前原型阶段使用 JSON 文件作为数据源，这是过渡方案。目标架构中所有数据必须存入 MySQL，通过 DRF API 提供。

---

## 第二原则: 组件化

**禁止大量重复代码。所有公共组件必须抽离。**

### Vue 组件规范 (目标架构)

```
components/
├── layout/
│   ├── AppHeader.vue          # 顶部导航
│   ├── AppFooter.vue          # 底部
│   └── AppSidebar.vue         # 侧边栏
├── rule/
│   ├── RuleCard.vue           # 规则卡片
│   ├── RuleTable.vue          # 规则表格
│   └── LevelTable.vue         # 等级表
├── lore/
│   ├── LoreCard.vue
│   └── LoreRelation.vue       # 关联条目
├── character/
│   ├── CharacterSheet.vue
│   ├── AttributeEditor.vue
│   └── SkillSelector.vue
├── common/
│   ├── GlossaryTooltip.vue    # 术语提示
│   ├── SearchBar.vue
│   └── PaginationBar.vue
└── user/
    ├── UserMenu.vue           # 右上角用户区
    └── ProfileEditor.vue
```

### 当前原型规范

当前静态 HTML 阶段，公共逻辑已抽离为:
- `js/ash-init.js` — CloudBase 初始化
- `js/ash-db.js` — 数据库操作
- `js/ash-nav.js` — 导航栏组件
- `data/page-render.js` — 渲染引擎
- `data/keyword-tooltip.js` — 术语提示
- `pages/common.css` — 共享样式

---

## 第三原则: 前后端完全分离

```
Vue 3 (前端)
    ↓ REST API (Axios)
Django + DRF (后端)
    ↓ ORM
MySQL (数据库)
```

**禁止前端直接操作数据库。** 前端只能通过 API 读写数据。

| 层 | 职责 | 禁止 |
|----|------|------|
| Vue | 渲染 UI、用户交互、表单校验 | 直接 SQL、直接操作数据库 |
| DRF | 业务逻辑、数据校验、权限控制 | 返回 HTML |
| Django ORM | 数据持久化、关联查询 | 在视图层写裸 SQL |

---

## 第四原则: 不改变整体视觉风格

### 保持

| 要素 | 说明 |
|------|------|
| 黑金色 | 主色 #0a0a0a / 强调色 #c9a84c |
| 暗黑幻想 | 沉重、神秘、古典 |
| 中古文献 | 衬线字体、羊皮纸纹理感 |
| 留白 | 大量负空间，不堆砌信息 |
| 沉浸感 | 微妙动画、渐变过渡 |

### 禁止

| 风格 | 原因 |
|------|------|
| 蓝色科技风 | 与品牌调性冲突 |
| 玻璃拟态 (Glassmorphism) | 过于现代，破坏沉浸感 |
| Material Design | 谷歌风格，与暗黑幻想不搭 |
| 苹果风 (Apple HIG) | 过于简洁轻快 |

> 详细的色板、字体、间距规范见 `04_UI_UX_GUIDE.md`。

---

## 第五原则: 每次只完成一个模块

**完成一个模块以后再开始下一个。不要连续开发多个模块。**

### 每个模块完成后必须输出:

```markdown
## 模块完成报告

### 修改文件列表
- `path/to/file.vue` — 新增/修改内容说明
- `path/to/api.py` — 新增/修改内容说明

### 新增接口
- `GET /api/rules/` — 获取规则列表
- `POST /api/characters/` — 创建角色卡

### 数据库变化
- 新增表 `rule_tags` (id, rule_id, tag_id)
- 修改表 `characters` 新增字段 `level`

### 测试方法
1. 访问 /rules 页面，验证...
2. 调用 API，验证...

### 剩余 TODO
- [ ] 搜索功能
- [ ] 批量导入
```

**输出后等待确认，不要自动开始下一个模块。**

---

## 第六原则: 代码质量

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| Vue 组件 | PascalCase | `RuleCard.vue` |
| Vue 文件 | kebab-case | `rule-card.vue` (路由级) |
| JS 函数 | camelCase | `fetchRules()` |
| JS 变量 | camelCase | `ruleList` |
| CSS 类 | kebab-case | `.rule-card` |
| Python 类 | PascalCase | `RuleViewSet` |
| Python 函数 | snake_case | `get_queryset()` |
| 数据库表 | snake_case 复数 | `rules`, `rule_tags` |
| API 路径 | kebab-case 复数 | `/api/rule-tags/` |

### 提交规范

见 `11_GIT_CONVENTIONS.md`。

### 语法检查

**所有 JS 文件修改后必须运行 `node -c` 语法检查。**

---

## 第七原则: 版本号管理

### JS/CSS 缓存控制

所有引用 `js/*.js` 和 `css/*.css` 的地方必须带版本号:
```html
<script src="js/ash-nav.js?v=9"></script>
```

每次修改文件后递增版本号以破坏浏览器缓存。

### API 版本

API 路径统一前缀 `/api/v1/`，版本升级时新增 `/api/v2/` 并保留旧版本。

---

## 第八原则: 安全

| 规则 | 说明 |
|------|------|
| 密码不明文存储 | Django 自带 PBKDF2 |
| API 需认证 | 除公开规则/世界观外，均需 JWT 认证 |
| XSS 防护 | Vue 默认转义，禁止使用 `v-html` 除非确认安全 |
| CSRF 防护 | Django 默认开启 |
| SQL 注入 | 禁止裸 SQL，必须用 ORM |
| 文件上传 | 限制类型 (jpg/png)、大小 (≤2MB)、路径白名单 |
