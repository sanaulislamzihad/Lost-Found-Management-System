Architecture
============

Architectural Overview
----------------------

The Lost & Found Management System is implemented with the Django web
framework. Its source structure follows Django's Model--View--Template (MVT)
organization:

* Models in ``core/models.py`` define the shared application data and selected
  data-related operations.
* Views in the feature apps handle HTTP requests, validate request data,
  query or update shared models, and select a response.
* Templates in ``templates/`` render the HTML pages returned by most views.

The ``lost_and_found`` package holds project-level configuration. The feature
apps separate the system's main functions, while ``core`` provides the shared
models used by those functions. The project also keeps site templates in a
single ``templates/`` directory and site static assets in ``static/``.

Project Configuration
---------------------

``lost_and_found/settings.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The settings module defines the Django configuration used by the project. It
registers Django's built-in applications and the project's ``core``, ``home``,
and feature apps in ``INSTALLED_APPS``. It configures:

* SQLite as the default database, with ``db.sqlite3`` under the project base
  directory.
* the Django template engine, with ``templates/`` as a project-level template
  directory and app template discovery enabled;
* standard Django middleware, including session, authentication, CSRF, and
  message middleware;
* ``static/`` as an additional static-files directory and ``media/`` as the
  upload location for item and profile images;
* ``login`` as the destination used by Django's ``login_required`` decorator;
  and
* custom template context processors for the unread notification count and the
  pending claim count.

``lost_and_found/urls.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The root URL configuration includes the URL patterns from the home app and all
ten feature apps. Each included app supplies its own path patterns, such as
``/items``, ``/login``, ``/verify``, and ``/manage``. The root configuration
also exposes Django's built-in admin site at ``/admin/`` and appends media URL
patterns using Django's ``static`` helper.

``manage.py``
~~~~~~~~~~~~~

``manage.py`` is the project's Django command-line entry point. It sets the
``DJANGO_SETTINGS_MODULE`` environment variable to ``lost_and_found.settings``
and delegates command-line arguments to Django's ``execute_from_command_line``
function.

Django Applications
-------------------

The source tree separates the major system features into Django apps. Their
URL modules map app-specific paths to view functions, and their view modules
implement the corresponding request handling.

* ``home`` renders the landing page.
* ``register`` creates user accounts and stores the university or employee ID
  on the user's profile.
* ``login_logout`` authenticates users, manages login attempt state through
  profiles, and ends sessions.
* ``report_lost_item`` creates, edits, deletes, and resolves a user's lost
  item reports.
* ``report_found_item`` creates, edits, and deletes a user's found item
  reports, and invokes the matching-lost-poster notification service after a
  new found report is created.
* ``search_items`` lists and filters item reports and renders individual item
  details.
* ``claim_item`` creates claims on found items and lists the current user's
  claims.
* ``verify_claims`` presents the claim queue and lets authorized users review
  a claim.
* ``notifications`` displays the current user's notifications, marks them as
  read, and updates the email-copy preference.
* ``profile_history`` updates permitted profile information and lists the
  current user's posts and claims.
* ``admin_panel`` provides administrator-only management views for dashboard
  statistics, users, posts, categories, and CSV export.

Request / Response Flow
-----------------------

For most browser page requests, the verified request path is as follows:

.. code-block:: text

   Browser request
       |
       v
   lost_and_found/urls.py
       |
       +--> included feature-app urls.py
                 |
                 v
              view function
                 |
                 +--> shared core model query or update, when required
                 |
                 +--> render(template, context) or redirect(...)
                            |
                            v
                       HTTP response to browser

For example, a request to ``/items`` is included through
``lost_and_found/urls.py`` and matched by ``search_items/urls.py`` to
``item_list``. That view begins with an ``Item`` queryset, optionally filters
it using request query parameters, obtains categories for the filter control,
and renders ``item_list.html`` with the resulting context. The template
extends ``base.html`` and uses the supplied items, categories, item types, and
filter values to create the response.

