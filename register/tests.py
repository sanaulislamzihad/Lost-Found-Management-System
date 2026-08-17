"""
This module is used to test the register app.
"""

from django.contrib.auth.models import User
from django.test import TestCase


class RegisterTest(TestCase):
    """
    This class is used to test the registration of a new account.
    """

    def test_all_four_fields_are_needed(self):
        """
        This method is used to test that an empty field does not create
        an account.
        """
        self.client.post('/register', {
            'full_name': '',
            'university_id': '2011234042',
            'email': 'rina@northsouth.edu',
            'password': 'Str0ngPassw0rd!',
        })

        self.assertEqual(User.objects.count(), 0)

    def test_the_email_must_be_valid(self):
        """
        This method is used to test that a wrong email does not create
        an account.
        """
        self.client.post('/register', {
            'full_name': 'Rina Akter',
            'university_id': '2011234042',
            'email': 'rina-at-northsouth',
            'password': 'Str0ngPassw0rd!',
        })

        self.assertEqual(User.objects.count(), 0)

    def test_a_short_password_is_refused(self):
        """
        This method is used to test that a password under eight
        characters is not accepted.
        """
        self.client.post('/register', {
            'full_name': 'Rina Akter',
            'university_id': '2011234042',
            'email': 'rina@northsouth.edu',
            'password': 'abc123',
        })

        self.assertEqual(User.objects.count(), 0)

    def test_the_same_email_or_id_cannot_be_used_again(self):
        """
        This method is used to test that only the first account is
        created.
        """
        self.client.post('/register', {
            'full_name': 'Rina Akter',
            'university_id': '2011234042',
            'email': 'rina@northsouth.edu',
            'password': 'Str0ngPassw0rd!',
        })

        # The same email again.
        self.client.post('/register', {
            'full_name': 'Someone Else',
            'university_id': '2011999999',
            'email': 'rina@northsouth.edu',
            'password': 'Str0ngPassw0rd!',
        })

        # A new email, but the same ID.
        self.client.post('/register', {
            'full_name': 'Someone Else',
            'university_id': '2011234042',
            'email': 'other@northsouth.edu',
            'password': 'Str0ngPassw0rd!',
        })

        self.assertEqual(User.objects.count(), 1)

    def test_the_password_is_stored_hashed(self):
        """
        This method is used to test that the password is not kept as
        plain text.
        """
        self.client.post('/register', {
            'full_name': 'Rina Akter',
            'university_id': '2011234042',
            'email': 'rina@northsouth.edu',
            'password': 'Str0ngPassw0rd!',
        })

        user = User.objects.get(username='rina@northsouth.edu')
        self.assertNotEqual(user.password, 'Str0ngPassw0rd!')
        self.assertTrue(user.check_password('Str0ngPassw0rd!'))
