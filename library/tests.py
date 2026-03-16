from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Category, Paragraph, Section, Work
from .parsers import parse_chatgpt_output


SAMPLE_OUTPUT = """1.

עברית:
צלי אש ומצות על מרורים.

English:
"Roasted with fire and unleavened bread, with bitter herbs."

2.

עברית:
משא\"כ כאן כתיב צלי אש ומצות.

English:
However, here it says "roasted with fire and unleavened bread."
"""


class ParserTests(TestCase):
    def test_parses_two_paragraphs(self):
        results = parse_chatgpt_output(SAMPLE_OUTPUT)
        self.assertEqual(len(results), 2)

    def test_paragraph_numbers(self):
        results = parse_chatgpt_output(SAMPLE_OUTPUT)
        self.assertEqual(results[0]['number'], 1)
        self.assertEqual(results[1]['number'], 2)

    def test_hebrew_content(self):
        results = parse_chatgpt_output(SAMPLE_OUTPUT)
        self.assertIn('צלי אש', results[0]['hebrew'])

    def test_english_content(self):
        results = parse_chatgpt_output(SAMPLE_OUTPUT)
        self.assertIn('Roasted with fire', results[0]['english'])

    def test_empty_string(self):
        self.assertEqual(parse_chatgpt_output(''), [])

    def test_missing_hebrew_skipped(self):
        bad = "1.\n\nEnglish:\nOnly English here.\n"
        results = parse_chatgpt_output(bad)
        self.assertEqual(results, [])


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Tanakh Commentaries', slug='tanakh-commentaries')
        self.work = Work.objects.create(
            category=self.category,
            name='Haamek Davar',
            slug='haamek-davar',
        )
        self.section = Section.objects.create(
            work=self.work,
            reference='Exodus 12:8',
            slug='exodus-12-8',
        )
        Paragraph.objects.create(
            section=self.section,
            number=1,
            hebrew_text='עברית כאן',
            english_text='English here',
        )
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'pass')

    def test_index_200(self):
        resp = self.client.get(reverse('library:index'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Tanakh Commentaries')

    def test_category_200(self):
        resp = self.client.get(reverse('library:category', kwargs={'category_slug': 'tanakh-commentaries'}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Haamek Davar')

    def test_work_200(self):
        resp = self.client.get(reverse('library:work', kwargs={
            'category_slug': 'tanakh-commentaries',
            'work_slug': 'haamek-davar',
        }))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Exodus 12:8')

    def test_section_200(self):
        resp = self.client.get(reverse('library:section', kwargs={
            'category_slug': 'tanakh-commentaries',
            'work_slug': 'haamek-davar',
            'section_slug': 'exodus-12-8',
        }))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'עברית כאן')
        self.assertContains(resp, 'English here')

    def test_upload_requires_login(self):
        resp = self.client.get(reverse('library:upload'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/accounts/login/', resp['Location'])

    def test_upload_authenticated_get(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('library:upload'))
        self.assertEqual(resp.status_code, 200)

    def test_upload_creates_paragraphs(self):
        self.client.login(username='admin', password='pass')
        resp = self.client.post(reverse('library:upload'), {
            'category': self.category.pk,
            'work': self.work.pk,
            'reference': 'Exodus 12:9',
            'slug': 'exodus-12-9',
            'order': 1,
            'title': '',
            'content': SAMPLE_OUTPUT,
            'replace_existing': False,
        })
        self.assertEqual(resp.status_code, 302)
        section = Section.objects.get(work=self.work, slug='exodus-12-9')
        self.assertEqual(section.paragraphs.count(), 2)

    def test_upload_replace_existing(self):
        self.client.login(username='admin', password='pass')
        # First upload
        self.client.post(reverse('library:upload'), {
            'category': self.category.pk,
            'work': self.work.pk,
            'reference': 'Exodus 12:8',
            'slug': 'exodus-12-8',
            'order': 0,
            'title': '',
            'content': SAMPLE_OUTPUT,
            'replace_existing': True,
        })
        self.section.refresh_from_db()
        self.assertEqual(self.section.paragraphs.count(), 2)

    def test_category_404(self):
        resp = self.client.get(reverse('library:category', kwargs={'category_slug': 'nonexistent'}))
        self.assertEqual(resp.status_code, 404)

    def test_section_urls(self):
        url = self.section.get_absolute_url()
        self.assertIn('tanakh-commentaries', url)
        self.assertIn('haamek-davar', url)
        self.assertIn('exodus-12-8', url)