Not every view renders a template. For example, successful form submissions in
the reporting and claim views redirect to another named route after their
model changes are saved.

Shared Core Layer
-----------------

``core/models.py`` holds the project's shared data models:

* ``Category`` stores a unique category name.
* ``Item`` represents both lost and found reports. It has a protected foreign
  key to ``Category`` and a cascading foreign key to the posting Django
  ``User``. It includes report fields, item type, status, optional image, and
  timestamps. Its methods identify open reports and mark reports claimed or
  resolved.
* ``Claim`` links an item to the user who submitted it, stores proof, status,
  an optional reviewing user, and an optional remark. It has a unique
  ``item``/``claimed_by`` constraint. Its ``approve`` and ``reject`` methods
  implement the model-level decision actions used by claim review.
* ``Notification`` belongs to a user and stores a message, optional link,
  read state, and timestamp. It provides methods to mark a message read and to
  create a notification through ``send``.
* ``Profile`` is a one-to-one extension of Django's ``User``. It stores the
  university ID, phone number, profile photo, role, failed-login state, and
  email-notification preference. Its methods support role checks and login
  lock handling.

The relationships verified in these models include a category with many items,
a user with many posted items, a user with many claims, an item with many
claims, a user with many notifications, and one profile per user. Deleting an
item or a claim's submitting user cascades to claims; the reviewer association
is set to null when its user is deleted. Categories are protected from deletion
by related items at the model relationship level.

``core/signals.py`` registers a ``post_save`` receiver for Django's ``User``
model. When a user is created, the receiver creates its ``Profile`` record.
``core/apps.py`` imports the signals module from ``CoreConfig.ready`` so that
the receiver is registered when the core app starts.

Frontend Layer
--------------

The project-level ``templates/`` directory contains the HTML templates used by
the feature views. ``base.html`` loads ``css/style.css``, provides the shared
navigation and message area, and defines template blocks used by the standard
page templates. Feature templates such as ``item_list.html``,
``item_detail.html``, ``register.html``, and ``verify_claim.html`` extend this
base template.

The administration templates use a second shared layer: ``manage_base.html``
extends ``base.html`` and defines management navigation and a
``manage_body`` block. The management page templates extend ``manage_base.html``.

``static/`` currently contains ``css/style.css`` and ``img/campus.webp``. The
settings module registers this directory as a static-files location; templates
use Django's ``static`` template tag for the stylesheet. Item and profile image
uploads are distinct from static assets and use the configured media location.

Authentication and Authorization
--------------------------------

Authentication uses Django's built-in authentication functions in the
``login_logout`` views and Django's session middleware. The registration view
creates Django ``User`` records with ``create_user``. Views that require an
authenticated user use Django's ``login_required`` decorator; based on
``LOGIN_URL``, anonymous visitors are sent to the ``login`` route.

The ``Profile.role`` field defines ``student``, ``staff``, ``officer``, and
``admin`` choices. Student and staff roles are stored separately, but the
source does not define a separate role-specific decorator for ordinary feature
views; those views use authentication and, where needed, ownership checks.

The ``verify_claims`` app uses ``officer_required``. It permits an authenticated
Security Officer, an Admin, or a Django superuser; authenticated users without
one of those permissions receive ``PermissionDenied``. The ``admin_panel`` app
uses ``admin_required``, which permits an authenticated Admin or Django
superuser and denies other authenticated users. The base template conditionally
shows the management link for a profile admin or superuser and the verification
link for users passing the profile officer check or superuser check.

Design Characteristics
----------------------

The directory structure demonstrates separation between project configuration,
shared data, feature-specific request handling, templates, and static assets.
The root URL configuration includes each feature app's URL module, and the
feature views import shared models from ``core`` rather than defining separate
feature-local data models. This organization supports the documented modular
Django app structure without requiring every feature to own a separate copy of
the shared data.
