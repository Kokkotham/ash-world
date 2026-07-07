from collections import Counter, defaultdict

from django.core.management.base import BaseCommand, CommandError

from apps.rules.models import RuleBook, RuleChapter, RuleContentBlock, RuleEntry, RuleSection


class IntegrityReport:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            'RuleBooks': 0,
            'Chapters': 0,
            'Sections': 0,
            'Entries': 0,
            'Blocks': 0,
        }

    def error(self, message):
        self.errors.append(message)

    def warning(self, message):
        self.warnings.append(message)


class RuleBookIntegrityValidator:
    def __init__(self, rulebook_slug='embers-world-core'):
        self.rulebook_slug = rulebook_slug
        self.report = IntegrityReport()

    def validate(self):
        self.collect_stats()
        rulebook = self.validate_rulebook_exists()
        if not rulebook:
            return self.report

        chapters = list(RuleChapter.objects.filter(rulebook=rulebook).order_by('sort_order', 'id'))
        sections = list(RuleSection.objects.filter(chapter__rulebook=rulebook).select_related('chapter', 'parent'))
        entries = list(RuleEntry.objects.select_related('section'))
        blocks = list(RuleContentBlock.objects.select_related('chapter', 'section', 'entry'))

        if not chapters:
            self.report.warning(f'RuleBook has no chapters: {rulebook.slug}')
        self.validate_duplicate_slugs(rulebook, chapters, sections, entries)
        self.validate_section_parent_cycles(sections)
        self.validate_entries(entries)
        self.validate_content_blocks(blocks)
        self.validate_sort_order(chapters, sections, entries, blocks)
        self.validate_source_keys(chapters, sections, entries)
        self.validate_content_block_presence(chapters, sections, entries)
        self.validate_renderer_metadata(sections)
        return self.report

    def collect_stats(self):
        self.report.stats = {
            'RuleBooks': RuleBook.objects.count(),
            'Chapters': RuleChapter.objects.count(),
            'Sections': RuleSection.objects.count(),
            'Entries': RuleEntry.objects.count(),
            'Blocks': RuleContentBlock.objects.count(),
        }

    def validate_rulebook_exists(self):
        rulebook = RuleBook.objects.filter(slug=self.rulebook_slug).first()
        if not rulebook:
            self.report.error(f'RuleBook not found: {self.rulebook_slug}')
        return rulebook

    def validate_duplicate_slugs(self, rulebook, chapters, sections, entries):
        chapter_slugs = Counter(chapter.slug for chapter in chapters)
        for slug, count in chapter_slugs.items():
            if count > 1:
                self.report.error(f'Duplicate chapter slug in {rulebook.slug}: {slug} ({count})')

        sections_by_chapter = defaultdict(list)
        for section in sections:
            sections_by_chapter[section.chapter_id].append(section.slug)
        for chapter_id, slugs in sections_by_chapter.items():
            for slug, count in Counter(slugs).items():
                if count > 1:
                    self.report.error(f'Duplicate section slug in chapter {chapter_id}: {slug} ({count})')

        entry_slugs = Counter(entry.slug for entry in entries)
        for slug, count in entry_slugs.items():
            if count > 1:
                self.report.error(f'Duplicate entry slug: {slug} ({count})')

    def validate_section_parent_cycles(self, sections):
        sections_by_id = {section.id: section for section in sections}
        for section in sections:
            seen = set()
            current = section
            while current and current.parent_id:
                if current.id in seen:
                    self.report.error(f'Section parent cycle detected at section: {section.slug}')
                    break
                seen.add(current.id)
                current = sections_by_id.get(current.parent_id)

    def validate_entries(self, entries):
        for entry in entries:
            if not entry.section_id:
                self.report.error(f'RuleEntry has no section: {entry.slug}')

    def validate_content_blocks(self, blocks):
        for block in blocks:
            owners = [block.chapter_id, block.section_id, block.entry_id]
            owner_count = sum(1 for owner in owners if owner)
            if owner_count == 0:
                self.report.error(f'ContentBlock has no owner: {block.id}')
            if owner_count > 1:
                self.report.error(f'ContentBlock has multiple owners: {block.id}')

    def validate_sort_order(self, chapters, sections, entries, blocks):
        for label, items in [
            ('Chapter', chapters),
            ('Section', sections),
            ('Entry', entries),
            ('ContentBlock', blocks),
        ]:
            for item in items:
                if item.sort_order is None:
                    self.report.error(f'{label} missing sort_order: {getattr(item, "slug", item.id)}')

    def validate_source_keys(self, chapters, sections, entries):
        for label, items in [
            ('Chapter', chapters),
            ('Section', sections),
            ('Entry', entries),
        ]:
            for item in items:
                if not item.source_key:
                    self.report.error(f'{label} missing source_key: {getattr(item, "slug", item.id)}')

    def validate_content_block_presence(self, chapters, sections, entries):
        for entry in entries:
            if not entry.content_blocks.exists():
                self.report.error(f'RuleEntry has no content blocks: {entry.slug}')

        for chapter in chapters:
            if not chapter.content_blocks.exists() and not chapter.sections.exists():
                self.report.warning(f'Chapter has no content blocks or sections: {chapter.slug}')

    def validate_renderer_metadata(self, sections):
        for section in sections:
            if not self.requires_renderer_metadata(section):
                continue
            if not self.has_inherited_data_source(section):
                self.report.warning(f'Section data_source missing: {section.slug}')
            if not self.has_inherited_renderer_type(section):
                self.report.warning(f'Section renderer_type missing: {section.slug}')

    def requires_renderer_metadata(self, section):
        if section.section_type == RuleSection.SectionType.DATA:
            return True
        if section.section_type == RuleSection.SectionType.GROUP and (section.data_source or section.data_path):
            return True
        return False

    def has_inherited_data_source(self, section):
        current = section
        while current:
            if current.data_source:
                return True
            current = current.parent
        return bool(section.chapter.metadata.get('data_source'))

    def has_inherited_renderer_type(self, section):
        current = section
        while current:
            if current.renderer_type:
                return True
            current = current.parent
        return bool(section.chapter.metadata.get('renderer_type'))


class Command(BaseCommand):
    help = 'Validate RuleBook Engine data integrity.'

    def add_arguments(self, parser):
        parser.add_argument('--strict', action='store_true', help='Treat warnings as failures.')
        parser.add_argument(
            '--rulebook',
            default='embers-world-core',
            help='RuleBook slug to validate.',
        )

    def handle(self, *args, **options):
        validator = RuleBookIntegrityValidator(rulebook_slug=options['rulebook'])
        report = validator.validate()

        self.stdout.write('RuleBook Integrity:')
        for name in ['RuleBooks', 'Chapters', 'Sections', 'Entries', 'Blocks']:
            self.stdout.write(f'  {name}: {report.stats[name]}')

        self.stdout.write(f'Errors: {len(report.errors)}')
        for error in report.errors:
            self.stdout.write(self.style.ERROR(f'  - {error}'))

        self.stdout.write(f'Warnings: {len(report.warnings)}')
        for warning in report.warnings:
            self.stdout.write(self.style.WARNING(f'  - {warning}'))

        if report.errors:
            raise CommandError('RuleBook integrity validation failed.')
        if options['strict'] and report.warnings:
            raise CommandError('RuleBook integrity validation failed in strict mode.')

        self.stdout.write(self.style.SUCCESS('RuleBook integrity validation passed.'))
