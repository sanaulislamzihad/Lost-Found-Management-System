"""The admin_panel app keeps no table of its own.

Managing the platform means reading and writing the tables the rest of
the system already uses, and those live in the ``core`` app, so this
app imports them with ``from core.models import Item``.
"""
