"""The report_lost_item app keeps no table of its own.

A lost item report is a row of the ``Item`` table with ``item_type``
set to ``lost``, and that table lives in the ``core`` app together
with every other table of the system. This app imports it with
``from core.models import Item``.
"""
