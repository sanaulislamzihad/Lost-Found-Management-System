"""Tests of the verify_claims app.

Ten tests, one for each line of the Feature 7 confirmation list in the
SRS and one for each rule that keeps everybody else out. Django builds
a separate test database and throws it away afterwards, so nothing here
touches the real db.sqlite3.
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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


class VerifyClaimsTest(TestCase):
    """Feature 7: a Security Officer reads the proof beside the item and
    either hands the item over or turns the claim down with a reason."""

    def setUp(self):
        self.bags = Category.objects.get(name='Bags')

        self.officer = make_user('nayeem', role='officer')
        self.boss = make_user('boss', role='admin')
        self.finder = make_user('sadia')
        self.first = make_user('arif')
        self.second = make_user('joya')

        self.item = Item.objects.create(
            item_name='Blue backpack', category=self.bags,
            description='Broken zip, maths notes inside.',
            location='Sports complex', date=date(2026, 7, 10),
            item_type='found', status='available', posted_by=self.finder,
        )

        self.first_claim = Claim.objects.create(
            item=self.item, claimed_by=self.first,
            proof='My name is written inside the front pocket.',
        )
        self.second_claim = Claim.objects.create(
            item=self.item, claimed_by=self.second,
            proof='It has a red sticker on the side.',
        )
        # The first claim is made to look older, so the order the SRS
        # asks for can be checked.
        Claim.objects.filter(pk=self.first_claim.pk).update(
            created_at=timezone.now() - timedelta(days=2),
        )
        self.first_claim.refresh_from_db()

        self.queue_url = reverse('claim_queue')
        self.client.force_login(self.officer)

    def test_the_queue_is_open_to_an_officer_alone(self):
        """A visitor is sent to log in, an ordinary member gets 403, an
        officer, an Admin and a superuser are let in."""
        pages = [
            self.queue_url,
            reverse('review_claim', args=[self.first_claim.pk]),
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

                self.client.force_login(self.first)
                self.assertEqual(self.client.get(url).status_code, 403)

                for allowed in (self.officer, self.boss, root):
                    self.client.force_login(allowed)
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_the_queue_shows_the_pending_claims_oldest_first(self):
        """The SRS asks for the pending claims sorted by date, so the
        person waiting longest is dealt with first."""
        response = self.client.get(self.queue_url)
        listed = [claim.pk for claim in response.context['claims']]

        self.assertEqual(listed, [self.first_claim.pk, self.second_claim.pk])

    def test_the_queue_can_show_the_decided_claims_too(self):
        """Pending is what opens, and the rest are one tab away."""
        self.first_claim.approve(self.officer)

        pending = self.client.get(self.queue_url)
        self.assertEqual(
            [claim.pk for claim in pending.context['claims']], [],
        )

        approved = self.client.get(self.queue_url + '?status=approved')
        self.assertEqual(
            [claim.pk for claim in approved.context['claims']],
            [self.first_claim.pk],
        )

        # A status nobody has heard of falls back to pending.
        junk = self.client.get(self.queue_url + '?status=banana')
        self.assertEqual(junk.context['status'], 'pending')

    def test_the_review_page_shows_the_proof_beside_the_item(self):
        """The SRS asks for both on the same screen."""
        response = self.client.get(
            reverse('review_claim', args=[self.first_claim.pk]),
        )

        self.assertContains(response, 'written inside the front pocket')
        self.assertContains(response, 'Blue backpack')
        self.assertContains(response, 'Sports complex')
        self.assertContains(response, 'Arif')

    def test_the_review_page_lists_the_other_claims_on_the_item(self):
        """Approving one closes the rest, so the officer sees them."""
        response = self.client.get(
            reverse('review_claim', args=[self.first_claim.pk]),
        )
        others = [claim.pk for claim in response.context['other_claims']]

        self.assertEqual(others, [self.second_claim.pk])

    def test_approving_closes_the_item_and_the_other_claims(self):
        """The SRS asks for the item to become "Claimed" and for the
        other pending claims on it to be closed."""
        self.client.post(
            reverse('review_claim', args=[self.first_claim.pk]),
            {'decision': 'approve'},
        )

        self.first_claim.refresh_from_db()
        self.second_claim.refresh_from_db()
        self.item.refresh_from_db()

        self.assertEqual(self.first_claim.status, 'approved')
        self.assertEqual(self.first_claim.reviewed_by, self.officer)
        self.assertEqual(self.item.status, 'claimed')
        self.assertEqual(self.second_claim.status, 'rejected')

    def test_rejecting_needs_a_remark(self):
        """The SRS makes the reason mandatory when rejecting, so the
        claimant is never left without one."""
        url = reverse('review_claim', args=[self.first_claim.pk])

        response = self.client.post(url, {'decision': 'reject',
                                          'remark': '   '})
        self.first_claim.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.first_claim.status, 'pending')

        self.client.post(url, {
            'decision': 'reject',
            'remark': 'The name inside the pocket is not yours.',
        })
        self.first_claim.refresh_from_db()
        self.assertEqual(self.first_claim.status, 'rejected')
        self.assertIn('not yours', self.first_claim.remark)

    def test_everybody_is_told_the_decision_automatically(self):
        """The SRS asks the system to inform the claimant itself."""
        self.client.post(
            reverse('review_claim', args=[self.first_claim.pk]),
            {'decision': 'approve'},
        )

        self.assertEqual(self.first.notifications.count(), 1)
        self.assertIn('approved', self.first.notifications.first().message)
        # The claim that was closed along the way is explained as well.
        self.assertEqual(self.second.notifications.count(), 1)

    def test_a_claim_is_decided_only_once(self):
        """Deciding twice would close the item again and send a second
        message to the claimant."""
        url = reverse('review_claim', args=[self.first_claim.pk])
        self.client.post(url, {'decision': 'approve'})

        response = self.client.post(url, {
            'decision': 'reject', 'remark': 'Changed my mind.',
        }, follow=True)

        self.first_claim.refresh_from_db()
        self.assertEqual(self.first_claim.status, 'approved')
        self.assertEqual(self.first.notifications.count(), 1)
        self.assertContains(response, 'already approved')

    def test_a_form_with_no_decision_changes_nothing(self):
        """Neither button was pressed, so nothing is decided."""
        response = self.client.post(
            reverse('review_claim', args=[self.first_claim.pk]),
            {'remark': 'Just typing.'},
        )

        self.first_claim.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.first_claim.status, 'pending')

    def test_the_navigation_shows_the_queue_only_to_an_officer(self):
        """And it carries the number of claims that are waiting."""
        officer_page = self.client.get(reverse('index'))
        self.assertContains(officer_page, 'Verify claims')
        self.assertContains(officer_page, 'nav-queue-count')

        self.client.force_login(self.first)
        member_page = self.client.get(reverse('index'))
        self.assertNotContains(member_page, 'Verify claims')
