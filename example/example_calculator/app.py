# -*- coding: utf-8 -*-

"""
Example Calculator — Qt GUI Application
----------------------------------------

A minimal QMainWindow-based calculator demonstrating a typical Qt application
that can be tested with ModuleTester manual GUI tests.
"""

import sys

from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from example_calculator import converter, operations


class CalculatorWindow(QW.QMainWindow):
    """Main window for the Example Calculator application."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Example Calculator")
        self.setMinimumSize(400, 350)

        central = QW.QWidget()
        self.setCentralWidget(central)
        layout = QW.QVBoxLayout(central)

        # --- Calculator tab ---
        tabs = QW.QTabWidget()
        layout.addWidget(tabs)

        # Tab 1: Arithmetic operations
        calc_widget = QW.QWidget()
        calc_layout = QW.QFormLayout(calc_widget)

        self.input_a = QW.QDoubleSpinBox()
        self.input_a.setRange(-1e9, 1e9)
        self.input_a.setDecimals(6)
        calc_layout.addRow("A:", self.input_a)

        self.input_b = QW.QDoubleSpinBox()
        self.input_b.setRange(-1e9, 1e9)
        self.input_b.setDecimals(6)
        calc_layout.addRow("B:", self.input_b)

        self.operation_combo = QW.QComboBox()
        self.operation_combo.addItems(
            ["Add", "Subtract", "Multiply", "Divide", "Power"]
        )
        calc_layout.addRow("Operation:", self.operation_combo)

        self.calc_button = QW.QPushButton("Compute")
        self.calc_button.clicked.connect(self._on_compute)
        calc_layout.addRow(self.calc_button)

        self.result_label = QW.QLabel("Result: —")
        self.result_label.setAlignment(QC.Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        calc_layout.addRow(self.result_label)

        tabs.addTab(calc_widget, "Operations")

        # Tab 2: Unit converter
        conv_widget = QW.QWidget()
        conv_layout = QW.QFormLayout(conv_widget)

        self.conv_input = QW.QDoubleSpinBox()
        self.conv_input.setRange(-1e9, 1e9)
        self.conv_input.setDecimals(6)
        conv_layout.addRow("Value:", self.conv_input)

        self.conv_combo = QW.QComboBox()
        self.conv_combo.addItems(
            [
                "Celsius → Fahrenheit",
                "Fahrenheit → Celsius",
                "Celsius → Kelvin",
                "Kelvin → Celsius",
                "Meters → Feet",
                "Feet → Meters",
                "Km → Miles",
                "Miles → Km",
            ]
        )
        conv_layout.addRow("Conversion:", self.conv_combo)

        self.conv_button = QW.QPushButton("Convert")
        self.conv_button.clicked.connect(self._on_convert)
        conv_layout.addRow(self.conv_button)

        self.conv_result_label = QW.QLabel("Result: —")
        self.conv_result_label.setAlignment(QC.Qt.AlignCenter)
        self.conv_result_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        conv_layout.addRow(self.conv_result_label)

        tabs.addTab(conv_widget, "Converter")

        # Status bar
        self.statusBar().showMessage("Ready")

    def _on_compute(self):
        """Execute the selected arithmetic operation."""
        a = self.input_a.value()
        b = self.input_b.value()
        op = self.operation_combo.currentText()

        op_map = {
            "Add": operations.add,
            "Subtract": operations.subtract,
            "Multiply": operations.multiply,
            "Divide": operations.divide,
            "Power": operations.power,
        }

        try:
            result = op_map[op](a, b)
            self.result_label.setText(f"Result: {result}")
            self.statusBar().showMessage(f"{a} {op} {b} = {result}")
        except (ZeroDivisionError, ValueError, OverflowError) as e:
            self.result_label.setText(f"Error: {e}")
            self.statusBar().showMessage(f"Error: {e}")

    def _on_convert(self):
        """Execute the selected unit conversion."""
        value = self.conv_input.value()
        conversion = self.conv_combo.currentText()

        conv_map = {
            "Celsius → Fahrenheit": converter.celsius_to_fahrenheit,
            "Fahrenheit → Celsius": converter.fahrenheit_to_celsius,
            "Celsius → Kelvin": converter.celsius_to_kelvin,
            "Kelvin → Celsius": converter.kelvin_to_celsius,
            "Meters → Feet": converter.meters_to_feet,
            "Feet → Meters": converter.feet_to_meters,
            "Km → Miles": converter.km_to_miles,
            "Miles → Km": converter.miles_to_km,
        }

        try:
            result = conv_map[conversion](value)
            self.conv_result_label.setText(f"Result: {result:.6f}")
            self.statusBar().showMessage(f"{value} → {result:.6f}")
        except ValueError as e:
            self.conv_result_label.setText(f"Error: {e}")
            self.statusBar().showMessage(f"Error: {e}")


def run():
    """Launch the Example Calculator application."""
    app = QW.QApplication.instance()
    standalone = app is None
    if standalone:
        app = QW.QApplication(sys.argv)

    window = CalculatorWindow()
    window.show()

    if standalone:
        app.exec()


if __name__ == "__main__":
    run()
