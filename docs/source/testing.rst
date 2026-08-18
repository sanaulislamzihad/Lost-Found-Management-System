Testing
=======

Testing Overview
----------------

The project uses Django's built-in testing framework through
``django.test.TestCase``. The README describes these tests as Python
``unittest``-based tests run through Django. Test modules are located in each
Django app as ``tests.py``.

The feature-specific suites use Django's test client to make requests, assert
HTTP responses and rendered content, and inspect records through the Django
ORM. Some image-upload tests use ``override_settings`` with a temporary media
directory so that uploads do not use the project's normal media location.

Running the Test Suite
----------------------

The README documents the following command for running the complete suite:

.. code-block:: bash

   .venv\Scripts\python manage.py test

``manage.py`` configures the ``lost_and_found.settings`` module and passes the
command to Django's command-line runner.

Running Tests for an Individual App
-----------------------------------

The documented example for running one app's tests is:

.. code-block:: bash

   .venv\Scripts\python manage.py test register

The app label can be used to select an individual Django app's test module.
The README explicitly demonstrates the ``register`` app; other app labels are
not listed there as separate commands.

Test Organization
-----------------

Each installed project app has a ``tests.py`` module. The feature suites create
their own test data in ``setUp`` methods or helpers, commonly using Django
``User``, ``Category``, ``Item``, and ``Claim`` records. Tests use named URLs
with ``reverse`` in several apps and direct request paths in others.

The available test modules are:

* ``register/tests.py``
* ``login_logout/tests.py``
* ``report_lost_item/tests.py``
* ``report_found_item/tests.py``
* ``search_items/tests.py``
* ``claim_item/tests.py``
* ``verify_claims/tests.py``
* ``notifications/tests.py``
* ``profile_history/tests.py``
* ``admin_panel/tests.py``

The shared ``core/tests.py`` and the ``home/tests.py`` modules also exist.

Feature Test Coverage
---------------------

Register
~~~~~~~~

``RegisterTest`` verifies required registration fields, email validation,
short-password rejection, duplicate email and university-ID prevention, and
password hashing.

Report Lost Item
~~~~~~~~~~~~~~~~

``ReportLostItemTest`` covers login protection, form rendering, pending-status
creation, required fields and invalid dates, owner-only editing and deletion,
delete confirmation, lost-item resolution, repeated resolution handling, and
owner-only detail-page actions.

Report Found Item
~~~~~~~~~~~~~~~~~

``ReportFoundItemTest`` covers login protection, available-status creation,
required fields and category selection, future-date rejection, item-list
appearance, photo upload, owner-only editing, delete confirmation, and the
claimed status after a claim approval.

Claim Item
~~~~~~~~~~

``ClaimItemTest`` verifies login protection, claim-form rendering, pending
claim creation, proof storage, empty-proof rejection, prevention of self
claims and duplicate claims, prevention of claims on closed items, and claim
status display in the user's claim list.

Verify Claims
~~~~~~~~~~~~~

``VerifyClaimsTest`` covers role-based queue access, pending-claim ordering,
status filtering, claim and item content on the review page, display of other
claims on the same item, approval effects, mandatory rejection remarks,
notification creation, repeated-decision prevention, no-decision submissions,
and officer-only navigation visibility.

Profile and History
~~~~~~~~~~~~~~~~~~~

``ProfileAndHistoryTest`` verifies login protection, profile details, phone
updates and invalid-phone rejection, unchanged email and university ID, valid
profile image saving, invalid-image rejection, user-specific item history,
status filtering, and claim status display.

Admin Management
~~~~~~~~~~~~~~~~

``ManagementTest`` covers administrator-only access, dashboard statistics,
member listing and role changes, protections against an administrator locking
out their own account, account activation changes, deletion confirmation,
post filtering and editing, category management, and CSV export.

Test Database
-------------

The README states that Django creates a separate test database and removes it
after the tests finish. It further states that this process does not modify the
project's ``db.sqlite3`` file. The source comments in the lost-item, claim
verification, and admin-management test modules describe the same separation.

For tests that upload files, the found-item and profile/history suites apply
``override_settings(MEDIA_ROOT=tempfile.mkdtemp())``. Their uploaded test files
therefore use a temporary media directory rather than the configured project
media directory.

Testing Limitations
-------------------

The following modules import ``TestCase`` but contain only Django's default
``Create your tests here.`` placeholder. No feature-specific automated test
cases could be verified in them:

* ``login_logout/tests.py``
* ``search_items/tests.py``
* ``notifications/tests.py``

The same placeholder-only status was also verified for ``core/tests.py`` and
``home/tests.py``. This documentation reports the presence of test code; it
does not provide coverage percentages or claim that the suite has been run.
