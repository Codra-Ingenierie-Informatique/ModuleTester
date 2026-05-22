# -*- coding: utf-8 -*-

"""
Example Calculator — Manual GUI Test

Basic tests and application launch

TEST-001: Application startup

This test verifies that the Example Calculator application starts correctly
and that the main window is displayed with all expected UI components.

.. list-table:: Test steps
   :header-rows: 1
   :widths: 50 50

    * - Action
      - Expected result
    * - Launch the Example Calculator application (in ModuleTester, select
        Manual GUI Tests/test-001 and click "Run Script").
      - The application starts and the main window appears with the title
        "Example Calculator".
    * - Verify that the main window contains two tabs: "Operations" and
        "Converter".
      - Both tabs are visible and can be selected.
    * - On the "Operations" tab, verify the presence of:

        - Two numeric input fields (A and B)
        - An operation selector (Add, Subtract, Multiply, Divide, Power)
        - A "Compute" button
        - A result label
      - All components are present and the result label shows "Result: —".
    * - On the "Converter" tab, verify the presence of:

        - One numeric input field (Value)
        - A conversion selector (8 conversions available)
        - A "Convert" button
        - A result label
      - All components are present and the result label shows "Result: —".
    * - Verify the status bar at the bottom of the window.
      - The status bar displays "Ready".
    * - Close the application.
      - The application closes without errors.
"""

# guitest: show

import example_calculator.app as app

if __name__ == "__main__":
    app.run()
