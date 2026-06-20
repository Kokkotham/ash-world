#!/usr/bin/env python3
"""
修复规则书阅读体验问题：
1. 移除切换子章节/反选时的滚动到顶部代码
2. 为ch1等内容中的小标题添加样式检测
"""

import re

# 读取文件
with open('data/page-render.js', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 修复1：移除 switchSubSection 中的滚动代码（第395-396行）
# ============================================================
# 在 switchSubSection 函数中，main.innerHTML 之后有滚动代码
old_switchSubSection_scroll = """    main.innerHTML = contentHTML;
    main.scrollTop = 0;
    window.scrollTo({ top: 0, behavior: 'smooth' });"""

new_switchSubSection_no_scroll = """    main.innerHTML = contentHTML;
    // 不滚动到顶部，保持当前阅读位置"""

content = content.replace(old_switchSubSection_scroll, new_switchSubSection_no_scroll)

# ============================================================
# 修复2：移除 renderChapterPreface 中的滚动代码（第460行）
# ============================================================
old_renderPreface_scroll = """    main.innerHTML = contentHTML;
    main.scrollTop = 0;"""

new_renderPreface_no_scroll = """    main.innerHTML = contentHTML;
    // 不滚动到顶部，保持当前阅读位置"""

content = content.replace(old_renderPreface_scroll, new_renderPreface_no_scroll)

# ============================================================
# 修复3：增强小标题检测逻辑
# ============================================================
# 在 switchChapter 函数中，渲染 ch.content 时，添加对小标题的检测
# 原代码（约第266-274行）：
# if (/^[^\s]+（[ABCL]）$/.test(p.trim()) || /^[^\s]+\([ABCL]\)$/.test(p.trim())) {
#   contentHTML += '<h4 class="overview-subtitle">' + p + '</h4>';
# } else if (p.match(/^[A-Za-z]/)) {
#   contentHTML += '<h3 class="overview-title">' + p + '</h3>';
# } else {
#   contentHTML += '<p>' + p + '</p>';
# }

old_heading_detect = """      ch.content.forEach(function(p) {
        // 以 "XXX专修（X）" 格式的是小标题
        if (/^[^\s]+（[ABCL]）$/.test(p.trim()) || /^[^\s]+\([ABCL]\)$/.test(p.trim())) {
          contentHTML += '<h4 class="overview-subtitle">' + p + '</h4>';
        } else if (p.match(/^[A-Za-z]/)) {
          // 英文开头的行作为副标题
          contentHTML += '<h3 class="overview-title">' + p + '</h3>';
        } else {
          contentHTML += '<p>' + p + '</p>';
        }
      });"""

new_heading_detect = """      ch.content.forEach(function(p) {
        // 以 "XXX专修（X）" 格式的是小标题
        if (/^[^\s]+（[ABCL]）$/.test(p.trim()) || /^[^\s]+\([ABCL]\)$/.test(p.trim())) {
          contentHTML += '<h4 class="overview-subtitle">' + p + '</h4>';
        // 中文开头+冒号：属性名小标题（如"躯魄："、"核心躯魄："、"躯魄劣势限制："）
        } else if (/^[\u4e00-\u9fff].*[:：]/.test(p.trim())) {
          contentHTML += '<h4 class="content-subheading">' + p + '</h4>';
        } else if (p.match(/^[A-Za-z]/)) {
          // 英文开头的行作为副标题
          contentHTML += '<h3 class="overview-title">' + p + '</h3>';
        } else {
          contentHTML += '<p>' + p + '</p>';
        }
      });"""

content = content.replace(old_heading_detect, new_heading_detect)

# 同样修复 renderChapterPreface 函数中的小标题检测（约第446-452行）
old_preface_detect = """      ch.content.forEach(function(p) {
        if (/^[^\s]+（[ABCL]）$/.test(p.trim()) || /^[^\s]+\([ABCL]\)$/.test(p.trim())) {
          contentHTML += '<h4 class="overview-subtitle">' + p + '</h4>';
        } else if (p.match(/^[A-Za-z]/)) {
          contentHTML += '<h3 class="overview-title">' + p + '</h3>';
        } else {
          contentHTML += '<p>' + p + '</p>';
        }
      });"""

new_preface_detect = """      ch.content.forEach(function(p) {
        // 以 "XXX专修（X）" 格式的是小标题
        if (/^[^\s]+（[ABCL]）$/.test(p.trim()) || /^[^\s]+\([ABCL]\)$/.test(p.trim())) {
          contentHTML += '<h4 class="overview-subtitle">' + p + '</h4>';
        // 中文开头+冒号：属性名小标题（如"躯魄："、"核心躯魄："）
        } else if (/^[\u4e00-\u9fff].*[:：]/.test(p.trim())) {
          contentHTML += '<h4 class="content-subheading">' + p + '</h4>';
        } else if (p.match(/^[A-Za-z]/)) {
          // 英文开头的行作为副标题
          contentHTML += '<h3 class="overview-title">' + p + '</h3>';
        } else {
          contentHTML += '<p>' + p + '</p>';
        }
      });"""

content = content.replace(old_preface_detect, new_preface_detect)

# 同样修复 renderChapterContent 函数中的小标题检测（约第652-658行）
# 需要找到 isHeadingLine 和 isSubHeadingLine 函数
# 让我们添加对 "中文+冒号" 格式的检测到 isSubHeadingLine 函数

# 查找 isSubHeadingLine 函数定义
isSubHeadingLine_pattern = r'function isSubHeadingLine\(c\)\s*\{[^}]+\}'
isSubHeadingLine_match = re.search(isSubHeadingLine_pattern, content)

if isSubHeadingLine_match:
    old_isSubHeading = isSubHeadingLine_match.group(0)
    # 在函数中添加对 "中文+冒号" 格式的检测
    new_isSubHeading = old_isSubHeading.replace(
        'return ',
        '// 中文开头+冒号：属性名小标题\n  if (/^[\\u4e00-\\u9fff].*[:：]/.test(c.trim())) return true;\n  return '
    )
    content = content.replace(old_isSubHeading, new_isSubHeading)

# ============================================================
# 修复4：为子分类前言中的内容也添加小标题检测
# ============================================================
# 在 switchSubSection 函数中，渲染 targetSub.content 时（约第379-385行）
old_sub_content_render = """      targetSub.content.forEach(function(p) {
        if (/^[A-Za-z]/.test(p.trim()) && !/[\u4e00-\u9fff]/.test(p)) {
          contentHTML += '<h4 class="overview-title">' + p + '</h4>';
        } else {
          contentHTML += '<p>' + p + '</p>';
        }
      });"""

new_sub_content_render = """      targetSub.content.forEach(function(p) {
        // 英文开头且无中文：作为小标题
        if (/^[A-Za-z]/.test(p.trim()) && !/[\u4e00-\u9fff]/.test(p)) {
          contentHTML += '<h4 class="overview-title">' + p + '</h4>';
        // 中文开头+冒号：属性名小标题
        } else if (/^[\u4e00-\u9fff].*[:：]/.test(p.trim())) {
          contentHTML += '<h4 class="content-subheading">' + p + '</h4>';
        } else {
          contentHTML += '<p>' + p + '</p>';
        }
      });"""

content = content.replace(old_sub_content_render, new_sub_content_render)

# 写入文件
with open('data/page-render.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ page-render.js 修复完成")
print("  - 移除了 switchSubSection 中的滚动代码")
print("  - 移除了 renderChapterPreface 中的滚动代码")
print("  - 增强了小标题检测逻辑（支持'中文+冒号'格式）")
print("  - 为子分类前言中的内容添加了小标题检测")
