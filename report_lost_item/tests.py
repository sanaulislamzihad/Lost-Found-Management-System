"""Tests of the report_lost_item app.

Ten tests, one for each line of the Feature 3 confirmation list in the
SRS and one for each rule that keeps bad data out. Django builds a
separate test database and throws it away afterwards, so nothing here
touches the real db.sqlite3.
"""

from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import Category, Item


def make_user(name):
    """Create a member the way registration would.

    Registration saves the email as the username as well, so the tests
    build their members the same way.

    :param name: the part of the email before the @.
    :type name: str.
    :return: the new member.
    :rtype: User.
    """
    email = '%s@northsouth.edu' % name
    user = User.objects.create_user(
        username=email,
        email=email,
        password='Str0ngPassw0rd!',
        first_name=name.title(),
    )

    return user


class ReportLostItemTest(TestCase):
    """Feature 3: a member posts what they lost, corrects it, closes it
    when it comes back, or takes it down."""

    def setUp(self):
        self.bags = Category.objects.get(name='Bags')
        self.docs = Category.objects.get(name='Documents')

        self.owner = make_user('rumana')
        self.stranger = make_user('imran')

        self.url = reverse('report_lost_item')
        self.client.force_login(self.owner)

    def good_form(self, **changed):
        """Build a form that should be accepted, with any field changed.

        :return: the fields to post.
        :rtype: dict.
        """
        form = {
            'item_name': 'Black leather wallet',
            'category': self.bags.pk,
            'description': 'Bi-fold, worn corners, blue stitching inside.',
            'location': 'Central library, 2nd floor',
            'date': '2026-07-12',
        }
        form.update(changed)

        return form

    def make_post(self, **changed):
        """Create a lost post straight in the database.

        :return: the new post.
        :rtype: Item.
        """
        fields = {
            'item_name': 'Lost umbrella',
            'category': self.bags,
            'description': 'Black, long handle.',
            'location': 'Library',
            'date': date(2026, 7, 2),
            'item_type': 'lost',
            'status': 'pending',
            'posted_by': self.owner,
        }
        fields.update(changed)

        return Item.objects.create(**fields)

    def test_a_visitor_who_is_not_logged_in_is_sent_to_the_login_page(self):
        """A post has to belong to somebody, so it needs an account."""
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_the_form_opens(self):
        """The five boxes and the photo box are all on the page."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="item_name"')
        self.assertContains(response, 'name="category"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="location"')
        self.assertContains(response, 'name="date"')
        self.assertContains(response, 'name="image"')

    def test_a_good_form_is_saved_as_pending(self):
        """The SRS asks for a lost post to start with the status
        "Pending" and to show up in the item list."""
        response = self.client.post(self.url, self.good_form())
        item = Item.objects.filter(posted_by=self.owner).first()

        self.assertIsNotNone(item)
        self.assertEqual(item.item_type, 'lost')
        self.assertEqual(item.status, 'pending')
        self.assertEqual(response.status_code, 302)

        listed = self.client.get(reverse('item_list'))
        self.assertContains(listed, 'Black leather wallet')

    def test_every_required_field_is_checked_on_the_server(self):
        """The template marks them required, which only stops an honest
        browser, so the view checks them again."""
        empty = {
            'item_name': '',
            'category': '',
            'description': '',
            'location': '',
            'date': '',
        }

        for field, value in empty.items():
            with self.subTest(field=field):
                response = self.client.post(
                    self.url, self.good_form(**{field: value}),
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(Item.objects.count(), 0)

    def test_a_date_that_cannot_be_right_is_refused(self):
        """Nothing was lost in the future, and 31 February is not a day."""
        for bad_date in ('2099-01-01', 'yesterday', '2026-02-31'):
            with self.subTest(date=bad_date):
                response = self.client.post(
                    self.url, self.good_form(date=bad_date),
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(Item.objects.count(), 0)

    def test_the_owner_can_edit_their_own_post(self):
        """The SRS lets a member correct their own report."""
        item = self.make_post()
        url = reverse('edit_lost_item', args=[item.pk])

        filled = self.client.get(url)
        self.assertContains(filled, 'Lost umbrella')

        self.client.post(url, self.good_form(
            item_name='Lost black umbrella',
            category=self.docs.pk,
            location='Cafeteria',
        ))
        item.refresh_from_db()

        self.assertEqual(item.item_name, 'Lost black umbrella')
        self.assertEqual(item.category_id, self.docs.pk)
        self.assertEqual(item.location, 'Cafeteria')

    def test_nobody_else_can_edit_or_delete_the_post(self):
        """The SRS says only the member who wrote it may change it."""
        item = self.make_post()
        self.client.force_login(self.stranger)

        edit = self.client.get(reverse('edit_lost_item', args=[item.pk]))
        self.assertEqual(edit.status_code, 302)

        self.client.post(reverse('delete_lost_item', args=[item.pk]))
        self.assertTrue(Item.objects.filter(pk=item.pk).exists())

    def test_a_post_is_deleted_only_after_the_question(self):
        """The SRS asks for a confirmation before deleting."""
        item = self.make_post()
        url = reverse('delete_lost_item', args=[item.pk])

        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Item.objects.filter(pk=item.pk).exists())

        self.client.post(url)
        self.assertFalse(Item.objects.filter(pk=item.pk).exists())

    def test_the_owner_can_mark_the_post_as_resolved(self):
        """The SRS keeps a recovered report in the history instead of
        deleting it, so it only changes status."""
        item = self.make_post()

        self.client.post(reverse('resolve_lost_item', args=[item.pk]))
        item.refresh_from_db()

        self.assertEqual(item.status, 'resolved')
        self.assertTrue(Item.objects.filter(pk=item.pk).exists())

    def test_resolving_needs_a_button_and_works_only_once(self):
        """A link followed by accident must not close a report, and a
        closed report cannot be closed a second time."""
        item = self.make_post()
        url = reverse('resolve_lost_item', args=[item.pk])

        self.client.get(url)
        item.refresh_from_db()
        self.assertEqual(item.status, 'pending')

        self.client.post(url)
        item.refresh_from_db()
        self.assertEqual(item.status, 'resolved')

        # A second press changes nothing and says so.
        response = self.client.post(url, follow=True)
        item.refresh_from_db()
        self.assertEqual(item.status, 'resolved')
        self.assertContains(response, 'already closed')

    def test_the_owner_alone_sees_the_buttons_on_the_post(self):
        """The detail page offers edit, delete and resolve to the member
        who wrote the post, and to nobody else."""
        item = self.make_post()
        url = reverse('item_detail', args=[item.pk])

        mine = self.client.get(url)
        self.assertContains(mine, 'Edit this post')
        self.assertContains(mine, 'I got it back')

        self.client.force_login(self.stranger)
        theirs = self.client.get(url)
        self.assertNotContains(theirs, 'Edit this post')
        self.assertNotContains(theirs, 'I got it back')
        # A lost post is not something anybody can claim either.
        self.assertNotContains(theirs, 'This is mine')
