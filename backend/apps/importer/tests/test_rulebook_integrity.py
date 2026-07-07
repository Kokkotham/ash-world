from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.rules.models import RuleBook, RuleContentBlock, RuleEntry


class RuleBookIntegrityCommandTests(TestCase):
    def test_validate_rulebook_passes_after_import(self):
        call_command('import_rulebook', include='core,races', stdout=StringIO())

        output = StringIO()
        call_command('validate_rulebook', stdout=output)

        self.assertIn('RuleBook integrity validation passed.', output.getvalue())

    def test_validate_rulebook_strict_passes_after_import(self):
        call_command('import_rulebook', include='core,races', stdout=StringIO())

        output = StringIO()
        call_command('validate_rulebook', strict=True, stdout=output)

        self.assertIn('Warnings: 0', output.getvalue())

    def test_validate_rulebook_fails_without_rulebook(self):
        with self.assertRaises(CommandError):
            call_command('validate_rulebook', stdout=StringIO())

    def test_validate_rulebook_detects_ownerless_content_block(self):
        call_command('import_rulebook', include='core,races', stdout=StringIO())
        RuleContentBlock.objects.create(block_type='paragraph', content='orphan', sort_order=10)

        with self.assertRaises(CommandError):
            call_command('validate_rulebook', stdout=StringIO())

    def test_validate_rulebook_detects_entry_without_content_blocks(self):
        call_command('import_rulebook', include='core,races', stdout=StringIO())
        entry = RuleEntry.objects.first()
        entry.content_blocks.all().delete()

        with self.assertRaises(CommandError):
            call_command('validate_rulebook', stdout=StringIO())

    def test_validate_rulebook_strict_fails_on_warning(self):
        call_command('import_rulebook', include='core,races', stdout=StringIO())
        RuleBook.objects.first().chapters.all().delete()

        with self.assertRaises(CommandError):
            call_command('validate_rulebook', strict=True, stdout=StringIO())
