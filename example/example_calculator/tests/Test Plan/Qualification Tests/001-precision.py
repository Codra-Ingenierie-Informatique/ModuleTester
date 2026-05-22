# -*- coding: utf-8 -*-

"""
Example Calculator — Qualification Test

QUAL-001: Arithmetic precision verification

This qualification test verifies the numerical precision of all arithmetic
operations by comparing computed results against known reference values.
A detailed report is generated.

.. list-table:: Test steps
   :header-rows: 1
   :widths: 50 50

    * - Action
      - Expected result
    * - Launch the qualification script (in ModuleTester, select
        Qualification Tests/001-precision and click "Run Script").
      - The script runs and displays results in the console. A text report
        is saved in the ``TestPlan/reports/YYYY-MM-DD/precision`` folder.
"""

# guitest: show

import math
import os
from datetime import datetime

from example_calculator import operations

# Reference values: (description, function, args, expected, tolerance)
REFERENCE_DATA = [
    ("add(0.1, 0.2)", operations.add, (0.1, 0.2), 0.3, 1e-15),
    ("add(1e15, 1e-15)", operations.add, (1e15, 1e-15), 1e15, 1.0),
    ("subtract(1.0, 0.9)", operations.subtract, (1.0, 0.9), 0.1, 1e-15),
    ("multiply(0.1, 0.1)", operations.multiply, (0.1, 0.1), 0.01, 1e-16),
    ("multiply(1e8, 1e8)", operations.multiply, (1e8, 1e8), 1e16, 1.0),
    ("divide(1, 3)", operations.divide, (1, 3), 1 / 3, 1e-15),
    ("divide(1e-10, 1e10)", operations.divide, (1e-10, 1e10), 1e-20, 1e-35),
    ("power(2, 10)", operations.power, (2, 10), 1024.0, 1e-10),
    ("power(2, 0.5)", operations.power, (2, 0.5), math.sqrt(2), 1e-15),
    ("sqrt(2)", operations.sqrt, (2,), math.sqrt(2), 1e-15),
    ("sqrt(1e-20)", operations.sqrt, (1e-20,), 1e-10, 1e-25),
    ("factorial(10)", operations.factorial, (10,), 3628800, 0),
    ("factorial(20)", operations.factorial, (20,), 2432902008176640000, 0),
]


def run(mode="print", save_path=None):
    """Run precision qualification tests.

    Args:
        mode: "print", "save", or "print_save"
        save_path: directory where the report will be saved
    """
    results = []
    all_passed = True

    for desc, func, args, expected, tolerance in REFERENCE_DATA:
        computed = func(*args)
        error = abs(computed - expected)
        passed = error <= tolerance
        if not passed:
            all_passed = False
        results.append((desc, computed, expected, error, tolerance, passed))

    # Build report
    lines = []
    lines.append("=" * 72)
    lines.append("QUALIFICATION REPORT — Arithmetic Precision")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"{'Test':<30} {'Computed':>18} {'Expected':>18} {'Error':>12} {'Status':>8}")
    lines.append("-" * 90)

    for desc, computed, expected, error, tolerance, passed in results:
        status = "PASS" if passed else "FAIL"
        lines.append(
            f"{desc:<30} {computed:>18.10g} {expected:>18.10g} {error:>12.2e} {status:>8}"
        )

    lines.append("-" * 90)
    total = len(results)
    passed_count = sum(1 for *_, p in results if p)
    lines.append(f"Results: {passed_count}/{total} passed")
    lines.append(f"Overall: {'PASS' if all_passed else 'FAIL'}")
    lines.append("")

    report_text = "\n".join(lines)

    if "print" in mode:
        print(report_text)

    if "save" in mode and save_path is not None:
        os.makedirs(save_path, exist_ok=True)
        report_file = os.path.join(save_path, "precision_report.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Report saved to: {report_file}")

    return all_passed


if __name__ == "__main__":
    project_root = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    )
    report_path = os.path.join(
        project_root,
        "TestPlan",
        "reports",
        datetime.now().strftime("%Y-%m-%d"),
        "precision",
    )
    success = run("print_save", save_path=report_path)
    if not success:
        print("\n*** QUALIFICATION FAILED ***")
