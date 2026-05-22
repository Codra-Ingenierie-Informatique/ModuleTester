# -*- coding: utf-8 -*-

"""
Example Calculator — Manual GUI Test

Unit conversions

TEST-003: Unit conversions via the GUI

This test verifies that the calculator correctly performs unit conversions
through the graphical user interface.

.. list-table:: Test steps
   :header-rows: 1
   :widths: 50 50

    * - Action
      - Expected result
    * - Launch the application (in ModuleTester, select
        Manual GUI Tests/test-003 and click "Run Script").
      - The application starts. Navigate to the "Converter" tab.
    * - Set Value = 100. Select "Celsius → Fahrenheit" and click "Convert".
      - The result label displays "Result: 212.000000".
    * - Select "Fahrenheit → Celsius" and click "Convert".
      - The result label displays "Result: 37.777778".
    * - Set Value = 0. Select "Celsius → Kelvin" and click "Convert".
      - The result label displays "Result: 273.150000".
    * - Set Value = 1. Select "Km → Miles" and click "Convert".
      - The result label displays "Result: 0.621371".
    * - Set Value = 1. Select "Meters → Feet" and click "Convert".
      - The result label displays "Result: 3.280840".
    * - Set Value = -300. Select "Celsius → Kelvin" and click "Convert".
      - The result label displays "Error: Temperature below absolute zero
        is not physical".
    * - Close the application.
      - The application closes without errors.
"""

# guitest: show

import example_calculator.app as app

if __name__ == "__main__":
    app.run()
