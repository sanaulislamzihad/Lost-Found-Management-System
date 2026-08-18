Installation and Setup
======================

This page documents the local development setup provided by the project
README and its Django management configuration.

Prerequisites
-------------

The project is a Python/Django application. The repository README provides
commands using ``python`` and installs Django and Pillow. It does not specify a
pinned Python version, a supported Python-version range, or a dependency lock
file; those details therefore cannot be verified from the repository.

The documented setup assumes access to Python and to ``pip`` through the
virtual environment's Python installation.

Clone the Repository
--------------------

Clone the repository and move into the project directory:

.. code-block:: bash

   git clone https://github.com/sanaulislamzihad/Lost-Found-Management-System.git
   cd Lost-Found-Management-System

Create a Virtual Environment
----------------------------

The README creates a virtual environment named ``.venv`` using:

.. code-block:: bash

   python -m venv .venv

The repository's ``.gitignore`` excludes both ``.venv/`` and ``venv/`` from
version control.

Install Dependencies
--------------------

The documented dependency installation command is:

.. code-block:: bash

   .venv\Scripts\pip install django pillow

This command installs Django and Pillow. Pillow is used by the project for the
``ImageField`` values defined for item and profile images. The README notes
that the corresponding virtual-environment executable path on Linux or macOS
is ``.venv/bin/pip``.

Database Setup
--------------

Apply the Django migrations before using the application:

.. code-block:: bash

   .venv\Scripts\python manage.py migrate

``manage.py`` sets ``lost_and_found.settings`` as the Django settings module.
That settings module configures SQLite with ``db.sqlite3`` in the project base
directory. The database file is excluded by ``.gitignore``, so a fresh clone
does not include existing database records.

Create a Superuser
------------------

Create a Django superuser with:

.. code-block:: bash

   .venv\Scripts\python manage.py createsuperuser

The README advises using an email address as the username because the
application login form expects an email address. A Django superuser can access
the management and claim-verification areas as well as Django's own admin
site.

Create Demo Accounts
--------------------

For local demonstration, the project includes the custom Django management
command ``createdemousers``:

.. code-block:: bash

   .venv\Scripts\python manage.py createdemousers

The command is implemented in
``core/management/commands/createdemousers.py``. It creates or resets the
following accounts and assigns their profile roles:

* **Admin** — ``admin@northsouth.edu`` / ``admin123456``. This user is also a
  Django superuser and can access the management pages, claim queue, and
  Django ``/admin/`` site.
* **Security Officer** — ``officer@northsouth.edu`` / ``officer123456``. This
  user can access the claim queue at ``/verify``.
* **Student** — ``student@northsouth.edu`` / ``student123456``. This user can
  use posting, search, claiming, and personal-history features.

The command uses ``get_or_create`` and resets the configured passwords when it
is run again. These are published, weak credentials intended for local testing
only and must not be used for a deployed system.

Run the Development Server
--------------------------

Start Django's development server with:

.. code-block:: bash

   .venv\Scripts\python manage.py runserver

Open the local application at:

.. code-block:: text

   http://127.0.0.1:8000/

The current settings enable ``DEBUG`` and configure the root URL module to
serve uploaded media files using Django's development ``static`` helper.

Initial Login and Roles
-----------------------

After creating either a superuser or the demo users, log in through the
application's ``/login`` route. The source-defined profile roles are Student,
Staff, Security Officer, and Admin. The demo command creates Admin, Security
Officer, and Student accounts; it does not create a Staff demo account.

According to the access logic in the source, the claim-verification views
allow Security Officers, Admins, and Django superusers. The management views
allow Admins and Django superusers. Other authenticated feature views use
Django login protection and, where relevant, ownership checks.
