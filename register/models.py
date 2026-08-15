"""The register app keeps no table of its own.

Registering writes into Django's own ``User`` table and into the
``Profile`` table, and both of those live in the ``core`` app. Ten
features of this system share the same five tables, so the tables are
kept together in one place and every feature app imports what it needs
with ``from core.models import Profile``.
"""
