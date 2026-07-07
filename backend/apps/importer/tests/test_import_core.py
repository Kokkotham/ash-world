from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from apps.importer.management.commands.import_rule_sources import build_core_attribute_rules
from apps.rules.models import RuleCategory, RuleEntry


class ImportCoreBuilderTests(SimpleTestCase):
    def test_build_core_attribute_rules_uses_stable_slugs(self):
        category = RuleCategory(slug='core-attributes', name='核心属性')
        data = {
            'version': 'test',
            'attributes': {
                '躯魄': {
                    'name': '躯魄',
                    'abbr': 'BOD',
                    'derived': {'HP': {'formula': '躯魄 × 10'}},
                }
            },
            'derived_formulas': {'速度': 'floor(敏韧/2)'},
        }

        rules = build_core_attribute_rules(data, category)

        self.assertEqual(rules[0]['slug'], 'core-attribute-bod')
        self.assertEqual(rules[0]['title'], '核心属性：躯魄')
        self.assertEqual(rules[0]['raw_data']['abbr'], 'BOD')
        self.assertEqual(rules[1]['slug'], 'core-derived-formulas')


class ImportCorePipelineTests(TestCase):
    def test_import_rulebook_core_entries(self):
        call_command('import_rulebook', include='core', stdout=StringIO())

        self.assertEqual(RuleEntry.objects.filter(entry_type='attribute').count(), 4)
        self.assertTrue(RuleEntry.objects.filter(slug='core-attribute-bod').exists())
        self.assertEqual(RuleEntry.objects.filter(metadata__source_file='01_核心属性_结构化.json').count(), 9)
