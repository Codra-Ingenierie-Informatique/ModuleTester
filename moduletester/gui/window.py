# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring

# guitest: skip
import os
from importlib import import_module
from pathlib import Path
from typing import Optional

from guidata.config import CONF  # type: ignore
from guidata.configtools import get_font, get_icon, get_image_file_path  # type: ignore
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from ..config import APP_NAME
from ..manager import TestManager
from ..model import Module, Test
from ..python_helpers import rst2odt
from .components.body_component import TMWidget
from .components.status_bar_component import TMStatusBar
from .components.tool_bar_component import TestManagerToolbar
from .states.signals import TMSignals
from .states.state_machine import TMStateMachine


class TMWindow(QW.QMainWindow):
    def __init__(
        self,
        signals: TMSignals,
        state_machine: TMStateMachine,
        package: Optional[Module] = None,
        moduletester_path: Optional[str] = None,
        parent: Optional[QW.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowIcon(get_icon("ModuleTester.svg"))
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(800, 480)

        font = get_font(CONF, "codeeditor")
        ffamily, fsize = font.family(), font.pointSize()
        bgurl = Path(get_image_file_path("ModuleTester-watermark.png")).as_posix()
        self.ss_nobg = f"QWidget {{ font-family: '{ffamily}'; font-size: {fsize}pt;}}"
        self.ss_withbg = f"QMainWindow {{ background: url({bgurl}) no-repeat center;}}"
        self.setStyleSheet(self.ss_withbg + " " + self.ss_nobg)

        self.signals = signals

        if package is not None and moduletester_path is None:
            self.manager = TestManager(package, _category="visible")
        elif package is None and moduletester_path is not None:
            self.manager = TestManager(
                moduletester_path=moduletester_path, _category="visible"
            )
        else:
            self.manager = None

        self.toolbar = TestManagerToolbar(self)
        self.statusbar = TMStatusBar(self)
        self.state_machine = state_machine
        self.is_file_saved = False

        self.connect_file_actions()
        self.addToolBar(self.toolbar)
        self.setStatusBar(self.statusbar)
        self.statusbar.set_state_label("Not loaded")
        self.statusbar.set_path_label("")

        if self.manager is not None:
            self.central_widget = TMWidget(
                self.signals, self.manager.test_suite, moduletester_path, self
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
            APP_NAME,
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
            APP_NAME,
            f"File Saved in {self.manager.moduletester_path}",
            parent=self,
        ).exec_()

    def setup(self):
        self.setWindowTitle(f"{APP_NAME} - Module {self.manager.module.full_name}")
        self.setMinimumSize(0, 0)
        self.setStyleSheet(self.ss_nobg)
        self.setCentralWidget(self.central_widget)
        self.signals.SIG_PROJECT_LOADED.emit()
        self.connect_test_actions()

    def show(self):
        super().show()
        if self.manager is not None and len(self.manager.test_suite.tests) == 0:
            QW.QMessageBox(
                f"No tests in module {self.manager.test_suite.package.last_name}",
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
        if self.manager is not None:
            path = self.manager.moduletester_path

        open_file_name = QW.QFileDialog.getOpenFileName(
            self, "Open .moduletester file", path, "*.moduletester"
        )
        file_path = open_file_name[0]
        return file_path

    def get_save_file_name(self):
        path = os.getcwd()
        if self.manager is not None:
            path = self.manager.moduletester_path

        save_file_name = QW.QFileDialog.getSaveFileName(
            self, "Save .moduletester file", path, "*.moduletester *.txt"
        )
        file_path = save_file_name[0]
        return file_path

    def get_existing_dir(self):
        dir_name = QW.QFileDialog.getExistingDirectory(
            self,
            "Export Directory",
            self.manager.module.root_path,
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

        self.manager = TestManager(moduletester_path=file_path, _category="visible")
        self.central_widget = TMWidget(
            self.signals, self.manager.test_suite, file_path, self
        )
        self.setup()
        self.signals.SIG_FILE_LOADED.emit(file_path)

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
            self.manager = TestManager(module, _category="visible")
            self.central_widget = TMWidget(
                self.signals, self.manager.test_suite, parent=self
            )
            self.setup()
            self.signals.SIG_PROJECT_LOADED.emit()
            self.signals.SIG_TEMPLATE_CREATED.emit()
        except ModuleNotFoundError:
            QW.QMessageBox(
                QW.QMessageBox.Icon.Critical,
                "Module not found",
                f"No module named {module_name}",
            ).exec()

    def save(self):
        if self.manager.moduletester_path is None:
            self.save_as()
        else:
            test = self.current_test
            self.apply_changes(test)
            self.manager.save()
            self.signals.SIG_FILE_LOADED.emit(self.manager.moduletester_path)
            self.signals.SIG_PROJECT_SAVED.emit(self.manager.moduletester_path)

    def save_as(self):
        file_path = self.get_save_file_name()
        if file_path == "":
            return
        elif not os.path.exists(file_path):
            open(file_path, "w", encoding="utf-8").close()

        test = self.current_test

        self.apply_changes(test)

        self.manager.save_as(file_path)
        self.central_widget.moduletester_path = self.manager.moduletester_path
        self.central_widget.set_item()

        self.signals.SIG_FILE_LOADED.emit(file_path)
        self.signals.SIG_PROJECT_SAVED.emit(file_path)

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

        self.manager.export(dir_name, "dtv")

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

        self.manager.export(dir_name, "rtv")

        source = os.path.join(target_dir, "rtv.rst")
        dest = os.path.join(target_dir, "rtv.odt")
        rst2odt(source, dest)

        self.odt_created(dest)

    def odt_created(self, file: str):
        odt_mb = QW.QMessageBox(
            QW.QMessageBox.NoIcon,
            "TestManager",
            f"Odt file generated in: \n{file}",
            QW.QMessageBox.StandardButtons(QW.QMessageBox.Open | QW.QMessageBox.Close),
        )
        odt_mb.accepted.connect(lambda: self.open_odt_files(file))  # type: ignore
        odt_mb.exec_()

    def open_odt_files(self, fname: str):
        QG.QDesktopServices.openUrl(QC.QUrl.fromLocalFile(fname))
