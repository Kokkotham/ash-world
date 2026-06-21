"""
 Comprehensive rules page UX overhaul:
 1. Chapter tabs → tiny "ChX" micro-labels (unobtrusive)
 2. Compact header: merge decorations, remove redundant spacing
 3. Match worldview typography: open flow layout (no card boxes), section-title style headings, better paragraph spacing
"""
import re

WORK = r'C:\ProgramData\WorkBuddy\chromium-env\13613ht\WorkBuddy\2026-06-07-11-51-51'

# ============================================================
# PART 1: rules.css — Complete overhaul
# ============================================================
css_path = f'{WORK}/pages/rules.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# --- 1A: Chapter tabs → tiny micro-labels ---
old_chapter_tab = """/* ---- 章节标签（替代原 .chapter-thumb）— 柔和标签风格 ---- */
.chapter-tab {
  flex-shrink: 0;
  padding: 6px 16px;
  border-radius: 20px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
  font-family: 'Noto Serif SC', serif;
  font-size: 0.84rem;
  color: var(--ash-text-muted);
  text-align: center;
  position: relative;
  overflow: hidden;
  min-height: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1px;
}

.chapter-tab::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 20px;
  background: var(--ash-gold);
  opacity: 0;
  transition: opacity 0.25s ease;
  pointer-events: none;
}

.chapter-tab:hover {
  color: var(--ash-text);
}
.chapter-tab:hover::before {
  opacity: 0.06;
}

/* 标签内部：章节号 + 标题 */
.chapter-tab .tab-num {
  font-family: 'Cinzel', serif;
  font-size: 0.6rem;
  color: var(--ash-gold-dim);
  letter-spacing: 0.1em;
  transition: color 0.25s ease;
  line-height: 1;
}

.chapter-tab .tab-title {
  font-size: 0.84rem;
  line-height: 1.2;
  transition: color 0.25s ease;
  font-weight: 400;
}

.chapter-tab:hover .tab-num,
.chapter-tab:hover .tab-title {
  color: var(--ash-gold);
}

/* 当前章节高亮 — 柔和金色填充 */
.chapter-tab.active {
  color: var(--ash-gold);
  background: transparent;
}
.chapter-tab.active::before {
  opacity: 0.12;
}
.chapter-tab.active .tab-num,
.chapter-tab.active .tab-title {
  color: var(--ash-gold);
  font-weight: 600;
}
/* active 下划线指示（轻柔） */
.chapter-tab.active::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 30%;
  right: 30%;
  height: 1.5px;
  background: var(--ash-gold);
  border-radius: 1px;
  opacity: 0.6;
}"""

