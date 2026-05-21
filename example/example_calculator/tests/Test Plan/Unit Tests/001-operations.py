# -*- coding: utf-8 -*-

"""
Example Calculator — Unit Tests

UT-001: Arithmetic operations (pytest + coverage)

These unit tests verify the arithmetic functions in the
``example_calculator.operations`` module using pytest. Code coverage is
collected and an HTML report is generated.

.. list-table:: Test steps
   :header-rows: 1
   :widths: 50 50

    * - Action
      - Expected result
    * - Launch the test script (in ModuleTester, select
        Unit Tests/001-operations and click "Run Script").
      - The test script runs. Unit test results are displayed in the console.
        An HTML coverage report is generated in the
        ``TestPlan/reports/YYYY-MM-DD/operations`` folder.
"""

# guitest: show

import os
from datetime import datetime

import coverage
import pytest

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    )
    test_dir = os.path.join(project_root, "example_calculator", "tests")

    cov = coverage.Coverage(
        include=["*/example_calculator/operations.py"],
    )
    cov.start()

    pytest.main(
        [
            os.path.join(test_dir, "processing", "test_operations.py"),
            "-v",
        ]
    )

    cov.stop()
    cov.save()
    cov.report(show_missing=False)

    report_dir = os.path.join(
        project_root,
        "TestPlan",
        "reports",
        datetime.now().strftime("%Y-%m-%d"),
        "operations",
    )
    cov.html_report(directory=report_dir)
    print(f"\nCoverage HTML report saved to: {report_dir}")
