"""
Build structured rulebook JSON from ew_raw + existing data.

Parses the ew_raw/*.json files, extracts ability definitions with
level tables, and merges them into the main data JSON files:
   data/professions.json   — 第3章 专修
   data/divine-arts.json   — 第4章 神术
   data/story-rules.json   — 第5章 故事运作

Usage:
    python tools/build_rulebook_data.py
"""

import json
import os
import re
import sys

# --------------- helpers ---------------
def slugify(name):
    """Convert Chinese name to an ASCII slug for id fields."""
    s = re.sub(r'[（(][^)）]*[)）]', '', name)  # 去掉括号内的标注
    s = s.strip()[:20]
    # keep Chinese chars, replace spaces with underscore
    s = re.sub(r'\s+', '_', s)
    return s


def parse_ability_paragraphs(paragraphs):
    """
    Parse an ew_raw paragraph list into a list of ability entries.
    
    Handles multiple formats:
      Format A: "能力名：SD(N）（MEB）描述..." (knowledge/communication/art)
      Format B: "能力名：（MEB）" then description paragraph (instinct)
      Format C: "能力名：" then "描述：..." (martial)
      Format D: "能力名（标注）" then description (arcane)
      Format E: "能力名：（C）（MEB）" then description (special)
    """
    abilities = []
    current = None
    
    # Pattern to detect new ability: anything that looks like a name followed by
    # special markers
    ability_start_pattern = re.compile(
        r'^(?:'
        r'([^：]+?)（[^）]*?）\s*(?:SD|前置需求|$)'
        r'|'
        r'([^：]+?)：(?:前置需求[^）]*?）)?\s*(?:SD|$)'
        r'|'
        r'([^：]+?)：(?:（[^）]+?）)?\s*$'
        r')'
    )
    
    # Simpler: check if paragraph starts with a known ability format
    def is_ability_header(para):
        # Skip headers/category descriptions
        if para.startswith("专修能力") or para.startswith("此类专修"):
            return False
        if para.startswith("后天专修"):
            return False
        if para.startswith("注") or para.startswith("PS") or para.startswith("注意"):
            return False
        if para.startswith("第") and "章" in para:
            return False
        if para.endswith("能力") or para.endswith("Innate ability"):
            return False
        if len(para) < 3:
            return False
        
        # Check for typical ability patterns by checking substring presence
        # instead of complex regex
        # Pattern: name followed by special markers like SD, (C), (1EB), etc.
        has_colon = "：" in para
        has_sd = "SD(" in para or "SD（" in para
        has_eb = "EB）" in para or "EB)" in para
        has_parent = "（" in para or "(" in para
        
        if has_sd:
            return True
        if has_colon and has_eb and not para.count("：") > 1:
            return True
        # Short name ending with colon - likely ability header
        if para.endswith("：") and para.count("：") == 1 and len(para) < 25:
            return True
        # Name with parenthesis markers (like "元素生现（奥术源）")
        if has_parent and not has_colon and len(para) < 30 and "前置需求" in para:
            return True
        return False
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Check if this paragraph starts a new ability
        if is_ability_header(para):
            if current:
                abilities.append(current)
            
            # Extract ability name
            name = para.split("：")[0].split("（")[0].strip() if "：" in para else para.split("（")[0].strip()
            # Clean up the name
            name = re.sub(r'\s+', '', name)
            
            current = {
                "name": name,
                "desc": [],
                "level_table": None,
                "prerequisites": None,
                "keywords": [],
                "id": slugify(name)
            }
            
            # Extract description from the same paragraph if present
            desc_text = ""
            # Try to extract text after SD() patterns
            m = re.search(r'(?:SD\([^)]*\)\s*(?:[（(][^)）]*[)）]\s*)?)(.*)', para)
            if m and m.group(1).strip():
                desc_text = m.group(1).strip()
            # Try to extract text after name:
            elif "：" in para:
                after_colon = para.split("：", 1)[1]
                # Remove prefix patterns
                after_colon = re.sub(r'^(?:前置需求[^）]*?）\s*)?', '', after_colon)
                after_colon = re.sub(r'^SD\([^)]*\)\s*(?:[（(][^)）]*[)）]\s*)?', '', after_colon)
                after_colon = re.sub(r'^（[^）]+?）\s*', '', after_colon)
                if after_colon.strip():
                    desc_text = after_colon.strip()
            
            if desc_text:
                current["desc"].append(desc_text)
        elif current:
            # Continuation of current ability
            if para.startswith("描述："):
                para = para[3:].strip()
            if para.startswith("前置需求"):
                if current["prerequisites"] is None:
                    current["prerequisites"] = para
                else:
                    current["desc"].append(para)
            elif para.startswith("注") or para.startswith("PS"):
                current["desc"].append(para)
            else:
                current["desc"].append(para)
    
    if current:
        abilities.append(current)
    
    return abilities


