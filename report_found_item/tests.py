"""Tests for the report_found_item app."""

import tempfile
from datetime import date
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from core.models import Category, Claim, Item


# Uploaded photos go to a throw-away folder, not the real media folder.
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ReportFoundItemTest(TestCase):

    def setUp(self):
        self.bags = Category.objects.get(name='Bags')

        self.finder = User.objects.create_user(
            username='sadia@northsouth.edu',
            email='sadia@northsouth.edu',
            password='Str0ngPassw0rd!',
            first_name='Sadia',
        )
        self.stranger = User.objects.create_user(
            username='imran@northsouth.edu',
            email='imran@northsouth.edu',
            password='Str0ngPassw0rd!',
            first_name='Imran',
        )

        self.client.force_login(self.finder)

    def test_a_visitor_who_is_not_logged_in_cannot_report(self):
        """Reporting needs an account, so the form is not open to all."""
        self.client.logout()

        response = self.client.get('/items/found')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response['Location'])

    def test_a_good_form_saves_the_post(self):
        """A found item post starts out available for claiming."""
        self.client.post('/items/found', {
            'item_name': 'Blue backpack',
            'category': self.bags.pk,
            'description': 'Broken zip, maths notes inside.',
            'location': 'Sports complex',
            'date': '2026-07-10',
        })

        item = Item.objects.get(item_name='Blue backpack')
        self.assertEqual(item.item_type, 'found')
        self.assertEqual(item.status, 'available')
        self.assertEqual(item.posted_by, self.finder)

    def test_all_the_fields_are_needed(self):
        """An empty field should not create a post."""
        self.client.post('/items/found', {
            'item_name': '',
            'category': self.bags.pk,
            'description': 'Broken zip, maths notes inside.',
            'location': 'Sports complex',
            'date': '2026-07-10',
        })

        self.assertEqual(Item.objects.count(), 0)

    def test_a_category_has_to_be_chosen(self):
        """The category is what the search filters are built on."""
        self.client.post('/items/found', {
            'item_name': 'Blue backpack',
            'category': '',
            'description': 'Broken zip, maths notes inside.',
            'location': 'Sports complex',
            'date': '2026-07-10',
        })

        self.assertEqual(Item.objects.count(), 0)

    def test_a_date_in_the_future_is_refused(self):
        """Nothing was found on a day that has not happened yet."""
        self.client.post('/items/found', {
            'item_name': 'Blue backpack',
            'category': self.bags.pk,
            'description': 'Broken zip, maths notes inside.',
            'location': 'Sports complex',
            'date': '2099-01-01',
        })

        self.assertEqual(Item.objects.count(), 0)

    def test_the_post_shows_up_in_the_item_list(self):
        """A new post is there for everybody to search."""
        self.client.post('/items/found', {
            'item_name': 'Blue backpack',
            'category': self.bags.pk,
            'description': 'Broken zip, maths notes inside.',
            'location': 'Sports complex',
            'date': '2026-07-10',
        })

        response = self.client.get('/items')
        self.assertContains(response, 'Blue backpack')

    def test_a_photo_can_be_uploaded(self):
        """The SRS lets the finder add a picture of the item."""
        buffer = BytesIO()
        Image.new('RGB', (12, 12), 'navy').save(buffer, format='PNG')
        photo = SimpleUploadedFile('bag.png', buffer.getvalue(), 'image/png')

        self.client.post('/items/found', {
            'item_name': 'Blue backpack',
            'category': self.bags.pk,
            'description': 'Broken zip, maths notes inside.',
            'location': 'Sports complex',
            'date': '2026-07-10',
            'image': photo,
        })

        item = Item.objects.get(item_name='Blue backpack')
        self.assertTrue(item.image)

    def test_only_the_owner_can_edit_the_post(self):
        """Somebody else's post is none of your business."""
        item = Item.objects.create(
            item_name='Blue backpack',
            category=self.bags,
            description='Broken zip, maths notes inside.',
            location='Sports complex',
            date=date(2026, 7, 10),
            item_type='found',
            status='available',
            posted_by=self.finder,
        )

        self.client.force_login(self.stranger)
        response = self.client.get('/items/found/%s/edit' % item.pk)

        self.assertEqual(response.status_code, 302)

    def test_deleting_asks_for_confirmation_first(self):
        """Opening the delete page only shows the question."""
        item = Item.objects.create(
            item_name='Blue backpack',
            category=self.bags,
            description='Broken zip, maths notes inside.',
            location='Sports complex',
            date=date(2026, 7, 10),
            item_type='found',
            status='available',
            posted_by=self.finder,
        )

        self.client.get('/items/found/%s/delete' % item.pk)
        self.assertTrue(Item.objects.filter(pk=item.pk).exists())

        self.client.post('/items/found/%s/delete' % item.pk)
        self.assertFalse(Item.objects.filter(pk=item.pk).exists())

    def test_the_status_becomes_claimed_when_a_claim_is_approved(self):
        """The SRS closes the post by itself once the item is handed
        over."""
        item = Item.objects.create(
            item_name='Blue backpack',
            category=self.bags,
            description='Broken zip, maths notes inside.',
            location='Sports complex',
            date=date(2026, 7, 10),
            item_type='found',
            status='available',
            posted_by=self.finder,
        )
        claim = Claim.objects.create(
            item=item,
            claimed_by=self.stranger,
            proof='My name is written inside the front pocket.',
        )

        claim.approve(self.finder)

        item.refresh_from_db()
        self.assertEqual(item.status, 'claimed')
