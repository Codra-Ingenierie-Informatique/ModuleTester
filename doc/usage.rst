Usage
=====

ModuleTester can be used either as a GUI application or as a command-line tool.


Graphical User Interface
------------------------

To launch the graphical interface:

.. code-block:: console

    $ moduletester

Or from Python:

.. code-block:: python

    from moduletester.gui.main import run_gui
    run_gui()

You can also open a project file or target a specific Python package directly:

.. code-block:: console

    $ moduletester --path /path/to/project.mtf
    $ moduletester --module mypackage


Command-Line Interface
----------------------

ModuleTester provides a CLI for running tests without the GUI:

.. code-block:: console

    $ moduletester-cli --help

Run all tests of a Python package:

.. code-block:: console

    $ moduletester-cli run mypackage

Export results to an HTML report:

.. code-block:: console

    $ moduletester-cli export mypackage --output report.html


Configuration
-------------

ModuleTester stores its configuration in a user-specific directory
managed by `guidata <https://pypi.python.org/pypi/guidata>`_.

The configuration can be edited from the GUI via the **Settings** menu
or by editing the configuration file directly through the built-in editor.