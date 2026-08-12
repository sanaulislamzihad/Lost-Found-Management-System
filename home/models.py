"""Database models of the Lost & Found Management System.

All the tables listed in section 3.3 of the SRS are written in this one
file. Every other app imports the models from here, so the whole team
works on the same tables instead of making their own copies.
"""

from django.db import models


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
