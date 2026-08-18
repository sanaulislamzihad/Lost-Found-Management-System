# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# -- Django setup for autodoc -------------------------------------------------
# api.rst documents the Django project's source with sphinx.ext.autodoc,
# which imports every module it documents. Django has to be configured
# before that happens, so this block puts the project on sys.path, points
# Django at its settings module, and calls django.setup() - the same three
# steps manage.py performs, done here only for the Sphinx process. It does
# not run migrations or touch the database, and it does not modify the
# Django application itself.
#
# conf.py lives in docs/source/, three levels below the project root (the
# folder that holds manage.py).
DJANGO_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(DJANGO_PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lost_and_found.settings')

import django  # noqa: E402 (must run after sys.path/env are set above)
django.setup()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Lost & Found Management System'
copyright = '2026, Md Sanaul Islam Zihad, Jannatun Ferdousi, Shahed Mehbub Shourov, Natasha Anwar, Ridita Rahman'
author = 'Md Sanaul Islam Zihad, Jannatun Ferdousi, Shahed Mehbub Shourov, Natasha Anwar, Ridita Rahman'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
