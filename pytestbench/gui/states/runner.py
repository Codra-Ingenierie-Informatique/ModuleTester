# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Optional

from PyQt5 import QtCore as QC

from ...model import TestSuite

# from PyQt5 import QtWidgets as QW


class QSubprocess(QC.QThread):
    run_ended = QC.pyqtSignal()
    result_modified = QC.pyqtSignal(str, str)
    run_started = QC.pyqtSignal()

    def __init__(
        self, test_suite: TestSuite, test_name: str, parent: Optional[QC.QObject] = None
    ) -> None:
        super().__init__(parent)

        self.test_suite = test_suite
        self.test_name = test_name

        self.timer = QC.QTimer()
        self.timer.setSingleShot(False)
        self._is_test_running = False

    def run(self) -> None:
        self.timer.timeout.connect(self.handle_timeout)  # type: ignore
        self._is_test_running = True

        self.test_suite.run("all", self.test_name)
        self.run_ended.emit()

    def stop(self, forced: bool = False) -> None:
        self.timer.stop()
        self.test_suite.running_test.stop(forced)
        self._is_test_running = False

    def handle_timeout(self):
        if self._is_test_running and self.test_suite.running_test is not None:
            if self.test_suite.running_test.is_running():
                self.run_started.emit()
            outs = self.test_suite.running_test.result.output_msg
            errs = self.test_suite.running_test.result.error_msg
            self.result_modified.emit(outs, errs)
        else:
            self.timer.stop()
