# Embers World — Git 提交规范

> **文档级别**: 协作规范
> **最后更新**: 2026-07-04

---

## 1. 分支策略

| 分支 | 用途 | 保护 |
|------|------|------|
| `main` | 生产分支，始终可部署 | 禁止直接 push，必须 PR |
| `dev` | 开发集成分支 | PR 合入 |
| `feature/*` | 功能分支 | 从 `dev` 拉出 |
| `fix/*` | 修复分支 | 从 `dev` 或 `main` 拉出 |
| `hotfix/*` | 紧急修复 | 从 `main` 拉出，合回 `main` 和 `dev` |

### 分支命名

```
feature/character-create     # 功能: 角色创建
feature/rule-search          # 功能: 规则搜索
fix/login-redirect           # 修复: 登录跳转
hotfix/avatar-upload-crash   # 紧急: 头像上传崩溃
```

---

## 2. Commit 规范

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 Bug |
| `refactor` | 重构 (不改变功能) |
| `style` | 样式调整 (不改变逻辑) |
| `docs` | 文档变更 |
| `test` | 测试相关 |
| `chore` | 构建/工具/依赖 |
| `perf` | 性能优化 |
| `ci` | CI/CD 配置 |

### Scope

模块名，如: `auth`, `rules`, `lore`, `characters`, `glossary`, `ui`, `nav`, `api`。

### 示例

```
feat(characters): 角色卡创建页面，支持种族选择和属性分配

- 新增 CharacterCreateView.vue
- 对接 POST /api/v1/characters/ 接口
- 属性分配: 4属性 1d4 随机 + 10点手动
- 种族选择后自动显示属性修正

Closes #12
```

```
fix(nav): 修复切换页面后用户区消失的问题

- 新增 ash-nav.js 共享导航组件
- 所有页面统一引入 ash-nav.js?v=9
- 导航栏从 localStorage 读取登录状态
```

---

## 3. PR 规范

### PR 标题

同 commit 格式: `<type>(<scope>): <subject>`

### PR 描述模板

```markdown
## 变更说明

简要描述本次 PR 做了什么。

## 变更类型

- [ ] 新功能
- [ ] Bug 修复
- [ ] 重构
- [ ] 样式调整
- [ ] 文档
- [ ] 其他

## 修改文件

- `path/to/file` — 修改说明
- `path/to/file` — 修改说明

## 数据库变化

- [ ] 无数据库变化
- [ ] 有 (描述变化)

## API 变化

- [ ] 无 API 变化
- [ ] 有 (描述变化)

## 测试

- [ ] 本地测试通过
- [ ] 语法检查通过
- [ ] 移动端适配检查

## 截图

(如有 UI 变化，附截图)
```

---

## 4. 版本标签

```
v0.1.0   # Phase 0 原型
v0.2.0   # Phase 0 用户系统
v0.3.0   # Phase 0 导航统一
v1.0.0   # Phase 1 正式版 (Vue + Django)
v1.1.0   # Phase 2 角色系统
v1.2.0   # Phase 3 搜索
```

### 语义化版本

| 位 | 说明 | 示例 |
|----|------|------|
| Major | 破坏性变更 | v1.0.0 → v2.0.0 |
| Minor | 新功能，向下兼容 | v1.0.0 → v1.1.0 |
| Patch | Bug 修复 | v1.0.0 → v1.0.1 |

---

## 5. .gitignore 关键项

```gitignore
# 依赖
node_modules/
__pycache__/
*.pyc
venv/

# 构建产物
dist/
build/
_deploy_live/

# 环境变量
.env
.env.local

# IDE
.vscode/
.idea/

# 系统
.DS_Store
Thumbs.db

# 临时文件
*.zip
_check_*.js
```

---

## 6. 当前仓库状态

| 项目 | 值 |
|------|-----|
| 仓库 | https://github.com/Kokkotham/ash-world |
| 主分支 | `main` |
| 部署方式 | CloudBase 静态托管 + GitHub Pages |
| CI/CD | 待配置 (Phase 1) |
