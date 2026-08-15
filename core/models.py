"""Database tables of the Lost & Found Management System.

Every table asked for in section 3.3 of the SRS is written in this one
app. Each feature of the system has an app of its own for its pages,
but the tables are shared between those features, so they are kept here
and imported with ``from core.models import Item``.
"""

from django.contrib.auth.models import User
from django.db import models

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
