import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError, transaction

from apps.rules.models import Rule, RuleCategory


SOURCE_FILES = {
    'core_attributes': '01_核心属性_结构化.json',
    'races': '02_种族_结构化.json',
}


def repo_root():
    return Path(__file__).resolve().parents[5]


def load_json(path):
    if not path.exists():
        raise CommandError(f'规则数据源不存在: {path}')
    with path.open('r', encoding='utf-8-sig') as file_obj:
        return json.load(file_obj)


def text_join(items):
    return '\n'.join(str(item) for item in items if item)


def rule_payload(slug, title, summary, content, content_blocks, raw_data, category, sort_order):
    return {
        'slug': slug,
        'title': title,
        'summary': summary,
        'content': content,
        'content_blocks': content_blocks,
        'raw_data': raw_data,
        'rule_type': Rule.RuleType.ATTRIBUTE if category.slug == 'core-attributes' else Rule.RuleType.OTHER,
        'category': category,
        'chapter_ref': '',
        'source': 'local-rule-data-package',
        'version_status': raw_data.get('version', '') if isinstance(raw_data, dict) else '',
        'status': Rule.Status.PUBLISHED,
        'sort_order': sort_order,
    }


def build_core_attribute_rules(data, category):
    rules = []
    sort_order = 10

    for key, value in data.get('attributes', {}).items():
        derived = value.get('derived', {})
        blocks = [
            {'type': 'attribute', 'name': key, 'data': value},
            {'type': 'derived', 'items': derived},
        ]
        derived_names = '、'.join(derived.keys())
        rules.append(rule_payload(
            slug=f'core-attribute-{value.get("abbr", key).lower()}',
            title=f'核心属性：{key}',
            summary=f'{key}的基础说明与关联衍生值。',
            content=f'{key}\n缩写：{value.get("abbr", "")}\n关联衍生：{derived_names}',
            content_blocks=blocks,
            raw_data=value,
            category=category,
            sort_order=sort_order,
        ))
        sort_order += 10

    grouped_sections = [
        ('core-focus', '核心属性选择', 'core_focus'),
        ('derived-formulas', '衍生公式', 'derived_formulas'),
        ('character-creation', '创建角色规则', 'character_creation'),
        ('specializations', '专修规则概览', 'specializations'),
        ('soul-traits', '灵涅特质', 'soul_traits'),
    ]

    for slug_suffix, title, key in grouped_sections:
        section = data.get(key)
        if not section:
            continue
        rules.append(rule_payload(
            slug=f'core-{slug_suffix}',
            title=title,
            summary=f'{title}的结构化规则数据。',
            content=json.dumps(section, ensure_ascii=False, indent=2),
            content_blocks=[{'type': key, 'data': section}],
            raw_data={key: section, 'version': data.get('version', '')},
            category=category,
            sort_order=sort_order,
        ))
        sort_order += 10

    return rules


def build_race_rules(data, category):
    rules = []
    for index, race in enumerate(data.get('races', []), start=1):
        race_id = race.get('id')
        if not race_id:
            raise CommandError(f'种族缺少 id: {race}')
        blocks = [
            {'type': 'profile', 'data': {
                'languages': race.get('languages', []),
                'body_size': race.get('body_size', ''),
                'adult_age': race.get('adult_age', ''),
                'resistances': race.get('resistances', {}),
                'attribute_bonus': race.get('attribute_bonus', {}),
            }},
            {'type': 'abilities', 'items': race.get('abilities', [])},
            {'type': 'description', 'content': race.get('description', '')},
        ]
        content = text_join([
            race.get('description', ''),
            '语言：' + '、'.join(race.get('languages', [])),
            '体型：' + str(race.get('body_size', '')),
            '成年年龄：' + str(race.get('adult_age', '')),
        ])
        summary = f"{race.get('name', race_id)}的种族资料、属性加成、抗性与能力。"
        rules.append(rule_payload(
            slug=f'race-{race_id}',
            title=f"种族：{race.get('name', race_id)}",
            summary=summary,
            content=content,
            content_blocks=blocks,
            raw_data=race,
            category=category,
            sort_order=index * 10,
        ))
    return rules


class Command(BaseCommand):
    help = 'Import minimal structured rule sources: core attributes and races.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Only report planned changes without writing data.')
        parser.add_argument(
            '--source-dir',
            default=str(repo_root() / 'data_sources' / 'rules'),
            help='Directory containing structured rule source JSON files.',
        )

    def handle(self, *args, **options):
        source_dir = Path(options['source_dir'])
        dry_run = options['dry_run']

        core_data = load_json(source_dir / SOURCE_FILES['core_attributes'])
        race_data = load_json(source_dir / SOURCE_FILES['races'])

        category_specs = [
            {
                'slug': 'core-attributes',
                'name': '核心属性',
                'sort_order': 10,
                'metadata': {'source_file': SOURCE_FILES['core_attributes']},
            },
            {
                'slug': 'races',
                'name': '种族',
                'sort_order': 20,
                'metadata': {'source_file': SOURCE_FILES['races']},
            },
        ]

        if dry_run:
            categories = {
                spec['slug']: RuleCategory(slug=spec['slug'], name=spec['name'], sort_order=spec['sort_order'])
                for spec in category_specs
            }
            rule_payloads = (
                build_core_attribute_rules(core_data, categories['core-attributes'])
                + build_race_rules(race_data, categories['races'])
            )
            existing_categories = None
            existing_rules = None
            try:
                existing_categories = set(RuleCategory.objects.filter(
                    slug__in=[spec['slug'] for spec in category_specs]
                ).values_list('slug', flat=True))
                existing_rules = set(Rule.objects.filter(
                    slug__in=[payload['slug'] for payload in rule_payloads]
                ).values_list('slug', flat=True))
            except OperationalError as exc:
                self.stdout.write(self.style.WARNING(
                    f'Database unavailable; existing-row counts skipped: {exc}'
                ))
            self.stdout.write(self.style.WARNING('DRY RUN: no data written.'))
            if existing_categories is None or existing_rules is None:
                self.stdout.write(f'Categories planned: {len(category_specs)}')
                self.stdout.write(f'Rules planned: {len(rule_payloads)}')
            else:
                self.stdout.write(f'Categories planned: {len(category_specs)} '
                                  f'(create {len(category_specs) - len(existing_categories)}, '
                                  f'update {len(existing_categories)})')
                self.stdout.write(f'Rules planned: {len(rule_payloads)} '
                                  f'(create {len(rule_payloads) - len(existing_rules)}, '
                                  f'update {len(existing_rules)})')
            return

        with transaction.atomic():
            categories = {}
            category_created = 0
            category_updated = 0
            for spec in category_specs:
                category, created = RuleCategory.objects.update_or_create(
                    slug=spec['slug'],
                    defaults={
                        'name': spec['name'],
                        'source': 'local-rule-data-package',
                        'sort_order': spec['sort_order'],
                        'metadata': spec['metadata'],
                    },
                )
                categories[spec['slug']] = category
                if created:
                    category_created += 1
                else:
                    category_updated += 1

            rule_payloads = (
                build_core_attribute_rules(core_data, categories['core-attributes'])
                + build_race_rules(race_data, categories['races'])
            )

            rule_created = 0
            rule_updated = 0
            for payload in rule_payloads:
                slug = payload.pop('slug')
                _, created = Rule.objects.update_or_create(slug=slug, defaults=payload)
                if created:
                    rule_created += 1
                else:
                    rule_updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Imported categories: create {category_created}, update {category_updated}; '
            f'rules: create {rule_created}, update {rule_updated}.'
        ))
