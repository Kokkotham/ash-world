"""
完整重建第4章（神术）——从 ew_raw 中提取全部内容，建立本体论层级。
用法：
  cd /path/to/project
  python tools/build_ch4_full.py

本体论结构（扁平化2级，适配渲染器）：
  第4章：神术
  ├── content: 总览文字（来自"4神术.json"）
  ├── sub_sections[0]: 4.1 纳露安人类神术（总览）
  │   └─ content: 神术概述 + 神谱系介绍等
  ├── sub_sections[1]: 4.1.1 父神系
  │   └─ content: 教条 + 神术详情 + 表格
  ├── sub_sections[2]: 4.1.2 母神系
  ├── sub_sections[3]: 4.1.3 深渊系
  ├── sub_sections[4]: 4.1.4 诸神系
  ├── sub_sections[5]: 4.2 精灵神术（总览）
  ├── sub_sections[6]: 4.2.1 太阳神系
  ├── sub_sections[7]: 4.2.2 月亮神系
  ├── sub_sections[8]: 4.3 荒野图腾神术（总览）
  ├── sub_sections[9]: 4.3.1 荒野神
  └── sub_sections[10]: 4.3.2 中立荒野神
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
EW_RAW_DIR = os.path.join(DATA_DIR, "ew_raw")


# ── 工具函数 ──────────────────────────────────────────────────────────────

def load_ew_raw(filename):
    path = os.path.join(EW_RAW_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_ew_files(pattern):
    """在 ew_raw 目录中找到所有匹配 pattern 的文件（忽略空格差异）"""
    results = []
    for f in sorted(os.listdir(EW_RAW_DIR)):
        if not f.endswith(".json"):
            continue
        if pattern.replace(" ", "") in f.replace(" ", ""):
            results.append(f)
    return results


def slugify(name):
    s = re.sub(r'[（(][^)）]*[)）]', '', name)
    s = re.sub(r'[（(].*?[)）]', '', s)
    s = s.strip()[:25]
    s = re.sub(r'\s+', '_', s)
    # 去掉中文括号等
    s = re.sub(r'[^\w\u4e00-\u9fff_-]', '', s)
    return s or "untitled"


def table_to_html(table):
    """
    智能表格渲染器：
    - 能力条目表（≥5列 + 合并单元格）→ 渲染为语义化 .ability-card
    - 等级进度表（2列，>10行）→ 渲染为双栏 .level-table
    - 目录式小表（2列，≤5行）→ 渲染为 .toc-table  
    - 其他普通表 → 渲染为 .ew-table
    """
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    if not headers or not rows:
        return ""

    num_cols = len(headers)
    num_rows = len(rows)

    # ── Case A: 能力条目表格（神术/技能等）──
    # 特征：≥5列，数据行中每行所有单元格值相同（原始docx合并单元格）
    if num_cols >= 5 and num_rows >= 2:
        is_ability = True
        for r in rows:
            vals = list(r.values())
            # 允许 header 行有不同值（那是元信息），但数据行必须全相同或接近全同
            unique_count = len(set(vals))
            if unique_count > 2:  # 超过2个不同值 → 不是能力表
                is_ability = False
                break
        if is_ability:
            return _render_ability_card(headers, rows)

    # ── Case B: 等级进度表（如 1P-100P 光化点）──
    # 特征：正好2列，较多行（通常>8），第一列是数字/等级格式
    if num_cols == 2 and num_rows >= 6:
        first_col_vals = [list(r.values())[0] for r in rows]
        if _looks_like_levels(first_col_vals):
            return _render_level_table(headers, rows)

    # ── Case C: 目录式小表（编号+名称）──
    if num_cols == 2 and num_rows <= 5:
        return _render_toc_table(headers, rows)

    # ── Case D: 去重后的普通表格 ──
    return _render_regular_table(headers, rows)


def _looks_like_levels(values):
    """判断第一列值是否像等级/段位（数字+p/P 或纯数字递增）"""
    import re
    for v in values[:min(5, len(values))]:
        s = str(v).strip()
        if re.match(r'^\d+[pP]?$', s) or re.match(r'^\d+$', s):
            continue
        # 也允许 "1P" 格式
        if re.match(r'^\d+[pP]$', s):
            continue
        return False
    return True


# ══════════════════════════════════════════════════════════
#  能力条目卡片渲染（处理合并单元格问题）
# ══════════════════════════════════════════════════════════

def _render_ability_card(headers, rows):
    """
    将 docx 中的"能力条目"合并单元格表格渲染为语义化 HTML 卡片。
    
    原始结构（docx 合并单元格）：
    | 能力名   | 类型     | MP | 前置X | 连接Y | 最大等级N |
    | （描述文字，跨所有列合并）                            |
    | 强化增益 | 强化增益 | ..| ..    | ..    | ..         |
    | 效果值   | 效果值   | ..| ..    | ..    | ..         |
    
    提取后 headers 是各列文字（可能有重复），rows 的每个 cell 都有相同内容。
    我们要去重并重新组织为卡片布局。
    """
    num_cols = len(headers)

    # 解析 header 行 — 提取能力元信息
    # 通常结构：[类型名, MP消耗, "前置连接", 前置值, "最大强化等级", 等级值]
    # 或者更复杂：[祝福神术, 0MP, 前置连接, 日蚀, 最大强化等级, 无]
    ability_type = headers[0].strip() if headers[0] else ""
    ability_cost = headers[1].strip() if num_cols > 1 else ""
    
    # 提取前置条件（col 2-3）和等级（col 4-5）
    prereq_parts = []
    level_parts = []
    for i in range(2, num_cols):
        val = headers[i].strip()
        if val in ("前置连接", "前置", ""):
            continue
        if i <= 3 or "前置" in headers[i-1] if i > 0 else False:
            prereq_parts.append(val)
        else:
            level_parts.append(val)
    
    prereq = " ".join(prereq_parts).strip()
    max_level = " ".join(level_parts).strip()

    # 如果没有明确分出前置和等级，用 fallback
    if not prereq and num_cols >= 4:
        prereq = f"{headers[2]} {headers[3]}".strip()
    if not max_level and num_cols >= 6:
        max_level = f"{headers[4]} {headers[5]}".strip()

    # 提取描述文字（第0行去重）
    desc = _dedup_row_value(rows[0]) if rows else ""
    
    # 提取强化增益（后续行）
    enhancement_lines = []
    for r in rows[1:]:
        label = _dedup_row_value(r)
        if label and label != desc:  # 避免和描述重复
            enhancement_lines.append(label)

    # 构建 HTML
    html = '<div class="ability-card">'
    # 元信息栏
    html += '<div class="ability-meta">'
    html += f'<span class="ab-type">{_esc(ability_type)}</span>'
    if ability_cost:
        html += f'<span class="ab-cost">{_esc(ability_cost)}</span>'
    if prereq:
        html += f'<span class="ab-prereq">前置 {_esc(prereq)}</span>'
    if max_level:
        html += f'<span class="ab-level">{_esc(max_level)}</span>'
    html += '</div>'  # .ability-meta
    
    # 描述
    if desc:
        html += f'<div class="ability-desc">{_esc(desc)}</div>'
    
    # 强化增益
    if enhancement_lines:
        html += '<div class="ability-enhancement">'
        for line in enhancement_lines:
            html += f'<div class="enh-line">{_esc(line)}</div>'
        html += '</div>'  # .ability-enhancement
    
    html += '</div>'  # .ability-card
    return html


def _dedup_row_value(row):
    """从可能因合并单元格而重复的行数据中去重，取唯一值"""
    values = list(row.values())
    unique = list(dict.fromkeys(values))  # 保重去序
    # 返回最长的那个值（通常是完整的描述文本）
    if len(unique) == 1:
        return unique[0]
    # 如果有多个不同值，返回最长非空值
    best = max((v for v in unique if v.strip()), key=len, default="")
    return best


def _esc(text):
    """HTML 转义"""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


# ══════════════════════════════════════════════════════════
#  等级进度表（双栏显示）
# ══════════════════════════════════════════════════════════

def _render_level_table(headers, rows):
    """渲染等级进度表（1P-100P 等），使用 CSS 双栏"""
    html = '<table class="ew-table ew-level-progress"><thead><tr>'
    for h in headers:
        html += f"<th>{_esc(h)}</th>"
    html += "</tr></thead><tbody>"
    for row in rows:
        html += "<tr>"
        for h in headers:
            v = row.get(h, "")
            html += f"<td>{_esc(v)}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html


# ══════════════════════════════════════════════════════════
#  目录式小表
# ══════════════════════════════════════════════════════════

def _render_toc_table(headers, rows):
    """渲染小型目录/索引表（编号 + 名称）"""
    html = '<table class="ew-table ew-toc-table"><tbody>'
    for row in rows:
        vals = list(row.values())
        html += f"<tr><td>{_esc(str(vals[0]))}</td><td><strong>{_esc(str(vals[1]))}</strong></td></tr>"
    html += "</tbody></table>"
    return html


# ══════════════════════════════════════════════════════════
#  去重普通表格
# ══════════════════════════════════════════════════════════

def _render_regular_table(headers, rows):
    """渲染普通表格（带基本的行内去重：同行相同值只输出一次）"""
    html = '<table class="ew-table"><thead><tr>'
    for h in headers:
        html += f"<th>{_esc(h)}</th>"
    html += "</tr></thead><tbody>"
    for row in rows:
        html += "<tr>"
        prev_val = None
        colspan_count = 1
        col_values = []
        for j, h in enumerate(headers):
            v = row.get(h, "")
            col_values.append(v)
        
        # 对连续相同的值做去重（colspan）
        i = 0
        while i < len(col_values):
            v = col_values[i]
            span = 1
            while i + span < len(col_values) and col_values[i + span] == v:
                span += 1
            if span > 1:
                html += f"<td colspan=\"{span}\">{_esc(v)}</td>"
            else:
                html += f"<td>{_esc(v)}</td>"
            i += span
        html += "</tr>"
    html += "</tbody></table>"
    return html


def extract_content(raw_data):
    """从 ew_raw 数据中提取内容列表（段落 + HTML 表格）"""
    content = []
    paras = [p for p in raw_data.get("paragraphs", []) if p.strip()]
    content.extend(paras)
    for t in raw_data.get("tables", []):
        html = table_to_html(t)
        if html:
            content.append(html)
    return content


def extract_title(content_list):
    """取第一个非空段作为标题"""
    for p in content_list:
        s = p.strip()
        if len(s) > 0 and len(s) < 80 and not s.startswith("<"):
            return s
    return ""


# ── 第4章 本体论配置（扁平化2级） ───────────────────────────────────────

CH4_ONTOLOGY = {
    "id": "ch4",
    "title": "神术",
    "number": "第4章",
    "type": "text",
    "intro_file_pattern": "4神术",
    # 扁平化：overview 和具体神系全部作为一级 sub_sections
    "flat_items": [
        # 4.1 纳露安人类神术（总览）
        {"pattern": "4.1纳露安人类神术", "display": "纳露安人类神术（总览）"},
        # 4.1.x 各神系
        {"pattern": "4.1.1纳露安人类父神系", "display": "父神系（德米乌尔格斯）"},
        {"pattern": "4.1.2纳露安人类母神系", "display": "母神系（克罗诺斯西拉）"},
        {"pattern": "4.1.3纳露安人类深渊系", "display": "深渊系"},
        {"pattern": "4.1.4纳露安人类诸神系", "display": "诸神系"},
        # 4.2 精灵神术
        {"pattern": "4.2精灵神术", "display": "精灵神术（总览）"},
        {"pattern": "4.2.1精灵太阳神系", "display": "太阳神系（艾恩）"},
        {"pattern": "4.2.2精灵月亮神系", "display": "月亮神系（艾莉娅提雅）"},
        # 4.3 荒野图腾神术
        {"pattern": "4.3荒野图腾神术", "display": "荒野图腾神术（总览）"},
        {"pattern": "4.3.1纳露安人类荒野神", "display": "荒野神"},
        {"pattern": "4.3.2中立荒野神", "display": "中立荒野神"},
    ],
}


def build_ch4():
    print("=== 构建第4章 神术（完整版 - 扁平化2级） ===\n")

    # 1. 章节总览内容
    intro_files = find_ew_files(CH4_ONTOLOGY["intro_file_pattern"])
    intro_content = []
    if intro_files:
        raw_intro = load_ew_raw(intro_files[0])
        if raw_intro:
            intro_content = extract_content(raw_intro)
            print(f"总览: {len(intro_content)} 段内容 (来自 {intro_files[0]})")

    # 2. 扁平化的子章节列表
    sub_sections = []
    for item_cfg in CH4_ONTOLOGY["flat_items"]:
        pattern = item_cfg["pattern"]
        display_name = item_cfg["display"]
        item_files = find_ew_files(pattern)

        if not item_files:
            print(f"  ⚠ 未找到: {pattern}")
            continue

        raw_item = load_ew_raw(item_files[0])
        if not raw_item:
            continue

        item_content = extract_content(raw_item)
        ss_id = f"ch4_{slugify(display_name)}"
        sub_sections.append({
            "id": ss_id,
            "title": display_name,
            "type": "text",
            "content": item_content,
            "sub_sections": [],  # 不再嵌套
        })

        html_count = sum(1 for c in item_content if c.startswith("<"))
        text_count = len(item_content) - html_count
        print(f"  OK {display_name}: 文本{text_count}段 + 表格{html_count}张 ({item_files[0]})")

    return {
        "id": CH4_ONTOLOGY["id"],
        "title": CH4_ONTOLOGY["title"],
        "number": CH4_ONTOLOGY["number"],
        "type": CH4_ONTOLOGY["type"],
        "data_source": None,
        "content": intro_content,
        "sub_sections": sub_sections,
    }


# ─── 主流程 ───────────────────────────────────────────────────────────────

def main():
    ch_path = os.path.join(DATA_DIR, "chapters.json")
    if not os.path.exists(ch_path):
        print(f"ERROR: {ch_path} 不存在，请先运行 build_all_data.py")
        sys.exit(1)

    with open(ch_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chapters = data.get("chapters", [])

    # 确保 ch4 存在
    while len(chapters) < 5:
        idx = len(chapters)
        ch = {"id": f"ch{idx}", "title": "", "number": f"第{idx}章",
               "type": "text", "data_source": None, "content": [], "sub_sections": []}
        chapters.append(ch)

    # 构建 ch4
    ch4 = build_ch4()

    # 统计
    total_content = len(ch4["content"])
    total_ss = len(ch4["sub_sections"])
    total_paras = total_content + sum(len(s.get("content", [])) for s in ch4["sub_sections"])

    chapters[4] = ch4
    data["chapters"] = chapters

    with open(ch_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"=== 第4章重建完成（扁平化2级） ===")
    print(f"  总览内容: {total_content} 段")
    print(f"  子章节: {total_ss} 个（全部扁平化）")
    print(f"  总段落数: ~{total_paras} 段")
    print(f"  输出文件: {ch_path}")


if __name__ == "__main__":
    main()
