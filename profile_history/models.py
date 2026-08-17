"""The profile_history app keeps no table of its own.

The details it shows are spread over Django's own ``User`` table and
the ``Profile``, ``Item`` and ``Claim`` tables of the ``core`` app, so
this app imports them with ``from core.models import Item``.
"""
