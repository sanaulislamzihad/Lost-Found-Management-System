Database
========

Database Overview
-----------------

The project configures Django to use SQLite. In
``lost_and_found/settings.py``, the default database engine is
``django.db.backends.sqlite3`` and the database file is configured as
``BASE_DIR / 'db.sqlite3'``.

The application uses Django's Object-Relational Mapper (ORM) rather than
writing SQL in the feature views. Shared application data is defined in
``core/models.py``. Feature apps import those shared models to create, query,
update, and delete records. The ``core`` application therefore provides the
database layer shared by item reporting, search, claims, notifications,
profiles, and management functions.

Models
------

Django supplies an implicit primary key for each of the following models. The
initial core migration identifies it as an automatically created
``BigAutoField`` named ``id``.

Category
~~~~~~~~

``Category`` stores a reusable classification for items.

* ``name`` is a ``CharField`` with a maximum length of 50 and ``unique=True``.
* Categories are ordered by name.
* The reverse relation ``items`` identifies the items assigned to a category.
* The initial data migration creates the ``Electronics``, ``Documents``,
  ``Accessories``, and ``Bags`` categories using ``get_or_create``.

Item
~~~~

``Item`` represents both lost and found item reports. The ``item_type`` field
distinguishes the two kinds of report.

* ``item_name`` is a required ``CharField`` with a maximum length of 100.
* ``category`` is a foreign key to ``Category`` with ``related_name='items'``
  and ``on_delete=models.PROTECT``.
* ``description`` is a required ``TextField``.
* ``location`` is a required ``CharField`` with a maximum length of 150.
* ``date`` is a required ``DateField``.
* ``item_type`` is a ``CharField`` with a maximum length of 10 and the choice
  values ``lost`` and ``found``.
* ``status`` is a ``CharField`` with a maximum length of 10. Its choices are
  documented in :ref:`item-and-claim-status` and its default is ``pending``.
* ``image`` is an optional ``ImageField`` uploaded under ``items``; both
  ``blank=True`` and ``null=True`` are set.
* ``posted_by`` is a foreign key to Django's ``User`` model, with
  ``related_name='items'`` and ``on_delete=models.CASCADE``.
* ``created_at`` is a ``DateTimeField`` set automatically when the record is
  created.

Items are ordered newest first by ``created_at``. The methods ``is_open()``,
``mark_as_claimed()``, and ``mark_as_resolved()`` respectively check for an
open status, save the ``claimed`` status, and save the ``resolved`` status.

Claim
~~~~~

``Claim`` stores a user's request to receive a found item.

* ``item`` is a foreign key to ``Item`` with ``related_name='claims'`` and
  ``on_delete=models.CASCADE``.
* ``claimed_by`` is a foreign key to Django's ``User`` model with
  ``related_name='claims'`` and ``on_delete=models.CASCADE``.
* ``proof`` is a required ``TextField``.
* ``status`` is a ``CharField`` with a maximum length of 10, choice values
  ``pending``, ``approved``, and ``rejected``, and default ``pending``.
* ``reviewed_by`` is an optional foreign key to ``User`` with
  ``related_name='reviewed_claims'`` and ``on_delete=models.SET_NULL``.
* ``remark`` is a ``TextField`` with ``blank=True``.
* ``created_at`` is a ``DateTimeField`` set automatically on creation.

Claims are ordered oldest first by ``created_at``. Their composite
``unique_together = ['item', 'claimed_by']`` constraint prevents more than one
claim record for the same item and claimant combination.

``approve(officer)`` saves the claim as approved, records the reviewer, marks
the related item claimed, rejects other pending claims on that item, and
creates notifications. ``reject(officer, remark)`` saves the rejection,
reviewer, and remark, and creates a notification. ``get_absolute_url()``
returns the related item's detail URL; it does not add a database field.

Notification
~~~~~~~~~~~~

``Notification`` stores an in-application message for one user.

* ``user`` is a foreign key to Django's ``User`` model with
  ``related_name='notifications'`` and ``on_delete=models.CASCADE``.
* ``message`` is a required ``CharField`` with a maximum length of 255.
* ``link`` is an optional ``CharField`` with a maximum length of 200. It
  stores a path rather than a foreign key.
* ``is_read`` is a ``BooleanField`` with default ``False``.
* ``created_at`` is a ``DateTimeField`` set automatically on creation.

Notifications are ordered newest first. ``mark_as_read()`` sets and saves the
read flag. The static ``send(user, message, link='')`` method creates a
notification, truncates its message to the field's 255-character capacity,
and then attempts an email copy according to the recipient's profile setting.

Profile
~~~~~~~

``Profile`` extends Django's built-in ``User`` model with system-specific user
data and role/login state.

* ``user`` is a one-to-one field to ``User`` with ``related_name='profile'``
  and ``on_delete=models.CASCADE``.
* ``university_id`` is a ``CharField`` with a maximum length of 20 and
  ``blank=True``.
* ``phone_number`` is a ``CharField`` with a maximum length of 20 and
  ``blank=True``.
* ``photo`` is an optional ``ImageField`` uploaded under ``profiles``; it has
  ``blank=True`` and ``null=True``.
* ``role`` is a ``CharField`` with a maximum length of 10. Its values are
  ``student``, ``staff``, ``officer``, and ``admin``; its default is
  ``student``.
* ``failed_login_attempts`` is a ``PositiveIntegerField`` with default 0.
* ``locked_until`` is an optional ``DateTimeField``.
* ``email_notifications`` is a ``BooleanField`` with default ``False``.

