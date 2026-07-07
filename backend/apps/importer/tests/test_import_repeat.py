from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.rules.models import RuleBook, RuleChapter, RuleContentBlock, RuleEntry, RuleSection


class ImportRuleBookRepeatTests(TestCase):
    def test_import_rulebook_is_repeatable_without_duplicates(self):
        call_command('import_rulebook', include='core,races', stdout=StringIO())
        first_counts = self.counts()

        call_command('import_rulebook', include='core,races', stdout=StringIO())
        second_counts = self.counts()

        self.assertEqual(first_counts, second_counts)
        self.assertEqual(second_counts, {
            'books': 1,
            'chapters': 8,
            'sections': 93,
            'entries': 25,
            'blocks': 2623,
        })

    def counts(self):
        return {
            'books': RuleBook.objects.count(),
            'chapters': RuleChapter.objects.count(),
            'sections': RuleSection.objects.count(),
            'entries': RuleEntry.objects.count(),
            'blocks': RuleContentBlock.objects.count(),
        }