def parse_tables_into_levels(tables, ability_count):
    """
    Assign each table to an ability. The pattern is usually:
    - Each ability gets one or more tables (e.g. level tables)
    - The number of tables relative to abilities helps determine mapping
    
    Returns a list of level_table arrays, one per ability.
    """
    if not tables or ability_count == 0:
        return [None] * ability_count
    
    # Strategy: if tables >= abilities, assign tables round-robin or one-per-ability
    # If tables < abilities, some abilities don't have tables
    level_tables = [None] * ability_count
    
    if len(tables) >= ability_count:
        # One table per ability (first N tables)
        for i in range(ability_count):
            t = tables[i]
            rows = t.get("rows", [])
            if rows:
                # Convert to level_table format
                lt = []
                for row in rows:
                    entry = {}
                    headers = t.get("headers", [])
                    # Map common header names
                    for h, v in row.items():
                        key = h
                        if "等级" in h or "Level" in h or "lvl" in h.lower():
                            key = "level"
                        elif "加值" in h or "加值" in h or "Bonus" in h:
                            key = "bonus"
                        elif "消耗" in h or "Cost" in h or "cost" in h.lower():
                            key = "cost"
                        elif "效果" in h or "Effect" in h or "effect" in h.lower() or "额外增益" in h:
                            key = "effect"
                        entry[key] = v
                    lt.append(entry)
                level_tables[i] = lt if lt else None
            else:
                level_tables[i] = None
    else:
        # Fewer tables than abilities — try to match by position
        for i in range(len(tables)):
            t = tables[i]
            rows = t.get("rows", [])
            if rows:
                lt = []
                for row in rows:
                    entry = {}
                    for h, v in row.items():
                        key = h
                        if "等级" in h or "lvl" in h.lower():
                            key = "level"
                        elif "加值" in h:
                            key = "bonus"
                        elif "消耗" in h or "cost" in h.lower():
                            key = "cost"
                        elif "效果" in h or "effect" in h.lower() or "额外增益" in h:
                            key = "effect"
                        entry[key] = v
                    lt.append(entry)
                level_tables[i] = lt if lt else None
    
    return level_tables


