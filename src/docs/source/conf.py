import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'simpleautogui'
copyright = '2024, artasov'
author = 'artasov'
release = '0.0.4'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.autodoc'
]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


html_theme = 'furo'
html_static_path = ['_static']
templates_path = ['./_templates']
html_baseurl = 'https://artasov.github.io/simpleautogui/'
html_css_files = [
    'css/custom.css',
]

html_js_files = [
    'js/custom.js',
]