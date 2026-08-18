API Reference
=============

This page is generated automatically from the docstrings in the project's
own source code, using Sphinx's ``autodoc`` extension. Every module below
is imported directly from the Django project, so this page changes only
when the source changes.

Core
----

``core`` holds the five database tables shared by every feature app:
Category, Item, Claim, Notification and Profile.

Core Models
~~~~~~~~~~~

.. automodule:: core.models
   :members:
   :show-inheritance:

Core Signals
~~~~~~~~~~~~

.. automodule:: core.signals
   :members:
   :show-inheritance:

Feature Applications
---------------------

Each of the ten features of the SRS, plus the landing page, lives in its
own app. The views module of each app is documented here.

Home
~~~~

.. automodule:: home.views
   :members:
   :show-inheritance:

Register
~~~~~~~~

.. automodule:: register.views
   :members:
   :show-inheritance:

Login / Logout
~~~~~~~~~~~~~~

.. automodule:: login_logout.views
   :members:
   :show-inheritance:

Report a Lost Item
~~~~~~~~~~~~~~~~~~~

.. automodule:: report_lost_item.views
   :members:
   :show-inheritance:

Report a Found Item
~~~~~~~~~~~~~~~~~~~~

.. automodule:: report_found_item.views
   :members:
   :show-inheritance:

Search and Filter Items
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: search_items.views
   :members:
   :show-inheritance:

Claim an Item
~~~~~~~~~~~~~

.. automodule:: claim_item.views
   :members:
   :show-inheritance:

Check and Approve Claims
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: verify_claims.views
   :members:
   :show-inheritance:

Notifications
~~~~~~~~~~~~~~

.. automodule:: notifications.views
   :members:
   :show-inheritance:

Profile and My History
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: profile_history.views
   :members:
   :show-inheritance:

Admin Management
~~~~~~~~~~~~~~~~~

.. automodule:: admin_panel.views
   :members:
   :show-inheritance:
