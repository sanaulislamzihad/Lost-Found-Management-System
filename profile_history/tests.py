"""Tests of the profile_history app.

Ten tests, one for each line of the Feature 9 confirmation list in the
SRS and one for each rule that keeps bad data out. Django builds a
separate test database and throws it away afterwards, so nothing here
touches the real db.sqlite3.
"""

import tempfile
from datetime import date
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from core.models import Category, Claim, Item


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
    user.profile.university_id = '201100%s' % len(name)
    user.profile.save()

    return user


def make_image():
    """Build a real PNG in memory for the upload tests.

    :return: the file, ready to be posted.
    :rtype: SimpleUploadedFile.
    """
    buffer = BytesIO()
    Image.new('RGB', (12, 12), 'navy').save(buffer, format='PNG')

    return SimpleUploadedFile('photo.png', buffer.getvalue(), 'image/png')


# The uploads go to a throw-away folder instead of the real media
# folder of the project.
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProfileAndHistoryTest(TestCase):
    """Feature 9: a member reads and corrects their own details, and
    follows everything they have posted and claimed."""

    def setUp(self):
        self.category = Category.objects.get(name='Bags')
        self.member = make_user('nadia')
        self.other = make_user('shuvo')

        self.member.profile.phone_number = '01712345678'
        self.member.profile.save()

        self.profile_url = reverse('my_profile')
        self.history_url = reverse('my_history')

        self.available = Item.objects.create(
            item_name='Blue backpack', category=self.category,
            description='Broken zip.', location='Sports complex',
            date=date(2026, 7, 10), item_type='found',
            status='available', posted_by=self.member,
        )
        self.pending = Item.objects.create(
            item_name='Lost umbrella', category=self.category,
            description='Black, long handle.', location='Library',
            date=date(2026, 7, 2), item_type='lost',
            status='pending', posted_by=self.member,
        )
        self.someone_elses = Item.objects.create(
            item_name='Grey scarf', category=self.category,
            description='Wool.', location='Cafeteria',
            date=date(2026, 7, 5), item_type='found',
            status='available', posted_by=self.other,
        )

        self.client.force_login(self.member)

    def save_profile(self, **fields):
        """Send the profile form with the given fields changed.

        :return: the response of the view.
        :rtype: HttpResponse.
        """
        form = {'full_name': 'Nadia', 'phone_number': '01712345678'}
        form.update(fields)

        return self.client.post(self.profile_url, form)

    def posted_names(self, url):
        """Read the item names the history page is showing.

        :return: the names, sorted.
        :rtype: list.
        """
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        return sorted(item.item_name for item in response.context['items'])

    def test_a_visitor_who_is_not_logged_in_is_sent_to_the_login_page(self):
        """A profile and a history both belong to one member."""
        self.client.logout()

        for url in (self.profile_url, self.history_url):
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('login'), response['Location'])

    def test_the_profile_shows_the_four_details(self):
        """The SRS asks for the name, the ID, the email and the phone."""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nadia')
        self.assertContains(response, self.member.profile.university_id)
        self.assertContains(response, self.member.email)
        self.assertContains(response, '01712345678')

    def test_the_phone_number_can_be_changed(self):
        """The SRS lets a member correct their own phone number."""
        self.save_profile(phone_number='01898765432')

        self.member.profile.refresh_from_db()
        self.assertEqual(self.member.profile.phone_number, '01898765432')

    def test_a_phone_number_that_is_not_one_is_refused(self):
        """The SRS asks for the new data to be checked before saving."""
        response = self.save_profile(phone_number='call me maybe')

        self.assertEqual(response.status_code, 200)
        self.member.profile.refresh_from_db()
        self.assertEqual(self.member.profile.phone_number, '01712345678')

    def test_the_email_and_the_id_cannot_be_changed(self):
        """The SRS locks both of them after registration."""
        old_id = self.member.profile.university_id

        self.save_profile(
            email='somebody.else@northsouth.edu',
            university_id='9999999',
        )

        self.member.refresh_from_db()
        self.member.profile.refresh_from_db()
        self.assertEqual(self.member.email, 'nadia@northsouth.edu')
        self.assertEqual(self.member.profile.university_id, old_id)

    def test_a_profile_photo_is_saved(self):
        """The SRS lets a member put a picture on their profile."""
        self.save_profile(photo=make_image())

        self.member.profile.refresh_from_db()
        self.assertTrue(self.member.profile.photo)

    def test_a_file_that_is_not_a_picture_is_refused(self):
        """A model ImageField checks nothing, so the view has to."""
        pretender = SimpleUploadedFile(
            'photo.png', b'this is not a picture', 'image/png',
        )
        response = self.save_profile(photo=pretender)

        self.assertEqual(response.status_code, 200)
        self.member.profile.refresh_from_db()
        self.assertFalse(self.member.profile.photo)

    def test_the_history_lists_only_the_posts_of_this_member(self):
        """Somebody else's post is nobody else's history."""
        self.assertEqual(
            self.posted_names(self.history_url),
            ['Blue backpack', 'Lost umbrella'],
        )

    def test_the_history_can_be_filtered_by_status(self):
        """The SRS names all four statuses as filters."""
        self.assertEqual(
            self.posted_names(self.history_url + '?status=available'),
            ['Blue backpack'],
        )
        self.assertEqual(
            self.posted_names(self.history_url + '?status=pending'),
            ['Lost umbrella'],
        )
        self.assertEqual(
            self.posted_names(self.history_url + '?status=claimed'), [],
        )
        # A status that does not exist must not empty the page.
        self.assertEqual(
            len(self.posted_names(self.history_url + '?status=banana')), 2,
        )

    def test_the_history_lists_the_claims_with_their_status(self):
        """The SRS asks for the claims of the member on this page too."""
        Claim.objects.create(
            item=self.someone_elses,
            claimed_by=self.member,
            proof='My initials are on the label.',
        )
        response = self.client.get(self.history_url)

        self.assertEqual(len(response.context['claims']), 1)
        self.assertContains(response, 'Grey scarf')
        self.assertContains(response, 'Pending')
