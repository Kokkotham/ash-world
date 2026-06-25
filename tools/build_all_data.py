"""
统一规则书数据构建脚本 —— 一次解析，同时生成阅读版和速查版数据。

解析 ew_raw/*.json，生成：
  1. data/chapters.json   —— 阅读版（按章节顺序排列）
  2. data/professions.json  —— 速查版·专修（按类型分类）
  3. data/divine-arts.json —— 速查版·神术（按神系分类）
  4. data/story-rules.json  —— 速查版·故事规则（按章节分类）

所有数据条目均含 "source": "core" 标签，扩展内容后续可加 "source": "expansion_xxx"。

Usage:
   cd /path/to/project
   python tools/build_all_data.py
"""

import json
import os
import re
import sys

# ─── 路径配置 ───────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(SCRIPT_DIR, "..", "data")
EW_RAW_DIR = os.path.join(DATA_DIR, "ew_raw")

# ─── 工具函数 ───────────────────────────────────────────────────────────────────
def load_ew_raw(filename):
    path = os.path.join(EW_RAW_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def slugify(name):
    s = re.sub(r'[（(][^)）]*[)）]', '', name)
    s = s.strip()[:20]
    s = re.sub(r'\s+', '_', s)
    return s

def table_to_html(table):
    """将 ew_raw 表格转为 HTML 字符串（用于注入 content 数组）。"""
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    if not headers or not rows:
        return ""
    html = '<table class="ew-table"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for row in rows:
        html += '<tr>'
        for h in headers:
            v = row.get(h, "")
            html += f'<td>{v}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# ─── ew_raw 文件名 → 章节键 的映射 ────────────────────────────────────────────
# 从文件名提取章节前缀，如 "3.1本能专修（改动）.json" → "3.1"
def extract_chapter_prefix(filename):
    name = filename.replace(".json", "")
    m = re.match(r'^(\d+(?:\.\d+)*)', name)
    return m.group(1) if m else None

# ─── 专修解析：从 ew_raw 段落提取能力列表 ──────────────────────────────────────
def parse_ability_paragraphs(paragraphs):
    abilities = []
    current = None

    def is_ability_header(para):
        if not para or len(para) < 2:
            return False
        if para.startswith("专修能力") or para.startswith("此类专修"):
            return False
        if para.startswith("后天专修"):
            return False
        if para.startswith("注") or para.startswith("PS") or para.startswith("注意"):
            return False
        if para.startswith("第") and "章" in para:
            return False
        if para.endswith("能力"):
            return False
        # 含 SD( 或 SD（ 的是能力头
        if "SD(" in para or "SD（" in para:
            return True
        # 含 ：（ 且长度合理，是能力头
        if "：" in para and len(para) < 40:
            return True
        # 含 （ 且含 前置需求 的，是能力头
        if "（" in para and "前置需求" in para:
            return True
        return False

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if is_ability_header(para):
            if current:
                abilities.append(current)
            name = para.split("：")[0].split("（")[0].strip() if "：" in para else para.split("（")[0].strip()
            name = re.sub(r'\s+', '', name)
            current = {
                "name": name,
                "desc": [],
                "level_table": None,
                "prerequisites": None,
                "keywords": [],
                "id": slugify(name),
                "source": "core"
            }
            # 尝试从同一段落提取描述
            desc_text = ""
            if "：" in para:
                after = para.split("：", 1)[1]
                after = re.sub(r'^前置需求[^）]*?）\s*', '', after)
                after = re.sub(r'^（[^）]+?）\s*', '', after)
                if after.strip():
                    desc_text = after.strip()
            if desc_text:
                current["desc"].append(desc_text)
        elif current:
            if para.startswith("描述："):
                para = para[3:].strip()
            if para.startswith("前置需求"):
                current["prerequisites"] = para
            else:
                current["desc"].append(para)
    if current:
        abilities.append(current)
    return abilities

def parse_tables_into_levels(tables, ability_count):
    if not tables or ability_count == 0:
        return [None] * ability_count
    level_tables = [None] * ability_count
    if len(tables) >= ability_count:
        for i in range(ability_count):
            t = tables[i]
            rows = t.get("rows", [])
            if rows:
                lt = []
                for row in rows:
                    entry = {}
                    for h, v in row.items():
                        key = h
                        if "等级" in h or "Level" in h or "lvl" in h.lower():
                            key = "level"
                        elif "加值" in h or "Bonus" in h:
                            key = "bonus"
                        elif "消耗" in h or "cost" in h.lower():
                            key = "cost"
                        elif "效果" in h or "effect" in h.lower() or "额外增益" in h:
                            key = "effect"
                        entry[key] = v
                    lt.append(entry)
                level_tables[i] = lt if lt else None
    return level_tables

# ─── 第3章 专修：构建统一数据 ─────────────────────────────────────────────────
# PR_FILES: (ew_raw文件名模式, category_id, category_name, chapter_number, parent_id)
PR_FILES = [
    # 大类
    ("3.1本能专修",           "instinct",        "本能专修",     "3.1",  None),
    ("3.2知识类专修",         "knowledge",       "知识类专修",   "3.2",  None),
    ("3.3交流类专修",         "communication",   "交流类专修",   "3.3",  None),
    ("3.4艺术类专修",         "art",             "艺术类专修",   "3.4",  None),
    ("3.5生存类专修",         "survival",        "生存类专修",   "3.5",  None),
    ("3.6特殊类专修",         "special",         "特殊类专修",   "3.6",  None),
    ("3.9战斗造诣专修",       "combat",          "战斗造诣专修", "3.9",  None),
    # 专业工艺子类
    ("3.7.1专业工艺加工",     "craft_processing","专业工艺加工", "3.7.1","craft"),
    ("3.7.2专业金属加工",     "craft_metal",     "专业金属加工", "3.7.2","craft"),
    ("3.7.3专业纺织加工",     "craft_textile",   "专业纺织加工", "3.7.3","craft"),
    ("3.7.4专业符文缔造",     "craft_rune",      "专业符文缔造", "3.7.4","craft"),
    ("3.7.5专业养殖培育",     "craft_farming",   "专业养殖培育", "3.7.5","craft"),
    ("3.7.6专业铭文卷轴",     "craft_scroll",    "专业铭文卷轴", "3.7.6","craft"),
    # 武器专修子类
    ("3.8.1短柄类武器专修",   "weapon_short",    "短柄类武器专修","3.8.1","weapon"),
    ("3.8.2中柄类武器专修",   "weapon_medium",   "中柄类武器专修","3.8.2","weapon"),
    ("3.8.3长柄类武器专修",   "weapon_long",     "长柄类武器专修","3.8.3","weapon"),
    ("3.8.4重柄类武器专修",   "weapon_heavy",    "重柄类武器专修","3.8.4","weapon"),
    ("3.8.5远程类武器专修",   "weapon_ranged",   "远程类武器专修","3.8.5","weapon"),
    ("3.8.6特殊类武器专修",   "weapon_special",  "特殊类武器专修","3.8.6","weapon"),
    # 武技子类
    ("3.10.1短柄武技",        "martial_short",    "短柄武技",     "3.10.1","martial"),
    ("3.10.2中柄武技",        "martial_medium",   "中柄武技",     "3.10.2","martial"),
    ("3.10.3长柄武技",        "martial_long",     "长柄武技",     "3.10.3","martial"),
    ("3.10.4重柄武技",        "martial_heavy",    "重柄武技",     "3.10.4","martial"),
    ("3.10.5特殊武技",        "martial_special",  "特殊武技",     "3.10.5","martial"),
    # 奥法专修子类
    ("3.11.2奥法元素专修",    "arcane_element",    "奥法元素专修", "3.11.2","arcane"),
    ("3.11.3奥法变形专修",    "arcane_transmutation","奥法变形专修","3.11.3","arcane"),
    ("3.11.4奥法环境专修",    "arcane_environment", "奥法环境专修","3.11.4","arcane"),
    ("3.11.5奥法保护专修",    "arcane_protection", "奥法保护专修","3.11.5","arcane"),
    ("3.11.6奥法召唤专修",    "arcane_summon",     "奥法召唤专修","3.11.6","arcane"),
    ("3.11.7奥法特感专修",    "arcane_extra_sense", "奥法特感专修","3.11.7","arcane"),
    ("3.11.8奥法乐理专修",    "arcane_music",      "奥法乐理专修","3.11.8","arcane"),
    ("3.11.9奥法拟象专修",    "arcane_mimicry",    "奥法拟象专修","3.11.9","arcane"),
    ("3.11.10统合法术聚变",    "arcane_fusion",     "统合法术聚变","3.11.10","arcane"),
]

def find_ew_file(pattern):
    """在 ew_raw 目录中找到匹配 pattern 的文件（忽略空格差异）"""
    for f in os.listdir(EW_RAW_DIR):
        if not f.endswith(".json"):
            continue
        if pattern.replace(" ", "") in f.replace(" ", ""):
            return f
    return None

def build_professions():
    """
    构建专修数据（同时用于速查版和阅读版ch3）。
    返回 (categories, ch3_sub_sections)：
      - categories: 速查版格式（professions.json 用）
      - ch3_sub_sections: 阅读版格式（chapters.json ch3 的 sub_sections 用）
    """
    # 父级分组（用于阅读版 ch3 的二级导航）
    PARENT_GROUPS = {
        "craft":    {"id": "ch3_craft",    "title": "专业工艺专修", "chapter": "3.7"},
        "weapon":   {"id": "ch3_weapon",   "title": "武器专修",     "chapter": "3.8"},
        "martial":  {"id": "ch3_martial",  "title": "武技",         "chapter": "3.10"},
        "arcane":   {"id": "ch3_arcane",   "title": "奥法专修",     "chapter": "3.11"},
    }
    # 版本状态映射
    VERSION_STATUS = {
        "instinct": "改动", "knowledge": "改动", "communication": "改动",
        "art": "改动", "survival": "改动", "special": "改动",
        "craft_processing": "改动", "craft_metal": "改动", "craft_textile": "改动",
        "craft_rune": "改动", "craft_farming": "改动", "craft_scroll": "改动",
        "weapon_short": "改动", "weapon_medium": "改动", "weapon_long": "改动",
        "weapon_heavy": "改动", "weapon_ranged": "改动", "weapon_special": "改动",
        "combat": "改动",
        "martial_short": "改动", "martial_medium": "改动", "martial_long": "改动",
        "martial_heavy": "改动", "martial_special": "改动",
        "arcane_element": "改动", "arcane_transmutation": "改动",
        "arcane_environment": "改动", "arcane_protection": "改动",
        "arcane_summon": "改动", "arcane_extra_sense": "改动",
        "arcane_music": "重做", "arcane_mimicry": "重做",
        "arcane_fusion": "改动",
    }

    categories = []       # 速查版
    ch3_sub_sections = [] # 阅读版 ch3 的 sub_sections

    # 先处理有父级的分组，创建父级 sub_section
    parent_children = {k: [] for k in PARENT_GROUPS}

    for pattern, cat_id, cat_name, chapter, parent_id in PR_FILES:
        ew_file = find_ew_file(pattern)
        if not ew_file:
            print(f"  SKIP {cat_id}: 未找到匹配 '{pattern}' 的文件")
            continue

        raw = load_ew_raw(ew_file)
        if not raw:
            continue

        paragraphs = raw.get("paragraphs", [])
        tables = raw.get("tables", [])

        abilities = parse_ability_paragraphs(paragraphs)
        level_tables = parse_tables_into_levels(tables, len(abilities))
        for i, lt in enumerate(level_tables):
            if i < len(abilities):
                abilities[i]["level_table"] = lt
                if lt:
                    abilities[i]["keywords"].append("有等级表")

        # 速查版条目
        cat_entry = {
            "id": cat_id,
            "name": cat_name,
            "chapter": chapter,
            "version_status": VERSION_STATUS.get(cat_id, "改动"),
            "source": "core",
            "desc": [],
            "abilities": abilities
        }
        categories.append(cat_entry)

        # 阅读版 sub_section 条目
        ss_entry = {
            "id": f"ch3_{cat_id}",
            "title": cat_name,
            "type": "data",
            "data_source": "professions",
            "data_path": cat_id,
            "source": "core",
            "renderer": "profession_category",
            "content": [],
            "sub_sections": []
        }
        if parent_id:
            parent_children[parent_id].append(ss_entry)
        else:
            ch3_sub_sections.append(ss_entry)

        print(f"  OK {cat_id}: {len(abilities)} 项能力（来自 {ew_file}）")

    # 把子分组挂到父级下面
    for parent_id, group in PARENT_GROUPS.items():
        children = parent_children.get(parent_id, [])
        if children:
            parent_ss = {
                "id": group["id"],
                "title": group["title"],
                "type": "group",
                "chapter": group["chapter"],
                "source": "core",
                "content": [],
                "sub_sections": children
            }
            ch3_sub_sections.append(parent_ss)

    return categories, ch3_sub_sections

# ─── 第4章 神术：构建统一数据 ─────────────────────────────────────────────────
def is_level_table(headers):
    """判断一个表格是否是等级表（表头是数字+神术名）"""
    if not headers or len(headers) < 2:
        return False
    # 表头第一项是数字（等级）
    try:
        int(str(headers[0]).strip())
        return True
    except:
        return False

def parse_divine_spell_from_table(table, all_tables=None, table_idx=None):
    """
    从一个表格解析神术数据。
    返回 {"name": ..., "desc": [...], "level_table": ..., "mp_cost": ...} 或 None
    """
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    if not headers:
        return None

    # 情况A：等级表（表头是 ['1', '神术名']）
    if is_level_table(headers):
        spell_name = headers[1] if len(headers) > 1 else "未知神术"
        level_table = []
        for row in rows:
            level = row.get(headers[0], "")
            effect = row.get(spell_name, "")
            if level and effect:
                level_table.append({"level": level, "effect": effect})
        return {
            "name": spell_name,
            "desc": [],
            "level_table": level_table if level_table else None,
            "mp_cost": None,
            "prerequisites": None,
            "keywords": ["等级神术"],
            "id": slugify(spell_name),
            "source": "core"
        }

    # 情况B：神术描述表（表头是 ['神术名或类型', 'MP消耗']）
    spell_name = headers[0] if headers else "未知神术"
    mp_cost = headers[1] if len(headers) > 1 else None

    # 从首行提取描述
    desc = []
    if rows:
        first_row = rows[0]
        desc_text = first_row.get(spell_name, "")
        if desc_text and desc_text not in ["强化选项", "多发神神矢"]:
            desc.append(desc_text)

    # 后续行可能是强化选项
    has_options = False
    options = []
    for row in rows[1:]:
        opt_name = row.get(spell_name, "")
        opt_desc = row.get(mp_cost, "") if mp_cost else ""
        if opt_name == "强化选项":
            has_options = True
            continue
        if has_options and opt_name:
            options.append(opt_name)
        elif opt_desc and opt_name not in ["强化选项"]:
            if desc_text != opt_name:
                desc.append(opt_name)

    result = {
        "name": spell_name,
        "desc": desc,
        "level_table": None,
        "mp_cost": mp_cost,
        "prerequisites": None,
        "keywords": [],
        "id": slugify(spell_name),
        "source": "core"
    }
    if options:
        result["options"] = options
    return result


def build_divine_arts():
    """
    构建神术数据。
    返回 (divine_data, ch4_sub_sections)：
      - divine_data: 速查版格式（divine-arts.json 用）
      - ch4_sub_sections: 阅读版格式（chapters.json ch4 的 sub_sections 用）
    """
    pantheons = []
    ch4_sub_sections = []

    # 处理父神系和母神系
    for file_pattern, pantheon_name, pantheon_id in [
        ("4.1.1纳露安人类父神系", "纳露安人类父神系", "father"),
        ("4.1.2纳露安人类母神系", "纳露安人类母神系", "mother"),
    ]:
        ew_file = find_ew_file(file_pattern)
        if not ew_file:
            print(f"  SKIP {pantheon_name}: 未找到匹配文件")
            continue

        raw = load_ew_raw(ew_file)
        if not raw:
            continue

        paragraphs = raw.get("paragraphs", [])
        tables = raw.get("tables", [])

        # 提取教条（在第一个神术表格之前的段落）
        doctrine = []
        in_doctrine = True
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            if in_doctrine and ("神术" in p or "SD(" in p or "SD（" in p):
                in_doctrine = False
            if in_doctrine and not p.startswith("第"):
                if len(p) > 5:
                    doctrine.append(p)
            if not in_doctrine:
                break

        # 解析所有神术（从表格）
        spells = []
        pending_level_table = None

        for i, t in enumerate(tables):
            headers = t.get("headers", [])
            if not headers:
                continue

            # 跳过 table 0（通常是信仰者描述表，不是神术）
            if i == 0 and len(tables) > 1:
                continue

            result = parse_divine_spell_from_table(t, tables, i)

            if result:
                # 检查前一个神术是否需要这个作为等级表
                if result.get("level_table") and spells:
                    # 这是一个等级表，关联到前一个神术
                    spells[-1]["level_table"] = result["level_table"]
                else:
                    spells.append(result)

        pantheons.append({
            "name": pantheon_name,
            "source": "core",
            "doctrine": doctrine[:8] if doctrine else [],
            "divine_spells": spells
        })
        ch4_sub_sections.append({
            "id": f"ch4_{pantheon_id}",
            "title": pantheon_name,
            "type": "data",
            "data_source": "divine-arts",
            "data_path": f"pantheons[{0 if pantheon_id=='father' else 1}]",
            "source": "core",
            "renderer": "pantheon",
            "content": doctrine[:3] if doctrine else [],
            "sub_sections": []
        })
        print(f"  OK {pantheon_name}: {len(spells)} 项神术")

    return {"pantheons": pantheons}, ch4_sub_sections

# ─── 第5章 故事运作：构建统一数据 ──────────────────────────────────────────────
STORY_FILES = [
    ("5.1战斗与挑战", "战斗与挑战"),
    ("5.2交流与生活", "交流与生活"),
    ("5.3经营与管理", "经营与管理"),
    ("5.4效应状态词缀", "效应状态词缀"),
]

def build_story_rules():
    """
    构建故事规则数据。
    返回 (story_data, ch5_sub_sections)
    正确处理段落和表格数据。
    """
    sections = []
    ch5_sub_sections = []

    for pattern, section_name in STORY_FILES:
        ew_file = find_ew_file(pattern)
        if not ew_file:
            print(f"  SKIP 故事规则 '{section_name}': 未找到匹配文件")
            continue

        raw = load_ew_raw(ew_file)
        if not raw:
            continue

        paragraphs = raw.get("paragraphs", [])
        tables = raw.get("tables", [])

        rules = []
        current_rule_name = ""
        current_rule_desc = []

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            if p.startswith("第") and "章" in p:
                # 保存上一条规则
                if current_rule_name or current_rule_desc:
                    rules.append({
                        "name": current_rule_name,
                        "desc": current_rule_desc,
                        "source": "core"
                    })
                continue

            # 判断是否是新的规则标题
            is_header = False
            if "：" in p and len(p) < 60:
                is_header = True
            elif len(p) < 30 and not p.endswith("。"):
                is_header = True

            if is_header:
                # 保存上一条规则
                if current_rule_name or current_rule_desc:
                    rules.append({
                        "name": current_rule_name,
                        "desc": current_rule_desc,
                        "source": "core"
                    })
                current_rule_name = p.split("：")[0].strip() if "：" in p else p
                desc_rest = p.split("：", 1)[1].strip() if "：" in p else ""
                current_rule_desc = [desc_rest] if desc_rest else []
            else:
                current_rule_desc.append(p)

        # 保存最后一条规则
        if current_rule_name or current_rule_desc:
            rules.append({
                "name": current_rule_name,
                "desc": current_rule_desc,
                "source": "core"
            })

        # 处理表格数据：把表格转成规则条目
        for t in tables:
            headers = t.get("headers", [])
            rows = t.get("rows", [])
            if not rows:
                continue
            # 表格作为一条规则，desc 里放表格的 HTML 描述
            table_desc = [f"【表格】{', '.join(headers)}"]
            for row in rows:
                row_str = " | ".join(str(v) for v in row.values() if v)
                if row_str:
                    table_desc.append(row_str)
            rules.append({
                "name": f"表格：{headers[0] if headers else '数据'}",
                "desc": table_desc,
                "source": "core",
                "is_table": True
            })

        sections.append({"name": section_name, "source": "core", "rules": rules})
        ch5_sub_sections.append({
            "id": f"ch5_{slugify(section_name)}",
            "title": section_name,
            "type": "data",
            "data_source": "story-rules",
            "data_path": section_name,
            "source": "core",
            "renderer": "story_section",
            "content": [],
            "sub_sections": []
        })
        print(f"  OK {section_name}: {len(rules)} 条规则")

    return {"sections": sections}, ch5_sub_sections

# ─── 构建 chapters.json（阅读版）────────────────────────────────────────────────
def build_chapters_json(prof_categories, ch3_sub_sections,
                        divine_data, ch4_sub_sections,
                        story_data, ch5_sub_sections):
    """
    构建完整的 chapters.json。
    ch0/ch1/ch2 的内容从 ew_raw 读取（如果尚未填充则填充）。
    ch3/ch4/ch5 使用传入的 sub_sections。
    """
    # 加载现有 chapters.json（保留已有的 ch0/ch1/ch2 内容）
    ch_path = os.path.join(DATA_DIR, "chapters.json")
    if os.path.exists(ch_path):
        with open(ch_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        chapters = existing.get("chapters", [])
    else:
        chapters = []

    # 确保至少有 6 章
    while len(chapters) < 6:
        idx = len(chapters)
        ch = {"id": f"ch{idx}", "title": "", "number": f"第{idx}章",
               "type": "text", "data_source": None, "content": [], "sub_sections": []}
        chapters.append(ch)

    # ── ch0 前言 ──
    raw = load_ew_raw("0前言.json")
    if raw:
        chapters[0]["content"] = [p for p in raw.get("paragraphs", []) if p.strip()]
        chapters[0]["source"] = "core"
        print(f"  ch0: {len(chapters[0]['content'])} 段")

    # ── ch1 创建角色 ──
    raw = load_ew_raw("1创建角色：属性(改动）.json")
    if raw:
        chapters[1]["content"] = [p for p in raw.get("paragraphs", []) if p.strip()]
        chapters[1]["source"] = "core"
        print(f"  ch1: {len(chapters[1]['content'])} 段")

    # ── ch2 种族 ──
    raw = load_ew_raw("2种族 (1).json")
    if raw:
        chapters[2]["content"] = [p for p in raw.get("paragraphs", []) if p.strip()]
        chapters[2]["source"] = "core"
        chapters[2]["type"] = "data"
        print(f"  ch2: {len(chapters[2]['content'])} 段引言")
    # ch2 的 sub_sections 从 races.json 来（由外面填入，这里不改）

    # ── ch3 专修 ──
    chapters[3]["title"] = "专修"
    chapters[3]["number"] = "第3章"
    chapters[3]["type"] = "data"
    chapters[3]["source"] = "core"
    chapters[3]["data_source"] = "professions"
    chapters[3]["sub_sections"] = ch3_sub_sections
    print(f"  ch3: {len(ch3_sub_sections)} 个分类")

    # ── ch4 神术 ──
    chapters[4]["title"] = "神术"
    chapters[4]["number"] = "第4章"
    chapters[4]["type"] = "data"
    chapters[4]["source"] = "core"
    chapters[4]["data_source"] = "divine-arts"
    chapters[4]["sub_sections"] = ch4_sub_sections
    print(f"  ch4: {len(ch4_sub_sections)} 个神系")

    # ── ch5 故事运作 ──
    chapters[5]["title"] = "故事运作与角色投掷"
    chapters[5]["number"] = "第5章"
    chapters[5]["type"] = "data"
    chapters[5]["source"] = "core"
    chapters[5]["data_source"] = "story-rules"
    chapters[5]["sub_sections"] = ch5_sub_sections
    print(f"  ch5: {len(ch5_sub_sections)} 个章节")

    # ── ch6 专业制作与创造 ──
    ch6 = build_ch6()
    # 确保 chapters 至少有 8 个
    while len(chapters) < 8:
        idx = len(chapters)
        ch = {"id": f"ch{idx}", "title": "", "number": f"第{idx}章",
               "type": "text", "data_source": None, "content": [], "sub_sections": []}
        chapters.append(ch)
    chapters[6] = ch6
    print(f"  ch6: {ch6['title']} ({len(ch6.get('sub_sections', []))} 个子章节)")

    # ── ch7 材料 ──
    ch7 = build_ch7()
    chapters[7] = ch7
    print(f"  ch7: {ch7['title']} ({len(ch7.get('sub_sections', []))} 个子章节)")

    return {
        "book_title": "灰烬世界规则书",
        "version": "1.0",
        "source": "core",
        "chapters": chapters
    }

# ─── 主流程 ────────────────────────────────────────────────────────────────────
def main():
    print("=== 灰烬世界规则书统一数据构建 ===\n")

    # 1. 构建专修数据（同时产出速查版和阅读版格式）
    print("--- 构建第3章 专修 ---")
    prof_categories, ch3_sub_sections = build_professions()
    print(f"  速查版: {len(prof_categories)} 个分类")
    print(f"  阅读版: {len(ch3_sub_sections)} 个分组\n")

    # 2. 构建神术数据
    print("--- 构建第4章 神术 ---")
    divine_data, ch4_sub_sections = build_divine_arts()
    print(f"  速查版: {len(divine_data.get('pantheons', []))} 个神系")
    print(f"  阅读版: {len(ch4_sub_sections)} 个神系\n")

    # 3. 构建故事规则数据
    print("--- 构建第5章 故事运作 ---")
    story_data, ch5_sub_sections = build_story_rules()
    print(f"  速查版: {len(story_data.get('sections', []))} 个章节")
    print(f"  阅读版: {len(ch5_sub_sections)} 个章节\n")

    # 4. 写入速查版数据文件
    print("--- 写入速查版数据 ---")
    prof_path = os.path.join(DATA_DIR, "professions.json")
    with open(prof_path, "w", encoding="utf-8") as f:
        json.dump({"categories": prof_categories}, f, ensure_ascii=False, indent=2)
    total_abilities = sum(len(c.get("abilities", [])) for c in prof_categories)
    print(f"  professions.json: {len(prof_categories)} 分类, {total_abilities} 项能力")

    da_path = os.path.join(DATA_DIR, "divine-arts.json")
    with open(da_path, "w", encoding="utf-8") as f:
        json.dump(divine_data, f, ensure_ascii=False, indent=2)
    total_spells = sum(len(p.get("divine_spells", [])) for p in divine_data.get("pantheons", []))
    print(f"  divine-arts.json: {len(divine_data.get('pantheons', []))} 神系, {total_spells} 项神术")

    sr_path = os.path.join(DATA_DIR, "story-rules.json")
    with open(sr_path, "w", encoding="utf-8") as f:
        json.dump(story_data, f, ensure_ascii=False, indent=2)
    total_rules = sum(len(s.get("rules", [])) for s in story_data.get("sections", []))
    print(f"  story-rules.json: {len(story_data.get('sections', []))} 章节, {total_rules} 条规则\n")

    # 5. 构建并写入阅读版数据
    print("--- 写入阅读版数据 ---")
    chapters_data = build_chapters_json(
        prof_categories, ch3_sub_sections,
        divine_data, ch4_sub_sections,
        story_data, ch5_sub_sections
    )
    ch_path = os.path.join(DATA_DIR, "chapters.json")
    with open(ch_path, "w", encoding="utf-8") as f:
        json.dump(chapters_data, f, ensure_ascii=False, indent=2)
    print(f"  chapters.json: {len(chapters_data['chapters'])} 章\n")

    print("=== 构建完成 ===")
    print("所有数据文件已生成，含 source: 'core' 标签。")
    print("扩展内容可加 source: 'expansion_xxx' 标签。")

if __name__ == "__main__":
    main()
