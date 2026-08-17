"""
This module is used to hold the createdemousers command.

The database file is not kept in the repository, so a fresh clone has
no accounts at all and there is no way to reach the Admin pages or the
claim queue. This command makes one account for each role, so the whole
system can be tried out straight after cloning.
"""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# The email is the username as well, because that is what registration
# does and what the login box on the site expects.
DEMO_USERS = [
    {
        'email': 'admin@northsouth.edu',
        'name': 'Admin',
        'role': 'admin',
        'password': 'admin123456',
        'superuser': True,
    },
    {
        'email': 'officer@northsouth.edu',
        'name': 'Security Officer',
        'role': 'officer',
        'password': 'officer123456',
        'superuser': False,
    },
    {
        'email': 'student@northsouth.edu',
        'name': 'Student',
        'role': 'student',
        'password': 'student123456',
        'superuser': False,
    },
]


class Command(BaseCommand):
    """
    This class is used to create one demo account for each role.
    """

    help = 'Create a demo account for each role, for local testing only.'

    def handle(self, *args, **options):
        """
        This method is used to make the accounts, or to reset them when
        they are already there.

        :return: nothing, it writes what it did to the console.
        :rtype: None.
        """
        for demo in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=demo['email'],
                defaults={'email': demo['email']},
            )

            user.email = demo['email']
            user.first_name = demo['name']
            user.is_superuser = demo['superuser']
            # A superuser also needs is_staff to open Django's own site.
            user.is_staff = demo['superuser']
            user.is_active = True
            # set_password hashes it, so the plain text is never saved.
            user.set_password(demo['password'])
            user.save()

            # The profile row is already there because of the post_save
            # signal in the core app.
            user.profile.role = demo['role']
            user.profile.save()

            self.stdout.write(
                '%s  %s  (%s)'
                % ('created' if created else 'reset  ',
                   demo['email'],
                   demo['role'])
            )

        self.stdout.write(self.style.SUCCESS(
            'Demo accounts ready. These are for local testing only.'
        ))
