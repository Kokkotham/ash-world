# Embers World — UI/UX 设计规范

> **文档级别**: 强制遵守
> **最后更新**: 2026-07-04
> **品牌视觉**: Dark Fantasy / 黑金暗黑幻想

---

## 1. 整体风格

| 关键词 | 说明 |
|--------|------|
| 黑金色 | 主色调，永不改变 |
| 暗黑幻想 | 沉重、神秘、古典的氛围 |
| 中古文献 | 衬线字体、羊皮纸质感、手抄本排版 |
| 留白 | 大量负空间，不堆砌信息 |
| 沉浸感 | 微妙动画、渐变过渡、粒子特效 |

### 禁止使用的风格

| 风格 | 原因 |
|------|------|
| 蓝色科技风 | 与品牌调性完全冲突 |
| 玻璃拟态 (Glassmorphism) | 过于现代，破坏沉浸感 |
| Material Design | 谷歌风格，不搭 |
| 苹果风 (Apple HIG) | 过于简洁轻快 |
| 扁平化 (Flat Design) | 缺乏层次感和氛围 |
| 霓虹色 | 不符合暗黑幻想 |

---

## 2. 色板

### 2.1 核心色

```css
:root {
    /* 背景色 */
    --bg-darkest: #050505;       /* 最深背景 */
    --bg-dark: #0a0a0a;          /* 主背景 */
    --bg-card: #141414;          /* 卡片背景 */
    --bg-elevated: #1a1a1a;      /* 弹层/悬浮 */

    /* 金色系 */
    --gold: #c9a84c;             /* 主金色 */
    --gold-bright: #e0c460;      /* 高亮金 */
    --gold-dim: #8a7430;         /* 暗金 */
    --gold-glow: rgba(201, 168, 76, 0.15);  /* 金色光晕 */

    /* 文字 */
    --text-primary: #e0d8c8;     /* 主文字（暖白） */
    --text-secondary: #9a9080;   /* 次要文字 */
    --text-muted: #5a5040;       /* 弱化文字 */

    /* 边框/分割线 */
    --border-gold: rgba(201, 168, 76, 0.2);
    --border-dark: rgba(255, 255, 255, 0.06);

    /* 功能色 */
    --danger: #8b2020;           /* 暗红，不用亮红 */
    --success: #4a6a3a;          /* 暗绿 */
    --info: #4a5a7a;             /* 暗蓝灰 */
}
```

### 2.2 不使用浅色主题

Embers World 只有暗色主题。不做 light/dark 切换。

---

## 3. 字体

```css
/* 标题字体 — 中古衬线 */
--font-heading: 'Cinzel', 'Noto Serif SC', 'Songti SC', serif;

/* 正文字体 — 易读衬线 */
--font-body: 'Noto Serif SC', 'Songti SC', 'SimSun', serif;

/* 等宽字体 — 代码/数据 */
--font-mono: 'JetBrains Mono', 'Consolas', monospace;
```

### 字号层级

| 类名 | 大小 | 行高 | 字重 | 用途 |
|------|------|------|------|------|
| `.text-3xl` | 1.875rem (30px) | 1.2 | 700 | 页面主标题 H1 |
| `.text-2xl` | 1.5rem (24px) | 1.3 | 700 | 章节标题 H2 |
| `.text-xl` | 1.25rem (20px) | 1.4 | 600 | 小节标题 H3 |
| `.text-lg` | 1.125rem (18px) | 1.5 | 500 | 强调文字 |
| `.text-base` | 1rem (16px) | 1.7 | 400 | 正文 |
| `.text-sm` | 0.875rem (14px) | 1.6 | 400 | 辅助文字 |
| `.text-xs` | 0.75rem (12px) | 1.5 | 400 | 标签/元信息 |

---

## 4. 间距系统

8 点网格系统:

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

---

## 5. 布局

### 5.1 页面结构

```
┌─────────────────────────────────────────┐
│           顶部导航 (固定)                 │  64px
├──────────┬──────────────────────────────┤
│          │                              │
│  侧边栏   │         正文区               │
│  (可选)   │     max-width: 800px        │
│  240px   │     居中，大量留白            │
│          │                              │
├──────────┴──────────────────────────────┤
│              底部                        │
└─────────────────────────────────────────┘
```

### 5.2 容器宽度

| 名称 | 宽度 | 用途 |
|------|------|------|
| `--container-sm` | 640px | 窄内容（术语表单条） |
| `--container-md` | 768px | 中等内容（角色卡） |
| `--container-lg` | 1024px | 标准内容（规则页） |
| `--container-xl` | 1280px | 宽内容（双栏布局） |

