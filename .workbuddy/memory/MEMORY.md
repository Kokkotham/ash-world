# 灰烬世界 Ash World — 工作进度交接

> 最后更新: 2026-06-17

## 项目概述

灰烬世界（Ash World / EW）是一个 TRPG 世界设定网站。用户是 DM（主持人），正在将 67 个 .docx 规则书文档逐步转化为数据驱动的 Web 页面。

## 部署地址

- **CloudStudio**: https://9a465c3434074b28a0eebbac66865030.app.codebuddy.work
- **GitHub Pages**: https://kokkotham.github.io/ash-world/ (当前 404，需在 Settings→Pages 手动恢复，选 main 分支 /root)
- **GitHub 仓库**: github.com/Kokkotham/ash-world

## 技术栈决策

- **静态 HTML + vanilla JS**（用户明确拒绝 React/Vite/TypeScript）
- 数据驱动范式：`data/*.json` + `data/page-render.js` 渲染引擎
- 零 npm 依赖
- Python (python-docx) 用于 docx 批量转换脚本

## 已完成工作

### EW 规则书 Web 化 (T01-T06 完整流程)

**数据层** (`data/` 目录):
- `races.json` — 原有 4 个远古种族 + 新增 `players` 数组（16 个玩家种族，每条含属性/特质/描述）
- `professions.json` — 11 大类专修骨架，**已填充**: instinct (本能22条) + knowledge (知识12条)
  - 剩余 9 类待填充: communication/art/survival/special/profession_craft/weapon/combat/martial/arcane
- `divine-arts.json` — 2 神系骨架（父神系/母神系），内容待填充
- `story-rules.json` — 4 类故事运作骨架（combat/social/management/status_effects），内容待填充
- `glossary.json` — **已填充 62 条术语**（核心系统29+种族20+神术13）
- `chapters.json` — 完整章节树（ch0-ch5，含所有子节 + data_source 绑定）
- `links.json` — 25 条交叉关联
- `ew_raw/*.json` — 65 个 docx 原始提取文件
- `glossary_candidates.json` — 502 条术语候选清单

**渲染引擎**:
- `data/page-render.js` — 核心渲染引擎，新增 renderRules/renderGlossary/renderPlayerRaces/renderLevelTable
- `data/ash-data.js` — 数据加载器，已扩展加载 10 个 JSON 文件
- `data/keyword-tooltip.js` — 关键词悬浮提示（IIFE，扫描 `[data-keyword]` 属性）

**页面**:
- `pages/rules.html` — 规则书阅读器（缩略图导航 + 分章滚动 + 下一章按钮）
- `pages/character-sheet.html` — 角色创建页（EW 4属性 1d4 + 10点手动分配双模式，玻璃质感）
- `pages/glossary.html` — 术语表（从 glossary.json 动态渲染）
- `pages/races-ontology.html` — 种族页（远古种族 + 16 玩家种族）
- `pages/common.css` — 共享样式（+tooltip/+表格/+侧栏/+导航栏玻璃质感）
- `pages/rules.css` — 规则书阅读器专用样式

**工具**:
- `tools/docx2json.py` — Python docx 批量转换脚本
- `tools/build_glossary.py` — 术语表生成脚本
- `tools/requirements.txt` — python-docx>=1.1.0

**导航栏** — 已在 `index.html` 和 `pages/common.css` 同步更新:
- 局部下拉面板（`position:absolute`，紧贴触发项）
- 玻璃质感（`backdrop-filter: blur(20px)`）
- 三角指示器 + 外侧光晕 + hover 桥接
- 链接 hover 侧边金条动画 + 文字发光

## 待完成工作（优先级排序）

### P0 — 内容填充
1. **继续填专修数据** — professions.json 还有 9 个分类是骨架
   - 数据源：`data/ew_raw/` 下对应的原始 JSON
   - 格式参考：已填充的 instinct/knowledge 分类
2. **填神术数据** — divine-arts.json（父神系/母神系）
3. **填故事运作数据** — story-rules.json（战斗/交流/经营/状态词缀）

### P1 — 交互增强
4. **给页面内容加 data-keyword 标记** — 在 races-ontology.html / rules.html 的渲染文本中嵌入 `<span data-keyword="hp">` 等标记，让 tooltip 悬浮提示真正亮起来
5. **术语表补充** — 从 glossary_candidates.json 中继续筛选更多术语

### P2 — 修复
6. **数据截断** — races.json 中 木林精"远古精魄"、混血者"有家之人" 描述被截断，需从原始 JSON 补全
7. **version_status 清除** — 发版后统一改为"稳定"
8. **GitHub Pages 恢复** — 需手动操作（Settings→Pages→Source: Deploy from a branch, main, /root）

## 用户偏好

- 使用截图反馈（非代码问题，用户不写代码）
- 先出一个样例确认再批量铺开（避免返工）
- 回答偏好：直接、带对比表格、避免过多技术细节
- 所有新产出放 E:\workbuddy（但当前项目在 C:\ProgramData\...\）

## 文件索引

- 项目根: `C:/ProgramData/WorkBuddy/chromium-env/13613ht/WorkBuddy/2026-06-07-11-51-51`
- docx 源文件: `E:/Desktop/跑团文件/规则/EW/`
- Python 环境: `C:/ProgramData/WorkBuddy/chromium-env/13613ht/.workbuddy/binaries/python/envs/docx-extract/`
