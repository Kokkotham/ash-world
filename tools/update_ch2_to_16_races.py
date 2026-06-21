#!/usr/bin/env python3
"""
修改chapters.json，将ch2的sub_sections从4个分类改为16个种族子分类
"""

import json
import re

# 读取chapters.json
with open('data/chapters.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 读取races.json获取16个种族的名称和顺序
with open('data/races.json', 'r', encoding='utf-8') as f:
    races_data = json.load(f)

players = races_data.get('players', [])
print(f"races.json中players数量: {len(players)}")

# 构建16个种族的sub_sections
race_sub_sections = []
for i, race in enumerate(players):
    race_name = race.get('name', f'种族{i+1}')
    race_id = f"ch2_{race_name.replace(' ', '_')}"
    
    # 从race.detail中提取前言（第一行或前几行）
    preface = []
    if race.get('detail') and len(race['detail']) > 0:
        # 前言取前3行（通常是名称+版本状态+描述）
        preface = race['detail'][:3]
    
    sub = {
        "id": race_id,
        "title": race_name,
        "type": "data",
        "data_source": "races",
        "data_path": f"players[{i}]",
        "source": "core",
        "content": preface,
        "sub_sections": []
    }
    race_sub_sections.append(sub)
    print(f"  {i+1}. {race_name} -> {race_id}")

# 找到ch2并更新sub_sections
for ch in data['chapters']:
    if ch['id'] == 'ch2':
        print(f"\n修改ch2的sub_sections: {len(ch['sub_sections'])} -> {len(race_sub_sections)}")
        ch['sub_sections'] = race_sub_sections
        break

# 写回chapters.json
with open('data/chapters.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✅ chapters.json 修改完成")
print(f"  - ch2现在有{len(race_sub_sections)}个sub_sections（每个种族一个）")
