# Embers World — Vue 组件规范

> **文档级别**: 前端架构
> **最后更新**: 2026-07-04
> **框架**: Vue 3 + Composition API + `<script setup>`

---

## 1. 组件命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | PascalCase | `RuleCard.vue` |
| 组件标签 | kebab-case | `<rule-card />` |
| 页面视图 | PascalCase + View 后缀 | `RuleDetailView.vue` |
| 组件目录 | kebab-case | `components/rule-card/` |

---

## 2. 目录结构

```
frontend/src/
├── components/
│   ├── layout/
│   │   ├── AppHeader.vue          # 顶部导航
│   │   ├── AppFooter.vue          # 底部
│   │   ├── AppSidebar.vue         # 侧边栏
│   │   └── AppContainer.vue       # 内容容器
│   ├── rule/
│   │   ├── RuleCard.vue           # 规则卡片
│   │   ├── RuleTable.vue          # 规则表格
│   │   ├── LevelTable.vue         # 等级表
│   │   └── RuleRelation.vue       # 关联规则
│   ├── lore/
│   │   ├── LoreCard.vue
│   │   ├── RaceCard.vue
│   │   └── DeityCard.vue
│   ├── character/
│   │   ├── CharacterSheet.vue     # 角色卡主组件
│   │   ├── AttributeEditor.vue    # 属性编辑器
│   │   ├── SkillSelector.vue      # 技能选择器
│   │   └── EquipmentList.vue      # 装备列表
│   ├── glossary/
│   │   ├── GlossaryList.vue       # 术语列表
│   │   └── GlossaryTooltip.vue    # 悬浮提示
│   ├── common/
│   │   ├── SearchBar.vue
│   │   ├── PaginationBar.vue
│   │   ├── LoadingSpinner.vue
│   │   ├── EmptyState.vue
│   │   └── ConfirmDialog.vue
│   └── user/
│       ├── UserMenu.vue           # 右上角用户区
│       ├── LoginForm.vue
│       ├── RegisterForm.vue
│       └── ProfileEditor.vue
├── views/
│   ├── HomeView.vue
│   ├── RuleListView.vue
│   ├── RuleDetailView.vue
│   ├── LoreIndexView.vue
│   ├── RaceListView.vue
│   ├── RaceDetailView.vue
│   ├── GlossaryView.vue
│   ├── CharacterListView.vue
│   ├── CharacterCreateView.vue
│   ├── CharacterDetailView.vue
│   ├── ProfileView.vue
│   ├── LoginView.vue
│   └── RegisterView.vue
├── stores/
│   ├── auth.js                    # 认证状态
│   ├── character.js               # 角色卡状态
│   └── ui.js                      # UI 状态 (侧边栏、弹窗)
├── api/
│   ├── index.js                   # Axios 实例 + 拦截器
│   ├── auth.js                    # 认证 API
│   ├── rules.js                   # 规则 API
│   ├── lore.js                    # 世界观 API
│   ├── characters.js              # 角色卡 API
│   ├── glossary.js                # 术语 API
│   └── users.js                   # 用户 API
├── router/
│   └── index.js
├── assets/
│   ├── styles/
│   │   ├── variables.css          # CSS 变量 (色板/间距)
│   │   ├── base.css               # 基础样式
│   │   └── animations.css         # 动画
│   ├── fonts/
│   └── images/
└── App.vue
```

---

## 3. 组件模板

### 3.1 标准组件

```vue
<script setup>
import { ref, onMounted } from 'vue'

// Props
const props = defineProps({
    rule: {
        type: Object,
        required: true
    },
    showRelations: {
        type: Boolean,
        default: true
    }
})

// Emits
const emit = defineEmits(['click', 'navigate'])

// 状态
const isExpanded = ref(false)

// 方法
function toggle() {
    isExpanded.value = !isExpanded.value
}

function handleClick() {
    emit('click', props.rule)
}
</script>

<template>
    <div class="rule-card" @click="handleClick">
        <h3 class="rule-card__title">{{ rule.title }}</h3>
        <p class="rule-card__summary">{{ rule.summary }}</p>
        <button class="rule-card__toggle" @click.stop="toggle">
            {{ isExpanded ? '收起' : '展开' }}
        </button>
    </div>
</template>

<style scoped>
.rule-card {
    background: var(--bg-card);
    border: 1px solid var(--border-gold);
    border-radius: 4px;
    padding: var(--space-6);
    cursor: pointer;
    transition: border-color 0.3s ease;
}

.rule-card:hover {
    border-color: rgba(201, 168, 76, 0.4);
}

.rule-card__title {
    color: var(--gold);
    font-size: var(--text-xl);
    margin-bottom: var(--space-2);
}

.rule-card__summary {
    color: var(--text-secondary);
    font-size: var(--text-sm);
    line-height: 1.6;
}
</style>
```

### 3.2 组件规范要点

| 规则 | 说明 |
|------|------|
| `<script setup>` | 统一使用 Composition API + script setup |
| `scoped` 样式 | 所有组件样式必须 scoped |
| Props 类型 | 必须声明 type，required 标注必填 |
| Emits 声明 | 必须用 defineEmits 声明事件 |
| 事件命名 | kebab-case: `@navigate`, `@rule-click` |
| CSS 类名 | BEM: `.rule-card__title`, `.rule-card--active` |

---

## 4. API 请求层

### 4.1 Axios 实例

```javascript
// api/index.js
import axios from 'axios'

const api = axios.create({
    baseURL: '/api/v1',
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
})

// 请求拦截: 附加 Token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// 响应拦截: 统一错误处理
api.interceptors.response.use(
    response => response.data,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token')
            window.location.href = '/login'
        }
        return Promise.reject(error.response?.data || error)
    }
)

export default api
```

### 4.2 API 模块

```javascript
// api/rules.js
import api from './index'

export default {
    list(params) {
        return api.get('/rules/', { params })
    },
    detail(slug) {
        return api.get(`/rules/${slug}/`)
    },
    search(query, params) {
        return api.get('/rules/search/', { params: { q: query, ...params } })
    }
}
```

---

## 5. Pinia Store 模板

```javascript
// stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authApi from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const token = ref(localStorage.getItem('access_token') || '')
    const isLoggedIn = computed(() => !!token.value)

    async function login(phone, code) {
        const res = await authApi.smsLogin(phone, code)
        token.value = res.data.access_token
        user.value = res.data.user
        localStorage.setItem('access_token', res.data.access_token)
        localStorage.setItem('refresh_token', res.data.refresh_token)
    }

    function logout() {
        token.value = ''
        user.value = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
    }

    return { user, token, isLoggedIn, login, logout }
})
```

---

## 6. 路由守卫

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', component: () => import('@/views/HomeView.vue') },
        { path: '/rules/:slug', component: () => import('@/views/RuleDetailView.vue') },
        { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
        { path: '/characters/new', component: () => import('@/views/CharacterCreateView.vue'), meta: { auth: true } },
        { path: '/profile', component: () => import('@/views/ProfileView.vue'), meta: { auth: true } }
    ]
})

router.beforeEach((to, from, next) => {
    const auth = useAuthStore()
    if (to.meta.auth && !auth.isLoggedIn) {
        next({ path: '/login', query: { redirect: to.fullPath } })
    } else if (to.meta.guest && auth.isLoggedIn) {
        next('/')
    } else {
        next()
    }
})

export default router
```
