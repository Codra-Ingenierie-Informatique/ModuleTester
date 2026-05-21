Command-Line Reference
======================

ModuleTester provides two entry points: the **GUI launcher** and the
**CLI utility**.


GUI launcher: ``moduletester``
------------------------------

Launch the graphical interface.

.. code-block:: console

   $ moduletester [OPTIONS]

**Options**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Flag
     - Type
     - Description
   * - ``-p``, ``--package``
     - str
     - Python package to load on startup. The package must be importable.
   * - ``-f``, ``--file``
     - str
     - Path to a ``.mt`` project file to open on startup.

**Examples**

.. code-block:: console

   # Launch with no project (empty window)
   $ moduletester

   # Open directly on a package
   $ moduletester -p guidata

   # Open a saved project file
   $ moduletester -f /path/to/project.mt

.. note::

   ``--package`` and ``--file`` are mutually exclusive. If both are provided,
   only one will be used.


CLI utility: ``moduletester-cli``
---------------------------------

Run tests and export reports without the GUI.

.. code-block:: console

   $ moduletester-cli <command> [OPTIONS]

**Commands**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Command
     - Description
   * - ``run <package>``
     - Run all tests of the given Python package headlessly.
   * - ``export <package>``
     - Export test results to a document.

**Export options**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Flag
     - Type
     - Description
   * - ``--output``
     - str
     - Output file path. The format is inferred from the file extension
       (``.html``, ``.docx``, ``.odt``, ``.pdf``, ``.md``, ``.rst``).

**Examples**

.. code-block:: console

   # Run all tests of a package
   $ moduletester-cli run mypackage

   # Export results to HTML
   $ moduletester-cli export mypackage --output report.html


Python API
----------

You can also launch ModuleTester programmatically:

.. code-block:: python

   from moduletester.gui.main import run_gui

   # Launches the GUI (blocking call)
   run_gui()

Or use the ``run()`` function for more control:

.. code-block:: python

   from guidata.qthelpers import qt_app_context
   from moduletester.gui.main import run

   with qt_app_context(True):
       main = run(package="mypackage")
       main.window.show()
