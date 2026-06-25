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
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    if not headers or not rows:
        return ""
    html = '<table class="ew-table"><thead><tr>'
    for h in headers:
        html += f"<th>{h}</th>"
    html += "</tr></thead><tbody>"
    for row in rows:
        html += "<tr>"
        for h in headers:
            v = row.get(h, "")
            html += f"<td>{v}</td>"
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
