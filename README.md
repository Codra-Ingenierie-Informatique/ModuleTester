![ModuleTester](https://raw.githubusercontent.com/Codra-Ingenierie-Informatique/ModuleTester/main/doc/_static/ModuleTester-banner.png)

[![license](https://img.shields.io/pypi/l/ModuleTester.svg)](./LICENSE)
[![pypi version](https://img.shields.io/pypi/v/ModuleTester.svg)](https://pypi.org/project/ModuleTester/)
[![PyPI status](https://img.shields.io/pypi/status/ModuleTester.svg)](https://github.com/Codra-Ingenierie-Informatique/ModuleTester)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ModuleTester.svg)](https://pypi.python.org/pypi/ModuleTester/)
[![CI](https://github.com/Codra-Ingenierie-Informatique/ModuleTester/actions/workflows/test.yml/badge.svg)](https://github.com/Codra-Ingenierie-Informatique/ModuleTester/actions/workflows/test.yml)

ℹ️ Created by [Codra](https://codra.net/) in 2023, developed and maintained by ModuleTester open-source project team with the support of [Codra](https://codra.net/).

ℹ️ ModuleTester is powered by [PlotPyStack](https://github.com/PlotPyStack) 🚀.

![PlotPyStack](https://raw.githubusercontent.com/PlotPyStack/.github/main/data/plotpy-stack-powered.png)

----

## Overview

ModuleTester is a GUI and CLI test management tool for Python packages. It
automatically discovers test scripts, runs them, and generates detailed reports
in multiple formats.

**Key features:**

- **Dockable panel layout** — fully customizable workspace with resizable,
  floatable panels
- **Tree view navigation** — hierarchical test browser with status icons,
  notifications, and live spinner during execution
- **Multi-format export** — generate reports in HTML, DOCX, ODT, PDF, Markdown,
  and reStructuredText via a Jinja2-based engine
- **CLI support** — run tests and export reports without the GUI
  (`moduletester-cli run`, `moduletester-cli export`)
- **Built-in configuration editor** — edit settings directly in the GUI with
  error handling and conflict resolution
- **Notification system** — visual indicators on tabs and tree items for new
  output and errors

ModuleTester is a spin-off of [DataLab](https://github.com/Codra-Ingenierie-Informatique/DataLab)
and is used to test [PlotPyStack](https://github.com/PlotPyStack) libraries.

![ModuleTester — empty window](https://raw.githubusercontent.com/Codra-Ingenierie-Informatique/ModuleTester/main/doc/images/shots/empty.png)

## Quick Start

1. **Install** ModuleTester:

   ```bash
   pip install ModuleTester
   ```

2. **Mark test scripts** you want to see in the GUI by adding a comment at the
   top of each script:

   ```python
   # guitest: show
   ```

3. **Launch the GUI** on your package:

   ```bash
   moduletester --module mypackage
   ```

   Or use the **CLI** to run tests headlessly:

   ```bash
   moduletester-cli run mypackage
   ```

4. **Export a report**:

   ```bash
   moduletester-cli export mypackage --output report.html
   ```

## Example

Using ModuleTester on the `guidata` Python package — the tree view shows test
hierarchy and execution status, while dockable panels display test properties,
output, and errors:

![ModuleTester — guidata tests](https://raw.githubusercontent.com/Codra-Ingenierie-Informatique/ModuleTester/main/doc/images/shots/guidata.moduletester.png)

## Documentation

Full documentation is available at
[moduletester.readthedocs.io](https://moduletester.readthedocs.io/en/latest/).

- [Installation guide](https://moduletester.readthedocs.io/en/latest/installation.html)
- [Usage (GUI & CLI)](https://moduletester.readthedocs.io/en/latest/usage.html)
- [Changelog](https://github.com/Codra-Ingenierie-Informatique/ModuleTester/blob/main/CHANGELOG.md)

## Credits

Copyrights and licensing:

* Copyright © 2023 [Codra](https://codra.net/).
* Licensed under the terms of the BSD 3-Clause (see [LICENSE](LICENSE)).

## Dependencies and other installation methods

See [Installation](https://moduletester.readthedocs.io/en/latest/installation.html)
section in the documentation for more details.
