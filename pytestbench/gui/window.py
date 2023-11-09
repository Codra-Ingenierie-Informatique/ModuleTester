# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring

# guitest: skip
import os
from importlib import import_module
from typing import Optional

from guidata.config import CONF  # type: ignore
from guidata.configtools import get_font, get_icon  # type: ignore
from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

from ..bench import TestBench
from ..config import APP_NAME
from ..model import Module, Test
from ..python_helpers import rst2odt
from .components.body_component import TMWidget
from .components.status_bar_component import TMStatusBar
from .components.tool_bar_component import TestBenchToolBar
from .states.bench_signals import TMSignals
from .states.bench_state_machine import TMStateMachine


class TMWindow(QW.QMainWindow):
    def __init__(
        self,
        signals: TMSignals,
        state_machine: TMStateMachine,
        package: Optional[Module] = None,
        testbench_path: Optional[str] = None,
        parent: Optional[QW.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowIcon(get_icon("PyTestBench.svg"))
        self.setWindowTitle(APP_NAME)
        self.signals = signals

        if package is not None and testbench_path is None:
            self.bench = TestBench(package, _category="visible")
        elif package is None and testbench_path is not None:
            self.bench = TestBench(testbench_path=testbench_path, _category="visible")
        else:
            self.bench = None

        self.toolbar = TestBenchToolBar(self)
        self.statusbar = TMStatusBar(self)
        self.state_machine = state_machine
        self.is_file_saved = False

        self.connect_file_actions()
        self.addToolBar(self.toolbar)
        self.setStatusBar(self.statusbar)
        self.statusbar.set_state_label("Not loaded")
        self.statusbar.set_path_label("")

        if self.bench is not None:
            self.central_widget = TMWidget(
                self.signals, self.bench.test_suite, testbench_path, self
            )
            self.setup()

    @property
    def current_test(self) -> Test:
        return self.central_widget.test_list.get_selected_test()

    def closeEvent(self, a0: QG.QCloseEvent) -> None:  # pylint: disable=C0103
        if self.state_machine.running_state.active():
            self.central_widget.stop_thread()

        if self.state_machine.modified_state.active():
            self.save_alert()

        return super().closeEvent(a0)

    def save_alert(self):
        save_mb = QW.QMessageBox(
            QW.QMessageBox.Warning,
            "Test bench",
            "Do you want to save modification ?",
        )
        save_mb.setStandardButtons(
            QW.QMessageBox.StandardButtons(QW.QMessageBox.Ok | QW.QMessageBox.No)
        )

        save_mb.accepted.connect(self.save_alert_accepted)  # type: ignore

        save_mb.exec()

    def save_alert_accepted(self):
        self.save()

        QW.QMessageBox(
            QW.QMessageBox.NoIcon,
            "Test bench",
            f"File Saved in {self.bench.testbench_path}",
            parent=self,
        ).exec_()

    def setup(self):
        self.setWindowTitle(f"Test bench - Module {self.bench.module.full_name}")
        self.setFont(get_font(CONF, "codeeditor"))
        self.setCentralWidget(self.central_widget)
        self.signals.benchLoaded.emit()

        self.connect_test_actions()

    def show(self):
        super().show()
        if self.bench is not None and len(self.bench.test_suite.tests) == 0:
            QW.QMessageBox(
                f"No tests in module {self.bench.test_suite.package.last_name}",
                parent=self,
            )

    def connect_file_actions(self):
        self.toolbar.new_file_action.triggered.connect(self.create_new_file)
        self.toolbar.open_action.triggered.connect(self.open)
        self.toolbar.save_action.triggered.connect(self.save)
        self.toolbar.save_as_action.triggered.connect(self.save_as)

        self.toolbar.export_dtv_action.triggered.connect(lambda: self.export_dtv(None))
        self.toolbar.export_rtv_action.triggered.connect(lambda: self.export_rtv(None))
        self.toolbar.export_action.triggered.connect(self.export)

    def connect_test_actions(self):
        self.toolbar.run_action.triggered.connect(self.central_widget.run_test)
        self.toolbar.stop_action.triggered.connect(self.central_widget.stop_thread)
        self.toolbar.restart_action.triggered.connect(
            self.central_widget.restart_thread
        )

    def apply_changes(self, test: Test):
        description = self.central_widget.test_information.description
        comment = self.central_widget.result_information.comment

        test.description = description
        if test.result is not None:
            test.result.comment = comment

    def get_open_file_name(self):
        path = os.getcwd()
        if self.bench is not None:
            path = self.bench.testbench_path

        open_file_name = QW.QFileDialog.getOpenFileName(
            self, "Open .testbench file", path, "*.testbench"
        )
        file_path = open_file_name[0]
        return file_path

    def get_save_file_name(self):
        path = os.getcwd()
        if self.bench is not None:
            path = self.bench.testbench_path

        save_file_name = QW.QFileDialog.getSaveFileName(
            self, "Save .testbench file", path, "*.testbench *.txt"
        )
        file_path = save_file_name[0]
        return file_path

    def get_existing_dir(self):
        dir_name = QW.QFileDialog.getExistingDirectory(
            self,
            "Export Directory",
            self.bench.module.root_path,
            QW.QFileDialog.ShowDirsOnly,
        )
        return dir_name

    def open(self):
        if (
            self.state_machine.modified_state.active()
            and self.state_machine.has_file_state.active()
        ):
            self.save_alert()

        file_path = self.get_open_file_name()
        if not os.path.exists(file_path):
            return

        self.bench = TestBench(testbench_path=file_path, _category="visible")
        self.central_widget = TMWidget(
            self.signals, self.bench.test_suite, file_path, self
        )
        self.setup()
        self.signals.testbenchLoaded.emit(file_path)

    def create_new_file(self):
        if (
            self.state_machine.modified_state.active()
            and self.state_machine.has_file_state.active()
        ):
            self.save_alert()

        dialog = QW.QDialog(parent=self)
        dialog.setWindowTitle("New template")
        dialog.setFont(self.font())
        dialog.setFixedSize(240, 80)

        vlayout = QW.QVBoxLayout(dialog)
        edit = QW.QLineEdit()
        edit.setPlaceholderText("Module name")
        btn = QW.QPushButton(get_icon("apply.png"), "Ok")
        edit.setFixedSize(220, 25)
        btn.setFixedWidth(80)

        vlayout.addWidget(edit, alignment=QC.Qt.AlignRight)
        vlayout.addWidget(btn, alignment=QC.Qt.AlignRight)

        btn.clicked.connect(lambda: self.create_template(edit.text(), dialog))

        dialog.exec()

    def create_template(self, module_name: str, dialog: QW.QDialog):
        try:
            module = Module(import_module(module_name))
            dialog.close()
            self.bench = TestBench(module, _category="visible")
            self.central_widget = TMWidget(
                self.signals, self.bench.test_suite, parent=self
            )
            self.setup()
            self.signals.benchLoaded.emit()
            self.signals.templateCreated.emit()
        except ModuleNotFoundError:
            QW.QMessageBox(
                QW.QMessageBox.Icon.Critical,
                "Module not found",
                f"No module named {module_name}",
            ).exec()

    def save(self):
        if self.bench.testbench_path is None:
            self.save_as()
        else:
            test = self.current_test
            self.apply_changes(test)
            self.bench.save()
            self.signals.testbenchLoaded.emit(self.bench.testbench_path)
            self.signals.benchSaved.emit(self.bench.testbench_path)

    def save_as(self):
        file_path = self.get_save_file_name()
        if file_path == "":
            return
        elif not os.path.exists(file_path):
            open(file_path, "w", encoding="utf-8").close()

        test = self.current_test

        self.apply_changes(test)

        self.bench.save_as(file_path)
        self.central_widget.testbench_path = self.bench.testbench_path
        self.central_widget.set_item()

        self.signals.testbenchLoaded.emit(file_path)
        self.signals.benchSaved.emit(file_path)

    def export(self):
        dir_name = self.get_existing_dir()

        if dir_name == "":
            return

        test = self.current_test
        self.apply_changes(test)

        self.export_dtv(dir_name)
        self.export_rtv(dir_name)

    def export_dtv(self, dir_name: Optional[str] = None):
        if dir_name is None:
            dir_name = self.get_existing_dir()
            if dir_name == "":
                return
            test = self.current_test
            self.apply_changes(test)

        target_dir = os.path.join(dir_name, "dtv")

        self.bench.export(dir_name, "dtv")

        source = os.path.join(target_dir, "dtv.rst")
        dest = os.path.join(target_dir, "dtv.odt")
        rst2odt(source, dest)

        self.odt_created(dest)

    def export_rtv(self, dir_name: Optional[str] = None):
        if dir_name is None:
            dir_name = self.get_existing_dir()
            if dir_name == "":
                return
            test = self.current_test
            self.apply_changes(test)

        target_dir = os.path.join(dir_name, "rtv")

        self.bench.export(dir_name, "rtv")

        source = os.path.join(target_dir, "rtv.rst")
        dest = os.path.join(target_dir, "rtv.odt")
        rst2odt(source, dest)

        self.odt_created(dest)

    def odt_created(self, file: str):
        odt_mb = QW.QMessageBox(
            QW.QMessageBox.NoIcon,
            "TestBench",
            f"Odt file generated in: \n{file}",
            QW.QMessageBox.StandardButtons(QW.QMessageBox.Open | QW.QMessageBox.Close),
        )
        odt_mb.accepted.connect(lambda: self.open_odt_files(file))  # type: ignore
        odt_mb.exec_()

    def open_odt_files(self, fname: str):
        QG.QDesktopServices.openUrl(QC.QUrl.fromLocalFile(fname))
