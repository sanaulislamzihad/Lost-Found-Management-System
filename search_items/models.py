"""The search_items app keeps no table of its own.

Searching only reads the ``Item`` and ``Category`` tables, and both of
them live in the ``core`` app together with every other table of the
system. This app imports them with ``from core.models import Item``.
"""
