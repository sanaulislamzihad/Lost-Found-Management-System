Introduction
============

The Lost & Found Management System is a web application developed for the
CSE-327 Software Engineering course at North South University. It provides a
centralized campus platform through which users can report lost and found
items, search available reports, and submit claims for found property.

The system supports a controlled handover process: a claimant provides proof
of ownership, and a Security Officer reviews the claim before an item is
released. It also retains records of posts, claims, and claim decisions to
support user history and administrative oversight.

Purpose
=======

The application is intended to make the campus lost-and-found process more
organized and accessible. Rather than relying on informal communication, users
can create lost or found item reports and search them by item information,
category, location, and date.

In addition to connecting people who have lost items with people who have
found them, the system provides a verification step for claims. Notifications
inform users about relevant claim activity and matching item reports, while
administrative functions support management of users, posts, categories, and
activity reports.

Technology
==========

The application is implemented in Python using the Django web framework. It
follows Django's Model--View--Template (MVT) architectural pattern:

* Models define the shared application data, including items, categories,
  claims, notifications, and user profiles.
* Views implement request handling and application logic.
* Templates provide the HTML pages displayed to users.

System Roles
============

The system defines the following roles:

Student / Staff
---------------

Student and staff users can report lost and found items, search item reports,
submit claims, and review their own activity history.

Security Officer
----------------

Security Officers have the capabilities available to Student / Staff users and
can also access the claim queue to review and approve or reject item claims.

Admin
-----

Administrators have the capabilities available to the other roles and can use
the management pages to oversee users, posts, item categories, system
statistics, and activity reports.

Project Organization
====================

The project is organized into a Django project package, shared components, and
feature-specific applications:

* ``lost_and_found/`` contains project-level configuration, including settings
  and the root URL configuration.
* ``core/`` contains the shared data models used across the system, such as
  categories, items, claims, notifications, and profiles.
* Feature-specific Django apps implement individual functions, including
  registration, authentication, lost and found item reporting, search,
  claiming, claim verification, notifications, profile history, and
  administration.
* ``templates/`` contains the HTML templates for the application's pages.
* ``static/`` contains static assets, including the stylesheet and images.