# --------------- main build ---------------
def build_profession_categories():
    """Build the professions.json categories from ew_raw files."""
    
    PR_RAW_FILES = {
        "3.1本能专修": "instinct",
        "3.2知识类专修": "knowledge",
        "3.3交流类专修": "communication",
        "3.4艺术类专修": "art",
        "3.5生存类专修": "survival",
        "3.6特殊类专修": "special",
        "3.7.1专业工艺加工": "craft_processing",
        "3.7.2专业金属加工": "craft_metal",
        "3.7.3专业纺织加工": "craft_textile",
        "3.7.4专业符文缔造": "craft_rune",
        "3.7.5专业养殖培育": "craft_farming",
        "3.7.6专业铭文卷轴": "craft_scroll",
        "3.8.1短柄类武器专修": "weapon_short",
        "3.8.2中柄类武器专修": "weapon_medium",
        "3.8.3长柄类武器专修": "weapon_long",
        "3.8.4重柄类武器专修": "weapon_heavy",
        "3.8.5远程类武器专修": "weapon_ranged",
        "3.8.6特殊类武器专修": "weapon_special",
        "3.9战斗造诣专修": "combat",
        "3.10.1短柄武技": "martial_short",
        "3.10.2中柄武技": "martial_medium",
        "3.10.3长柄武技": "martial_long",
        "3.10.4重柄武技": "martial_heavy",
        "3.10.5特殊武技": "martial_special",
        "3.11.2奥法元素专修": "arcane_element",
        "3.11.3奥法变形专修": "arcane_transmutation",
        "3.11.4奥法环境专修": "arcane_environment",
        "3.11.5奥法保护专修": "arcane_protection",
        "3.11.6奥法召唤专修": "arcane_summon",
        "3.11.7奥法特感专修": "arcane_extra_sense",
        "3.11.8奥法乐理专修": "arcane_music",
        "3.11.9奥法拟象专修": "arcane_mimicry",
        "3.11.10统合法术聚变": "arcane_fusion",
    }

    EW_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "ew_raw")
    
    # Category metadata
    CATEGORY_META = {
        "instinct":     {"name": "本能专修",     "chapter": "3.1", "version_status": "改动"},
        "knowledge":    {"name": "知识类专修",   "chapter": "3.2", "version_status": "改动"},
        "communication":{"name": "交流类专修",   "chapter": "3.3", "version_status": "改动"},
        "art":          {"name": "艺术类专修",   "chapter": "3.4", "version_status": "改动"},
        "survival":     {"name": "生存类专修",   "chapter": "3.5", "version_status": "改动"},
        "special":      {"name": "特殊类专修",   "chapter": "3.6", "version_status": "改动"},
        "craft_processing": {"name": "专业工艺加工", "chapter": "3.7.1", "version_status": "改动"},
        "craft_metal":  {"name": "专业金属加工", "chapter": "3.7.2", "version_status": "改动"},
        "craft_textile":{"name": "专业纺织加工", "chapter": "3.7.3", "version_status": "改动"},
        "craft_rune":   {"name": "专业符文缔造", "chapter": "3.7.4", "version_status": "改动"},
        "craft_farming":{"name": "专业养殖培育", "chapter": "3.7.5", "version_status": "改动"},
        "craft_scroll": {"name": "专业铭文卷轴", "chapter": "3.7.6", "version_status": "改动"},
        "weapon_short": {"name": "短柄类武器专修", "chapter": "3.8.1", "version_status": "改动"},
        "weapon_medium":{"name": "中柄类武器专修", "chapter": "3.8.2", "version_status": "改动"},
        "weapon_long":  {"name": "长柄类武器专修", "chapter": "3.8.3", "version_status": "改动"},
        "weapon_heavy": {"name": "重柄类武器专修", "chapter": "3.8.4", "version_status": "改动"},
        "weapon_ranged":{"name": "远程类武器专修", "chapter": "3.8.5", "version_status": "改动"},
        "weapon_special":{"name": "特殊类武器专修","chapter": "3.8.6", "version_status": "改动"},
        "combat":       {"name": "战斗造诣专修", "chapter": "3.9", "version_status": "改动"},
        "martial_short":{"name": "短柄武技",     "chapter": "3.10.1", "version_status": "改动"},
        "martial_medium":{"name": "中柄武技",   "chapter": "3.10.2", "version_status": "改动"},
        "martial_long": {"name": "长柄武技",     "chapter": "3.10.3", "version_status": "改动"},
        "martial_heavy":{"name": "重柄武技",     "chapter": "3.10.4", "version_status": "改动"},
        "martial_special":{"name": "特殊武技",   "chapter": "3.10.5", "version_status": "改动"},
        "arcane_element":{"name": "奥法元素专修","chapter": "3.11.2", "version_status": "改动"},
        "arcane_transmutation":{"name": "奥法变形专修","chapter": "3.11.3", "version_status": "改动"},
        "arcane_environment":{"name": "奥法环境专修","chapter": "3.11.4", "version_status": "改动"},
        "arcane_protection":{"name": "奥法保护专修","chapter": "3.11.5", "version_status": "改动"},
        "arcane_summon":{"name": "奥法召唤专修",  "chapter": "3.11.6", "version_status": "改动"},
        "arcane_extra_sense":{"name": "奥法特感专修","chapter": "3.11.7", "version_status": "改动"},
        "arcane_music":{"name": "奥法乐理专修",  "chapter": "3.11.8", "version_status": "重做"},
        "arcane_mimicry":{"name": "奥法拟象专修","chapter": "3.11.9", "version_status": "重做"},
        "arcane_fusion":{"name": "统合法术聚变",  "chapter": "3.11.10","version_status": "改动"},
    }
    
    # Desc mappings for categories
    CATEGORY_DESC = {
        "instinct": ["本能能力专修为所有角色与生灵与生俱来的基础判定能力，无需后天修习与培养即可天然拥有，同时亦是诸多专项专修的下位替代判定途径。所有本能专修均设有 0 至 20 级等级区间，可通过等级提升进一步丰富角色特质、完善人物塑造。"],
        "knowledge": ["知识类专修代表角色对各类学识体系、文化理论、专业知识的基础认知与理解深度。掌握知识类专修是进修诸多高阶专修的必要前置条件，同时也是角色在剧情中获取关键信息与破解谜题的重要途径。"],
        "communication": ["此类专修能力需满足对应前置条件，方可在角色创建阶段选择携带。每项额外专修均设有 1 至 20 级等级上限，部分专修允许以本能专修作为下位替代进行判定。"],
        "art": [],
        "survival": [],
        "special": [],
        "craft_processing": [],
        "craft_metal": [],
        "craft_textile": [],
        "craft_rune": [],
        "craft_farming": [],
        "craft_scroll": [],
        "weapon_short": [],
        "weapon_medium": [],
        "weapon_long": [],
        "weapon_heavy": [],
        "weapon_ranged": [],
        "weapon_special": [],
        "combat": [],
        "martial_short": [],
        "martial_medium": [],
        "martial_long": [],
        "martial_heavy": [],
        "martial_special": [],
        "arcane_element": [],
        "arcane_transmutation": [],
        "arcane_environment": [],
        "arcane_protection": [],
        "arcane_summon": [],
        "arcane_extra_sense": [],
        "arcane_music": [],
        "arcane_mimicry": [],
        "arcane_fusion": [],
    }
    
    categories = []
    processed = set()
    
    for raw_pattern, cat_id in PR_RAW_FILES.items():
        meta = CATEGORY_META.get(cat_id)
        if not meta:
            continue
        
        # Find matching ew_raw file
        ew_file = None
        for f in os.listdir(EW_RAW_DIR):
            if not f.endswith(".json"):
                continue
            # Try to match the pattern
            if raw_pattern.replace(" ", "") in f.replace(" ", ""):
                ew_file = f
                break
        
        if not ew_file:
            print(f"  SKIP {cat_id}: no matching ew_raw file for '{raw_pattern}'")
            continue
        
        ew_path = os.path.join(EW_RAW_DIR, ew_file)
        try:
            with open(ew_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            print(f"  ERROR reading {ew_file}: {e}")
            continue
        
        paragraphs = raw.get("paragraphs", [])
        tables = raw.get("tables", [])
        
        abilities = parse_ability_paragraphs(paragraphs)
        if not abilities:
            print(f"  WARN {cat_id}: no abilities parsed from {ew_file}")
        
        # Assign level tables
        level_tables = parse_tables_into_levels(tables, len(abilities))
        for i, lt in enumerate(level_tables):
            if i < len(abilities):
                abilities[i]["level_table"] = lt
                if lt:
                    abilities[i]["keywords"].append("有等级表")
        
        cat_entry = {
            "id": cat_id,
            "name": meta["name"],
            "chapter": meta["chapter"],
            "version_status": meta["version_status"],
            "desc": CATEGORY_DESC.get(cat_id, []),
            "abilities": abilities
        }
        categories.append(cat_entry)
        processed.add(cat_id)
        print(f"  OK  {cat_id}: {len(abilities)} abilities from {ew_file}")
    
    # Preserve existing categories (instinct, knowledge) already in professions.json
    # They will be merged by the caller
    return categories


def build_divine_arts():
    """Build divine-arts.json from ew_raw files."""
    EW_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "ew_raw")
    
    # Files: 4神术.json (header), 4.1.1 (父神系), 4.1.2 (母神系)
    pantheons = []
    
    # Read父神系（纳露安人类父神系）
    father_path = os.path.join(EW_RAW_DIR, "4.1.1纳露安人类父神系（改动）.json")
    if os.path.exists(father_path):
        with open(father_path, "r", encoding="utf-8") as f:
            father_raw = json.load(f)
        
        para = father_raw.get("paragraphs", [])
        tables = father_raw.get("tables", [])
        
        # Skip first few intro paragraphs as doctrine
        doctrine = []
        abilities = []
        for p in para:
            p = p.strip()
            if not p:
                continue
            # Check if this paragraph looks like a divine spell header
            # Format: "神术名：描述..." or "神术名 SD(N）"
            if re.match(r'^[^：]+?神术', p) and '：' in p:
                name = p.split('：')[0].strip()
                desc = p.split('：', 1)[1].strip() if '：' in p else ''
                abilities.append({
                    "name": name,
                    "desc": desc,
                    "level_table": None,
                    "prerequisites": None,
                    "keywords": [],
                    "id": slugify(name)
                })
            elif not abilities:
                # Before first ability, these are doctrine paragraphs
                if len(p) > 10:
                    doctrine.append(p)
        
        level_tables = parse_tables_into_levels(tables, len(abilities))
        for i, lt in enumerate(level_tables):
            if i < len(abilities):
                abilities[i]["level_table"] = lt
        
        pantheons.append({
            "name": "纳露安人类父神系",
            "doctrine": doctrine[:5] if doctrine else [],
            "divine_spells": abilities
        })
        print(f"  OK 父神系: {len(abilities)} divine spells")
    
    # Read母神系（纳露安人类母神系）
    mother_path = os.path.join(EW_RAW_DIR, "4.1.2纳露安人类母神系（改动） (1).json")
    if os.path.exists(mother_path):
        with open(mother_path, "r", encoding="utf-8") as f:
            mother_raw = json.load(f)
        
        para = mother_raw.get("paragraphs", [])
        tables = mother_raw.get("tables", [])
        
        abilities = []
        for p in para:
            p = p.strip()
            if not p:
                continue
            if re.match(r'^[^：]+?神术', p) and '：' in p:
                name = p.split('：')[0].strip()
                desc = p.split('：', 1)[1].strip() if '：' in p else ''
                abilities.append({
                    "name": name,
                    "desc": desc,
                    "level_table": None,
                    "prerequisites": None,
                    "keywords": [],
                    "id": slugify(name)
                })
        
        level_tables = parse_tables_into_levels(tables, len(abilities))
        for i, lt in enumerate(level_tables):
            if i < len(abilities):
                abilities[i]["level_table"] = lt
        
        pantheons.append({
            "name": "纳露安人类母神系",
            "doctrine": [],
            "divine_spells": abilities
        })
        print(f"  OK 母神系: {len(abilities)} divine spells")
    
    return {"pantheons": pantheons}


