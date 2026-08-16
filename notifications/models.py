"""The notifications app keeps no table of its own.

A message is a row of the ``Notification`` table, and the switch that
asks for an email copy is a column of the ``Profile`` table. Both of
those live in the ``core`` app together with every other table of the
system, so this app imports them with
``from core.models import Notification``.
"""
