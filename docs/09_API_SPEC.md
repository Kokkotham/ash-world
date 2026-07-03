# Embers World — API 接口规范

> **文档级别**: 后端设计
> **最后更新**: 2026-07-04
> **基础路径**: `/api/v1/`
> **认证方式**: JWT (Bearer Token)

---

## 1. 通用规范

### 1.1 请求格式

```
Content-Type: application/json
Authorization: Bearer <access_token>
```

### 1.2 响应格式

```json
{
    "code": 200,
    "message": "success",
    "data": { ... }
}
```

### 1.3 分页格式

```json
{
    "code": 200,
    "data": {
        "count": 150,
        "page": 1,
        "page_size": 20,
        "results": [ ... ]
    }
}
```

### 1.4 错误码

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 请求过频 |
| 500 | 服务器错误 |

---

## 2. 认证接口

### 2.1 手机号发送验证码

```
POST /api/v1/auth/sms/send/
```

**请求:**
```json
{
    "phone": "13800138000"
}
```

**响应:**
```json
{
    "code": 200,
    "message": "验证码已发送"
}
```

### 2.2 手机号登录

```
POST /api/v1/auth/sms/login/
```

**请求:**
```json
{
    "phone": "13800138000",
    "code": "123456"
}
```

**响应:**
```json
{
    "code": 200,
    "data": {
        "access_token": "eyJ...",
        "refresh_token": "eyJ...",
        "user": {
            "id": 1,
            "username": "player01",
            "display_name": "旅人",
            "avatar_url": "/media/avatars/1.jpg"
        }
    }
}
```

### 2.3 邮箱注册

```
POST /api/v1/auth/register/
```

**请求:**
```json
{
    "username": "player01",
    "email": "user@example.com",
    "password": "securePassword123",
    "email_code": "123456"
}
```

### 2.4 邮箱登录

```
POST /api/v1/auth/login/
```

**请求:**
```json
{
    "username": "player01",
    "password": "securePassword123"
}
```

### 2.5 刷新 Token

```
POST /api/v1/auth/refresh/
```

**请求:**
```json
{
    "refresh_token": "eyJ..."
}
```

### 2.6 退出登录

```
POST /api/v1/auth/logout/
```

---

## 3. 用户接口

### 3.1 获取个人资料

```
GET /api/v1/users/me/
```

**响应:**
```json
{
    "code": 200,
    "data": {
        "id": 1,
        "username": "player01",
        "email": "u***@example.com",
        "phone": "138****8000",
        "display_name": "余烬行者",
        "bio": "在灰烬中寻找光明",
        "avatar_url": "/media/avatars/1.jpg",
        "gender": "男",
        "created_at": "2026-06-01T10:00:00Z"
    }
}
```

### 3.2 更新个人资料

```
PATCH /api/v1/users/me/
```

**请求:**
```json
{
    "display_name": "余烬行者",
    "bio": "在灰烬中寻找光明",
    "gender": "男"
}
```

### 3.3 上传头像

```
POST /api/v1/users/me/avatar/
Content-Type: multipart/form-data
```

**请求:**
```
file: <image file>
```

### 3.4 修改密码

```
POST /api/v1/users/me/password/
```

**请求:**
```json
{
    "old_password": "oldPass123",
    "new_password": "newPass456"
}
```

---

## 4. 角色卡接口

### 4.1 角色卡列表

```
GET /api/v1/characters/?page=1&page_size=20
```

### 4.2 创建角色卡

```
POST /api/v1/characters/
```

**请求:**
```json
{
    "name": "艾尔登",
    "race_slug": "naluan_human",
    "profession_slug": "instinct",
    "level": 1,
    "attributes": {
        "strength": 12,
        "agility": 10,
        "intellect": 8,
        "spirit": 10
    },
    "skills": [],
    "equipment": [],
    "background": "一个来自纳露安的年轻冒险者..."
}
```

### 4.3 获取角色卡详情

```
GET /api/v1/characters/:id/
```

### 4.4 更新角色卡

```
PATCH /api/v1/characters/:id/
```

### 4.5 删除角色卡 (软删除)

```
DELETE /api/v1/characters/:id/
```

### 4.6 导出角色卡

```
GET /api/v1/characters/:id/export/?format=json
```

---

## 5. 规则接口

### 5.1 规则列表

```
GET /api/v1/rules/?category=profession&page=1
```

### 5.2 规则详情

```
GET /api/v1/rules/:slug/
```

**响应:**
```json
{
    "code": 200,
    "data": {
        "id": 1,
        "title": "本能",
        "slug": "instinct",
        "summary": "野兽般的直觉与反应...",
        "content": "<p>...</p>",
        "category": {
            "id": 2,
            "name": "专修",
            "slug": "profession"
        },
        "chapter_ref": "3.1",
        "level_table": [
            {"level": 1, "bonus": "+1", "cost": "2点", "effect": "..."}
        ],
        "related_rules": [
            {"slug": "knowledge", "title": "知识"}
        ],
        "glossary_terms": [
            {"key": "hp", "term": "生命值"}
        ],
        "version_number": 3,
        "updated_at": "2026-07-01T10:00:00Z"
    }
}
```

### 5.3 搜索规则

```
GET /api/v1/rules/search/?q=生命值&page=1
```

---

## 6. 世界观接口

### 6.1 世界观条目列表

```
GET /api/v1/lore/?type=race&page=1
```

### 6.2 世界观详情

```
GET /api/v1/lore/:slug/
```

---

## 7. 术语表接口

### 7.1 术语列表

```
GET /api/v1/glossary/?category=core&page=1
```

### 7.2 术语详情

```
GET /api/v1/glossary/:key/
```

### 7.3 搜索术语

```
GET /api/v1/glossary/search/?q=生命
```

---

## 8. 游戏记录接口

### 8.1 记录列表

```
GET /api/v1/sessions/?page=1
```

### 8.2 创建记录

```
POST /api/v1/sessions/
```

**请求:**
```json
{
    "title": "第一幕：灰烬之心",
    "role": "GM"
}
```

---

## 9. 后台管理接口 (Admin only)

> 后台通过 Django Admin + SimpleUI 操作，不直接暴露 API。
> 以下接口仅供内部使用，需要 `is_staff=True` 权限。

### 9.1 规则 CRUD

```
GET    /api/v1/admin/rules/           # 列表
POST   /api/v1/admin/rules/           # 创建
GET    /api/v1/admin/rules/:id/       # 详情
PUT    /api/v1/admin/rules/:id/       # 更新
DELETE /api/v1/admin/rules/:id/       # 删除
```

### 9.2 版本管理

```
GET  /api/v1/admin/rules/:id/versions/      # 版本列表
POST /api/v1/admin/rules/:id/versions/      # 创建快照
GET  /api/v1/admin/rules/:id/versions/:v/   # 查看某版本
POST /api/v1/admin/rules/:id/rollback/:v/   # 回滚到某版本
```

### 9.3 审核流程

```
POST /api/v1/admin/rules/:id/submit/    # 提交审核
POST /api/v1/admin/rules/:id/approve/   # 审核通过
POST /api/v1/admin/rules/:id/reject/    # 驳回
```
