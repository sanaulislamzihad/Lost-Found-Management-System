"""
This app keeps no table of its own. Logging in reads Django's own User
table and the Profile table that counts the wrong attempts, and both of
those live in the core app.
"""
