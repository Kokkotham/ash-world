"""Extract player race data from ew_raw JSONs into races.json players array."""
import json
import os
import sys

raw_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ew_raw')
races_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'races.json')

# Read existing races.json
with open(races_path, 'r', encoding='utf-8') as f:
    races_data = json.load(f)

race_files = {
    '2.2.1纳露安人类(改动）.json': ('naluan_human', '纳露安人类', '2.2.1', '改动'),
    '2.2.2精灵(改动） (1).json': ('elf', '精灵', '2.2.2', '改动'),
    '2.2.3矮人(改动）.json': ('dwarf', '矮人', '2.2.3', '改动'),
    '2.2.4侏儒(改动）.json': ('gnome', '侏儒', '2.2.4', '改动'),
    '2.2.5维拉斯人(改动） (3).json': ('vilas', '维拉斯人', '2.2.5', '改动'),
    '2.2.6兽人(改动）.json': ('orc', '兽人', '2.2.6', '改动'),
    '2.2.7哥布林（改动）.json': ('goblin', '哥布林', '2.2.7', '改动'),
    '2.2.8龙族（改动）.json': ('dragon', '龙族', '2.2.8', '改动'),
    '2.2.9蛛灵（改动）.json': ('spiderfolk', '蛛灵', '2.2.9', '改动'),
    '2.2.10亡灵(改动） (1).json': ('undead', '亡灵', '2.2.10', '改动'),
    '2.2.11北地人（改动）.json': ('northerner', '北地人', '2.2.11', '改动'),
    '2.2.12豺狼人（改动）.json': ('gnoll', '豺狼人', '2.2.12', '改动'),
    '2.2.13牛头人(改动）.json': ('minotaur', '牛头人', '2.2.13', '改动'),
    '2.2.14木林精（改动）.json': ('wood_sprite', '木林精', '2.2.14', '改动'),
    '2.2.15猪人(改动）.json': ('boarman', '猪人', '2.2.15', '改动'),
    '2.2.16混血者与通用灵涅特质（新）.json': ('mixed_blood', '混血者', '2.2.16', '新'),
}

attr_map = {
    '躯魄': 'strength', '敏韧': 'agility', '体质': 'constitution',
    '心智': 'intelligence', '洞识': 'wisdom', '魅力': 'charisma'
}

keyword_map = {
    'naluan_human': ['封建制度', '新神谱系', '骑士文化'],
    'elf': ['日月信仰', '太阳之嗣', '月亮之嗣', '希尔梵尼'],
    'dwarf': ['宝石之神', '六宝石氏族', '钱庄体系', '商业公会'],
    'gnome': ['蒸汽科技', '魔械造物', '飞行载具', '安卡洛斯'],
    'vilas': ['集体平等', '荒野之灵', '赤色之母'],
    'orc': ['凯撒元帅', '军衔制度', '重工业', '钢铁帝国'],
    'goblin': ['享乐主义', '公会体系', '艺术审美'],
    'dragon': ['古龙尊者', '龙塔', '进化飞升', '龙息'],
    'spiderfolk': ['蛛灵女王', '艾舍林', '记忆蛛丝', '暗影法庭'],
    'undead': ['瑞坦维亚诅咒', '灵魂信物', '亡灵祭司'],
    'northerner': ['大劫掠', '凛冬之民', '奥恩涅斯', '荒蛮野兽'],
    'gnoll': ['拾荒食腐', '腐烂之神', '化豺妖'],
    'minotaur': ['大地朝圣', '三位一体', '灵纹', '邦尔提大会'],
    'wood_sprite': ['集群意识', '巨古树', '菌丝网络', '自然精魄'],
    'boarman': ['贪婪经商', '物质主义', '金骨獠牙'],
    'mixed_blood': ['混血', '跨界血脉', '自定义', '通用灵涅'],
}

