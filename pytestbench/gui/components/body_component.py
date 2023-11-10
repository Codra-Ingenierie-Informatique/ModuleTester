# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Optional

from guidata.configtools import get_icon  # type: ignore
from guidata.guitest import get_test_package  # type: ignore
from guidata.widgets.codeeditor import CodeEditor  # type: ignore
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from ...model import ResultEnum, TestSuite
from ..states.bench_signals import TMSignals
from ..states.runner import QSubprocess
from ..widgets.cli_widget import CLIWidget
from ..widgets.test_list_widget import TestListWidget
from .result_information import ResultInformation
from .test_information import TestInformation


class TMWidget(QW.QWidget):
    def __init__(
        self,
        signals: TMSignals,
        test_suite: TestSuite,
        testbench_path: Optional[str] = None,
        parent: Optional[QW.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        # Fields
        self.test_suite = test_suite
        self.origin_path = self.test_suite.package.root_path
        self.testbench_path = testbench_path
        self.signals = signals
        self._run_thread: Optional[QSubprocess] = None

        # Widgets
        self.test_list = TestListWidget(self.test_suite.tests, self)
        self.run_btn = QW.QPushButton(get_icon("apply.png"), "Run Script", self)
        self.test_information = TestInformation(self.signals, self)
        self.result_information = ResultInformation(self.signals, self)
        self.cli_group = CLIWidget(self)

        # Layouts
        self.glayout = QW.QGridLayout(self)

        self.setup()

    @property
    def run_thread(self):
        return self._run_thread

    def setup(self):
        # Widget setup
        self.set_item(False)

        # Layout setup
        list_layout = QW.QVBoxLayout()
        list_layout.addWidget(self.test_list)
        list_layout.addWidget(self.run_btn)

        self.glayout.addLayout(list_layout, 0, 0, 9, 2)
        self.glayout.addWidget(self.test_information, 0, 2, 4, 4)
        self.glayout.addWidget(self.result_information, 4, 2, 4, 4)
        self.glayout.addWidget(self.cli_group, 8, 2, 1, 4)

        for ind in range(self.glayout.columnCount()):
            self.glayout.setColumnMinimumWidth(ind, 250)
        for ind in range(self.glayout.rowCount()):
            self.glayout.setRowMinimumHeight(ind, 85)

        # Event Handlers
        self.run_btn.clicked.connect(self.run_test)
        self.test_list.currentItemChanged.connect(
            lambda current, previous: self.set_item(False, current)
        )
        self.result_information.result_enum.currentTextChanged.connect(
            self.update_result
        )

        self.test_list.menu.run_script.triggered.connect(self.run_test)
        self.test_list.menu.code_snippet.triggered.connect(self.pop_code_snippet)

        self.test_information.table_group.table.itemChanged.connect(self.update_test)

    def set_item(
        self,
        is_test_modified: bool = True,
        current_item: Optional[QW.QTreeWidgetItem] = None,
    ):
        self.test_list.setup_list(current_item)

        test = self.test_list.get_selected_test()

        self.test_information.set_item(test, self.origin_path)
        self.result_information.set_item(test)
        self.cli_group.set_item(test)

        if is_test_modified:
            self.signals.benchModified.emit()

    def update_result(self, result_value: str):
        test = self.test_list.get_selected_test()
        if test.result is not None:
            test.result.result = ResultEnum(result_value)
            self.test_list.setup_list(self.test_list.current_item)
            self.signals.benchModified.emit()

    def update_test(self, item: QW.QTreeWidgetItem, column: int):
        if column == 1:
            test = self.test_list.get_selected_test()

            self.test_information.update_command(item, test)
            self.set_item(current_item=self.test_list.current_item)

    def run_test(self):
        if self._run_thread is None:
            test = self.test_list.get_selected_test()
            test_name = test.package.last_name

            self._run_thread = QSubprocess(self.test_suite, test_name)
            self._run_thread.run_ended.connect(self.handle_thread_end)
            self._run_thread.result_modified.connect(self.handle_result_modified)
            self._run_thread.run_started.connect(self.signals.run_started.emit)
            self._run_thread.start()
            self._run_thread.timer.start(1000)

        else:
            QW.QMessageBox(
                QW.QMessageBox.NoIcon, "Thread Error", "A test is already running"
            ).exec()

    def stop_thread(self):
        if self._run_thread is not None:
            self._run_thread.stop(forced=True)
        else:
            QW.QMessageBox(
                QW.QMessageBox.NoIcon, "Thread Error", "No test currently running"
            ).exec()

    def restart_thread(self):
        if self._run_thread is not None:
            self.stop_thread()
            self.run_test()
        else:
            QW.QMessageBox(
                QW.QMessageBox.NoIcon,
                "Thread Error",
                "No test currently paused or running",
            ).exec()

    def handle_thread_end(self):
        if self._run_thread is not None:
            self._run_thread.result_modified.disconnect()
            self._run_thread.run_ended.disconnect()
            self._run_thread.run_started.disconnect()

            self._run_thread = None
            self.signals.run_stopped.emit()
            current_item = self.test_list.current_item
            self.set_item(current_item=current_item)

    def handle_result_modified(self, _outs, _errs):
        current_item = self.test_list.selectedItems()[0]
        self.set_item(current_item=current_item)

    def pop_code_snippet(self):
        test = self.test_list.get_selected_test()
        test_package = get_test_package(self.test_suite.package.module)

        code_snippet = test.get_code_snippet(test_package)
        editor = CodeEditor(
            self, columns=100, rows=45, language="python", font=self.font()
        )
        editor.setReadOnly(True)
        editor.setPlainText(code_snippet)
        editor.setWindowFlags(QC.Qt.Window)
        editor.setWindowTitle(f"Code snippet - {test.package.last_name}")
        editor.setWindowIcon(get_icon("python.png"))
        editor.show()
