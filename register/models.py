"""
This app keeps no table of its own. Registering writes into Django's
own User table and into the Profile table, and both of those live in
the core app, so every feature app imports what it needs with
``from core.models import Profile``.
"""