gameplay_notes_map = {
    'naluan_human': '属性均衡，文明开化度高，适合新手玩家',
    'elf': '长寿优雅，擅长远程与魔法，信仰分支决定玩法方向',
    'dwarf': '皮糙肉厚，锻造经商特长，宝石氏族决定专属能力',
    'gnome': '科技发明家，蒸汽与魔械大师，爆发力惊人',
    'vilas': '集体协作型，荒野亲和力强，战斗民族坚韧不拔',
    'orc': '近战猛男，重工业锻造加持，军衔决定社会地位',
    'goblin': '高魅力交涉型，公会体系独特，享乐主义驱动力',
    'dragon': '高智力施法者，龙息为核心，塔顶/地表两派分歧',
    'spiderfolk': '隐秘行动者，记忆操控与占卜，雌雄集权社会',
    'undead': '不死之身，灵魂绑定机制，诅咒带来的独特生存',
    'northerner': '狂战士型，大劫掠传统，荒蛮野兽伙伴加持',
    'gnoll': '拾荒游击型，投掷专精，欺软避硬游击战术',
    'minotaur': '重装坦克，大地信仰体系，灵纹朝圣文化深厚',
    'wood_sprite': '自然灵能者，植物操控与古树变身，集群意识',
    'boarman': '商贩型角色，寻宝嗅觉敏锐，金钱万能主义',
    'mixed_blood': '自由度最高，双种族混搭，通用灵涅特质可选',
}

# Identify sub-race header names for each race (short 2-8 char proper names)
skippable_prefixes = [
    '奥弗丹人', '安温提人', '芬恩莱特人', '旧瑞坦维亚人',
    '太阳之嗣', '月亮之嗣',
    '奥夫红钢', '诺罗吉', '利弗斯', '格恩耶斯', '麦斯克', '栝尔茨', '玛克特',
    '塞普林恩', '基尔斯罗班纳',
    '赤色之母', '荒野之血',
    '凡尔瑞斯', '槌肯维坦',
    '红色享乐会', '米莱欧公会',
    '迈格玛卡拉', '阿斯提拉提', '克尔纳皮亚',
    '艾舍林女王亲族', '艾舍林女王之眼',
    '瑞坦维亚后民', '瑞坦维亚先民',
    '奥恩涅斯血民', '严冬之民奥图海姆',
    '平原聚落', '山间聚落', '沼泽聚落',
    '草原族', '苔原族',
    '鲜根之灵', '古树之灵',
    '奥斯枉商族', '金骨獠牙',
]

def parse_attrs(paragraph):
    """Parse attribute line like '基础主属性加成：躯魄+1，敏韧+1，心智+1，洞识+1' or '主属性加成：躯魄+2，心智+1，洞识1'"""
    result = {'strength': 0, 'agility': 0, 'constitution': 0, 'intelligence': 0, 'wisdom': 0, 'charisma': 0}
    if '：' in paragraph:
        part = paragraph.split('：', 1)[1]
    elif ':' in paragraph:
        part = paragraph.split(':', 1)[1]
    else:
        return result

    segments = part.replace('，', ',').split(',')
    for seg in segments:
        seg = seg.strip()
        for cn, en in attr_map.items():
            if cn in seg:
                val_str = seg.split(cn)[-1].strip()
                sign = 1
                if val_str.startswith('+'):
                    val_str = val_str[1:]
                elif val_str.startswith('-'):
                    sign = -1
                    val_str = val_str[1:]
                try:
                    result[en] = sign * int(val_str)
                except ValueError:
                    pass
    return result


