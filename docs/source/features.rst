Features
========

Overview
--------

The Lost & Found Management System is divided into ten major Django feature
apps. Each app provides a focused part of the user journey, while shared data
is held in ``core``. The feature apps work with the shared ``Item``,
``Category``, ``Claim``, ``Notification``, and ``Profile`` models where
appropriate.

Register an Account
-------------------

Purpose
~~~~~~~

The ``register`` app creates a user account using a full name, university or
employee ID, email address, and password. The email address is stored as the
user's username.

Application Components
~~~~~~~~~~~~~~~~~~~~~~

* Django app: ``register``.
* View: ``register`` in ``register/views.py``.
* Route: ``/register`` (route name ``register``).
* Template: ``register.html``.
* Shared models: Django's ``User`` model and ``core.models.Profile``.

Workflow
~~~~~~~~

* A GET request displays the registration form.
* On submission, the view checks that the full name and university or employee
  ID are present, validates the email address, and applies Django password
  validation.
* The view rejects an email already used by a user or an ID already used by a
  profile.
* It creates the Django user with ``create_user``, which hashes the password,
  then saves the university or employee ID to the profile created by the core
  post-save signal.
* A successful registration redirects the user to ``/login``.

Testing
~~~~~~~

``RegisterTest`` verifies required fields, email validation, rejection of a
short password, prevention of duplicate email or ID values, and hashed
password storage.

Log In and Log Out
------------------

Purpose
~~~~~~~

The ``login_logout`` app authenticates users, records failed login attempts,
and ends an authenticated session when the user logs out.

Application Components
~~~~~~~~~~~~~~~~~~~~~~

* Django app: ``login_logout``.
* Views: ``login`` and ``logout`` in ``login_logout/views.py``.
* Routes: ``/login`` (``login``) and ``/logout`` (``logout``).
* Template: ``login.html``.
* Shared model: ``core.models.Profile``; it supplies the lock state and login
  attempt methods used by the view.

Workflow
~~~~~~~~

* The login view displays the form on GET and authenticates the submitted email
  and password on POST.
* Before authentication, it checks whether the corresponding profile is locked.
* On an unsuccessful attempt for an existing profile, it records the failed
  login. The same error message is returned for an unknown email and a wrong
  password.
* On success, it records a successful login, creates the Django session, and
  redirects to the home page.
* The logout view ends the session, adds a confirmation message, and redirects
  to the home page.

Testing
~~~~~~~

``login_logout/tests.py`` contains only Django's default placeholder; no
feature-specific automated tests could be verified in that file.

Report a Lost Item
------------------

Purpose
~~~~~~~

The ``report_lost_item`` app lets an authenticated user create, edit, delete,
or resolve their own lost-item report.

Application Components
~~~~~~~~~~~~~~~~~~~~~~

* Django app: ``report_lost_item``.
* Views: ``report_lost_item``, ``edit_lost_item``, ``delete_lost_item``, and
  ``resolve_lost_item``. The app also uses ``clean_lost_form`` and
  ``own_lost_item`` helpers.
* Routes: ``/items/lost``, ``/items/lost/<pk>/edit``,
  ``/items/lost/<pk>/delete``, and ``/items/lost/<pk>/resolve``.
* Templates: ``report_lost_item.html`` and ``delete_lost_item.html``.
  The resulting report is displayed through the shared ``item_detail.html``
  page.
* Shared models: ``Item`` and ``Category``.

Workflow
~~~~~~~~

* All routes require login. The form validates the item name, category,
  description, location, date, and optional image before saving.
* A new report is stored as an ``Item`` with type ``lost`` and status
  ``pending``; the user is then sent to its detail page.
* Only the user who posted the report may edit or delete it. Deletion displays
  a confirmation page on GET and deletes only on POST.
* The owner can resolve an open report using a POST request. A resolved report
  remains in the data rather than being deleted.

Testing
~~~~~~~

``ReportLostItemTest`` covers login protection, form display, successful
creation with pending status, required-field and invalid-date validation,
owner-only edit and delete access, delete confirmation, resolution behavior,
and owner-only detail-page controls.

Report a Found Item
-------------------

Purpose
~~~~~~~

The ``report_found_item`` app lets an authenticated user publish, edit, or
delete a found-item report that can later be claimed.

Application Components
~~~~~~~~~~~~~~~~~~~~~~

* Django app: ``report_found_item``.
* Views: ``report_found_item``, ``edit_found_item``, and
  ``delete_found_item``. Supporting helpers include ``clean_found_form`` and
  ``own_found_item``.
* Routes: ``/items/found``, ``/items/found/<pk>/edit``, and
  ``/items/found/<pk>/delete``.
* Templates: ``report_found_item.html`` and ``delete_found_item.html``.
  Reports use the shared ``item_detail.html`` page after saving.