def build_story_rules():
    """Build story-rules.json from ew_raw files."""
    EW_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "ew_raw")
    
    sections = []
    
    # 5.1 战斗与挑战
    path = os.path.join(EW_RAW_DIR, "5.1战斗与挑战（新） (1).json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        paras = raw.get("paragraphs", [])
        rules = []
        for p in paras:
            if p and not p.startswith("第") and not p.startswith("5."):
                rules.append({"name": "", "desc": p})
        sections.append({
            "name": "战斗与挑战",
            "rules": rules
        })
        print(f"  OK 战斗与挑战: {len(rules)} rules")
    
    # 5.2 交流与生活
    path = os.path.join(EW_RAW_DIR, "5.2交流与生活（新） (1).json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        paras = raw.get("paragraphs", [])
        rules = []
        for p in paras:
            if p and not p.startswith("第") and not p.startswith("5."):
                rules.append({"name": "", "desc": p})
        sections.append({
            "name": "交流与生活",
            "rules": rules
        })
        print(f"  OK 交流与生活: {len(rules)} rules")
    
    # 5.3 经营与管理
    path = os.path.join(EW_RAW_DIR, "5.3经营与管理（新） (1).json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        paras = raw.get("paragraphs", [])
        tables = raw.get("tables", [])
        rules = []
        for p in paras:
            if p and not p.startswith("第") and not p.startswith("5."):
                rules.append({"name": "", "desc": p})
        # Add table data
        for t in tables:
            if t.get("rows"):
                rules.append({"name": "表格数据", "desc": json.dumps(t, ensure_ascii=False)})
        sections.append({
            "name": "经营与管理",
            "rules": rules
        })
        print(f"  OK 经营与管理: {len(rules)} rules")
    
    # 5.4 效应状态词缀
    path = os.path.join(EW_RAW_DIR, "5.4效应状态词缀(改动）.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        paras = raw.get("paragraphs", [])
        rules = []
        for p in paras:
            if p and not p.startswith("第") and not p.startswith("5."):
                rules.append({"name": "", "desc": p})
        sections.append({
            "name": "效应状态词缀",
            "rules": rules
        })
        print(f"  OK 效应状态词缀: {len(rules)} rules")
    
    return {"sections": sections}


def main():
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
    
    # --- 1. Build professions ---
    print("=== Building professions.json ===")
    new_categories = build_profession_categories()
    
    # Load existing professions.json to keep instinct + knowledge data
    prof_path = os.path.join(DATA_DIR, "professions.json")
    existing_prof = {}
    if os.path.exists(prof_path):
        with open(prof_path, "r", encoding="utf-8") as f:
            existing_prof = json.load(f)
        print(f"Loaded existing professions.json ({len(existing_prof.get('categories', []))} categories)")
    
    # Merge: keep existing categories that already have data unless new data is superior
    existing_cats = {c["id"]: c for c in existing_prof.get("categories", [])}
    for nc in new_categories:
        if nc["id"] in existing_cats:
            existing = existing_cats[nc["id"]]
            new_abilities = nc.get("abilities", [])
            existing_abilities = existing.get("abilities", [])
            # Only replace if we successfully parsed abilities from ew_raw
            if new_abilities and len(new_abilities) >= len(existing_abilities) and len(new_abilities) > 0:
                print(f"  REPLACED {nc['id']}: {len(existing_abilities)}→{len(new_abilities)} abilities")
                existing_cats[nc["id"]] = nc
            elif new_abilities and len(new_abilities) > 0:
                print(f"  MERGED {nc['id']}: kept existing ({len(existing_abilities)}), new had {len(new_abilities)}")
            else:
                print(f"  KEPT {nc['id']}: existing ({len(existing_abilities)}) > new empty")
        else:
            existing_cats[nc["id"]] = nc
            print(f"  ADDED {nc['id']}: {len(nc.get('abilities', []))} abilities")
    
    # Sort categories by chapter number
    CHAPTER_ORDER = {
        "instinct": 0, "knowledge": 1, "communication": 2, "art": 3,
        "survival": 4, "special": 5,
        "craft_processing": 6, "craft_metal": 7, "craft_textile": 8,
        "craft_rune": 9, "craft_farming": 10, "craft_scroll": 11,
        "weapon_short": 12, "weapon_medium": 13, "weapon_long": 14,
        "weapon_heavy": 15, "weapon_ranged": 16, "weapon_special": 17,
        "combat": 18,
        "martial_short": 19, "martial_medium": 20, "martial_long": 21,
        "martial_heavy": 22, "martial_special": 23,
        "arcane_element": 24, "arcane_transmutation": 25, "arcane_environment": 26,
        "arcane_protection": 27, "arcane_summon": 28, "arcane_extra_sense": 29,
        "arcane_music": 30, "arcane_mimicry": 31, "arcane_fusion": 32,
    }
    sorted_cats = sorted(existing_cats.values(), key=lambda c: CHAPTER_ORDER.get(c["id"], 999))
    
    prof_result = {"categories": sorted_cats}
    with open(prof_path, "w", encoding="utf-8") as f:
        json.dump(prof_result, f, ensure_ascii=False, indent=2)
    total_abilities = sum(len(c.get("abilities", [])) for c in sorted_cats)
    print(f"Written professions.json: {len(sorted_cats)} categories, {total_abilities} abilities")
    
    # --- 2. Build divine arts ---
    print("\n=== Building divine-arts.json ===")
    da = build_divine_arts()
    da_path = os.path.join(DATA_DIR, "divine-arts.json")
    with open(da_path, "w", encoding="utf-8") as f:
        json.dump(da, f, ensure_ascii=False, indent=2)
    total_spells = sum(len(p.get("divine_spells", [])) for p in da.get("pantheons", []))
    print(f"Written divine-arts.json: {len(da.get('pantheons', []))} pantheons, {total_spells} spells")
    
    # --- 3. Build story rules ---
    print("\n=== Building story-rules.json ===")
    sr = build_story_rules()
    sr_path = os.path.join(DATA_DIR, "story-rules.json")
    with open(sr_path, "w", encoding="utf-8") as f:
        json.dump(sr, f, ensure_ascii=False, indent=2)
    total_rules = sum(len(s.get("rules", [])) for s in sr.get("sections", []))
    print(f"Written story-rules.json: {len(sr.get('sections', []))} sections, {total_rules} rules")
    
    print("\nDone.")


if __name__ == "__main__":
    main()
