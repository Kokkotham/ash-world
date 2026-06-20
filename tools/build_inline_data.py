"""
将 data/*.json 转换为单个内联 JS 文件（ash-data-inline.js）
通过 <script> 标签加载，解决 file:// 协议下 fetch/XHR 被浏览器安全策略阻止的问题

用法: python tools/build_inline_data.py
输出: data/ash-data-inline.js
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'ash-data-inline.js')

# 需要内联的数据文件及其对应的 AshData 属性名
DATA_MAP = {
    'races.json': 'races',
    'deities.json': 'deities',
    'regions.json': 'regions',
    'modules.json': 'modules',
    'links.json': 'links',
    'professions.json': 'professions',
    'divine-arts.json': 'divineArts',
    'story-rules.json': 'storyRules',
    'glossary.json': 'glossary',
    'chapters.json': 'chapters',
}


def main():
    lines = [
        '// 灰烬世界数据内联文件 — 由 build_inline_data.py 自动生成',
        '// 请勿手动修改，重新运行构建脚本即可更新',
        '// 此文件通过 <script> 标签加载，兼容 file:// 协议',
        '(function() {',
        '  window.__AshDataInline = window.__AshDataInline || {};',
    ]

    total = 0
    for filename, varname in DATA_MAP.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f'  [SKIP] {filename} 不存在')
            lines.append(f"  // {filename} 文件不存在")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        # 截断过长的单行，保持可读性但不影响功能
        if len(json_str) > 200:
            lines.append(f"  window.__AshDataInline['{varname}'] = {json_str};")
        else:
            lines.append(f"  window.__AshDataInline['{varname}'] = {json_str};")
        total += 1
        print(f'  [OK] {filename} -> __AshDataInline.{varname} ({len(json_str)} chars)')

    lines.append('})();')

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f'\n生成完成: ash-data-inline.js ({total} 个文件, {size_kb:.1f} KB)')
    print(f'路径: {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
