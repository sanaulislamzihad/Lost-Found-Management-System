"""The verify_claims app keeps no table of its own.

Checking a claim reads and writes the ``Claim`` and ``Item`` tables,
and both of them live in the ``core`` app together with every other
table of the system. The two decisions themselves are written as
``Claim.approve`` and ``Claim.reject`` inside that app, so the rule
stays with the data and this app only calls them.
"""
