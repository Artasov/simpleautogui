# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'simpleautogui'
copyright = '2024, artasov'
author = 'artasov'
release = '0.0.4'
templates_path = ['./_templates']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.autodoc'
]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


html_theme = 'furo'
html_static_path = ['_static']
html_baseurl = 'https://<username>.github.io/<repository>/'
html_css_files = [
    'css/custom.css',
]

html_js_files = [
    'js/custom.js',
]