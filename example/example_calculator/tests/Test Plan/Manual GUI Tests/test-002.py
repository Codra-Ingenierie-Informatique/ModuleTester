# -*- coding: utf-8 -*-

"""
Example Calculator — Manual GUI Test

Arithmetic operations

TEST-002: Basic arithmetic operations via the GUI

This test verifies that the calculator correctly performs basic arithmetic
operations through the graphical user interface.

.. list-table:: Test steps
   :header-rows: 1
   :widths: 50 50

    * - Action
      - Expected result
    * - Launch the application (in ModuleTester, select
        Manual GUI Tests/test-002 and click "Run Script").
      - The application starts and the "Operations" tab is displayed.
    * - Set A = 10 and B = 5. Select "Add" and click "Compute".
      - The result label displays "Result: 15.0".
    * - Select "Subtract" and click "Compute".
      - The result label displays "Result: 5.0".
    * - Select "Multiply" and click "Compute".
      - The result label displays "Result: 50.0".
    * - Select "Divide" and click "Compute".
      - The result label displays "Result: 2.0".
    * - Select "Power" and click "Compute".
      - The result label displays "Result: 100000.0".
    * - Set B = 0 and select "Divide". Click "Compute".
      - The result label displays "Error: Cannot divide by zero".
    * - Verify the status bar after each operation.
      - The status bar shows a summary of the last operation or error.
    * - Close the application.
      - The application closes without errors.
"""

# guitest: show

import example_calculator.app as app

if __name__ == "__main__":
    app.run()
