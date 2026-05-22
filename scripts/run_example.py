# -*- coding: utf-8 -*-

"""Launch the ModuleTester GUI with the Example Calculator test suite.

This script mirrors the pattern used in X-GRID's ``run_test_plan.bat`` /
``moduleTester_launcher.py``, but as a standalone Python script suitable
for use as a VS Code task.

Usage::

    python scripts/run_example.py
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

LAUNCHER = (
    PROJECT_ROOT
    / "example"
    / "example_calculator"
    / "tests"
    / "moduletester_launcher.py"
)


def main():
    """Run the Example Calculator ModuleTester launcher."""
    if not LAUNCHER.exists():
        print(f"Error: launcher not found at {LAUNCHER}")
        sys.exit(1)

    print(f"Launching ModuleTester example from: {LAUNCHER}")
    result = subprocess.run(
        [sys.executable, str(LAUNCHER)],
        cwd=str(PROJECT_ROOT / "example"),
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
