# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring, no-value-for-parameter

from qtpy import QtWidgets as QW
from qtpy.QtCore import Signal


class TMSignals(QW.QWidget):
    benchLoaded = Signal()
    benchSaved = Signal(str)
    benchModified = Signal()
    testbenchLoaded = Signal(str)
    templateCreated = Signal()

    # concerning run
    run_started = Signal()
    run_paused = Signal()
    run_stopped = Signal()
    run_reloaded = Signal()
