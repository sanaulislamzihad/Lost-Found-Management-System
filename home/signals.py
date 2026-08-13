"""Signals of the home app.

A signal is a function that Django runs by itself after something
happens. Here we use one so that every new user gets a Profile row
without any view having to remember to create it.
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a Profile as soon as a new user is saved.

    :param sender: the model that sent the signal, always User here.
    :type sender: type.
    :param instance: the user row that was just saved.
    :type instance: User.
    :param created: True only the first time this user is saved.
    :type created: bool.
    """
    if created:
        Profile.objects.create(user=instance)
