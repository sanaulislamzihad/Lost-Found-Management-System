"""Database tables of the Lost & Found Management System.

Every table asked for in section 3.3 of the SRS is written in this one
app. Each feature of the system has an app of its own for its pages,
but the tables are shared between those features, so they are kept here
and imported with ``from core.models import Item``.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# How many wrong logins in a row are allowed, and how long the account
# stays shut after that. SRS Feature 2 asks for exactly these numbers.
MAX_LOGIN_ATTEMPTS = 5
LOCK_MINUTES = 15

ITEM_TYPE_CHOICES = [
    ('lost', 'Lost'),
    ('found', 'Found'),
]

ITEM_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('available', 'Available'),
    ('claimed', 'Claimed'),
    ('resolved', 'Resolved'),
]

CLAIM_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

ROLE_CHOICES = [
    ('student', 'Student'),
    ('staff', 'Staff'),
    ('officer', 'Security Officer'),
    ('admin', 'Admin'),
]


class Category(models.Model):
    """A group that an item belongs to, for example Electronics or Bags.

    Categories are kept in their own table so that the Admin can add or
    remove one without any code change, as asked in Feature 10.
    """

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        """Return the text shown for this category in the admin site.

        :return: the name of the category.
        :rtype: str.
        """
        return self.name


class Item(models.Model):
    """One lost item report or one found item report.

    Both kinds of report are kept in the same table and told apart by
    the ``item_type`` field, the way the SRS describes the Items table.
    """

    item_name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='items',
    )
    description = models.TextField()
    location = models.CharField(max_length=150)
    date = models.DateField()
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    status = models.CharField(
        max_length=10,
        choices=ITEM_STATUS_CHOICES,
        default='pending',
    )
    image = models.ImageField(upload_to='items', blank=True, null=True)
    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='items',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """Return the text shown for this item in the admin site.

        :return: the item name followed by its type.
        :rtype: str.
        """
        return '%s (%s)' % (self.item_name, self.get_item_type_display())

    def is_open(self):
        """Tell whether the item is still waiting to be returned.

        :return: True while the report is pending or available.
        :rtype: bool.
        """
        return self.status in ('pending', 'available')

    def mark_as_claimed(self):
        """Close the report because an officer approved a claim on it.

        Feature 7 calls this method after approving a claim, so the rule
        lives in the model instead of being repeated in every view.
        """
        self.status = 'claimed'
        self.save()

    def mark_as_resolved(self):
        """Close the report because the owner got the item back.

        Feature 3 calls this method, so a recovered report is kept in
        the history instead of being deleted.
        """
        self.status = 'resolved'
        self.save()


class Claim(models.Model):
    """A request from a user to get back an item that they say is theirs.

    A Security Officer reads the proof of ownership and then approves or
    rejects the claim, which is Feature 7 of the SRS.
    """

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='claims',
    )
    claimed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='claims',
    )
    proof = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=CLAIM_STATUS_CHOICES,
        default='pending',
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='reviewed_claims',
        blank=True,
        null=True,
    )
    remark = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        # The SRS says one user cannot have two live claims on one item.
        unique_together = ['item', 'claimed_by']

    def __str__(self):
        """Return the text shown for this claim in the admin site.

        :return: who claimed which item.
        :rtype: str.
        """
        return '%s claimed %s' % (
            self.claimed_by.username,
            self.item.item_name,
        )

    def approve(self, officer):
        """Accept the claim and hand the item over to the claimant.

        Approving also closes the item and rejects every other claim
        waiting on the same item, exactly as the SRS asks.

        :param officer: the Security Officer taking the decision.
        :type officer: User.
        """
        self.status = 'approved'
        self.reviewed_by = officer
        self.save()

        self.item.mark_as_claimed()

        other_claims = Claim.objects.filter(
            item=self.item,
            status='pending',
        ).exclude(pk=self.pk)
        other_claims.update(
            status='rejected',
            remark='Another claim on this item was approved.',
        )

    def reject(self, officer, remark):
        """Turn the claim down with a reason written by the officer.

        :param officer: the Security Officer taking the decision.
        :type officer: User.
        :param remark: why the claim was rejected. The SRS makes this
            field mandatory when rejecting.
        :type remark: str.
        """
        self.status = 'rejected'
        self.reviewed_by = officer
        self.remark = remark
        self.save()


class Notification(models.Model):
    """One message shown to a user inside the notification panel.

    Feature 8 writes a row here whenever a claim is decided, a new
    matching item is posted, or somebody claims a found item.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """Return the text shown for this notification in the admin site.

        :return: the owner of the message and the message itself.
        :rtype: str.
        """
        return '%s: %s' % (self.user.username, self.message)

    def mark_as_read(self):
        """Mark the message as seen so it stops showing as new."""
        self.is_read = True
        self.save()

    @staticmethod
    def send(user, message):
        """Create a notification for one user.

        Every feature calls this one method instead of writing its own
        ``Notification.objects.create(...)`` line, so the way we notify
        people stays in a single place.

        :param user: who should receive the message.
        :type user: User.
        :param message: the text to show.
        :type message: str.
        :return: the notification that was saved.
        :rtype: Notification.
        """
        return Notification.objects.create(user=user, message=message)


class Profile(models.Model):
    """The extra details of a user that Django does not store by itself.

    Django's own User table keeps the name, email and password. The SRS
    also asks for a university ID, a phone number, a photo and a role,
    so those four are kept here and joined to the user one to one.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    university_id = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='profiles', blank=True, null=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
    )

    # Used by the login view to shut an account for a while after too
    # many wrong tries. The SRS calls this part of the account status.
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        """Return the text shown for this profile in the admin site.

        :return: the username followed by the role.
        :rtype: str.
        """
        return '%s (%s)' % (self.user.username, self.get_role_display())

    def is_officer(self):
        """Tell whether this user is allowed to decide on claims.

        Feature 7 checks this before showing the verification page, so
        the rule is written once here instead of in every view.

        :return: True for a Security Officer.
        :rtype: bool.
        """
        return self.role == 'officer'

    def is_locked(self):
        """This method tells whether the account is still shut because
        of too many wrong logins.

        :return: True while the lock time has not passed yet.
        :rtype: bool.
        """
        if self.locked_until is None:
            return False
        return self.locked_until > timezone.now()

    def note_failed_login(self):
        """This method counts one wrong login and shuts the account
        when there are too many of them in a row.

        The counter starts again after the account is locked, so the
        next lock also needs a fresh set of wrong tries.
        """
        self.failed_login_attempts += 1

        if self.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            self.locked_until = timezone.now() + timedelta(
                minutes=LOCK_MINUTES,
            )
            self.failed_login_attempts = 0

        self.save()

    def note_successful_login(self):
        """This method clears the counter and the lock after the member
        gets in."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save()