### 5.3 响应式断点

| 断点 | 宽度 | 布局变化 |
|------|------|----------|
| mobile | < 768px | 单栏，侧边栏收起为抽屉 |
| tablet | 768px - 1024px | 可选双栏，侧边栏可折叠 |
| desktop | > 1024px | 完整双栏/三栏 |

---

## 6. 组件规范

### 6.1 卡片 (Card)

```css
.ew-card {
    background: var(--bg-card);
    border: 1px solid var(--border-gold);
    border-radius: 4px;              /* 小圆角，不用大圆角 */
    padding: var(--space-6);
    transition: border-color 0.3s ease;
}
.ew-card:hover {
    border-color: rgba(201, 168, 76, 0.4);
}
```

### 6.2 按钮 (Button)

```css
/* 主按钮 — 金色描边 */
.btn-gold {
    background: transparent;
    border: 1px solid var(--gold);
    color: var(--gold);
    padding: 8px 24px;
    border-radius: 2px;
    transition: all 0.3s ease;
}
.btn-gold:hover {
    background: var(--gold-glow);
    box-shadow: 0 0 12px var(--gold-glow);
}

/* 次要按钮 — 暗色 */
.btn-dark {
    background: var(--bg-elevated);
    border: 1px solid var(--border-dark);
    color: var(--text-secondary);
}
```

### 6.3 表格 (Table)

```css
.ew-table {
    width: 100%;
    border-collapse: collapse;
}
.ew-table th {
    background: var(--bg-elevated);
    color: var(--gold);
    font-weight: 600;
    padding: var(--space-2) var(--space-4);
    border-bottom: 2px solid var(--border-gold);
    text-align: left;
}
.ew-table td {
    padding: var(--space-2) var(--space-4);
    border-bottom: 1px solid var(--border-dark);
    color: var(--text-primary);
}
.ew-table tr:hover td {
    background: rgba(201, 168, 76, 0.05);
}
```

### 6.4 术语提示 (Tooltip)

悬浮在带 `[data-keyword]` 属性的文字上时，显示金色描边的浮动卡片，展示术语定义。

### 6.5 导航栏 (Navbar)

```
┌──────────────────────────────────────────────────┐
│  [Logo] Embers World    规则  世界观  词条  角色   [用户区]  │
│                                                  头像+名字  │
└──────────────────────────────────────────────────┘
```

- 高度: 64px
- 背景: `rgba(10, 10, 10, 0.85)` + `backdrop-filter: blur(20px)`
- 导航链接: 左对齐，hover 时左侧金色竖条 + 文字发光
- 用户区: 右对齐 (`margin-left: auto`)
- 未登录: 显示「登录」按钮
- 已登录: 显示头像 + 昵称，hover 下拉菜单

---

## 7. 页面模板

### 7.1 规则页面统一结构

```
标题
简介
正文 (含表格)
相关规则
更新时间
```

### 7.2 世界观页面统一结构

```
概述
正文
关联人物
关联地点
关联规则
更新时间
```

### 7.3 角色卡页面

```
角色名 + 种族 + 专修 + 等级
─────────────────────
属性区 (力量/敏捷/智力/精神)
技能区
装备区
背景故事
日志区
```

---

## 8. 动画

| 场景 | 动画 | 时长 |
|------|------|------|
| 页面切换 | 淡入淡出 + 轻微上移 | 300ms |
| 卡片 hover | 边框金光 + 微微上浮 | 300ms |
| 按钮点击 | 缩放 0.97 + 金光扩散 | 200ms |
| 弹窗打开 | 淡入 + 轻微缩放 (0.95→1) | 200ms |
| 鼠标拖尾 | 金色粒子拖尾 (ash-bg.js) | 持续 |

> 所有动画使用 `ease` 或 `ease-out`，不用 `bounce` 或 `elastic`。

---

## 9. 无障碍

| 规则 | 说明 |
|------|------|
| 对比度 | 文字与背景对比度 ≥ 4.5:1 (WCAG AA) |
| 焦点可见 | 键盘导航时焦点描边使用 `--gold` |
| ARIA 标签 | 弹窗、下拉菜单、tooltip 均需 ARIA 属性 |
| 键盘导航 | Tab 顺序符合视觉顺序，Esc 关闭弹窗 |
| 图片 alt | 所有图片必须有 alt 文本 |
