import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError, transaction

from apps.rules.models import (
    RuleBook,
    RuleCategory,
    RuleChapter,
    RuleContentBlock,
    RuleEntry,
    RuleSection,
)


RULEBOOK_SLUG = 'embers-world-core'
RULEBOOK_SOURCE = 'data_sources'
SUPPORTED_INCLUDES = {'core', 'races'}
IMPORTED_SOURCE_FILES = [
    '01_核心属性_结构化.json',
    '02_种族_结构化.json',
]


def repo_root():
    return Path(__file__).resolve().parents[5]


def load_json(path):
    if not path.exists():
        raise CommandError(f'RuleBook source does not exist: {path}')
    with path.open('r', encoding='utf-8-sig') as file_obj:
        return json.load(file_obj)


def stable_slug(value, fallback):
    raw = str(value or fallback or '').strip().lower()
    ascii_part = re.sub(r'[^a-z0-9]+', '-', raw).strip('-')
    has_non_ascii = any(ord(char) > 127 for char in raw)
    if ascii_part and len(ascii_part) >= 3 and not has_non_ascii:
        return ascii_part[:240]
    digest = hashlib.sha1(raw.encode('utf-8')).hexdigest()[:8]
    fallback_part = ascii_part or re.sub(r'[^a-z0-9]+', '-', str(fallback or 'item').lower()).strip('-') or 'item'
    return f'{fallback_part[:80]}-{digest}'


def compact_text(items):
    return '\n'.join(str(item) for item in items if item)


def normalize_block(block_type, content='', data=None, renderer_hint='', raw_data=None, sort_order=0):
    return {
        'block_type': block_type,
        'content': content or '',
        'data': data or {},
        'renderer_hint': renderer_hint or '',
        'raw_data': raw_data or {},
        'metadata': {},
        'sort_order': sort_order,
    }


def content_to_blocks(content, renderer_hint=''):
    blocks = []
    for index, item in enumerate(content or [], start=1):
        sort_order = index * 10
        if isinstance(item, str):
            text = item.strip()
            if text.startswith('<'):
                blocks.append(normalize_block(
                    RuleContentBlock.BlockType.RAW_JSON,
                    data={'html': item},
                    renderer_hint=renderer_hint or 'legacy_html',
                    raw_data={'content': item},
                    sort_order=sort_order,
                ))
            else:
                blocks.append(normalize_block(
                    RuleContentBlock.BlockType.PARAGRAPH,
                    content=item,
                    renderer_hint=renderer_hint,
                    raw_data={'content': item},
                    sort_order=sort_order,
                ))
        else:
            blocks.append(normalize_block(
                RuleContentBlock.BlockType.RAW_JSON,
                data={'value': item},
                renderer_hint=renderer_hint,
                raw_data={'content': item},
                sort_order=sort_order,
            ))
    return blocks


@dataclass
class ImportStats:
    created: dict = field(default_factory=lambda: {
        'RuleBooks': 0,
        'Chapters': 0,
        'Sections': 0,
        'Entries': 0,
        'Blocks': 0,
    })
    updated: dict = field(default_factory=lambda: {
        'RuleBooks': 0,
        'Chapters': 0,
        'Sections': 0,
        'Entries': 0,
        'Blocks': 0,
    })
    deleted: dict = field(default_factory=lambda: {
        'RuleBooks': 0,
        'Chapters': 0,
        'Sections': 0,
        'Entries': 0,
        'Blocks': 0,
    })
    warnings: list = field(default_factory=list)

    def mark(self, model_name, created):
        if created:
            self.created[model_name] += 1
        else:
            self.updated[model_name] += 1