new_chapter_tab = """/* ---- 章节标签 — 极简微标签（不重要的位置指示器） ---- */
.chapter-tab {
  flex-shrink: 0;
  padding: 3px 10px;
  border-radius: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  font-family: 'Cinzel', serif;
  font-size: 0.65rem;
  color: #4a4638;
  text-align: center;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 20px;
  line-height: 1;
}

/* 隐藏标题文字，只保留章节号 */
.chapter-tab .tab-title {
  display: none;
}

.chapter-tab .tab-num {
  font-family: 'Cinzel', serif;
  font-size: 0.62rem;
  color: inherit;
  letter-spacing: 0.08em;
  transition: color 0.2s ease;
}

.chapter-tab:hover {
  color: var(--ash-gold-dim);
}

/* 当前章节 — 微妙金色提示 */
.chapter-tab.active {
  color: var(--ash-gold);
  background: rgba(201, 168, 76, 0.08);
}
.chapter-tab.active .tab-num {
  font-weight: 600;
}*/

css = css.replace(old_chapter_tab, new_chapter_tab)

# Fix empty tab style
old_empty = """.chapter-tab.empty:hover {
  color: #666;
}"""

new_empty = """.chapter-tab.empty:hover {
  color: #777;
  background: transparent;
}"""

css = css.replace(old_empty, new_empty)

# --- 1B: Reader nav wrapper — more compact ---
old_nav_wrapper = """/* ---- 顶部导航包裹层（sticky） ---- */
.reader-nav-wrapper {
  position: sticky;
  top: 0;
  z-index: 100;
  background: linear-gradient(180deg, rgba(3, 5, 8, 0.99) 0%, rgba(3, 5, 8, 0.97) 100%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(201, 168, 76, 0.12);
}"""

new_nav_wrapper = """/* ---- 顶部导航包裹层（sticky，极简） ---- */
.reader-nav-wrapper {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(3, 5, 8, 0.98);
  border-bottom: 1px solid rgba(201, 168, 76, 0.06);
}"""

css = css.replace(old_nav_wrapper, new_nav_wrapper)

# --- 1C: Reader nav — smaller padding ---
old_reader_nav = """/* ---- 横向章节标签导航（始终横向） ---- */
.reader-nav {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding: 10px 16px;
  gap: 8px;
  /* 隐藏横向滚动条 */
  scrollbar-width: none;
  scroll-behavior: smooth;
}"""

new_reader_nav = """/* ---- 横向章节微标签导航（始终横向） ---- */
.reader-nav {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding: 6px 20px;
  gap: 2px;
  scrollbar-width: none;
  scroll-behavior: smooth;
}"""

css = css.replace(old_reader_nav, new_reader_nav)

# --- 1D: Sub-nav-bar — compact ---
old_subnav_visible = """.sub-nav-bar.visible {
  min-height: 36px;
  max-height: 80px;
  opacity: 1;
  padding: 8px 40px;       /* 左右留出箭头空间 */"""

new_subnav_visible = """.sub-nav-bar.visible {
  min-height: 32px;
  max-height: 72px;
  opacity: 1;
  padding: 6px 40px;       /* 左右留出箭头空间 */"""

css = css.replace(old_subnav_visible, new_subnav_visible)

# --- 1E: reader-main — less padding ---
old_reader_main = """/* ---- 内容面板（速查模式：单章节展示，内容区可滚动） ---- */
.reader-main {
  padding: 24px 36px 80px;
  overflow-y: auto;
  flex: 1;
  /* 不限制最大高度：让内容自然撑开，超出时自身滚动 */
}"""

new_reader_main = """/* ---- 内容面板（开放流式排版，对齐世界观页风格） ---- */
.reader-main {
  padding: 16px 40px 60px;
  overflow-y: visible;
  flex: 1;
}"""

css = css.replace(old_reader_main, new_reader_main)

# --- 1F: reader-chapter → remove card styling, open flow like worldview ---
old_reader_chapter = """/* ---- 章节面板 ---- */
.reader-chapter {
  padding: 32px 36px;
  background: rgba(10, 14, 20, 0.6);
  border: 1px solid rgba(201, 168, 76, 0.1);
  border-radius: 8px;
  position: relative;
  min-height: 200px;
}

/* 章节顶部玻璃微光 */
.reader-chapter::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(201, 168, 76, 0.15), transparent);
  opacity: 0.6;
  pointer-events: none;
}"""

new_reader_chapter = """/* ---- 章节面板 — 开放流式（无卡片框，对齐世界观页） ---- */
.reader-chapter {
  padding: 8px 0 0;
  background: transparent;
  border: none;
  border-radius: 0;
  position: relative;
  min-height: auto;
}

/* 移除玻璃微光 */
.reader-chapter::before {
  display: none;
}"""

css = css.replace(old_reader_chapter, new_reader_chapter)

# --- 1G: chapter-heading → left-align section-title style (like worldview) ---
old_chapter_heading = """/* 章节标题 */
.reader-chapter .chapter-heading {
  text-align: center;
  margin-bottom: 28px;
}

.reader-chapter .chapter-heading .chapter-num {
  font-family: 'Cinzel', serif;
  font-size: 0.85rem;
  color: var(--ash-gold-dim);
  letter-spacing: 0.15em;
  margin-bottom: 6px;
  display: block;
}

.reader-chapter .chapter-heading h2 {
  font-family: 'Cinzel', serif;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--ash-gold);
  letter-spacing: 0.12em;
  margin: 0 0 12px 0;
  border-bottom: none;
}

.reader-chapter .chapter-heading .heading-divider {
  width: 80px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--ash-gold-dim), transparent);
  margin: 0 auto;
}"""

new_chapter_heading = """/* 章节标题 — 对齐世界观 .section-title 风格（左对齐 + 金色底线） */
.reader-chapter .chapter-heading {
  text-align: left;
  margin: 8px 0 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(201, 168, 76, 0.15);
}

.reader-chapter .chapter-heading .chapter-num {
  font-family: 'Cinzel', serif;
  font-size: 0.72rem;
  color: var(--ash-gold-dim);
  letter-spacing: 0.12em;
  margin-bottom: 2px;
  display: block;
}

.reader-chapter .chapter-heading h2 {
  font-family: 'Cinzel', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--ash-gold);
  letter-spacing: 0.1em;
  margin: 0;
  border-bottom: none;
}

