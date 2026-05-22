Example — Integrating ModuleTester into your project
=====================================================

This guide walks you through integrating ModuleTester into an existing Python
project, step by step. It uses the **Example Calculator** shipped in the
``example/`` directory of the ModuleTester repository as a reference
implementation. By the end, you will have a fully functional ModuleTester
setup with manual GUI tests, automated unit tests with coverage, and
qualification scripts.

.. contents:: Steps
   :local:
   :depth: 1


Overview of the example project
--------------------------------

The Example Calculator is a minimal Python package with a Qt GUI that
demonstrates the three test categories ModuleTester supports:

- **Manual GUI Tests** — launch the application and follow step-by-step
  instructions displayed in ModuleTester.
- **Unit Tests** — wrapper scripts that run ``pytest`` with ``coverage``
  and generate HTML coverage reports.
- **Qualification Tests** — standalone scripts that verify numerical
  precision and performance against reference values.

.. code-block:: text

   example/
   ├── pyproject.toml
   ├── README.md
   └── example_calculator/
       ├── __init__.py
       ├── app.py                          # Qt GUI (QMainWindow)
       ├── operations.py                   # Arithmetic functions
       ├── converter.py                    # Unit conversion functions
       ├── moduletester.ini                # ModuleTester configuration
       └── tests/
           ├── __init__.py
           ├── moduletester_launcher.py    # Launches ModuleTester GUI
           ├── templates/                  # Export templates and assets
           ├── processing/                 # Actual pytest test files
           │   ├── test_operations.py
           │   └── test_converter.py
           └── Test Plan/
               ├── Manual GUI Tests/
               │   ├── test-001.py
               │   ├── test-002.py
               │   └── test-003.py
               ├── Unit Tests/
               │   ├── 001-operations.py
               │   └── 002-converter.py
               └── Qualification Tests/
                   ├── 001-precision.py
                   └── 002-performance.py


Step 1 — Make your package importable
--------------------------------------

ModuleTester discovers tests by importing your package and scanning its
sub-modules. Your package must be importable from the Python environment
where ModuleTester runs.

For the example project, install it in editable mode:

.. code-block:: console

   $ cd example
   $ pip install -e ".[test]"

.. tip::

   If your project is already installed in your environment (via ``pip install
   -e .`` or similar), you can skip this step.


Step 2 — Organise your tests
------------------------------

Create a ``tests/`` sub-package inside your main package. ModuleTester scans
this sub-package recursively and groups tests by directory.

Use the ``# guitest:`` directive at the top of each Python file to control
how ModuleTester treats it:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Directive
     - Effect
   * - ``# guitest: show``
     - The script appears in the ModuleTester tree view. Use this for all
       test files that should be visible to testers.
   * - ``# guitest: skip``
     - The script is completely ignored during discovery. Use this for
       utility modules, ``pytest`` files, and launchers.
   * - ``# guitest: hide``
     - The script is discovered but hidden from the default "visible"
       category. Useful for batch-only tests.

In the example, the directory structure under ``Test Plan/`` determines how
tests are grouped in the tree view. You are free to choose any directory
names — ModuleTester uses them as-is.


Step 3 — Write manual GUI tests
---------------------------------

Manual GUI tests launch your application and display step-by-step
instructions to the tester. ModuleTester renders the module docstring as
HTML, so write it in reStructuredText with a ``.. list-table::`` describing
actions and expected results.

Here is an annotated example from the calculator project:

.. code-block:: python

   """
   Example Calculator — Manual GUI Test

   TEST-001: Application startup

   This test verifies that the application starts correctly.

   .. list-table:: Test steps
      :header-rows: 1
      :widths: 50 50

       * - Action
         - Expected result
       * - Launch the application.
         - The main window appears with the title "Example Calculator".
       * - Verify that both tabs ("Operations" and "Converter") are present.
         - Both tabs are visible and selectable.
       * - Close the application.
         - The application closes without errors.
   """

   # guitest: show

   import example_calculator.app as app

   if __name__ == "__main__":
       app.run()

Key points:

- The docstring must come **before** the ``# guitest: show`` directive.
- The ``if __name__ == "__main__":`` guard is required — ModuleTester
  executes each test in a subprocess.
- Your application must expose a ``run()`` function (or equivalent) that
  starts the Qt event loop.


Step 4 — Write unit test wrappers with coverage
-------------------------------------------------

You could add ``# guitest: show`` and a ``if __name__`` block directly to
your existing ``pytest`` files, but a cleaner approach is to keep them
untouched and create thin **wrapper scripts** instead. This way your test
files remain standard ``pytest`` modules — the only change is adding
``# guitest: skip`` so ModuleTester ignores them during discovery. The
wrappers call ``pytest.main()`` and optionally collect code coverage.