class RuleBookImporter:
    def __init__(self, source_dir, includes, dry_run=False, reset=False):
        self.source_dir = Path(source_dir)
        self.includes = includes
        self.dry_run = dry_run
        self.reset = reset
        self.stats = ImportStats()
        self.sections_by_source_key = {}
        self.sections_by_title = {}
        self.core_category = None
        self.race_category = None

    @property
    def chapters_path(self):
        return self.source_dir / 'rulebook' / 'chapters.json'

    @property
    def rules_dir(self):
        return self.source_dir / 'rules'

    def load_sources(self):
        chapters_data = load_json(self.chapters_path)
        core_data = None
        race_data = None
        if 'core' in self.includes:
            core_data = load_json(self.rules_dir / '01_核心属性_结构化.json')
        if 'races' in self.includes:
            race_data = load_json(self.rules_dir / '02_种族_结构化.json')
        return chapters_data, core_data, race_data

    def validate_source_boundary(self):
        source_root = self.source_dir.resolve()
        expected_root = (repo_root() / 'data_sources').resolve()
        try:
            self.chapters_path.resolve().relative_to(expected_root)
            self.rules_dir.resolve().relative_to(expected_root)
        except ValueError as exc:
            raise CommandError('import_rulebook may only read from data_sources/.') from exc
        if source_root != expected_root:
            self.stats.warnings.append(f'Custom source dir in use: {source_root}')

    def plan(self):
        self.validate_source_boundary()
        chapters_data, core_data, race_data = self.load_sources()
        chapter_count, section_count, chapter_blocks, section_blocks = self.count_chapter_tree(chapters_data)
        entry_payloads = self.build_entry_payloads(core_data, race_data, planning=True)
        block_count = chapter_blocks + section_blocks + sum(len(item['blocks']) for item in entry_payloads)

        self.stats.created['RuleBooks'] = 1
        self.stats.created['Chapters'] = chapter_count
        self.stats.created['Sections'] = section_count
        self.stats.created['Entries'] = len(entry_payloads)
        self.stats.created['Blocks'] = block_count

        try:
            rulebook = RuleBook.objects.filter(slug=RULEBOOK_SLUG).first()
            if rulebook:
                existing = self.count_existing(rulebook)
                for key, value in existing.items():
                    self.stats.updated[key] = min(self.stats.created[key], value)
                    self.stats.created[key] = max(self.stats.created[key] - value, 0)
                if self.reset:
                    self.stats.deleted.update(existing)
        except OperationalError as exc:
            self.stats.warnings.append(f'Database unavailable; existing counts skipped: {exc}')

    def import_all(self):
        self.validate_source_boundary()
        chapters_data, core_data, race_data = self.load_sources()
        with transaction.atomic():
            if self.reset:
                self.reset_existing()
            self.core_category = RuleCategory.objects.filter(slug='core-attributes').first()
            self.race_category = RuleCategory.objects.filter(slug='races').first()
            if not self.core_category and 'core' in self.includes:
                self.stats.warnings.append('RuleCategory core-attributes not found; core entries category left empty.')
            if not self.race_category and 'races' in self.includes:
                self.stats.warnings.append('RuleCategory races not found; race entries category left empty.')

            rulebook = self.upsert_rulebook(chapters_data)
            self.import_chapters(rulebook, chapters_data)
            self.import_entries(core_data, race_data)

    def count_existing(self, rulebook):
        chapters = RuleChapter.objects.filter(rulebook=rulebook)
        sections = RuleSection.objects.filter(chapter__rulebook=rulebook)
        entries = self.imported_entries()
        blocks = RuleContentBlock.objects.filter(chapter__rulebook=rulebook)
        section_blocks = RuleContentBlock.objects.filter(section__chapter__rulebook=rulebook)
        entry_blocks = RuleContentBlock.objects.filter(entry__in=entries)
        return {
            'RuleBooks': 1,
            'Chapters': chapters.count(),
            'Sections': sections.count(),
            'Entries': entries.count(),
            'Blocks': blocks.count() + section_blocks.count() + entry_blocks.count(),
        }

    def imported_entries(self):
        queryset = RuleEntry.objects.none()
        for source_file in IMPORTED_SOURCE_FILES:
            queryset = queryset | RuleEntry.objects.filter(metadata__source_file=source_file)
        return queryset.distinct()

    def reset_existing(self):
        rulebook = RuleBook.objects.filter(slug=RULEBOOK_SLUG).first()
        if not rulebook:
            entries = self.imported_entries()
            entry_count = entries.count()
            if entry_count:
                block_count = RuleContentBlock.objects.filter(entry__in=entries).count()
                entries.delete()
                self.stats.deleted['Entries'] += entry_count
                self.stats.deleted['Blocks'] += block_count
            return
        existing = self.count_existing(rulebook)
        self.imported_entries().delete()
        rulebook.delete()
        for key, value in existing.items():
            self.stats.deleted[key] += value

    def count_chapter_tree(self, chapters_data):
        chapter_count = 0
        section_count = 0
        chapter_blocks = 0
        section_blocks = 0
        for chapter in chapters_data.get('chapters', []):
            chapter_count += 1
            chapter_blocks += len(content_to_blocks(chapter.get('content', []), chapter.get('renderer', '')))
            sec_count, sec_blocks = self.count_sections(chapter.get('sub_sections', []))
            section_count += sec_count
            section_blocks += sec_blocks
        return chapter_count, section_count, chapter_blocks, section_blocks

    def count_sections(self, sections):
        count = 0
        blocks = 0
        for section in sections or []:
            count += 1
            blocks += len(content_to_blocks(section.get('content', []), section.get('renderer', '')))
            child_count, child_blocks = self.count_sections(section.get('sub_sections', []))
            count += child_count
            blocks += child_blocks
        return count, blocks

    def upsert_rulebook(self, data):
        defaults = {
            'title': data.get('book_title', '灰烬世界规则书'),
            'version': str(data.get('version', '')),
            'status': RuleBook.Status.PUBLISHED,
            'source': data.get('source', 'core'),
            'description': 'Embers World core rulebook imported from data_sources.',
            'raw_data': {
                'book_title': data.get('book_title', ''),
                'version': data.get('version', ''),
                'source': data.get('source', ''),
            },
            'metadata': {'source_file': 'data_sources/rulebook/chapters.json'},
        }
        rulebook, created = RuleBook.objects.update_or_create(slug=RULEBOOK_SLUG, defaults=defaults)
        self.stats.mark('RuleBooks', created)
        return rulebook

    def import_chapters(self, rulebook, data):
        self.sections_by_source_key = {}
        self.sections_by_title = {}
        for index, chapter_data in enumerate(data.get('chapters', []), start=1):
            source_key = chapter_data.get('id') or f'chapter-{index}'
            chapter, created = RuleChapter.objects.update_or_create(
                rulebook=rulebook,
                slug=stable_slug(source_key, f'chapter-{index}'),
                defaults={
                    'title': chapter_data.get('title') or chapter_data.get('name') or source_key,
                    'number': chapter_data.get('number', ''),
                    'summary': self.summary_from_content(chapter_data.get('content', [])),
                    'source_key': source_key,
                    'sort_order': index * 1000,
                    'raw_data': chapter_data,
                    'metadata': {
                        'type': chapter_data.get('type', ''),
                        'data_source': chapter_data.get('data_source', ''),
                        'renderer_type': chapter_data.get('renderer', ''),
                    },
                },
            )
            self.stats.mark('Chapters', created)
            self.replace_blocks(chapter=chapter, blocks=content_to_blocks(
                chapter_data.get('content', []),
                chapter_data.get('renderer', ''),
            ))
            self.import_sections(chapter, None, chapter_data.get('sub_sections', []), index * 1000)

    def import_sections(self, chapter, parent, sections, base_order):
        for index, section_data in enumerate(sections or [], start=1):
            source_key = section_data.get('id') or f'{chapter.source_key}-section-{index}'
            section, created = RuleSection.objects.update_or_create(
                chapter=chapter,
                slug=stable_slug(source_key, f'{chapter.slug}-section-{index}'),
                defaults={
                    'parent': parent,
                    'title': section_data.get('title') or section_data.get('name') or source_key,
                    'section_type': self.section_type(section_data.get('type')),
                    'summary': self.summary_from_content(section_data.get('content', [])),
                    'source_key': source_key,
                    'data_source': (section_data.get('data_source') or ''),
                    'data_path': (section_data.get('data_path') or ''),
                    'renderer_type': (section_data.get('renderer') or ''),
                    'sort_order': base_order + index * 100,
                    'raw_data': section_data,
                    'metadata': {},
                },
            )
            self.stats.mark('Sections', created)
            self.sections_by_source_key[source_key] = section
            self.sections_by_title[section.title] = section
            self.replace_blocks(section=section, blocks=content_to_blocks(
                section_data.get('content', []),
                section_data.get('renderer', ''),
            ))
            self.import_sections(chapter, section, section_data.get('sub_sections', []), section.sort_order)

    def section_type(self, value):
        known = {choice[0] for choice in RuleSection.SectionType.choices}
        return value if value in known else RuleSection.SectionType.OTHER

    def summary_from_content(self, content):
        for item in content or []:
            if isinstance(item, str) and item.strip() and not item.strip().startswith('<'):
                return item.strip()[:220]
        return ''

    def replace_blocks(self, chapter=None, section=None, entry=None, blocks=None):
        queryset = RuleContentBlock.objects.all()
        if chapter:
            queryset = queryset.filter(chapter=chapter, section__isnull=True, entry__isnull=True)
        elif section:
            queryset = queryset.filter(section=section, chapter__isnull=True, entry__isnull=True)
        elif entry:
            queryset = queryset.filter(entry=entry, chapter__isnull=True, section__isnull=True)
        else:
            return
        deleted, _ = queryset.delete()
        self.stats.deleted['Blocks'] += deleted
        for block in blocks or []:
            RuleContentBlock.objects.create(chapter=chapter, section=section, entry=entry, **block)
            self.stats.created['Blocks'] += 1

    def build_entry_payloads(self, core_data, race_data, planning=False):
        payloads = []
        if core_data:
            payloads.extend(self.core_entry_payloads(core_data, planning=planning))
        if race_data:
            payloads.extend(self.race_entry_payloads(race_data, planning=planning))
        return payloads

    def core_entry_payloads(self, data, planning=False):
        payloads = []
        target_section = None if planning else self.sections_by_source_key.get('ch1_main_attr')
        for index, (name, value) in enumerate(data.get('attributes', {}).items(), start=1):
            abbr = value.get('abbr', name)
            derived = value.get('derived', {})
            blocks = [
                normalize_block(
                    RuleContentBlock.BlockType.PROFILE,
                    content=f'{name} / {abbr}',
                    data={'name': name, 'abbr': abbr},
                    renderer_hint='core_attribute',
                    raw_data=value,
                    sort_order=10,
                ),
                normalize_block(
                    RuleContentBlock.BlockType.STAT_BLOCK,
                    data={'derived': derived},
                    renderer_hint='derived_values',
                    raw_data=derived,
                    sort_order=20,
                ),
            ]
            payloads.append({
                'slug': f'core-attribute-{str(abbr).lower()}',
                'title': f'核心属性：{name}',
                'entry_type': RuleEntry.EntryType.ATTRIBUTE,
                'summary': f'{name}的基础说明与关联衍生值。',
                'content': compact_text([name, f'缩写：{abbr}', '关联衍生：' + '、'.join(derived.keys())]),
                'source_key': f'attribute-{abbr}',
                'section': target_section,
                'category': self.core_category,
                'raw_data': value,
                'metadata': {'source_file': '01_核心属性_结构化.json'},
                'sort_order': 1100 + index * 10,
                'blocks': blocks,
            })

        grouped_sections = [
            ('core-focus', '核心属性选择', 'core_focus', 'ch1_main_attr'),
            ('derived-formulas', '衍生公式', 'derived_formulas', 'ch1_base_calc'),
            ('character-creation', '创建角色规则', 'character_creation', 'ch1_choose_race'),
            ('specializations', '专修规则概览', 'specializations', 'ch1_profession'),
            ('soul-traits', '灵涅特质', 'soul_traits', 'ch1_soul_trait'),
        ]
        for offset, (slug_suffix, title, key, section_key) in enumerate(grouped_sections, start=1):
            section = data.get(key)
            if not section:
                continue
            payloads.append({
                'slug': f'core-{slug_suffix}',
                'title': title,
                'entry_type': RuleEntry.EntryType.RULE,
                'summary': f'{title}的结构化规则数据。',
                'content': json.dumps(section, ensure_ascii=False, indent=2),
                'source_key': f'core-{key}',
                'section': None if planning else self.sections_by_source_key.get(section_key),
                'category': self.core_category,
                'raw_data': {key: section, 'version': data.get('version', '')},
                'metadata': {'source_file': '01_核心属性_结构化.json', 'source_key': key},
                'sort_order': 1200 + offset * 10,
                'blocks': [
                    normalize_block(
                        RuleContentBlock.BlockType.RAW_JSON,
                        data={key: section},
                        renderer_hint=key,
                        raw_data=section,
                        sort_order=10,
                    )
                ],
            })
        return payloads

    def race_entry_payloads(self, data, planning=False):
        payloads = []
        chapter_section = None if planning else self.sections_by_source_key.get('ch2')
        for index, race in enumerate(data.get('races', []), start=1):
            race_id = race.get('id')
            if not race_id:
                self.stats.warnings.append(f'Skipped race without id: {race}')
                continue
            section = None
            if not planning:
                section = self.sections_by_title.get(race.get('name')) or chapter_section
            blocks = [
                normalize_block(
                    RuleContentBlock.BlockType.PROFILE,
                    data={
                        'languages': race.get('languages', []),
                        'body_size': race.get('body_size', ''),
                        'adult_age': race.get('adult_age', ''),
                    },
                    renderer_hint='race_profile',
                    raw_data=race,
                    sort_order=10,
                ),
                normalize_block(
                    RuleContentBlock.BlockType.STAT_BLOCK,
                    data={
                        'resistances': race.get('resistances', {}),
                        'attribute_bonus': race.get('attribute_bonus', {}),
                    },
                    renderer_hint='race_stats',
                    raw_data=race,
                    sort_order=20,
                ),
                normalize_block(
                    RuleContentBlock.BlockType.ABILITY,
                    data={'abilities': race.get('abilities', [])},
                    renderer_hint='race_abilities',
                    raw_data=race.get('abilities', []),
                    sort_order=30,
                ),
                normalize_block(
                    RuleContentBlock.BlockType.PARAGRAPH,
                    content=race.get('description', ''),
                    renderer_hint='race_description',
                    raw_data={'description': race.get('description', '')},
                    sort_order=40,
                ),
            ]
            payloads.append({
                'slug': f'race-{stable_slug(race_id, race.get("name", "race"))}',
                'title': f'种族：{race.get("name", race_id)}',
                'entry_type': RuleEntry.EntryType.RACE,
                'summary': f'{race.get("name", race_id)}的种族资料、属性加成、抗性与能力。',
                'content': compact_text([
                    race.get('description', ''),
                    '语言：' + '、'.join(race.get('languages', [])),
                    '体型：' + str(race.get('body_size', '')),
                    '成年年龄：' + str(race.get('adult_age', '')),
                ]),
                'source_key': f'race-{race_id}',
                'section': section,
                'category': self.race_category,
                'raw_data': race,
                'metadata': {'source_file': '02_种族_结构化.json'},
                'sort_order': 2000 + index * 10,
                'blocks': blocks,
            })
        return payloads

    def import_entries(self, core_data, race_data):
        for payload in self.build_entry_payloads(core_data, race_data):
            blocks = payload.pop('blocks')
            slug = payload.pop('slug')
            entry, created = RuleEntry.objects.update_or_create(slug=slug, defaults=payload)
            self.stats.mark('Entries', created)
            self.replace_blocks(entry=entry, blocks=blocks)

    def write_report(self, stdout, style):
        if self.dry_run:
            stdout.write(style.WARNING('DRY RUN: no data written.'))
        if self.reset:
            stdout.write('Reset: enabled')
        stdout.write('Imported:')
        for name in ['RuleBooks', 'Chapters', 'Sections', 'Entries', 'Blocks']:
            stdout.write(
                f'  {name}: create {self.stats.created[name]}, '
                f'update {self.stats.updated[name]}, delete {self.stats.deleted[name]}'
            )
        if self.stats.warnings:
            stdout.write('Warnings:')
            for warning in self.stats.warnings:
                stdout.write(f'  - {warning}')


class Command(BaseCommand):
    help = 'Import RuleBook Engine phase 1 data from data_sources into RuleBook models.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Report planned changes without writing data.')
        parser.add_argument('--reset', action='store_true', help='Delete the current imported RuleBook before importing.')
        parser.add_argument(
            '--include',
            default='core,races',
            help='Comma-separated entry groups to import. Supported: core,races. Chapters are always imported.',
        )
        parser.add_argument(
            '--source-dir',
            default=str(repo_root() / 'data_sources'),
            help='Official data_sources directory. Legacy data/ is not allowed.',
        )

    def handle(self, *args, **options):
        includes = {item.strip() for item in options['include'].split(',') if item.strip()}
        unknown = includes - SUPPORTED_INCLUDES
        if unknown:
            raise CommandError(f'Unsupported include values: {", ".join(sorted(unknown))}')

        importer = RuleBookImporter(
            source_dir=Path(options['source_dir']),
            includes=includes,
            dry_run=options['dry_run'],
            reset=options['reset'],
        )
        if options['dry_run']:
            importer.plan()
        else:
            importer.import_all()
        importer.write_report(self.stdout, self.style)