/* 隐藏居中分隔线 — 已由 border-bottom 替代 */
.reader-chapter .chapter-heading .heading-divider {
  display: none;
}"""

css = css.replace(old_chapter_heading, new_chapter_heading)

# --- 1H: chapter-body → match worldview .text-block typography ---
old_chapter_body = """/* 章节内容 */
.reader-chapter .chapter-body {
  color: var(--ash-text);
  line-height: 1.85;
  font-size: 0.93rem;
}

.reader-chapter .chapter-body p {
  margin-bottom: 14px;
}

.reader-chapter .chapter-body h3 {
  color: var(--ash-gold);
  font-family: 'Cinzel', serif;
  font-size: 1.1rem;
  margin: 24px 0 12px;
  letter-spacing: 0.08em;
}

.reader-chapter .chapter-body h4 {
  color: var(--ash-gold-dim);
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  margin: 18px 0 8px;
}"""

new_chapter_body = """/* 章节内容 — 对齐 worldview .text-block 排版 */
.reader-chapter .chapter-body {
  color: var(--ash-text);
  line-height: 1.9;
  font-size: 0.95rem;
}

.reader-chapter .chapter-body p {
  margin-bottom: 18px;
  text-align: justify;
}

.reader-chapter .chapter-body h3 {
  color: var(--ash-gold);
  font-family: 'Cinzel', serif;
  font-size: 1.15rem;
  margin: 32px 0 14px;
  letter-spacing: 0.08em;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(201, 168, 76, 0.1);
}

.reader-chapter .chapter-body h4 {
  color: var(--ash-gold-dim);
  font-family: 'Noto Serif SC', serif;
  font-size: 1rem;
  margin: 22px 0 10px;
}"""

css = css.replace(old_chapter_body, new_chapter_body)

# --- 1I: Sub-section divider — lighter ---
old_sub_section = """/* 子章节分隔 */
.reader-chapter .sub-section {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid rgba(201, 168, 76, 0.08);
}

.reader-chapter .sub-section:first-child {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}"""

new_sub_section = """/* 子章节分隔 — 更轻 */
.reader-chapter .sub-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(201, 168, 76, 0.06);
}

.reader-chapter .sub-section:first-child {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}"""

css = css.replace(old_sub_section, new_sub_section)

# --- 1J: Overview/preface panels — lighter card style ---
old_overview = """/* ---- 章节概述区域（大章节概览模式） ---- */
.chapter-overview {
  margin-bottom: 32px;
  padding: 24px 28px;
  background: rgba(10, 14, 20, 0.5);
  border: 1px solid rgba(201, 168, 76, 0.08);
  border-radius: 8px;
  border-left: 3px solid rgba(201, 168, 76, 0.3);
}"""

new_overview = """/* ---- 章节概述区域 — 轻量化面板 ---- */
.chapter-overview {
  margin-bottom: 28px;
  padding: 20px 24px;
  background: rgba(10, 14, 20, 0.35);
  border: none;
  border-left: 3px solid rgba(201, 168, 76, 0.2);
  border-radius: 0;
}"""

css = css.replace(old_overview, new_overview)

old_sub_preface = """/* ---- 子分类前言区域（点击子pill后显示） ---- */
.sub-section-preface {
  margin-bottom: 24px;
  padding: 20px 24px;
  background: rgba(10, 14, 20, 0.45);
  border: 1px solid rgba(201, 168, 76, 0.06);
  border-radius: 8px;
  border-left: 3px solid rgba(201, 168, 76, 0.2);
}"""

new_sub_preface = """/* ---- 子分类前言区域 — 轻量化面板 ---- */
.sub-section-preface {
  margin-bottom: 24px;
  padding: 16px 24px;
  background: rgba(10, 14, 20, 0.3);
  border: none;
  border-left: 3px solid rgba(201, 168, 76, 0.15);
  border-radius: 0;
}"""

css = css.replace(old_sub_preface, new_sub_preface)

# --- 1K: ability-main-title — left align to match new heading style ---
old_ability_main_title = """/* 技能主标题（选中技能时替代章节标题位置） */
.ability-main-title {
  text-align: center;
  padding: 24px 20px 12px;
}
.ability-main-title h2 {
  font-family: 'Cinzel', serif;
  font-size: 1.6rem;
  color: var(--ash-gold);
  margin: 0 0 6px;
  letter-spacing: 0.08em;
  font-weight: 700;
}
.ability-main-title .detail-eb {
  font-size: 0.9rem;
  color: var(--ash-gold-dim);
  font-family: 'Noto Serif SC', serif;
}
.ability-main-title .heading-divider {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--ash-gold), transparent);
  margin: 10px auto 0;
}"""

new_ability_main_title = """/* 技能主标题（选中技能时）— 对齐 section-title 风格 */
.ability-main-title {
  text-align: left;
  padding: 8px 0 12px;
  margin-bottom: 4px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(201, 168, 76, 0.15);
}
.ability-main-title h2 {
  font-family: 'Cinzel', serif;
  font-size: 1.4rem;
  color: var(--ash-gold);
  margin: 0;
  letter-spacing: 0.1em;
  font-weight: 700;
}
.ability-main-title .detail-eb {
  font-size: 0.82rem;
  color: var(--ash-gold-dim);
  font-family: 'Noto Serif SC', serif;
  margin-top: 2px;
  display: block;
}
/* 隐藏旧居中分隔线 */
.ability-main-title .heading-divider {
  display: none;
}"""

css = css.replace(old_ability_main_title, new_ability_main_title)

# --- 1L: detail-desc — better typography ---
old_detail_desc = """.ability-detail .detail-desc {
  color: var(--ash-text);
  line-height: 1.9;
  font-size: 0.92rem;
  margin-bottom: 16px;
}

