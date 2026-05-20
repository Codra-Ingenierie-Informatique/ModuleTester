# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Optional

from guidata.configtools import get_icon  # type: ignore
from guidata.guitest import get_test_package  # type: ignore
from guidata.widgets.codeeditor import CodeEditor  # type: ignore
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from moduletester.config import PACKAGE_CONF
from moduletester.gui.components.test_list_component import TestListComponent
from moduletester.gui.widgets.dockable_widget import DockableQWidget
from moduletester.gui.widgets.toolbox_widget import Toolbox

from ...model import Test, TestSuite
from ..states.runner import QSubprocess
from ..states.signals import TMSignals
from ..widgets.cli_widget import CLIWidget
from ..widgets.dock_wrapper import QDockWrapper
from .result_information import ResultInformation
from .test_information import TestInformation


class TMWidget(DockableQWidget):
    def __init__(
        self,
        signals: TMSignals,
        test_suite: TestSuite,
        moduletester_path: Optional[str] = None,
        parent: Optional[QW.QMainWindow] = None,
    ) -> None:
        super().__init__(parent)
        # Fields
        self.test_suite = test_suite
        self.origin_path = self.test_suite.package.root_path
        self.moduletester_path = moduletester_path
        self.signals = signals
        self._run_thread: Optional[QSubprocess] = None
        self._running_test: Optional[Test] = None

        # Widgets
        self.h_splitter = QW.QSplitter(QC.Qt.Orientation.Horizontal, self)
        self.v_splitter = QW.QSplitter(QC.Qt.Orientation.Vertical, self)

        self.test_list_comp = TestListComponent(self.test_suite.tests, parent=self)
        self.test_list = self.test_list_comp.test_list_widget
        self.run_btn = self.test_list_comp.run_btn
        self.test_information = TestInformation(self.signals, self)
        self.result_information = ResultInformation(self.signals, parent=self)
        self.cli_group = CLIWidget(self)

        self.toolbox = Toolbox(self, signals=signals, title="Toolbox")

        self.dock_widgets: list[QDockWrapper] = []
        # Layouts
        self.glayout = QW.QHBoxLayout(self)

        self.view_menu = QW.QMenu()

        self.setup()
        self.setup_dock_widgets()

    def update_widget(
        self, test_suite: TestSuite, moduletester_path: Optional[str] = None
    ):
        """Update widget with new test_suite

        Args:
            test_suite: The new TestSuite object to update the widget with.
            moduletester_path: The new path to the moduletester file.
        """
        self.test_suite = test_suite
        self.origin_path = self.test_suite.package.root_path
        self.moduletester_path = moduletester_path
        self.test_list_comp.test_list_widget.reset_widget(self.test_suite.tests)

    @property
    def run_thread(self):
        return self._run_thread

    def get_main_window(self) -> QW.QMainWindow:
        """Get the main window of the widget

        Returns:
            The main window of the widget.
        """
        window = self.window()
        assert isinstance(window, QW.QMainWindow)
        return window

    def setup(self) -> None:
        """Setup the widget layout and event handlers."""
        self.glayout.addWidget(self.test_information)

        # Event Handlers
        self.run_btn.clicked.connect(self.run_test)
        self.test_list.itemDoubleClicked.connect(self._run_on_double_click)
        self.test_list.currentItemChanged.connect(
            lambda: self.set_item(is_test_modified=False)
        )
        self.result_information.result_enum.currentIndexChanged.connect(
            self.update_result
        )

        self.test_list.menu.run_script.triggered.connect(self.run_test)
        self.test_list.menu.code_snippet.triggered.connect(self.pop_code_snippet)

        self.test_information.table_group.dataset_gbox.SIG_APPLY_BUTTON_CLICKED.connect(
            self.update_test
        )
        self.signals.SIG_PROJECT_LOADED.connect(
            lambda: self.test_list.reset_widget(self.test_suite.tests)
        )
        self.set_item(is_test_modified=False)

    def setup_dock_widgets(self):
        """Setup the dock widgets for the widget layout using the configuration and the
        main window.
        """
        window = self.get_main_window()
        for widget, str_area, visible in (
            (
                self.cli_group,
                PACKAGE_CONF["gui"].cli_pos,
                PACKAGE_CONF["gui"].cli_visible,
            ),
            (
                self.result_information,
                PACKAGE_CONF["gui"].result_tab_pos,
                PACKAGE_CONF["gui"].result_tab_visible,
            ),
            (
                self.test_information.table_group,
                PACKAGE_CONF["gui"].test_props_pos,
                PACKAGE_CONF["gui"].test_props_visible,
            ),
            (
                self.result_information.prop_group,
                PACKAGE_CONF["gui"].result_props_pos,
                PACKAGE_CONF["gui"].result_props_visible,
            ),
            (
                self.test_list_comp,
                PACKAGE_CONF["gui"].test_list_pos,
                PACKAGE_CONF["gui"].test_list_visible,
            ),
            (
                self.toolbox,
                PACKAGE_CONF["gui"].toolbox_pos,
                PACKAGE_CONF["gui"].toolbox_visible,
            ),
        ):
            dock_widget = QDockWrapper(
                self,
                widget,
            )
            area = QDockWrapper.get_area_from_str(str_area)
            self.dock_widgets.append(dock_widget)
            self.view_menu.addAction(dock_widget.toggleViewAction())
            window.addDockWidget(area, dock_widget)
            dock_widget.setVisible(visible)
            self.view_menu.addAction(dock_widget.toggleViewAction())

    def _run_on_double_click(self, clicked_item: QW.QTreeWidgetItem):
        """Run the test when the item is double clicked.

        Args:
            clicked_item: The item that was double clicked in the test list.
        """
        self.test_list.setCurrentItem(clicked_item)
        selected_item = self.test_list.current_item
        selected_test = self.test_list.get_selected_test()
        if (
            selected_item is clicked_item
            and self.run_btn.isEnabled()
            and selected_test is not None
            and self.validate_command(selected_test)
        ):
            self.set_item(is_test_modified=False)
            self.run_test()

    def validate_command(self, test: Test) -> bool:
        """Validate the command for the test.

        Args:
            test: The test to validate the command for.

        Returns:
            True if the command is valid, otherwise False.
        """
        return self.test_information.validate_command(test)

    def set_item(
        self,
        test: Optional[Test] = None,
        is_test_modified: bool = True,
    ):
        """Set the item for the widget.

        Args:
            test: The test to set the item for.
            is_test_modified: Whether the test was modified.
        """
        test = test or self.test_list.get_selected_test()
        if test is None:
            return
        self.test_information.set_item(test, self.origin_path or "None")
        self.result_information.set_item(test)
        self.cli_group.set_item(test)

        if is_test_modified:
            self.test_list.update_result(test)
            self.signals.SIG_PROJECT_MODIFIED.emit()

    def update_result(self, _index: int):
        """Update the result for the test.

        Args:
            index: The index of the result to update. Unused.
        """
        test = self.test_list.get_selected_test()
        if test is not None and test.result is not None:
            new_result = self.result_information.result_enum.currentData()
            test.result.result = new_result

            self.test_list.update_result(test)
            self.signals.SIG_PROJECT_MODIFIED.emit()

    def update_test(self):
        """Update the test."""
        test = self.test_list.get_selected_test()
        if test is None:
            return
        self.test_information.update_command(test)
        self.test_list.update_result(test)
        self.cli_group.set_item(test)

    def run_test(self):
        """Run the test."""
        if self._run_thread is None:
            test = self.test_list.get_selected_test()
            if test is None:
                return

            test_name = test.package.last_name
            test_item = self.test_list.current_item

            if not self.validate_command(test):
                return

            self._run_thread = QSubprocess(self.test_suite, test_name)
            self._running_test = test
            self.result_information.result_enum.setEnabled(False)
            self.result_information.comment_widget.readonly(False)
            self.result_information.comment_widget.comment_label.clear()

            if test_item is not None:
                self.test_list.start_test_spinner(test_item)

            self._run_thread.run_ended.connect(self.handle_thread_end)
            self._run_thread.result_modified.connect(self.handle_result_modified)
            self._run_thread.SIG_RUN_STARTED.connect(self.signals.SIG_RUN_STARTED.emit)
            self._run_thread.start()
            self._run_thread.timer.start(1000)

        else:
            QW.QMessageBox(
                QW.QMessageBox.NoIcon, "Thread Error", "A test is already running"
            ).exec()

    def stop_thread(self):
        """Stop the test thread."""
        if self._run_thread is not None:
            self._run_thread.stop(forced=True)
        else:
            QW.QMessageBox(
                QW.QMessageBox.NoIcon, "Thread Error", "No test currently running"
            ).exec()

    def restart_thread(self):
        """Restart the test thread."""
        if self._run_thread is not None:
            self.stop_thread()
            self.run_test()
        else:
            QW.QMessageBox(
                QW.QMessageBox.NoIcon,
                "Thread Error",
                "No test currently paused or running",
            ).exec()

    def notify_test(self, test: Optional[Test]):
        """Update the test so other widgets know what to display
        (e.g. notification icon in the treeview).

        Args:
            test: The test to notify.
        """
        if test is not None:
            result = test.result
            is_message_new = False
            is_error_new = False
            if result is not None:
                is_message_new = result.output_msg not in ("", None)
                is_error_new = result.error_msg not in ("", None)

            test.set_message_state(is_message_new)
            test.set_error_state(is_error_new)

    def handle_thread_end(self):
        """Handle the end of the test thread."""
        if self._run_thread is not None and self._running_test is not None:
            self._run_thread.result_modified.disconnect()
            self._run_thread.run_ended.disconnect()
            self._run_thread.SIG_RUN_STARTED.disconnect()
            self._run_thread = None

            self.notify_test(self._running_test)

            if self._running_test is self.test_list.get_selected_test():
                self.set_item(self._running_test, is_test_modified=True)
            else:
                self.test_list.update_result(self._running_test)
                self.test_list.set_test_icon(self._running_test, "file-notify.svg")

            self._running_test = None
            self.signals.SIG_RUN_STOPPED.emit()

    def handle_result_modified(self, _outs, _errs):
        """Handle the modification of the result.

        Args:
            _outs: stdouts, unused
            _errs: stderrs, unused
        """
        if self._running_test is not None:
            self.test_list.update_result(self._running_test)

    def pop_code_snippet(self):
        """Show the code snippet for the test in a popup dialog."""
        test = self.test_list.get_selected_test()
        if test is None:
            return

        test_package = get_test_package(self.test_suite.package.module)

        code_snippet = test.get_code_snippet(test_package)
        editor = CodeEditor(
            self,
            columns=100,
            rows=45,
            language="python",  # font=self.font()
        )
        editor.setReadOnly(True)
        editor.setPlainText(code_snippet)
        editor.setWindowFlags(QC.Qt.WindowType.Window)
        editor.setWindowTitle(f"Code snippet - {test.package.last_name}")
        editor.setWindowIcon(get_icon("python.png"))
        editor.show()
