# -*- coding: utf-8 -*-

# pylint: skip-file

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

import pytestbench  # noqa: E402

# -- Project information -----------------------------------------------------

project = "PyTestBench"
author = "Pierre Raybaut"
copyright = "2023, Codra - " + author
html_logo = latex_logo = "_static/PyTestBench-title.png"
release = pytestbench.__version__

# -- General configuration ---------------------------------------------------

extensions = ["sphinx.ext.intersphinx", "sphinx.ext.napoleon", "sphinx.ext.mathjax"]
templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_theme_options = {"show_toc_level": 2}
htmlhelp_basename = project
html_static_path = ["_static"]

# -- Options for sphinx-intl package -----------------------------------------

locale_dirs = ["locale/"]  # path is example but recommended.
gettext_compact = False  # optional.

# -- Options for autodoc extension -------------------------------------------

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
}

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "guidata": ("https://guidata.readthedocs.io/en/latest/", None),
}