.ability-detail .detail-desc p {
  margin-bottom: 12px;
  text-indent: 0;
}"""

new_detail_desc = """.ability-detail .detail-desc {
  color: var(--ash-text);
  line-height: 1.9;
  font-size: 0.95rem;
  margin-bottom: 20px;
}

.ability-detail .detail-desc p {
  margin-bottom: 16px;
  text-indent: 0;
  text-align: justify;
}"""

css = css.replace(old_detail_desc, new_detail_desc)

# --- 1M: race-detail — open style ---
old_race_detail = """/* 种族详情样式 */
.race-detail {
  padding: 20px;
}

.race-detail .detail-header h2 {
  font-size: 1.4rem;
  color: var(--ash-gold);
  margin-bottom: 12px;
}"""

new_race_detail = """/* 种族详情 — 开放流式 */
.race-detail {
  padding: 8px 0 0;
}

.race-detail .detail-header h2 {
  font-size: 1.4rem;
  color: var(--ash-gold);
  margin: 0 0 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(201, 168, 76, 0.12);
}"""

css = css.replace(old_race_detail, new_race_detail)

old_race_body = """.race-detail-body {
  margin-top: 16px;
  line-height: 1.8;
}

.race-detail-body p {
  margin-bottom: 10px;
  text-align: justify;
}"""

new_race_body = """.race-detail-body {
  margin-top: 12px;
  line-height: 1.9;
}

