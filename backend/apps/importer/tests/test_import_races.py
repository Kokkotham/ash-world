from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from apps.importer.management.commands.import_rule_sources import build_race_rules
from apps.rules.models import RuleCategory, RuleEntry


class ImportRaceBuilderTests(SimpleTestCase):
    def test_build_race_rules_creates_one_rule_per_race(self):
        category = RuleCategory(slug='races', name='种族')
        data = {
            'races': [
                {
                    'id': 'human',
                    'name': '纳露安人类',
                    'languages': ['商用语'],
                    'body_size': '5级体型',
                    'adult_age': '20岁',
                    'resistances': {'水': 3},
                    'attribute_bonus': {'躯魄': 1},
                    'abilities': ['智慧研习'],
                    'description': '测试描述',
                }
            ]
        }

        rules = build_race_rules(data, category)

        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]['slug'], 'race-human')
        self.assertEqual(rules[0]['title'], '种族：纳露安人类')
        self.assertEqual(rules[0]['content_blocks'][0]['type'], 'profile')


class ImportRacePipelineTests(TestCase):
    def test_import_rulebook_race_entries(self):
        call_command('import_rulebook', include='races', stdout=StringIO())

        self.assertEqual(RuleEntry.objects.filter(entry_type='race').count(), 16)
        self.assertTrue(RuleEntry.objects.filter(slug='race-human').exists())
        self.assertTrue(RuleEntry.objects.filter(slug='race-hybrid').exists())