The profile methods support role checks and login state. ``is_officer()`` and
``is_admin()`` compare the stored role value. ``is_locked()`` compares
``locked_until`` with the current time. ``note_failed_login()`` increases the
counter and, after the configured number of failed attempts, saves a lock time;
``note_successful_login()`` clears the counter and lock time.

Model Relationships
-------------------

The following relationships are defined directly in ``core/models.py``:

* One ``Category`` can be related to many ``Item`` records through
  ``Item.category``; items use the reverse name ``category.items``.
* One Django ``User`` can post many ``Item`` records through
  ``Item.posted_by``; the reverse name is ``user.items``.
* One ``Item`` can have many ``Claim`` records through ``Claim.item``; the
  reverse name is ``item.claims``.
* One Django ``User`` can submit many ``Claim`` records through
  ``Claim.claimed_by``; the reverse name is ``user.claims``.
* One Django ``User`` can review many ``Claim`` records through
  ``Claim.reviewed_by``; the reverse name is ``user.reviewed_claims``.
* One Django ``User`` has one ``Profile`` through ``Profile.user``; the reverse
  name is ``user.profile``.
* One Django ``User`` can have many ``Notification`` records through
  ``Notification.user``; the reverse name is ``user.notifications``.

Entity Relationship Diagram
---------------------------

.. code-block:: text

   Django User
      |
      |-- 1 : 1 --> Profile
      |
      |-- 1 : many --> Item (posted_by)
      |
      |-- 1 : many --> Claim (claimed_by)
      |
      |-- 1 : many --> Claim (reviewed_by, optional)
      |
      `-- 1 : many --> Notification

   Category -- 1 : many --> Item
   Item     -- 1 : many --> Claim

Item and Claim Status
---------------------

.. _item-and-claim-status:

Item status
~~~~~~~~~~~

The ``Item.status`` choices are ``pending``, ``available``, ``claimed``, and
``resolved``. ``is_open()`` considers only ``pending`` and ``available`` to be
open.

The reporting views establish the following source-verified transitions:

* ``report_lost_item`` creates lost reports with ``pending`` status.
* ``report_found_item`` creates found reports with ``available`` status.
* ``Item.mark_as_resolved()``, called by the lost-item resolution workflow,
  saves ``resolved``.
* ``Claim.approve()``, called by claim review, calls
  ``Item.mark_as_claimed()`` and saves ``claimed``.

The model field offers all four choices; the model definition itself does not
contain a database rule restricting a particular status to a particular item
type.

Claim status
~~~~~~~~~~~~

The ``Claim.status`` choices are ``pending``, ``approved``, and ``rejected``.
The claim submission view creates claims with the default ``pending`` status.
During review, ``Claim.approve()`` saves the selected claim as ``approved`` and
changes other pending claims on the same item to ``rejected``. ``Claim.reject``
saves the reviewed claim as ``rejected`` with its supplied remark.

Database Signals
----------------

``core/signals.py`` defines ``create_profile`` as a receiver for Django's
``post_save`` signal on ``User``. When the signal reports that a user was newly
created, the receiver calls ``Profile.objects.create(user=instance)``. This
creates the one-to-one profile automatically rather than requiring each user
creation view to create it.

``CoreConfig.ready()`` imports the signals module when the core application
starts, causing the receiver decorator to register the signal handler.

Database Configuration
----------------------

The configured default database is:

.. code-block:: python

   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }

The same settings module configures ``MEDIA_ROOT`` as ``BASE_DIR / 'media'``.
The ``Item.image`` and ``Profile.photo`` fields use Django ``ImageField``
upload paths, so their uploaded files are stored in media storage while the
database holds the field value/path.

Django ORM Usage
----------------

Feature views use ORM calls against the core models. Two examples are:

* ``search_items.views.item_list`` begins with
  ``Item.objects.select_related('category', 'posted_by')`` and successively
  applies ``filter`` operations for the supplied search and filter values.
  This is the query used to render the item list.
* ``claim_item.views.claim_item`` creates a record with
  ``Claim.objects.create(item=item, claimed_by=request.user, proof=proof)``.
  During review, ``Claim.approve()`` queries other pending claims with
  ``Claim.objects.filter(...).exclude(...)`` and saves their rejection state.

Other verified ORM operations in feature views include ``get_object_or_404``
lookups, ``select_related`` reads, ``annotate`` count queries in the management
views, ``save`` updates, and confirmed ``delete`` operations.

Data Integrity
--------------

The following integrity mechanisms are present in the model definitions,
migrations, or feature code:

* ``Category.name`` is unique.
* ``Claim`` has a composite unique constraint on ``item`` and ``claimed_by``.
* Item-category deletion is protected by ``on_delete=models.PROTECT``.
* Deleting a posting user deletes that user's items; deleting an item deletes
  its claims; deleting a claimant deletes that user's claims; and deleting a
  notification owner deletes that user's notifications, all through
  ``on_delete=models.CASCADE``.
* Deleting a claim reviewer sets ``Claim.reviewed_by`` to null through
  ``on_delete=models.SET_NULL``.
* Deleting a user deletes its one-to-one profile through
  ``Profile.user`` with ``on_delete=models.CASCADE``.
* Required model fields are represented without ``blank=True`` or
  ``null=True``; optional fields are explicitly marked in the model definitions
  as described above.
* The models define choices for item type, item status, claim status, and
  profile role. Feature views additionally validate submitted form values such
  as category, dates, required text, proof, uploaded photos, and profile phone
  numbers before saving.

No additional database-level check constraint for item-status transitions,
claim-review remarks, or profile phone format could be verified from the core
model definitions or migrations.
