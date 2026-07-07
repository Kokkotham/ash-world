from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from apps.importer.management.commands.import_rulebook import stable_slug
from apps.rules.models import RuleBook, RuleChapter, RuleContentBlock, RuleEntry, RuleSection


class ImportRuleBookBuilderTests(SimpleTestCase):
    def test_stable_slug_keeps_chinese_source_keys_unique(self):
        human_slug = stable_slug('ch2_纳露安人类', 'human')
        elf_slug = stable_slug('ch2_精灵', 'elf')

        self.assertNotEqual(human_slug, elf_slug)
        self.assertTrue(human_slug.startswith('ch2-'))
        self.assertTrue(elf_slug.startswith('ch2-'))

    def test_stable_slug_preserves_ascii_source_keys(self):
        self.assertEqual(stable_slug('ch1_main_attr', 'main attr'), 'ch1-main-attr')


class ImportRuleBookPipelineTests(TestCase):
    def test_import_rulebook_creates_reader_tree(self):
        call_command('import_rulebook', include='core,races', stdout=StringIO())

        self.assertEqual(RuleBook.objects.count(), 1)
        self.assertEqual(RuleChapter.objects.count(), 8)
        self.assertEqual(RuleSection.objects.count(), 93)
        self.assertEqual(RuleEntry.objects.count(), 25)
        self.assertEqual(RuleContentBlock.objects.count(), 2623)
        self.assertTrue(RuleSection.objects.filter(source_key='ch1_main_attr').exists())
        self.assertTrue(RuleSection.objects.filter(source_key='ch2_精灵').exists())
