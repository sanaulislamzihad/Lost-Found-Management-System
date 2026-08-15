"""Database tables of the Lost & Found Management System.

Every table asked for in section 3.3 of the SRS is written in this one
app. Each feature of the system has an app of its own for its pages,
but the tables are shared between those features, so they are kept here
and imported with ``from core.models import Item``.
"""

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
