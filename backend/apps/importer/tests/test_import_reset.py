from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.rules.models import RuleBook, RuleChapter, RuleContentBlock, RuleEntry, RuleSection


class ImportRuleBookResetTests(TestCase):
    def test_import_rulebook_reset_rebuilds_same_dataset(self):
        call_command('import_rulebook', include='core,races', stdout=StringIO())
        first_counts = self.counts()

        call_command('import_rulebook', include='core,races', reset=True, stdout=StringIO())
        reset_counts = self.counts()

        self.assertEqual(first_counts, reset_counts)
        self.assertEqual(reset_counts['books'], 1)
        self.assertEqual(reset_counts['sections'], 93)
        self.assertEqual(reset_counts['entries'], 25)

    def counts(self):
        return {
            'books': RuleBook.objects.count(),
            'chapters': RuleChapter.objects.count(),
            'sections': RuleSection.objects.count(),
            'entries': RuleEntry.objects.count(),
            'blocks': RuleContentBlock.objects.count(),
        }
