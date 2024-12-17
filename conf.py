# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
sys.path.insert(0, "/Users/xgrmir/Documents/DeepTrack_review/deeplay_docs_test/")

import os

# get release from environment variable
version = os.environ.get("VERSION", "")
if not version:
    print("Error: VERSION environment variable not set.")
    sys.exit(1)


project = 'testing_docs_deeplay'
copyright = '2024, Mirja'
author = 'Mirja'
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
# html_static_path = ['_static']

extensions = ["sphinx_automodapi.automodapi", "sphinx.ext.githubpages"]
numpydoc_show_class_members = False
automodapi_inheritance_diagram = False

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_theme_options = {
    "switcher": {
        "json_url": "https://mirjagranfors.github.io/deeplay_docs_test/latest/_static/switcher.json",
        "version_match": version,
    },
    "navbar_end": [
        "version-switcher",
        "navbar-icon-links",
    ],
}