.race-detail-body p {
  margin-bottom: 16px;
  text-align: justify;
}"""

css = css.replace(old_race_body, new_race_body)

# --- 1N: Content subheading — match new style ---
old_subheading = """/* ---- 内容小标题样式（中文+冒号格式） ---- */
.content-subheading {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ash-gold);
  margin: 18px 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(201, 168, 76, 0.15);
  letter-spacing: 0.05em;
}"""

new_subheading = """/* ---- 内容小标题样式（中文+冒号格式） ---- */
.content-subheading {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ash-gold);
  margin: 22px 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(201, 168, 76, 0.12);
  letter-spacing: 0.05em;
}"""

css = css.replace(old_subheading, new_subheading)

# --- 1O: Responsive — update mobile styles to match new design ---
old_mobile_768 = """/* 移动端（≤768px）：导航更紧凑，阅读区收窄 */
@media (max-width: 768px) {
  .reader-nav-wrapper {
    top: 0;
  }

  .reader-nav {
    padding: 8px 10px;
    gap: 6px;
  }

  .chapter-tab {
    padding: 7px 14px;
    min-height: 32px;
    font-size: 0.78rem;
  }

  .chapter-tab .tab-num {
    font-size: 0.58rem;
  }

  .chapter-tab .tab-title {
    font-size: 0.78rem;
  }"""

new_mobile_768 = """/* 移动端（≤768px）：导航更紧凑，阅读区收窄 */
@media (max-width: 768px) {
  .reader-nav-wrapper {
    top: 0;
  }

  .reader-nav {
    padding: 5px 14px;
    gap: 2px;
  }

  .chapter-tab {
    padding: 2px 7px;
    min-height: 18px;
    font-size: 0.6rem;
  }

  .chapter-tab .tab-num {
    font-size: 0.55rem;
  }

  .chapter-tab .tab-title {
    display: none;
  }"""

css = css.replace(old_mobile_768, new_mobile_768)

# Update mobile chapter styles
old_mobile_chapter = """  .reader-chapter {
    padding: 18px 14px;
    margin-bottom: 24px;
    border-radius: 6px;
  }

  .reader-chapter .chapter-heading h2 {
    font-size: 1.25rem;
    letter-spacing: 0.08em;
  }

  .reader-chapter .chapter-body {
    font-size: 0.9rem;
    line-height: 1.88;
  }"""

new_mobile_chapter = """  .reader-chapter {
    padding: 4px 0 0;
    margin-bottom: 0;
    border-radius: 0;
  }

  .reader-chapter .chapter-heading h2 {
    font-size: 1.2rem;
    letter-spacing: 0.08em;
  }

  .reader-chapter .chapter-body {
    font-size: 0.92rem;
    line-height: 1.9;
  }"""

css = css.replace(old_mobile_chapter, new_mobile_chapter)

# Update tiny mobile styles
old_tiny_mobile = """/* 极小屏（≤480px）导航项更紧凑 */
@media (max-width: 480px) {
  .reader-nav {
    padding: 6px 8px;
    gap: 5px;
  }

  .chapter-tab {
    padding: 6px 10px;
    font-size: 0.72rem;
    min-height: 28px;
  }

  .chapter-tab .tab-num {
    font-size: 0.55rem;
  }

  .chapter-tab .tab-title {
    font-size: 0.72rem;
  }

  .sub-pill {
    padding: 2px 8px;
    font-size: 0.65rem;
  }

  .reader-chapter {
    padding: 14px 10px;
    border-radius: 4px;
  }

  .reader-chapter .chapter-heading h2 {
    font-size: 1.1rem;
  }

  .reader-chapter .chapter-body {
    font-size: 0.88rem;
  }

  .reader-main {
    padding: 12px 10px 40px;
  }"""

new_tiny_mobile = """/* 极小屏（≤480px）导航项更紧凑 */
@media (max-width: 480px) {
  .reader-nav {
    padding: 4px 10px;
    gap: 2px;
  }

  .chapter-tab {
    padding: 2px 6px;
    font-size: 0.55rem;
    min-height: 16px;
  }

  .chapter-tab .tab-num {
    font-size: 0.5rem;
  }

  .chapter-tab .tab-title {
    display: none;
  }

  .sub-pill {
    padding: 2px 8px;
    font-size: 0.65rem;
  }

  .reader-chapter {
    padding: 2px 0 0;
    border-radius: 0;
  }

  .reader-chapter .chapter-heading h2 {
    font-size: 1.05rem;
  }

  .reader-chapter .chapter-body {
    font-size: 0.9rem;
  }

  .reader-main {
    padding: 10px 12px 36px;
  }"""

css = css.replace(old_tiny_mobile, new_tiny_mobile)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("✅ rules.css updated")

# ============================================================
# PART 2: rules.html — minimize page-header
# ============================================================
html_path = f'{WORK}/pages/rules.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the big page-header with a minimal version
old_header = """    <header class="page-header">
        <h1>游戏规则</h1>
        <p class="subtitle">RULES &amp; SYSTEM</p>
        <div class="divider"></div>
    </header>"""

new_header = """    <header class="page-header page-header--compact">
        <h1>游戏规则</h1>
        <p class="subtitle">RULES &amp; SYSTEM</p>
        <div class="divider"></div>
    </header>"""

html = html.replace(old_header, new_header)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ rules.html updated")

# ============================================================
# PART 3: common.css — add compact page-header override for rules
# ============================================================
common_path = f'{WORK}/pages/common.css'
with open(common_path, 'r', encoding='utf-8') as f:
    common = f.read()

# Add compact page-header style after the regular page-header rule
compact_header_css = """
/* 规则书页面：紧凑型页面标题（因为已有章节导航，不需要大标题占空间） */
.page-header--compact {
    padding: 24px 20px 12px;
}
.page-header--compact h1 {
    font-size: 1.3rem;
    letter-spacing: 0.15em;
    text-shadow: none;
    margin-bottom: 2px;
}
.page-header--compact .subtitle {
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    opacity: 0.5;
}
.page-header--compact .divider {
    width: 60px;
    height: 1px;
    margin: 8px auto 0;
    opacity: 0.4;
}
"""

# Insert before /* 内容容器 */
if '.page-header--compact' not in common:
    common = common.replace('/* 内容容器 */', compact_header_css + '/* 内容容器 */')
    with open(common_path, 'w', encoding='utf-8') as f:
        f.write(common)
    print("✅ common.css updated (added compact header)")
else:
    print("⏭️ compact header already exists in common.css")

print("\n🎉 All files updated successfully!")
