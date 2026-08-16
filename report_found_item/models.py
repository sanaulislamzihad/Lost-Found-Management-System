"""The report_found_item app keeps no table of its own.

A found item report is a row of the ``Item`` table with ``item_type``
set to ``found``, and that table lives in the ``core`` app together
with every other table of the system. This app imports it with
``from core.models import Item``.
"""
