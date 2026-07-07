from django.test import SimpleTestCase

from apps.importer.management.commands.import_rule_sources import (
    build_core_attribute_rules,
    build_race_rules,
)
from apps.rules.models import RuleCategory


class ImportRuleSourcesBuilderTests(SimpleTestCase):
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
