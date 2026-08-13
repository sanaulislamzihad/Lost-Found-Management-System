"""Put the starting categories into the database.

The SRS names these four as the example categories. Adding them through
a migration means every team member gets the same list after running
migrate, instead of typing them in the admin site one by one.
"""

from django.db import migrations

DEFAULT_CATEGORIES = [
    'Electronics',
    'Documents',
    'Accessories',
    'Bags',
]


def add_categories(apps, schema_editor):
    """Create the four starting categories.

    :param apps: registry used to reach the model as it was at this
        point in the migration history.
    :type apps: Apps.
    """
    Category = apps.get_model('home', 'Category')
    for name in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(name=name)


def remove_categories(apps, schema_editor):
    """Delete the four starting categories again.

    Django runs this when the migration is undone.

    :param apps: registry used to reach the model.
    :type apps: Apps.
    """
    Category = apps.get_model('home', 'Category')
    Category.objects.filter(name__in=DEFAULT_CATEGORIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_categories, remove_categories),
    ]
