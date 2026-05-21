# -*- coding: utf-8 -*-

"""
ModuleTester Integration Launcher for Example Calculator

This script creates a .moduletester template file for the example_calculator
package and launches the ModuleTester GUI. It follows the same pattern as
the X-GRID launcher (xgrid/tests/module_tester/moduleTester_launcher.py).

Usage::

    # Generate a new template and launch ModuleTester GUI
    python moduletester_launcher.py

    # Open an existing .moduletester file
    python moduletester_launcher.py path/to/file.moduletester
"""

# guitest: skip

import os
import sys
from importlib import import_module

from qtpy import QtWidgets as QW

from example_calculator import __version__
from moduletester.gui.main import run
from moduletester.manager import TestManager
from moduletester.model import Module


def create_template():
    """Create a .moduletester template file for Example Calculator tests.

    Returns:
        str: Path to the generated .moduletester file.
    """
    mod = import_module("example_calculator")

    project_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    test_plan_dir = os.path.join(project_dir, "TestPlan")
    os.makedirs(test_plan_dir, exist_ok=True)

    output_path = os.path.join(
        test_plan_dir,
        f"example_calculator_v{__version__}_.moduletester",
    )
    print(f"Creating template at: {output_path}")

    manager = TestManager(Module(mod), _template_path=output_path, _category="visible")

    print(f"\nTemplate created successfully: {output_path}")
    print(f"Found {len(manager.test_suite.tests)} tests")

    return output_path


if __name__ == "__main__":
    app = QW.QApplication.instance()
    if not app:
        app = QW.QApplication(sys.argv)

    if len(sys.argv) > 1:
        moduletester_file = sys.argv[1]
        if not os.path.exists(moduletester_file):
            print(f"Error: File not found: {moduletester_file}")
            sys.exit(1)
    else:
        moduletester_file = create_template()

    moduletester = run(path=moduletester_file)
    moduletester.window.show()
    app.exec_()
