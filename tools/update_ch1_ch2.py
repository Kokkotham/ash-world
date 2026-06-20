#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 chapters.json 和 races.json：
1. ch1（创建角色）：拆分前言 + 7个子章节
2. ch2（种族）：写入前言 + 4个分类子章节
3. races.json：为每个玩家种族添加 detail 字段（从DOCX提取）
"""
import json, re, os
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def extract_docx(path):
    try:
        with ZipFile(path) as z:
            tree = ET.parse(z.open('word/document.xml'))
            root = tree.getroot()
            paras = root.findall('.//w:p', ns)
            lines = []
            for p in paras:
                texts = [t.text for t in p.findall('.//w:t', ns) if t.text]
                if texts:
                    lines.append(''.join(texts))
            return lines
    except Exception as e:
        return ['ERROR: ' + str(e)]

ew_dir = 'E:/Desktop/跑团文件/规则/EW'

# 加载现有数据
with open('data/chapters.json', 'r', encoding='utf-8') as f:
    chapters_data = json.load(f)
with open('data/races.json', 'r', encoding='utf-8') as f:
    races_data = json.load(f)

# ================================================================
# STEP 1: 拆分 ch1 内容 → 前言 + 7 个子章节
# ================================================================
ch1 = None
for ch in chapters_data['chapters']:
    if ch['id'] == 'ch1':
        ch1 = ch
        break

if ch1:
    content = ch1['content']
    sub_markers = [1, 5, 38, 45, 71, 88, 90]
    sub_titles = ['选择种族', '主属性', '成长值', '基础值计算', '专修能力携带', '选择灵涅特质', '选择装备']
    sub_ids = ['choose_race', 'main_attr', 'growth', 'base_calc', 'profession', 'soul_trait', 'equipment']

    ch1['content'] = [content[0]]
    ch1['sub_sections'] = []
    for i, start in enumerate(sub_markers):
        end = sub_markers[i+1] if i+1 < len(sub_markers) else len(content)
        sub_content = [l for l in content[start:end] if len(l.strip()) > 0]
        ch1['sub_sections'].append({
            'id': 'ch1_' + sub_ids[i],
            'title': sub_titles[i],
            'type': 'text',
            'content': sub_content,
            'sub_sections': [],
            'source': 'core',
        })
    print('ch1: 前言' + str(len(ch1['content'])) + '行, ' + str(len(ch1['sub_sections'])) + '个子章节')
else:
    print('ch1 not found!')

# ================================================================
# STEP 2: 更新 ch2 前言（从 2种族(1).docx 提取）
# ================================================================
ch2 = None
for ch in chapters_data['chapters']:
    if ch['id'] == 'ch2':
        ch2 = ch
        break

if ch2:
    ch2_lines = extract_docx(os.path.join(ew_dir, '2种族 (1).docx'))
    ch2['content'] = [l for l in ch2_lines if len(l.strip()) > 0]
    cat_config = [
        ('ancient', '古代种族', '源自远古岁月的古老种族，承载着大陆最悠久的文明记忆与力量本源。'),
        ('spirit_mixed', '精魂混血', '承载精魂之力的混血种族，兼具多重血脉特质与独特的灵能天赋。'),
        ('nature_psionic', '自然灵能', '与自然和灵能深度共鸣的种族，天生怀揣对万物生灵的敏锐感知。'),
        ('human_branches', '人类支系', '源自人类母系的不同地域支系，适应各异的生存环境，文明风貌迥然不同。'),
    ]
    ch2['sub_sections'] = []
    for cat_key, cat_title, cat_desc in cat_config:
        ch2['sub_sections'].append({
            'id': 'ch2_' + cat_key,
            'title': cat_title,
            'type': 'data',
            'data_source': 'races.json',
            'data_path': cat_key,
            'content': [cat_desc],
            'sub_sections': [],
            'source': 'core',
        })
    print('ch2: 前言' + str(len(ch2['content'])) + '行, ' + str(len(ch2['sub_sections'])) + '个分类')
else:
    print('ch2 not found!')

# ================================================================
# STEP 3: 提取 16 个种族 DOCX 内容，写入 races.json 的 detail 字段
# ================================================================
race_docx_map = [
    ('2.2.1纳露安人类(改动）.docx', '纳露安人'),
    ('2.2.2精灵(改动） (1).docx', '精灵'),
    ('2.2.3矮人(改动）.docx', '矮人'),
    ('2.2.4侏儒(改动）.docx', '侏儒'),
    ('2.2.5维拉斯人(改动） (3).docx', '维拉斯人'),
    ('2.2.6兽人(改动）.docx', '兽人'),
    ('2.2.7哥布林（改动）.docx', '哥布林'),
    ('2.2.8龙族（改动）.docx', '龙族'),
    ('2.2.9蛛灵（改动）.docx', '蛛灵'),
    ('2.2.10亡灵(改动） (1).docx', '亡灵'),
    ('2.2.11北地人（改动）.docx', '北地人'),
    ('2.2.12豺狼人（改动）.docx', '豺狼人'),
    ('2.2.13牛头人(改动）.docx', '牛头人'),
    ('2.2.14木林精（改动）.docx', '木林精'),
    ('2.2.15猪人(改动）.docx', '猪人'),
    ('2.2.16混血者与通用灵涅特质（新）.docx', '混血者'),
]

race_detail_map = {}
for docx_name, race_name in race_docx_map:
    path = os.path.join(ew_dir, docx_name)
    lines = extract_docx(path)
    if lines and len(lines) > 0 and lines[0].startswith('ERROR'):
        print('  ERROR: ' + docx_name + ': ' + lines[0])
        continue
    clean_lines = [l for l in lines if len(l.strip()) > 0]
    race_detail_map[race_name] = clean_lines
    print('  ' + race_name + ': ' + str(len(clean_lines)) + '行')

# 写入 races.json（只遍历 list 类型的分类）
updated_count = 0
list_categories = ['ancient', 'spirit_mixed', 'nature_psionic', 'human_branches', 'players']
for cat in list_categories:
    items = races_data.get(cat, [])
    if not isinstance(items, list):
        continue
    for race in items:
        name = race.get('name', '')
        if name in race_detail_map:
            race['detail'] = race_detail_map[name]
            updated_count += 1

print('races.json: 写入了' + str(updated_count) + '个种族的 detail 字段')

# ================================================================
# 写回文件
# ================================================================
with open('data/chapters.json', 'w', encoding='utf-8') as f:
    json.dump(chapters_data, f, ensure_ascii=False, indent=2)
print('已写回 data/chapters.json')

with open('data/races.json', 'w', encoding='utf-8') as f:
    json.dump(races_data, f, ensure_ascii=False, indent=2)
print('已写回 data/races.json')

print('全部完成！')
