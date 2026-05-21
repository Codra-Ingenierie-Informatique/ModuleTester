# -*- coding: utf-8 -*-

"""Update requirements.rst file from pyproject.toml file.

Warning: this has to be done manually at release time.
It is not done automatically by the sphinx 'conf.py' file because it
requires an internet connection to fetch the dependencies metadata - this
is not always possible (e.g., when building the documentation on a machine
without internet connection like the Debian package management infrastructure).
"""

import os

from guidata.utils.genreqs import generate_requirements_rst  # noqa: E402

if __name__ == "__main__":
    print("Updating requirements.rst file...", end=" ")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pyproject_path = os.path.join(root_dir, "pyproject.toml")
    doc_dir = os.path.join(root_dir, "doc")
    generate_requirements_rst(pyproject_path, doc_dir)
    print("done.")
