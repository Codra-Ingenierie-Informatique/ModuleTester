# -*- coding: utf-8 -*-

"""
Example Calculator — Qualification Test

QUAL-002: Performance benchmark

This qualification test measures the execution time of all arithmetic and
conversion operations to verify they remain within acceptable performance
thresholds.

.. list-table:: Test steps
   :header-rows: 1
   :widths: 50 50

    * - Action
      - Expected result
    * - Launch the qualification script (in ModuleTester, select
        Qualification Tests/002-performance and click "Run Script").
      - The script runs and displays benchmark results in the console.
        A text report is saved in the
        ``TestPlan/reports/YYYY-MM-DD/performance`` folder.
"""

# guitest: show

import os
import time
from datetime import datetime

from example_calculator import converter, operations

# Benchmark definitions: (name, function, args, iterations, max_time_seconds)
BENCHMARKS = [
    ("add", operations.add, (1.5, 2.5), 100_000, 1.0),
    ("subtract", operations.subtract, (10.0, 3.0), 100_000, 1.0),
    ("multiply", operations.multiply, (3.0, 4.0), 100_000, 1.0),
    ("divide", operations.divide, (10.0, 3.0), 100_000, 1.0),
    ("power", operations.power, (2.0, 10.0), 100_000, 1.0),
    ("sqrt", operations.sqrt, (144.0,), 100_000, 1.0),
    ("factorial(20)", operations.factorial, (20,), 100_000, 2.0),
    ("celsius_to_fahrenheit", converter.celsius_to_fahrenheit, (100.0,), 100_000, 1.0),
    ("km_to_miles", converter.km_to_miles, (42.195,), 100_000, 1.0),
]


def run(mode="print", save_path=None):
    """Run performance benchmark.

    Args:
        mode: "print", "save", or "print_save"
        save_path: directory where the report will be saved
    """
    results = []
    all_passed = True

    for name, func, args, iterations, max_time in BENCHMARKS:
        start = time.perf_counter()
        for _ in range(iterations):
            func(*args)
        elapsed = time.perf_counter() - start
        passed = elapsed <= max_time
        if not passed:
            all_passed = False
        per_call = elapsed / iterations
        results.append((name, iterations, elapsed, per_call, max_time, passed))

    # Build report
    lines = []
    lines.append("=" * 80)
    lines.append("QUALIFICATION REPORT — Performance Benchmark")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")
    lines.append(
        f"{'Function':<25} {'Iterations':>12} {'Total (s)':>12} "
        f"{'Per call':>14} {'Max (s)':>10} {'Status':>8}"
    )
    lines.append("-" * 85)

    for name, iterations, elapsed, per_call, max_time, passed in results:
        status = "PASS" if passed else "FAIL"
        lines.append(
            f"{name:<25} {iterations:>12,} {elapsed:>12.4f} "
            f"{per_call:>14.2e} {max_time:>10.1f} {status:>8}"
        )

    lines.append("-" * 85)
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
        report_file = os.path.join(save_path, "performance_report.txt")
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
        "performance",
    )
    success = run("print_save", save_path=report_path)
    if not success:
        print("\n*** QUALIFICATION FAILED ***")
