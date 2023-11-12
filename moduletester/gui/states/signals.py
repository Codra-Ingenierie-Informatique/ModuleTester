# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring, no-value-for-parameter

from qtpy import QtWidgets as QW
from qtpy.QtCore import Signal


class TMSignals(QW.QWidget):
    SIG_PROJECT_LOADED = Signal()
    SIG_PROJECT_SAVED = Signal(str)
    SIG_PROJECT_MODIFIED = Signal()
    SIG_FILE_LOADED = Signal(str)
    SIG_TEMPLATE_CREATED = Signal()

    # concerning run
    SIG_RUN_STARTED = Signal()
    SIG_RUN_PAUSED = Signal()
    SIG_RUN_STOPPED = Signal()
    SIG_RUN_RELOADED = Signal()
