"""
给 chapters.json 追加第6章（专业制作与创造）和第7章（材料）。
用法：
  cd /path/to/project
  python tools/build_ch6_ch7.py
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(SCRIPT_DIR, "..", "data")
EW_RAW_DIR = os.path.join(DATA_DIR, "ew_raw")


def load_ew_raw(filename):
    path = os.path.join(EW_RAW_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_ew_file(pattern):
    """在 ew_raw 目录中找到匹配 pattern 的文件（忽略空格差异）"""
    for f in os.listdir(EW_RAW_DIR):
        if not f.endswith(".json"):
            continue
        if pattern.replace(" ", "") in f.replace(" ", ""):
            return f
    return None


def slugify(name):
    s = re.sub(r'[（(][^)）]*[)）]', '', name)
    s = s.strip()[:20]
    s = re.sub(r'\s+', '_', s)
    return s


def table_to_html(table):
    """将 ew_raw 表格转为 HTML 字符串。"""
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


# ── 第6章 子章节配置 ────────────────────────────────────────────────────────
CH6_GUIDE_FILES = [
    ("6.1锻造指南",       "锻造"),
    ("6.2弹药制作指南",   "弹药"),
    ("6.3科技建造指南",   "科技建造"),
    ("6.4衣物缝纫指南",   "衣物缝纫"),
    ("6.5烹饪与酿造指南", "烹饪与酿造"),
    ("6.6炼金指南",       "炼金"),
    ("6.7魔法物品制作指南", "魔法物品制作"),
    ("6.8养殖与栽培指南", "养殖与栽培"),
]


def build_ch6():
    raw0 = load_ew_raw("6专业制作与创造（新）.json")
    content0 = [p for p in raw0.get("paragraphs", []) if p.strip()] if raw0 else []

    sub_sections = []
    for guide_pattern, title in CH6_GUIDE_FILES:
        guide_file = find_ew_file(guide_pattern)
        sub_content = []
        if guide_file:
            raw_g = load_ew_raw(guide_file)
            if raw_g:
                sub_content.extend([p for p in raw_g.get("paragraphs", []) if p.strip()])

        # 找该大类下的所有模板文件（前缀为 "数字." 格式）
        # 从 guide_pattern 提取数字前缀，如 "6.1锻造指南" → "6.1"
        prefix_num = re.match(r'^\d+(\.\d+)*', guide_pattern)
        prefix_num = prefix_num.group() if prefix_num else ""
        tpl_files = sorted([
            f for f in os.listdir(EW_RAW_DIR)
            if f.endswith(".json") and prefix_num and f.startswith(prefix_num + ".") and "模板" in f
        ])

        for tpl_f in tpl_files:
            print(f"    processing template: {tpl_f}")
            raw_t = load_ew_raw(tpl_f)
            if not raw_t:
                continue
            paras_t = [p for p in raw_t.get("paragraphs", []) if p.strip()]
            if paras_t:
                sub_content.append(f"## {paras_t[0]}")
            for t in raw_t.get("tables", []):
                html = table_to_html(t)
                if html:
                    sub_content.append(html)

        sub_sections.append({
            "id": f"ch6_{slugify(title)}",
            "title": title,
            "type": "text",
            "content": sub_content,
            "sub_sections": []
        })
        print(f"  OK ch6.{title}: {len(sub_content)} 段内容")

    return {
        "id": "ch6",
        "title": "专业制作与创造",
        "number": "第6章",
        "type": "text",
        "data_source": None,
        "content": content0,
        "sub_sections": sub_sections
    }


# ── 第7章 材料文件配置 ────────────────────────────────────────────────────────
CH7_FILES = [
    ("7.1宝石",       "宝石"),
    ("7.2布料",       "布料"),
    ("7.3草药",       "草药"),
    ("7.4矿石",       "矿石"),
    ("7.5零件",       "零件"),
    ("7.6木料",       "木料"),
    ("7.7石料",       "石料"),
    ("7.8皮料",       "皮料"),
    ("7.9食物",       "食物"),
    ("7.10杂料",     "杂料"),
]


def build_ch7():
    sub_sections = []
    for file_pattern, title in CH7_FILES:
        ew_file = find_ew_file(file_pattern)
        sub_content = []
        if ew_file:
            raw = load_ew_raw(ew_file)
            if raw:
                paras = [p for p in raw.get("paragraphs", []) if p.strip()]
                if paras:
                    sub_content.append(paras[0])
                for t in raw.get("tables", []):
                    html = table_to_html(t)
                    if html:
                        sub_content.append(html)
        sub_sections.append({
            "id": f"ch7_{slugify(title)}",
            "title": title,
            "type": "text",
            "content": sub_content,
            "sub_sections": []
        })
        print(f"  OK ch7.{title}: {len(sub_content)} 段内容")

    return {
        "id": "ch7",
        "title": "材料",
        "number": "第7章",
        "type": "text",
        "data_source": None,
        "content": [],
        "sub_sections": sub_sections
    }


# ─── 主流程 ────────────────────────────────────────────────────────────────────
def main():
    print("=== 追加第6/7章到 chapters.json ===\n")

    ch_path = os.path.join(DATA_DIR, "chapters.json")
    if not os.path.exists(ch_path):
        print(f"ERROR: {ch_path} 不存在，请先运行 build_all_data.py")
        sys.exit(1)

    with open(ch_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chapters = data.get("chapters", [])

    # 确保至少有 8 章
    while len(chapters) < 8:
        idx = len(chapters)
        ch = {"id": f"ch{idx}", "title": "", "number": f"第{idx}章",
               "type": "text", "data_source": None, "content": [], "sub_sections": []}
        chapters.append(ch)

    # 构建 ch6
    print("--- 构建第6章 专业制作与创造 ---")
    ch6 = build_ch6()
    chapters[6] = ch6

    # 构建 ch7
    print("\n--- 构建第7章 材料 ---")
    ch7 = build_ch7()
    chapters[7] = ch7

    data["chapters"] = chapters

    with open(ch_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n=== 完成 ===")
    print(f"chapters.json 现在有 {len(chapters)} 章")


if __name__ == "__main__":
    main()