Wrapper example (``Unit Tests/001-operations.py``):

.. code-block:: python

   """
   UT-001: Arithmetic operations (pytest + coverage)

   .. list-table:: Test steps
      :header-rows: 1
      :widths: 50 50

       * - Action
         - Expected result
       * - Launch the test script.
         - Unit test results and a coverage report are generated.
   """

   # guitest: show

   import os
   from datetime import datetime
   import coverage
   import pytest

   if __name__ == "__main__":
       current_dir = os.path.dirname(os.path.abspath(__file__))
       # Navigate to the project root
       project_root = os.path.dirname(
           os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
       )
       test_dir = os.path.join(project_root, "example_calculator", "tests")

       cov = coverage.Coverage(
           include=["*/example_calculator/operations.py"],
       )
       cov.start()
       pytest.main([
           os.path.join(test_dir, "processing", "test_operations.py"),
           "-v",
       ])
       cov.stop()
       cov.save()
       cov.report(show_missing=False)
       cov.html_report(directory=os.path.join(
           project_root, "TestPlan", "reports",
           datetime.now().strftime("%Y-%m-%d"), "operations",
       ))

The actual ``pytest`` file (``processing/test_operations.py``) must start
with ``# guitest: skip`` to stay hidden from ModuleTester:

.. code-block:: python

   # guitest: skip

   import pytest
   from example_calculator.operations import add, divide

   class TestAdd:
       def test_positive_numbers(self):
           assert add(2, 3) == 5

       def test_negative_numbers(self):
           assert add(-1, -2) == -3

   class TestDivide:
       def test_divide_by_zero(self):
           with pytest.raises(ZeroDivisionError):
               divide(1, 0)


Step 5 — Write qualification scripts
--------------------------------------

Qualification tests are standalone scripts that run computations, compare
results against reference values, and generate reports. They are useful for
performance benchmarks, numerical accuracy checks, or any test that does not
fit the ``pytest`` model.

Because ModuleTester executes every test as a **subprocess**, it is entirely
agnostic to what the script does internally. This makes it straightforward to
integrate any custom test script your project already has — numerical
simulations, hardware-in-the-loop checks, data-processing pipelines, etc. —
without modifying them beyond adding the ``# guitest: show`` directive and a
docstring. This approach even extends to **non-Python projects** (C++, C#,
web applications, …): the wrapper script just needs to call the external
tool via ``subprocess.run()`` or equivalent. The only requirement is that the
wrapper itself is a ``.py`` file so ModuleTester can discover it.

Example (``Qualification Tests/001-precision.py``):

.. code-block:: python

   """
   QUAL-001: Arithmetic precision verification

   .. list-table:: Test steps
      :header-rows: 1
      :widths: 50 50

       * - Action
         - Expected result
       * - Launch the qualification script.
         - The script displays results and saves a report.
   """

   # guitest: show

   import os
   from example_calculator import operations

   REFERENCE_DATA = [
       ("add(0.1, 0.2)", operations.add, (0.1, 0.2), 0.3, 1e-15),
       # ... more test cases
   ]

   def run(mode="print", save_path=None):
       results = []
       for desc, func, args, expected, tol in REFERENCE_DATA:
           computed = func(*args)
           error = abs(computed - expected)
           results.append((desc, computed, expected, error, error <= tol))
       # ... build and save report

   if __name__ == "__main__":
       run("print_save", save_path="TestPlan/reports/precision")


Step 6 — Customise export templates
--------------------------------------

ModuleTester uses **Jinja2 templates** to generate reports. The default
templates are shipped in ``moduletester/default_templates/`` — copy them into
your project's ``tests/templates/`` directory so you can customise them.

Two templates control the exported documents:

- ``test_list_template.j2`` — the **test list** report (test catalogue with
  descriptions only, no results).
- ``test_results_template.j2`` — the **test results** report (full campaign
  output with descriptions, statuses, comments, images, and a summary table).

Both templates have access to the ``doc_obj`` context object, which exposes
the full ``test_suite`` — including the package description, grouped tests,
results, and execution dates.

**Typical customisations:**

- **Project description tracking** — edit the ``<h1>Description</h1>``
  section to include project-specific metadata (version, author, release
  date, reference documents, …).
- **Choosing which information to display** — add or remove sections in each
  test block: description, command, result status, execution date, comments,
  screenshots, etc.
- **Summary table columns** — adjust the summary table at the end of the
  results template to match your reporting needs (e.g. add a "Duration"
  column, remove unused result categories).
- **Styling** — edit ``default_style.css`` to match your organisation's
  branding.

