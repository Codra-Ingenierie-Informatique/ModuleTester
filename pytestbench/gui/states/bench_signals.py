# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring, no-value-for-parameter

from PyQt5 import QtWidgets as QW
from PyQt5.QtCore import pyqtSignal  # pylint: disable=no-name-in-module


class TMSignals(QW.QWidget):
    benchLoaded = pyqtSignal()
    benchSaved = pyqtSignal(str)
    benchModified = pyqtSignal()
    testbenchLoaded = pyqtSignal(str)
    templateCreated = pyqtSignal()

    # concerning run
    run_started = pyqtSignal()
    run_paused = pyqtSignal()
    run_stopped = pyqtSignal()
    run_reloaded = pyqtSignal()
