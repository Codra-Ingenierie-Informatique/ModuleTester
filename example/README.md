# Example Calculator — ModuleTester Reference Implementation

This project is a minimal, self-contained example demonstrating how to integrate
[ModuleTester](https://github.com/Codra-Ingenierie-Informatique/ModuleTester/)
into a Python project with a Qt GUI. It mirrors the integration pattern used in
[X-GRID](https://github.com/Codra-Ingenierie-Informatique/X-GRID/).

## Project structure

```
example/
├── pyproject.toml                          # Project metadata & dependencies
├── README.md                               # This file
└── example_calculator/
    ├── __init__.py                          # Package metadata
    ├── app.py                              # Qt GUI application (QMainWindow)
    ├── operations.py                       # Arithmetic functions
    ├── converter.py                        # Unit conversion functions
    ├── moduletester.ini                    # ModuleTester configuration
    └── tests/
        ├── __init__.py
        ├── moduletester_launcher.py        # Launcher for ModuleTester GUI
        ├── templates/                      # Export templates (copied from defaults)
        ├── processing/
        │   ├── test_operations.py          # Actual pytest test cases
        │   └── test_converter.py           # Actual pytest test cases
        └── Test Plan/
            ├── Manual GUI Tests/
            │   ├── test-001.py             # Application startup
            │   ├── test-002.py             # Arithmetic operations via GUI
            │   └── test-003.py             # Unit conversions via GUI
            ├── Unit Tests/
            │   ├── 001-operations.py       # pytest + coverage wrapper
            │   └── 002-converter.py        # pytest + coverage wrapper
            └── Qualification Tests/
                ├── 001-precision.py        # Numerical precision verification
                └── 002-performance.py      # Performance benchmark
```

## Prerequisites

- Python >= 3.9
- A Qt binding (PyQt5, PyQt6, PySide2, or PySide6)
- ModuleTester installed (from the parent directory: `pip install ..`)

## Installation

```bash
cd example
pip install -e ".[test]"
```

## Running the application

```bash
python -m example_calculator.app
```

## Running tests

### With pytest directly

```bash
pytest example_calculator/tests/processing/ -v
```

### With ModuleTester

```bash
python example_calculator/tests/moduletester_launcher.py
```

This will:
1. Discover all tests in `example_calculator.tests` (manual GUI, unit, qualification)
2. Generate a `.moduletester` template in `TestPlan/`
3. Open the ModuleTester GUI where you can run and manage tests

## How to add ModuleTester to your own project

### Step 1: Install ModuleTester

```bash
pip install moduletester
```

### Step 2: Organize your tests

Create a `tests/` subpackage inside your main package with subdirectories for
each test category. Use the `# guitest:` directives at the top of each test file:

- `# guitest: show` — Test is visible in ModuleTester GUI (manual GUI tests,
  wrapper scripts)
- `# guitest: skip` — File is ignored by ModuleTester (actual pytest files,
  utility modules)
- `# guitest: hide` — Test exists but is hidden from the default "visible"
  category

### Step 3: Write test docstrings in RST

ModuleTester extracts the module docstring to display test instructions.
Use RST `.. list-table::` for step-by-step instructions:

```python
"""
TEST-001: My test description

.. list-table:: Test steps
   :header-rows: 1
   :widths: 50 50

    * - Action
      - Expected result
    * - Do something
      - Something happens
"""
# guitest: show
```

### Step 4: Create a `moduletester.ini`

Place a `moduletester.ini` file next to your package's `__init__.py`. See
[example_calculator/moduletester.ini](example_calculator/moduletester.ini) for a
fully commented reference.

### Step 5: Create a launcher

Write a launcher script that uses `TestManager` to discover tests and open the
ModuleTester GUI. See
[moduletester_launcher.py](example_calculator/tests/moduletester_launcher.py).

### Step 6: Create pytest wrappers (for unit tests)

For unit tests, create wrapper scripts that call `pytest.main()` with the
`coverage` API. These wrappers use `# guitest: show` so they appear in
ModuleTester, while the actual pytest files use `# guitest: skip`.

### Step 7: Create qualification scripts (optional)

For qualification or acceptance tests, create standalone scripts that run
computations, compare results to references, and generate text or HTML reports.