When exporting to **DOCX** or **ODT**, ModuleTester first renders the
Jinja2 template to HTML, then converts that HTML via Pandoc using a
``--reference-doc`` flag. The reference files (``custom-reference.docx`` and
``custom-reference.odt``) act as **style templates**: Pandoc extracts fonts,
heading styles, page layout, headers/footers, and margins from them, then
applies those styles to the generated content. In other words, the
**structure and data** come from the ``.j2`` templates, while the **visual
formatting** comes from the reference document. To match your organisation's
formatting, open the reference file in Word or LibreOffice, adjust the
styles (e.g. ``Heading 1``, ``Normal``, page margins), and save it back.

For the Example Calculator, the templates are used as-is from the defaults.
See :doc:`templates` for the full template API reference.


Step 7 — Create the configuration file
----------------------------------------

Place a ``moduletester.ini`` file next to your package's ``__init__.py``.
This file must declare **all** options in every section — ModuleTester raises
a ``ConfigConflictError`` if any field is missing.

The easiest way to start is to copy the example configuration file and
adapt it:

.. code-block:: ini

   [general]
   docstring_fmt = rst
   category = visible

   [export]
   template_dir = tests/templates
   test_results_template_name = test_results_template.j2
   test_list_template_name = test_list_template.j2
   docx_reference = custom-reference.docx
   odt_reference = custom-reference.odt
   css_style = default_style.css
   export_fmts = html
   reload_templates_on_export = 0
   docstrings_header_shift = 3
   toc_depth = 2

   [gui]
   test_list_visible = 1
   test_list_pos = left
   test_props_visible = 0
   test_props_pos = right
   result_tab_visible = 1
   result_tab_pos = bottom
   result_props_visible = 1
   result_props_pos = bottom
   cli_visible = 0
   cli_pos = bottom
   toolbox_visible = 0
   toolbox_pos = bottom

The ``template_dir`` path is relative to the package directory. You need to
provide the template and asset files in that directory (see
:doc:`templates`). The simplest approach is to copy ModuleTester's default
templates from ``moduletester/default_templates/``.

See :doc:`configuration` for the full reference of all options.


Step 8 — Create a launcher script (optional)
-----------------------------------------------

The launcher script is a convenience tool that generates a ``.moduletester``
template file by discovering all tests in your package, then opens the
ModuleTester GUI. It is typically used by developers to keep the test plan
up to date or to prepare a test campaign before a milestone release.

.. note::

   This step is **optional**. You can achieve the same result by launching
   ModuleTester directly on your package:

   .. code-block:: console

      $ moduletester -p my_package

   Or by opening an existing ``.moduletester`` file:

   .. code-block:: console

      $ moduletester -f TestPlan/my_package_v1.0.0_.moduletester

   The launcher script simply automates the template generation step and can
   be wired to a VS Code task or a CI script for convenience.

.. code-block:: python

   # guitest: skip

   import os
   import sys
   from importlib import import_module

   from qtpy import QtWidgets as QW
   from moduletester.gui.main import run
   from moduletester.manager import TestManager
   from moduletester.model import Module

   from my_package import __version__

   def create_template():
       mod = import_module("my_package")
       project_dir = os.path.dirname(
           os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
       )
       test_plan_dir = os.path.join(project_dir, "TestPlan")
       os.makedirs(test_plan_dir, exist_ok=True)

       output_path = os.path.join(
           test_plan_dir,
           f"my_package_v{__version__}_.moduletester",
       )
       manager = TestManager(
           Module(mod), _template_path=output_path, _category="visible"
       )
       print(f"Found {len(manager.test_suite.tests)} tests")
       return output_path

   if __name__ == "__main__":
       app = QW.QApplication.instance()
       if not app:
           app = QW.QApplication(sys.argv)

       if len(sys.argv) > 1:
           moduletester_file = sys.argv[1]
       else:
           moduletester_file = create_template()

       moduletester = run(path=moduletester_file)
       moduletester.window.show()
       app.exec_()

Run it to launch ModuleTester:

.. code-block:: console

   $ python my_package/tests/moduletester_launcher.py

The launcher generates a ``.moduletester`` file in ``TestPlan/`` and opens
the GUI. You can also pass an existing ``.moduletester`` file as an argument
to reload a previous test session.

.. note::

   The launcher must use ``# guitest: skip`` to avoid appearing in the test
   tree itself.


Running the example
--------------------

To try the full example shipped with ModuleTester:

.. code-block:: console

   $ cd example
   $ pip install -e ".[test]"
   $ python example_calculator/tests/moduletester_launcher.py

This discovers 7 tests (3 manual GUI, 2 unit, 2 qualification) and opens
the ModuleTester GUI. You can run each test, inspect its output, and export
a report.
