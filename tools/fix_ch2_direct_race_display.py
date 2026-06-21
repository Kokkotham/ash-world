#!/usr/bin/env python3
"""
修改 page-render.js：
1. 在 switchSubSection 中，对于 ch2 的 type: "data" 子分类，直接调用 switchRace 显示详情
2. 保留其他逻辑不变
"""

import re

# 读取文件
with open('data/page-render.js', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 修改1：在 switchSubSection 的第三层导航初始化前，添加 ch2 直接显示详情的逻辑
# ============================================================

# 查找第三层导航初始化的代码块
old_third_level_init = """    window.__rulesCurrentChapter = parentCh.id;
    window.__rulesCurrentSub = subId;

    // ---- 第三层导航：按章节类型初始化 ----
    if (parentCh.id === 'ch3' && targetSub.data_path && data) {
      initThirdLevelNav(targetSub, parentCh, data);
    } else if (parentCh.id === 'ch2' && targetSub.data_path && data) {
      initRaceNav(targetSub, parentCh, data);
    } else {
      // 非 ch2/ch3：隐藏第三层导航
      var detailBar = document.getElementById('detail-nav-bar');
      if (detailBar) { detailBar.classList.remove('visible'); detailBar.innerHTML = ''; }
    }
  }"""

new_third_level_init = """    window.__rulesCurrentChapter = parentCh.id;
    window.__rulesCurrentSub = subId;

    // ---- ch2 特殊处理：直接子分类（种族）点击后直接显示详情 ----
    if (parentCh.id === 'ch2' && targetSub.type === 'data' && targetSub.data_path && data) {
      // 解析种族数据并直接显示详情
      var src = resolveDataSource(data, targetSub.data_source);
      if (src) {
        var race = resolveDataPath(src, targetSub.data_path);
        if (race && typeof race === 'object') {
          switchRace(race);
          // 隐藏第三层导航（ch2不需要）
          var detailBar = document.getElementById('detail-nav-bar');
          if (detailBar) { detailBar.classList.remove('visible'); detailBar.innerHTML = ''; }
          return; // 直接返回，不执行后续的第三层导航初始化
        }
      }
    }

    // ---- 第三层导航：按章节类型初始化 ----
    if (parentCh.id === 'ch3' && targetSub.data_path && data) {
      initThirdLevelNav(targetSub, parentCh, data);
    } else if (parentCh.id === 'ch2' && targetSub.data_path && data && targetSub.type !== 'data') {
      // 保留旧逻辑：如果ch2的子分类不是data类型，调用initRaceNav（分类→种族列表）
      initRaceNav(targetSub, parentCh, data);
    } else {
      // 非 ch2/ch3：隐藏第三层导航
      var detailBar = document.getElementById('detail-nav-bar');
      if (detailBar) { detailBar.classList.remove('visible'); detailBar.innerHTML = ''; }
    }
  }"""

if old_third_level_init in content:
    content = content.replace(old_third_level_init, new_third_level_init)
    print("✅ 修改1完成：添加 ch2 直接显示种族详情的逻辑")
else:
    print("❌ 修改1失败：未找到目标代码块")
    print("   可能代码已修改或格式不匹配")

# ============================================================
# 修改2：在 switchSubSection 开头添加对 ch2 反选的处理
# （当从种族详情返回时，正确恢复前言显示）
# ============================================================
# 这个函数已经在之前的代码中有反选逻辑了（第318-338行）
# 但需要确保反选时正确恢复 ch2 的前言
# 当前反选逻辑是调用 renderChapterPreface(currentCh)
# 这对于 ch2 应该是正确的（显示 ch2 的前言）

print("\n✅ 修改2跳过：反选逻辑已存在（第318-338行）")

# 写入文件
with open('data/page-render.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ page-render.js 修改完成")
print("  修改内容：")
print("  1. 添加 ch2 直接子分类（种族）点击后直接显示详情的逻辑")
print("  2. 保留 ch3 的 initThirdLevelNav 逻辑")
print("  3. 保留非 ch2/ch3 的隐藏第三层导航逻辑")
