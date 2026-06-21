# 灰烬世界（Ash World）网站 — 工作接手文档
**日期**：2026-06-21  
**状态**：rules.html 页面有 5 项设计调整待完成，上次对话中断

---

## 项目基本信息

| 项目 | 内容 |
|------|------|
| 项目名称 | 灰烬世界（Ash World）TRPG 规则书网站 |
| 真实工作区 | `C:\ProgramData\WorkBuddy\chromium-env\13613ht\WorkBuddy\2026-06-07-11-51-51` |
| GitHub 仓库 | https://github.com/Kokkotham/ash-world |
| 本次修改页面 | `pages/rules.html` + `pages/rules.css` + `data/page-render.js` |

---

## 上次已完成的修复

### ✅ rules.css — 两处 CSS 语法破损已修复
1. **Bug 1**：`.detail-pill.active` 规则闭合后残留孤立属性（`color`、`font-weight`）→ 已删除
2. **Bug 2**：`.next-chapter-btn` 过早闭合，导致后续属性变成孤立代码块 → 已将闭合括号移到正确位置

### ✅ page-render.js — 语法检查通过
- 三层导航逻辑（章节 → 子分类 → 技能条目）完整
- `renderRules()` 函数无语法错误

---

## 待完成：5 项设计调整（来自用户截图反馈）

> 用户通过 5 张截图提出了以下设计问题，需要逐一修改。

### 问题 1：金边装饰线位置错误
- **现状**：金色装饰线（`.section-title::after` 伪元素）显示在「RULES & SYSTEM」下方
- **期望**：金边装饰线应该显示在中文标题「**游戏规则**」正下方
- **涉及文件**：`pages/rules.css` — `.lookup-header .section-title` 相关样式
- **分析**：HTML 结构是 `<h2 class="section-title">RULES & SYSTEM<br>游戏规则</h2>`，伪元素在整行底部。需要让伪元素只跟在「游戏规则」后面，或者调整 HTML 结构把两行分开。

### 问题 2：章节导航 Tab 去掉「第X章」字样
- **现状**：左侧章节导航显示「第一章 前言」「第二章 创建角色」…
- **期望**：只显示「前言」「创建角色」「种族」…
- **涉及文件**：`data/page-render.js` — `renderRules()` 函数中的 `chapterNavHTML` 生成逻辑
- **具体位置**：约第 79-91 行，`chapterName` 变量包含「第${i+1}章」前缀
- **修改方向**：去掉 `第${i+1}章 ` 前缀，只保留章节名称

### 问题 3：详情区标题去掉「第X章」字样
- **现状**：点击章节后，右侧详情区大标题显示「第一章 前言」…
- **期望**：只显示「前言」…
- **涉及文件**：`data/page-render.js` — `renderRules()` 中更新 `.lookup-detail-title` 的逻辑
- **具体位置**：约第 207-219 行，设置 `detailTitle.textContent` 处

### 问题 4：整体配色质感向主导航栏看齐
- **现状**：规则书页面的配色、质感不如主导航栏（首页）精致
- **期望**：规则书页面配色/质感与首页导航栏保持一致（参考首页 `index.html` 的配色风格）
- **涉及文件**：`pages/rules.css` — 整体配色变量和组件样式
- **需要参考**：`index.html` 或 `common.css` 中的配色定义

### 问题 5：内容区小标题应该是金色
- **现状**：详情区内的小标题（如「宇宙观与灰烬」）颜色不是金色
- **期望**：内容区小标题使用金色（`var(--ash-gold)` 或等效金色）
- **涉及文件**：`pages/rules.css` — `.detail-content h3` 或等效选择器
- **备注**：用户确认这是上次已理解的需求，但尚未修改

---

## 文件结构（关键文件）

```
C:\ProgramData\WorkBuddy\chromium-env\13613ht\WorkBuddy\2026-06-07-11-51-51\
├── pages\
│   ├── rules.html      ← 规则书页面 HTML
│   └── rules.css       ← 规则书页面样式（主要修改对象）
├── data\
│   ├── page-render.js  ← 三层导航渲染逻辑（修改对象：问题2、3）
│   └── ash-data.js     ← 规则书数据源
├── index.html           ← 首页（参考其配色风格）
└── common.css          ← 全局公共样式（参考配色）
```

---

## 修改顺序建议

1. **问题 2 + 3**（最简单）→ 修改 `page-render.js`，去掉「第X章」
2. **问题 5** → 修改 `rules.css`，给 `.detail-content h3` 加金色
3. **问题 1** → 调整 HTML 结构或 CSS，让金边装饰线跟在「游戏规则」下方
4. **问题 4** → 参考首页配色，调整 `rules.css` 的整体配色和质感

---

## 关键技术细节

### page-render.js 中的章节数据格式
```js
const ruleData = [
  { title: "前言", categories: [...] },
  { title: "创建角色", categories: [...] },
  // ...共 9 个章节
];
```
`title` 字段已经不包含「第X章」前缀（数据源本身就是干净的），问题出在渲染时拼接的前缀。

### 金边装饰线的 CSS 实现
当前使用 `::after` 伪元素实现：
```css
.section-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 2px;
  background: var(--ash-gold);
}
```
由于 `<h2>` 内有 `<br>`，伪元素在整个块底部。解决方案：把「RULES & SYSTEM」和「游戏规则」拆成两个元素。

---

## 验证方式

每次修改后：
1. 用 `node -c data/page-render.js` 检查 JS 语法
2. 在浏览器打开 `pages/rules.html` 验证视觉效果
3. 检查移动端响应式表现

---

## 用户信息

- **称呼**：编创者
- **偏好**：简洁直接，不要多余修饰；做完给我看结果，不要问我
- **决策特点**：感受优先，效果达不到 80% 直接说
- **验证方式**：主要靠视觉（显示不对能发现，其他层面无法判断）

---

*本文档由 AI 助手生成，用于对话中断后的工作接手。*