def extract_race_data(paragraphs):
    """Extract desc, attribute_mods, traits from raw paragraphs."""
    result = {
        'desc': [],
        'attribute_mods': {'strength': 0, 'agility': 0, 'constitution': 0,
                           'intelligence': 0, 'wisdom': 0, 'charisma': 0},
        'traits': []
    }

    in_traits = False
    current_trait_name = None
    current_trait_desc = None
    desc_candidates = []

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue

        # Skip epigraph/motto lines
        if p.startswith('\u300c') and p.endswith('\u300d'):
            continue

        # Parse attribute line
        if '主属性加成' in p:
            result['attribute_mods'] = parse_attrs(p)
            continue

        # Skip game data lines
        skip_kw = ['平均身高', '生育率', '种族体型', '成年岁数', '种族抗性']
        if any(kw in p for kw in skip_kw):
            continue

        # Skip language line
        if p.startswith('语言：') or p.startswith('语言:'):
            continue

        # Skip race name header (e.g. "纳露安人类Humans of Naluan")
        name_headers = [
            '纳露安人类Humans', '精灵Elf', '矮人Dwarf', '侏儒Gnome',
            '维拉斯', '兽人Orc', '哥布林Goblin', '龙族Draconian',
            '蛛灵Spyrit', '亡灵Undead', '北地人Northlanders',
            '豺狼人Gnoll', '牛头人Minotaur', '木林精Foresyad',
            '猪人Pigman', '混血者Hybrid'
        ]
        if any(p.startswith(h) for h in name_headers):
            continue

        # Skip sub-race header lines
        if p in skippable_prefixes:
            continue

        # Detect trait section start
        if '种族灵涅特质' in p or '灵涅特质' in p:
            in_traits = True
            continue

        # Detect end of trait section
        if in_traits and ('姓名与根源分类' in p or '姓名与根源' in p or
                          '通用灵涅特质' in p):
            # Flush current trait
            if current_trait_name and current_trait_desc:
                result['traits'].append({
                    'name': current_trait_name.strip(),
                    'desc': current_trait_desc.strip()[:200]
                })
                current_trait_name = None
                current_trait_desc = None
            # Don't enter generic traits for mixed_blood - just stop
            if '通用灵涅特质' in p:
                in_traits = False
            else:
                in_traits = False
            continue

        # Skip "种族能力" line (special ability of the race, not a trait)
        if '种族能力' in p and not in_traits:
            continue

        if in_traits:
            # Detect new trait entry: "TraitName：description..."
            if '：' in p and not p.startswith('\u300c'):
                # Save previous
                if current_trait_name and current_trait_desc:
                    result['traits'].append({
                        'name': current_trait_name.strip(),
                        'desc': current_trait_desc.strip()[:200]
                    })
                colon = p.index('：')
                current_trait_name = p[:colon].strip()
                current_trait_desc = p[colon + 1:].strip()
            elif current_trait_desc is not None:
                # Continuation of previous trait description
                current_trait_desc += p
            continue

        # Collect description candidates: long narrative paragraphs
        # Skip very short metadata-like lines
        if len(p) > 30 and '：' not in p[:20]:
            desc_candidates.append(p)

    # Flush last trait
    if current_trait_name and current_trait_desc:
        result['traits'].append({
            'name': current_trait_name.strip(),
            'desc': current_trait_desc.strip()[:200]
        })

    # Select best desc paragraphs (2-3 items, ~200 chars total target)
    sorted_desc = sorted(desc_candidates, key=len, reverse=True)
    selected = []
    total_len = 0
    for d in sorted_desc:
        if total_len > 200 and selected:
            break
        selected.append(d)
        total_len += len(d)
        if len(selected) >= 3:
            break

    result['desc'] = selected
    return result


# Process all race files
players = []
errors = []

for fname, (race_id, name, chapter, vs) in race_files.items():
    fpath = os.path.join(raw_dir, fname)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        extracted = extract_race_data(data['paragraphs'])

        player = {
            'id': race_id,
            'name': name,
            'category': '玩家种族',
            'chapter': chapter,
            'version_status': vs,
            'desc': extracted['desc'],
            'attribute_mods': extracted['attribute_mods'],
            'traits': extracted['traits'],
            'gameplay_notes': gameplay_notes_map.get(race_id, ''),
            'related_keywords': keyword_map.get(race_id, [])
        }
        players.append(player)
    except Exception as e:
        errors.append((fname, str(e)))

# Report
for e in errors:
    print(f'ERROR: {e[0]} -> {e[1]}')

print(f'\nExtracted {len(players)} races:')
for p in players:
    print(f"  {p['id']:20s} | {len(p['desc']):1d} desc | {len(p['traits']):2d} traits | "
          f"S:{p['attribute_mods']['strength']} A:{p['attribute_mods']['agility']} "
          f"C:{p['attribute_mods']['constitution']} I:{p['attribute_mods']['intelligence']} "
          f"W:{p['attribute_mods']['wisdom']} Ch:{p['attribute_mods']['charisma']}")

# Assemble final races.json
races_data['players'] = players
races_data['total'] = races_data.get('total', 0) + 16

with open(races_path, 'w', encoding='utf-8') as f:
    json.dump(races_data, f, ensure_ascii=False, indent=2)

print(f'\nWrote {races_path} with {len(players)} players')
print(f'Total races: {races_data["total"]}')
