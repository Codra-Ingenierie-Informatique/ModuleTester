# -*- coding: utf-8 -*-

"""Update requirements.txt from pyproject.toml.

Combines [project.dependencies] and all [project.optional-dependencies]
groups into a single requirements.txt file at the repository root.
"""

import os
import re
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore


def strip_version_specifiers(dep: str) -> str:
    """Return the package name without version specifiers.

    Example: 'guidata >= 3.14' -> 'guidata'
    """
    return re.split(r"[><=!~\s;]", dep)[0].strip()


def generate_requirements_txt(pyproject_path: str, output_path: str) -> None:
    """Generate requirements.txt from pyproject.toml."""
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    all_deps: dict[str, str] = {}

    # Collect main dependencies
    for dep in project.get("dependencies", []):
        name = strip_version_specifiers(dep)
        all_deps[name.lower()] = name

    # Collect all optional-dependencies groups
    for group, deps in project.get("optional-dependencies", {}).items():
        for dep in deps:
            name = strip_version_specifiers(dep)
            all_deps[name.lower()] = name

    # Sort case-insensitively and write
    sorted_deps = sorted(all_deps.values(), key=str.lower)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted_deps) + "\n")


if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pyproject_path = os.path.join(root_dir, "pyproject.toml")
    output_path = os.path.join(root_dir, "requirements.txt")
    print("Updating requirements.txt from pyproject.toml...", end=" ")
    generate_requirements_txt(pyproject_path, output_path)
    print("done.")
