"""Tests for the claim_item app."""

from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from core.models import Category, Claim, Item


class ClaimItemTest(TestCase):

    def setUp(self):
        self.bags = Category.objects.get(name='Bags')

        self.finder = User.objects.create_user(
            username='sadia@northsouth.edu',
            email='sadia@northsouth.edu',
            password='Str0ngPassw0rd!',
            first_name='Sadia',
        )
        self.owner = User.objects.create_user(
            username='arif@northsouth.edu',
            email='arif@northsouth.edu',
            password='Str0ngPassw0rd!',
            first_name='Arif',
        )

        self.item = Item.objects.create(
            item_name='Blue backpack',
            category=self.bags,
            description='Broken zip, maths notes inside.',
            location='Sports complex',
            date=date(2026, 7, 10),
            item_type='found',
            status='available',
            posted_by=self.finder,
        )

        self.client.force_login(self.owner)

    def test_claiming_needs_a_login(self):
        """A claim belongs to somebody, so it needs an account."""
        self.client.logout()

        response = self.client.get('/items/%s/claim' % self.item.pk)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response['Location'])

    def test_the_claim_form_opens_and_names_the_item(self):
        """The claimant sees what they are about to claim."""
        response = self.client.get('/items/%s/claim' % self.item.pk)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Blue backpack')

    def test_a_claim_is_saved_as_pending(self):
        """A new claim goes to the Security Officer, not straight
        through."""
        self.client.post('/items/%s/claim' % self.item.pk, {
            'proof': 'My name is written inside the front pocket.',
        })

        claim = Claim.objects.get(claimed_by=self.owner)
        self.assertEqual(claim.status, 'pending')
        self.assertEqual(claim.item, self.item)

    def test_the_proof_is_saved_with_the_claim(self):
        """The officer reads this text before handing the item over."""
        self.client.post('/items/%s/claim' % self.item.pk, {
            'proof': 'My name is written inside the front pocket.',
        })

        claim = Claim.objects.get(claimed_by=self.owner)
        self.assertEqual(
            claim.proof,
            'My name is written inside the front pocket.',
        )

    def test_an_empty_proof_is_refused(self):
        """A claim without proof is not a claim."""
        self.client.post('/items/%s/claim' % self.item.pk, {
            'proof': '   ',
        })

        self.assertEqual(Claim.objects.count(), 0)

    def test_the_finder_cannot_claim_their_own_post(self):
        """They handed the item in, so there is nothing to claim."""
        self.client.force_login(self.finder)

        self.client.post('/items/%s/claim' % self.item.pk, {
            'proof': 'It is mine really.',
        })

        self.assertEqual(Claim.objects.count(), 0)

    def test_the_same_member_cannot_claim_twice(self):
        """One member, one live claim on one item."""
        self.client.post('/items/%s/claim' % self.item.pk, {
            'proof': 'My name is written inside the front pocket.',
        })
        self.client.post('/items/%s/claim' % self.item.pk, {
            'proof': 'Trying again.',
        })

        self.assertEqual(Claim.objects.count(), 1)

    def test_a_closed_item_cannot_be_claimed(self):
        """Once the item is handed over the post is finished with."""
        self.item.status = 'claimed'
        self.item.save()

        self.client.post('/items/%s/claim' % self.item.pk, {
            'proof': 'My name is written inside the front pocket.',
        })

        self.assertEqual(Claim.objects.count(), 0)

    def test_my_claims_shows_the_claim_and_its_status(self):
        """The SRS lets a member follow every claim they made."""
        self.client.post('/items/%s/claim' % self.item.pk, {
            'proof': 'My name is written inside the front pocket.',
        })

        response = self.client.get('/my-claims')

        self.assertContains(response, 'Blue backpack')
        self.assertContains(response, 'Pending')
