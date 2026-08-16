"""The claim_item app keeps no table of its own.

A claim is a row of the ``Claim`` table, and that table lives in the
``core`` app together with every other table of the system. This app
imports it with ``from core.models import Claim``.
"""