* Shared models: ``Item`` and ``Category``.
* Related service: ``notifications.services.notify_matching_lost_posters``.

Workflow
~~~~~~~~

* The login-protected form validates the required item fields and accepts an
  optional image.
* A saved report is an ``Item`` with type ``found`` and status ``available``.
* After creation, the app calls the notification service to notify users with
  open lost-item reports in the same category, excluding the finder.
* Only the owner may edit or delete the report. The delete action requires a
  POST confirmation; a successful deletion returns to the item list.

Testing
~~~~~~~

``ReportFoundItemTest`` tests login protection, successful creation, required
fields and category validation, future-date rejection, item-list visibility,
image upload, owner-only editing, delete confirmation, and the transition to
``claimed`` after an approved claim.

Search and Filter Items
-----------------------

Purpose
~~~~~~~

The ``search_items`` app lists lost and found reports, applies optional search
filters, and displays an individual report.

Application Components
~~~~~~~~~~~~~~~~~~~~~~

* Django app: ``search_items``.
* Views: ``item_list`` and ``item_detail``; ``read_date`` parses optional date
  filters.
* Routes: ``/items`` and ``/items/<pk>``.
* Templates: ``item_list.html`` and ``item_detail.html``.
* Shared models: ``Item`` and ``Category``; the item type choices are also
  supplied from ``core.models``.

Workflow
~~~~~~~~

* The item-list view begins with all item reports and applies supplied filters
  to the same query.
* A keyword can match an item name, description, or category name.
* Optional filters narrow results by category, item type, location, and lower
  and upper item-date bounds. Invalid hand-entered dates are ignored rather
  than raising an error.
* The view preserves the submitted filter values for the list template and
  indicates whether any filter is active.
* The detail view retrieves one item with its category and poster, returning a
  standard Django 404 response if it does not exist.

Testing
~~~~~~~

``search_items/tests.py`` contains only Django's default placeholder; no
feature-specific automated tests could be verified in that file.

Claim an Item
-------------

Purpose
~~~~~~~

The ``claim_item`` app enables an authenticated user to submit proof of
ownership for a found item and to review their submitted claims.

Application Components
~~~~~~~~~~~~~~~~~~~~~~

* Django app: ``claim_item``.
* Views: ``claim_item`` and ``my_claims``; ``blocked_reason`` determines
  whether a claim may be submitted.
* Routes: ``/items/<pk>/claim`` and ``/my-claims``.
* Templates: ``claim_item.html`` and ``my_claims.html``.
* Shared models: ``Item`` and ``Claim``.
* Related service: ``notifications.services.notify_finder_of_new_claim``.

Workflow
~~~~~~~~

* The claim route accepts only found-item records and requires login.
* The user cannot claim their own post, a closed item, or an item they have
  already claimed.
* The form requires non-empty proof of ownership. A valid submission creates a
  pending ``Claim`` for the current user.
* The finder is notified about the newly submitted claim, and the claimant is
  redirected to their claim list.
* The claim-list view shows the current user's claims with item and category
  details, ordered newest first.

Testing
~~~~~~~

``ClaimItemTest`` covers login protection, form display, pending-claim and
proof storage, empty-proof validation, the self-claim, duplicate-claim, and
closed-item restrictions, and claim status visibility in ``my_claims``.

Check and Approve Claims
------------------------

Purpose
~~~~~~~

The ``verify_claims`` app provides the Security Officer claim queue and the
review action used to approve or reject a claim.

Application Components
~~~~~~~~~~~~~~~~~~~~~~

* Django app: ``verify_claims``.
* Views: ``claim_queue`` and ``review_claim``; both use the
  ``officer_required`` access decorator.
* Routes: ``/verify`` and ``/verify/<pk>``.
* Templates: ``verify_queue.html`` and ``verify_claim.html``.
* Shared model: ``Claim``. The claim's ``approve`` and ``reject`` model methods
  perform the state changes and notification work.

Workflow
~~~~~~~~

* Officers, administrators, and superusers are permitted by the access
  control used in this app; ordinary authenticated users are denied.
* The queue defaults to pending claims, relies on the claim model's oldest-first
  ordering, and can also show claims in another valid status.
* The review page shows a claim, the associated item, and the other claims for
  that item.
* Approving a pending claim invokes ``Claim.approve``. This marks the item as
  claimed, approves the selected claim, rejects the other pending claims for
  the same item, and creates the related notifications.
* Rejecting requires a non-empty written remark and invokes ``Claim.reject``.
  A claim that is already decided cannot be decided again.

Testing
~~~~~~~

``VerifyClaimsTest`` verifies role access, queue ordering and status filters,
review-page content, display of competing claims, approval effects, mandatory
rejection remarks, decision notifications, prevention of repeated decisions,
no-op submissions without a decision, and officer-only navigation visibility.

Notifications
-------------

