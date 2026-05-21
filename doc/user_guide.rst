User Guide
==========

This guide walks you through the full ModuleTester workflow: setting up a
project, discovering tests, running them, and exporting reports.


Setting up your project
-----------------------

ModuleTester discovers tests inside a Python package by looking for the
``# guitest: show`` annotation at the top of each test script.

1. Make sure your package is importable (installed or on ``PYTHONPATH``).

2. Add the annotation comment to every test file you want ModuleTester to
   manage:

   .. code-block:: python

      # guitest: show

      def test_example():
          assert 1 + 1 == 2

   Scripts without this annotation are ignored by default (see the
   ``category`` option in :doc:`configuration`).

3. *(Optional)* Create a ``moduletester.ini`` file at the root of your
   package to customise export templates, GUI layout, and other options.
   See :doc:`configuration` for the full reference.


Test discovery
--------------

When you open a package in ModuleTester, it uses
``guidata.guitest.get_test_package()`` to scan the package tree and collect
every script annotated with ``# guitest: show`` (or ``# guitest: skip`` to
explicitly exclude a script).

The discovered tests are displayed in a **tree view** that mirrors the package
structure. Each node shows the test name, its last execution status, and the
date of the last run.

.. figure:: images/shots/empty.png
   :align: center

   ModuleTester main window with dockable panels and tree view navigation


Running tests
-------------

**From the GUI**

1. Launch ModuleTester on your package:

   .. code-block:: console

      $ moduletester -p mypackage

2. Select one or more tests in the tree view.

3. Click the **Run** button in the toolbar (or double-click a test).

4. While a test is running, a spinner appears next to it in the tree view.
   The **Output** and **Error** tabs in the Execution Results panel update
   in real time. A notification icon appears when new output is available.

5. When the test finishes, its status icon updates (accepted, failed, etc.).

**From the command line**

You can also run tests headlessly. See :doc:`cli` for details.


Viewing results
---------------

After execution, select a test in the tree view to inspect its results in
the dockable panels:

- **Test Properties** — shows the test module path, command, and parameters.
- **Execution Results** — contains three tabs:

  - *Comment* — free-text field to annotate the result.
  - *Output Message* — standard output captured during execution.
  - *Error Message* — standard error captured during execution.

- **CLI** — displays the exact command line used to run the test.

.. figure:: images/shots/guidata.moduletester.png
   :align: center

   Running tests on the ``guidata`` package — tree view with status icons,
   test properties, and execution results panels


Working with project files
--------------------------

ModuleTester can save and load project files (**.mt** format) that persist
the test list, results, and comments.

- **Save**: *File → Save* (or *Save As* for a new file).
- **Open**: *File → Open* and select an existing ``.mt`` file.
- **Reload**: *File → Reload* to refresh the test list from the package
  without losing saved results.

You can also open a project file directly from the command line:

.. code-block:: console

   $ moduletester -f /path/to/project.mt


Exporting reports
-----------------

ModuleTester can export test results to several document formats through its
Jinja2-based export engine.

**Supported formats**: HTML, DOCX, ODT, PDF, Markdown, reStructuredText.

**From the GUI**

Use *File → Export* to generate a report. The export dialog lets you choose
the output format and destination.

**From the command line**

.. code-block:: console

   $ moduletester-cli export mypackage --output report.html

See :doc:`templates` to learn how to customise the report appearance using
your own Jinja2 templates and CSS styles.
