from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient


class RuleBookApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_rule_sources', stdout=StringIO())
        call_command('import_rulebook', include='core,races', stdout=StringIO())

    def setUp(self):
        self.client = APIClient()

    def test_rulebooks_list_and_detail(self):
        response = self.client.get('/api/v1/rulebooks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['slug'], 'embers-world-core')

        detail = self.client.get('/api/v1/rulebooks/embers-world-core/')
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['title'], '灰烬世界规则书')

    def test_rulebook_chapters_returns_tree(self):
        response = self.client.get('/api/v1/rulebooks/embers-world-core/chapters/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['rulebook']['slug'], 'embers-world-core')
        self.assertEqual(len(response.data['chapters']), 8)
        self.assertIn('sections', response.data['chapters'][1])

    def test_rulebook_chapter_detail(self):
        response = self.client.get('/api/v1/rulebook-chapters/ch1/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], 'ch1')
        self.assertGreater(len(response.data['content_blocks']), 0)
        self.assertGreater(len(response.data['sections']), 0)

    def test_rulebook_section_detail(self):
        response = self.client.get('/api/v1/rulebook-sections/ch1-main-attr/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['source_key'], 'ch1_main_attr')
        self.assertIn('children', response.data)
        self.assertIn('entries', response.data)
        self.assertIn('content_blocks', response.data)

    def test_rulebook_entry_detail(self):
        response = self.client.get('/api/v1/rulebook-entries/core-attribute-bod/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['slug'], 'core-attribute-bod')
        self.assertEqual(response.data['entry_type'], 'attribute')
        self.assertGreater(len(response.data['content_blocks']), 0)

    def test_existing_rule_apis_still_work(self):
        categories = self.client.get('/api/v1/rule-categories/')
        rules = self.client.get('/api/v1/rules/')

        self.assertEqual(categories.status_code, 200)
        self.assertEqual(rules.status_code, 200)
        self.assertGreaterEqual(categories.data['count'], 2)
        self.assertGreaterEqual(rules.data['count'], 25)