Purpose
~~~~~~~

The ``notifications`` app lets an authenticated user read their notifications,
mark them as read, and choose whether notification email copies are enabled.

Application Components
~~~~~~~~~~~~~~~~~~~~~~

* Django app: ``notifications``.
* Views: ``notification_list``, ``open_notification``, ``mark_all_read``, and
  ``set_email_copy``.
* Routes: ``/notifications``, ``/notifications/read-all``,
  ``/notifications/email``, and ``/notifications/<pk>/open``.
* Template: ``notifications.html``.
* Shared models: ``Notification`` and ``Profile``.
* Related services: ``notify_finder_of_new_claim`` and
  ``notify_matching_lost_posters``. Claim decision notifications are created
  by the ``Claim`` model methods in ``core``.

Workflow
~~~~~~~~

* The notification page shows only the logged-in user's notifications and
  their current email-copy setting.
* Opening a notification checks ownership, marks it as read, and redirects only
  to a stored link that begins with ``/``; otherwise it returns to the list.
* A POST to the read-all route updates all unread notifications belonging to
  the current user.
* A POST to the email route updates the profile's ``email_notifications`` flag
  from the presence of the ``email_copy`` form field.

Testing
~~~~~~~

``notifications/tests.py`` contains only Django's default placeholder; no
feature-specific automated tests could be verified in that file.

Profile and My History
----------------------

Purpose
~~~~~~~

The ``profile_history`` app allows an authenticated user to update permitted
profile details and review their item posts and claims.

Application Components
~~~~~~~~~~~~~~~~~~~~~~

* Django app: ``profile_history``.
* Views: ``my_profile`` and ``my_history``; ``clean_photo`` validates an
  uploaded profile image.
* Routes: ``/profile`` and ``/my-history``.
* Templates: ``profile.html`` and ``my_history.html``.
* Shared models: ``Profile``, ``Item``, and ``Claim``.

Workflow
~~~~~~~~

* Both pages require login. The profile page displays the user's profile on
  GET.
* On POST, the user may update their full name, optional phone number, and
  optional profile photo. Phone numbers are checked against the app's pattern;
  images must be valid pictures and no larger than 2 MB.
* The view does not read email or university ID from the submitted form, so
  those fields are not changed by this workflow.
* The history page lists only items posted and claims submitted by the current
  user. Item posts can be filtered by a valid item status; claims are ordered
  newest first.

Testing
~~~~~~~

``ProfileAndHistoryTest`` covers login protection, displayed profile details,
name and phone updates, phone validation, non-editability of email and ID,
photo saving and invalid-file rejection, user-specific item history, status
filtering, and claim-status history.

Admin Management
----------------

Purpose
~~~~~~~

The ``admin_panel`` app provides application-specific management pages for
administrators, separate from Django's built-in ``/admin/`` site.

Application Components
~~~~~~~~~~~~~~~~~~~~~~

* Django app: ``admin_panel``.
* Views: ``dashboard``, ``user_list``, ``set_user_role``, ``set_user_active``,
  ``delete_user``, ``post_list``, ``edit_post``, ``delete_post``,
  ``category_list``, ``rename_category``, ``delete_category``, and
  ``export_report``. The helper ``clean_post_form`` validates administrator
  edits.
* Routes: ``/manage``, ``/manage/report.csv``, ``/manage/users`` and its
  role, active, and delete routes; ``/manage/posts`` and its edit and delete
  routes; and ``/manage/categories`` with rename and delete routes.
* Templates: ``manage_dashboard.html``, ``manage_users.html``,
  ``manage_delete_user.html``, ``manage_posts.html``, ``manage_post_form.html``,
  ``manage_delete_post.html``, and ``manage_categories.html``.
* Shared models: Django's ``User`` model plus ``Category``, ``Item``, and
  ``Claim`` from ``core``.

Workflow
~~~~~~~~

* Every management view is protected by ``admin_required``.
* The dashboard shows counts of lost and found posts, approved and pending
  claims, users, categories, and recent items.
* The user list can be searched by name or email and filtered by role. An admin
  can change another user's role, toggle another account's active state, or
  delete another user after confirmation. The code prevents an admin from
  removing their own admin role, disabling their own account, or deleting
  their own account.
* The post list supports name, type, and status filters. An admin can edit the
  item fields, item type, and status, or remove a post after confirmation.
* The category page creates and renames categories while checking for blank or
  duplicate names. Category deletion is handled by the view, including the
  protected-relation case when items still use the category.
* The report route returns a CSV file with one row per item and includes item,
  category, status, location, posting, and claim-count data.

Testing
~~~~~~~

``ManagementTest`` verifies administrator-only page access, dashboard
statistics, user listing and role changes, self-lockout protections, account
activation changes, confirmed user deletion, post listing/filtering/editing
and deletion confirmation, category management, and CSV report generation.
