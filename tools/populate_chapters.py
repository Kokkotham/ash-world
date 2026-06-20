"""
Build full text content for chapters.json from ew_raw files.
Populates ch0(前言), ch1(创建角色), and ch2(种族引言) with
the complete paragraph text from the original DOCX exports.
"""
import json, os, re

def load_ew_raw(filename):
    path = os.path.join(os.path.dirname(__file__), "..", "data", "ew_raw", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    # ── 1. 加载现有 chapters.json ──
    ch_path = os.path.join(os.path.dirname(__file__), "..", "data", "chapters.json")
    with open(ch_path, "r", encoding="utf-8") as f:
        chapters = json.load(f)

    # ── 2. 填充 ch0 (前言) ──
    raw = load_ew_raw("0前言.json")
    ch0 = chapters["chapters"][0]  # id == "ch0"
    # Skip first line "灰烬世界Ember world" as a sub-heading, rest is content
    ch0["content"] = []
    for p in raw["paragraphs"]:
        ch0["content"].append(p)
    print(f"ch0: {len(ch0['content'])} paragraphs")

    # ── 3. 填充 ch1 (创建角色) ──
    raw = load_ew_raw("1创建角色：属性(改动）.json")
    ch1 = chapters["chapters"][1]  # id == "ch1"
    ch1["content"] = []
    # The paragraphs contain mixed content: intro text, headings like "1.选择种族"
    # and attribute descriptions. We keep them as sequential paragraphs.
    for p in raw["paragraphs"]:
        ch1["content"].append(p)
    # Also add the sub-section "属性系统" if already exists
    print(f"ch1: {len(ch1['content'])} paragraphs")

    # ── 4. 填充 ch2 (种族引言) ──
    # ch2 is type "data" but we can add introductory text via content
    raw = load_ew_raw("2种族 (1).json")
    ch2 = chapters["chapters"][2]  # id == "ch2"
    for p in raw["paragraphs"]:
        ch2["content"].append(p)
    print(f"ch2 intro: {len(raw['paragraphs'])} paragraphs added")

    # ── 5. 写入 ──
    with open(ch_path, "w", encoding="utf-8") as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)
    print("\nchapters.json updated successfully.")

if __name__ == "__main__":
    main()
