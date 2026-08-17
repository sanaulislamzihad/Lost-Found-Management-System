"""Tests of the admin_panel app.

Ten tests, one for each line of the Feature 10 confirmation list in the
SRS and one for each rule that keeps everybody else out. Django builds
a separate test database and throws it away afterwards, so nothing here
touches the real db.sqlite3.
"""

from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import Category, Claim, Item


def make_user(name, role='student'):
    """Create a member the way registration would.

    :param name: the part of the email before the @.
    :type name: str.
    :param role: the role to put on the profile.
    :type role: str.
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
    user.profile.role = role
    user.profile.save()

    return user


class ManagementTest(TestCase):
    """Feature 10: the Admin looks after the members, the posts and the
    categories, reads the statistics and exports the report."""

    def setUp(self):
        self.bags = Category.objects.get(name='Bags')
        self.docs = Category.objects.get(name='Documents')

        self.boss = make_user('boss', role='admin')
        self.member = make_user('rakib')
        self.claimant = make_user('mim')

        self.found = Item.objects.create(
            item_name='Blue backpack', category=self.bags,
            description='Broken zip.', location='Sports complex',
            date=date(2026, 7, 10), item_type='found',
            status='available', posted_by=self.member,
        )
        self.lost = Item.objects.create(
            item_name='NSU ID card', category=self.docs,
            description='CSE department.', location='Bus stop 3',
            date=date(2026, 6, 2), item_type='lost',
            status='pending', posted_by=self.claimant,
        )
        self.claim = Claim.objects.create(
            item=self.found, claimed_by=self.claimant,
            proof='My name is on the label.',
        )

        self.client.force_login(self.boss)

    def post_names(self, url):
        """Read the item names the management list is showing.

        :return: the names, sorted.
        :rtype: list.
        """
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        return sorted(item.item_name for item in response.context['items'])

    def test_the_management_pages_are_open_to_an_admin_alone(self):
        """A visitor is sent to log in, a member gets 403, an Admin and
        a Django superuser are let in."""
        pages = [
            reverse('manage_dashboard'),
            reverse('manage_users'),
            reverse('manage_posts'),
            reverse('manage_categories'),
            reverse('manage_report'),
        ]
        root = User.objects.create_superuser(
            username='root@northsouth.edu',
            email='root@northsouth.edu',
            password='Str0ngPassw0rd!',
        )

        for url in pages:
            with self.subTest(url=url):
                self.client.logout()
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response['Location'])

                self.client.force_login(self.member)
                self.assertEqual(self.client.get(url).status_code, 403)

                self.client.force_login(self.boss)
                self.assertEqual(self.client.get(url).status_code, 200)

                self.client.force_login(root)
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_the_statistics_of_the_whole_system_are_right(self):
        """The SRS names the lost, the found and the successful claims."""
        response = self.client.get(reverse('manage_dashboard'))

        self.assertEqual(response.context['total_lost'], 1)
        self.assertEqual(response.context['total_found'], 1)
        self.assertEqual(response.context['successful_claims'], 0)
        self.assertEqual(response.context['pending_claims'], 1)

        self.claim.approve(self.boss)
        response = self.client.get(reverse('manage_dashboard'))
        self.assertEqual(response.context['successful_claims'], 1)

    def test_every_member_is_listed_with_their_role(self):
        """The SRS asks for the list of members with role and status."""
        response = self.client.get(reverse('manage_users'))
        listed = {
            member.username: member.profile.role
            for member in response.context['users']
        }

        self.assertEqual(len(listed), 3)
        self.assertEqual(listed['rakib@northsouth.edu'], 'student')
        self.assertEqual(listed['boss@northsouth.edu'], 'admin')

    def test_the_role_of_a_member_can_be_changed(self):
        """The SRS names all four roles as choices for the Admin."""
        self.client.post(
            reverse('manage_user_role', args=[self.member.pk]),
            {'role': 'officer'},
        )
        self.member.profile.refresh_from_db()
        self.assertEqual(self.member.profile.role, 'officer')

        # A role nobody has heard of changes nothing.
        self.client.post(
            reverse('manage_user_role', args=[self.member.pk]),
            {'role': 'wizard'},
        )
        self.member.profile.refresh_from_db()
        self.assertEqual(self.member.profile.role, 'officer')

    def test_an_admin_cannot_lock_themselves_out(self):
        """Taking away their own role or account shuts these pages for
        good, because nobody else can put either of them back."""
        self.client.post(
            reverse('manage_user_role', args=[self.boss.pk]),
            {'role': 'student'},
        )
        self.client.post(reverse('manage_user_active', args=[self.boss.pk]))
        self.client.post(reverse('manage_user_delete', args=[self.boss.pk]))

        self.boss.refresh_from_db()
        self.boss.profile.refresh_from_db()
        self.assertEqual(self.boss.profile.role, 'admin')
        self.assertTrue(self.boss.is_active)
        self.assertTrue(User.objects.filter(pk=self.boss.pk).exists())

    def test_an_account_can_be_switched_off_and_on_again(self):
        """Django refuses the login of a user whose is_active is off."""
        url = reverse('manage_user_active', args=[self.member.pk])

        self.client.post(url)
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)

        self.client.post(url)
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_active)

    def test_a_member_is_deleted_only_after_the_question(self):
        """Opening the page asks, and the button does it."""
        url = reverse('manage_user_delete', args=[self.member.pk])

        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(User.objects.filter(pk=self.member.pk).exists())

        self.client.post(url)
        self.assertFalse(User.objects.filter(pk=self.member.pk).exists())

    def test_any_post_can_be_listed_filtered_and_edited(self):
        """The SRS lets the Admin work on a post of any member."""
        posts = reverse('manage_posts')

        self.assertEqual(
            self.post_names(posts), ['Blue backpack', 'NSU ID card'],
        )
        self.assertEqual(self.post_names(posts + '?type=lost'),
                         ['NSU ID card'])
        self.assertEqual(self.post_names(posts + '?status=available'),
                         ['Blue backpack'])

        self.client.post(
            reverse('manage_post_edit', args=[self.found.pk]),
            {
                'item_name': 'Blue rucksack',
                'category': self.docs.pk,
                'description': 'Broken zip, fixed now.',
                'location': 'Security office',
                'date': '2026-07-11',
                'item_type': 'found',
                'status': 'resolved',
            },
        )
        self.found.refresh_from_db()
        self.assertEqual(self.found.item_name, 'Blue rucksack')
        self.assertEqual(self.found.category_id, self.docs.pk)
        self.assertEqual(self.found.status, 'resolved')

    def test_a_post_is_removed_only_after_the_question(self):
        """Opening the page asks, and the button does it."""
        url = reverse('manage_post_delete', args=[self.found.pk])

        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Item.objects.filter(pk=self.found.pk).exists())

        self.client.post(url)
        self.assertFalse(Item.objects.filter(pk=self.found.pk).exists())

    def test_categories_can_be_added_renamed_and_removed(self):
        """A category still holding posts stays, because the foreign
        key is PROTECT and no post may be left without one."""
        self.client.post(reverse('manage_categories'), {'name': 'Keys'})
        keys = Category.objects.get(name='Keys')

        self.client.post(
            reverse('manage_category_rename', args=[keys.pk]),
            {'name': 'Keys and cards'},
        )
        keys.refresh_from_db()
        self.assertEqual(keys.name, 'Keys and cards')

        self.client.post(reverse('manage_category_delete', args=[keys.pk]))
        self.assertFalse(Category.objects.filter(pk=keys.pk).exists())

        response = self.client.post(
            reverse('manage_category_delete', args=[self.bags.pk]),
            follow=True,
        )
        self.assertTrue(Category.objects.filter(pk=self.bags.pk).exists())
        self.assertContains(response, 'cannot be removed')

    def test_the_activity_report_comes_out_as_a_csv_file(self):
        """One heading row and then one row for every post."""
        response = self.client.get(reverse('manage_report'))
        lines = [
            line for line in response.content.decode().splitlines() if line
        ]

        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertTrue(lines[0].startswith('Id,Type,Item,Category'))
        self.assertEqual(len(lines), 1 + Item.objects.count())
        self.assertIn('Blue backpack', response.content.decode())
