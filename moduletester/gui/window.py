# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring

# guitest: skip
from __future__ import annotations

import os
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Optional

from guidata.config import CONF  # type: ignore
from guidata.configtools import get_font, get_icon, get_image_file_path  # type: ignore
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from moduletester import config
from moduletester.config import _
from moduletester.test_exporter import TestListDocument, TestResultsDocument

from ..config import APP_NAME
from ..manager import TestManager
from ..model import Module, Test, TestSuite
from .components.body_component import TMWidget
from .components.status_bar_component import TMStatusBar
from .components.tool_bar_component import TestManagerToolbar

if TYPE_CHECKING:
    from .states.signals import TMSignals
    from .states.state_machine import TMStateMachine


class TMWindow(QW.QMainWindow):
    export_finished = QC.Signal(str)  # type: ignore

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
        _ffamily, fsize = font.family(), font.pointSize()
        bgurl = Path(get_image_file_path("ModuleTester-watermark.png")).as_posix()
        # self.ss_nobg = f"QWidget {{ font-family: '{ffamily}'; font-size: {fsize}pt;}}"
        self.ss_nobg = f"QWidget {{ font-size: {fsize}pt;}}"
        self.ss_withbg = f"QMainWindow {{ background: url({bgurl}) no-repeat center;}}"
        self.setStyleSheet(self.ss_withbg + " " + self.ss_nobg)
        # self.setStyleSheet(self.ss_withbg)

        self.signals = signals

        self.last_file_dir: str
        self.last_export_dir: str
        self.manager: Optional[TestManager] = None
        if package is not None and moduletester_path is None:
            self.manager = self.new_test_manager(
                package, _category=config.PACKAGE_CONF["general"].category
            )
            self.last_export_dir = self.last_file_dir = package.root_path or os.getcwd()
        elif package is None and moduletester_path is not None:
            self.manager = self.new_test_manager(
                moduletester_path=moduletester_path,
                _category=config.PACKAGE_CONF["general"].category,
            )
            self.last_export_dir = self.last_file_dir = moduletester_path
        else:
            self.manager = None
            self.last_export_dir = self.last_file_dir = os.getcwd()

        self.toolbar = TestManagerToolbar(self)
        self.statusbar = TMStatusBar(self)
        self.state_machine = state_machine
        self.is_file_saved = False

        self.connect_file_actions()
        self.addToolBar(self.toolbar)
        self.setStatusBar(self.statusbar)
        self.statusbar.set_state_label("Not loaded")
        self.statusbar.set_path_label("")

        self.export_finished.connect(self.doc_exported)

        if self.manager is not None:
            self.set_central_widget(self.manager.test_suite, moduletester_path)
            self.setup()

    def set_central_widget(
        self, test_suite: TestSuite, path: Optional[str] = None
    ) -> None:
        """Create or update the central widget with the given test_suite and path. This
        methods avoids to create a new widget if the central widget already exists.

        Args:
            test_suite: The test_suite to display in the central widget.
            path: The path of the moduletester file. Defaults
             to None.
        """
        if hasattr(self, "central_widget"):
            self.central_widget.update_widget(test_suite, path)
        else:
            self.central_widget = TMWidget(self.signals, test_suite, path, self)

    @property
    def current_test(self) -> Test:
        return self.central_widget.test_list.get_selected_test()

    def closeEvent(self, a0: QG.QCloseEvent) -> None:  # pylint: disable=C0103
        """Close the main window and stop the thread if it is running. If the file has
        been modified, a message box is displayed to ask the user if he wants to save
        the file.

        Args:
            a0: The close event.
        """
        if self.state_machine.running_state.active():
            self.central_widget.stop_thread()

        if self.state_machine.modified_state.active():
            self.save_alert()

        return super().closeEvent(a0)

    def save_alert(self):
        """
        Display a message box to ask the user if he wants to save the current file.
        """
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
        """Save the current file if the user wants to save the modifications."""
        self.save()

        QW.QMessageBox(
            QW.QMessageBox.NoIcon,
            APP_NAME,
            f"File Saved in {self.manager.moduletester_path}",
            parent=self,
        ).exec_()

    def setup(self):
        """Setup the main window with the current test_suite."""
        self.setWindowTitle(f"{APP_NAME} - Module {self.manager.module.full_name}")
        self.setMinimumSize(0, 0)
        self.setStyleSheet(self.ss_nobg)
        self.setCentralWidget(self.central_widget)
        self.signals.SIG_PROJECT_LOADED.emit()
        self.connect_test_actions()
        self.toolbar.setup_view(self.central_widget.view_menu)

    def show(self):
        super().show()
        if self.manager is not None and len(self.manager.test_suite.tests) == 0:
            QW.QMessageBox(
                f"No tests in module {self.manager.test_suite.package.last_name}",
                parent=self,
            )

    def refresh_package(self):
        """Refresh the package and the central widget. This method should keep the
        current results."""
        if self.manager is None:
            return
        self.manager.refresh_package(category=config.PACKAGE_CONF["general"].category)
        self.signals.SIG_PROJECT_LOADED.emit()

    def connect_file_actions(self):
        """Connect the toolbar file actions to instance methods."""
        self.toolbar.new_file_action.triggered.connect(self.create_new_file)
        self.toolbar.open_action.triggered.connect(self.open)
        self.toolbar.update_action.triggered.connect(self.refresh_package)
        self.toolbar.save_action.triggered.connect(self.save)
        self.toolbar.save_as_action.triggered.connect(self.save_as)

        self.toolbar.export_test_list_action.triggered.connect(
            lambda: self.export_test_list(None)
        )
        self.toolbar.export_test_results_action.triggered.connect(
            lambda: self.export_test_results(None)
        )
        self.toolbar.export_action.triggered.connect(self.export)

    def connect_test_actions(self):
        """Connect the toolbar test actions to the central widget methods."""
        self.toolbar.run_action.triggered.connect(self.central_widget.run_test)
        self.toolbar.stop_action.triggered.connect(self.central_widget.stop_thread)
        self.toolbar.restart_action.triggered.connect(
            self.central_widget.restart_thread
        )

    def apply_changes(self, test: Test):
        """Save the comment of the test in the result object."""
        comment = (
            self.central_widget.result_information.comment_widget.cached_comments.get(
                test.package.full_name, None
            )
        )

        if test.result is not None and comment is not None:
            test.result.comment = comment

    def apply_all_changes(self):
        """Parse all the tests and apply the changes to the result object."""
        if self.manager is None:
            return

        # Updates the cached comment of the current test if the timer is still running
        comment_widget = self.central_widget.result_information.comment_widget
        if comment_widget.timer.isActive():
            comment_widget.timer.stop()
            comment_widget.update_cached_comment()
        for test in self.manager.test_suite.tests:
            self.apply_changes(test)

    def get_open_file_name(self) -> str:
        """Open a file dialog to select a .moduletester file to open.

        Returns:
            str: The path of the selected file.
        """
        open_file_name = QW.QFileDialog.getOpenFileName(
            self, "Open .moduletester file", self.last_file_dir, "*.moduletester"
        )
        file_path = open_file_name[0]
        self.last_file_dir = os.path.dirname(file_path)
        return file_path

    def get_save_file_name(self) -> str:
        """Open a file dialog to select a file to save the .moduletester file.

        Returns:
            str: The path of the selected file.
        """
        save_file_name = QW.QFileDialog.getSaveFileName(
            self, "Save .moduletester file", self.last_file_dir, "*.moduletester *.txt"
        )
        file_path = save_file_name[0]
        self.last_file_dir = os.path.dirname(file_path)
        return file_path

    def get_existing_dir(self) -> str:
        """Open a file dialog to select an existing directory.

        Returns:
            str: The path of the selected directory.
        """
        dir_name = QW.QFileDialog.getExistingDirectory(
            self,
            "Export Directory",
            self.last_export_dir,
            QW.QFileDialog.ShowDirsOnly,
        )
        return dir_name

    def open(self):
        """Open a .moduletester file and load the tests."""
        if (
            self.state_machine.modified_state.active()
            and self.state_machine.has_file_state.active()
        ):
            self.save_alert()

        file_path = self.get_open_file_name()
        if not os.path.exists(file_path):
            return

        if os.path.exists(
            bkp_file := (file_path + ".bkp")
        ) and self.backup_file_exists_warning(bkp_file):
            file_path = bkp_file

        self.manager = self.new_test_manager(
            moduletester_path=file_path,
            _category=config.PACKAGE_CONF["general"].category,
        )
        if self.manager is None:
            return

        if len(missing_modules := self.manager.get_missing_modules()) > 0:
            self._handle_missing_module(missing_modules)

        if len(errored_modules := self.manager.get_errored_modules()) > 0:
            self._notifiy_errored_module(errored_modules)

        self.set_central_widget(self.manager.test_suite, file_path)
        self.setup()
        self.signals.SIG_FILE_LOADED.emit(file_path)

    def new_test_manager(
        self,
        module: Module | None = None,
        moduletester_path: str | None = None,
        _category: str = config.PACKAGE_CONF["general"].category,
        _template_path: str = "",
    ) -> TestManager | None:
        """Create a new TestManager object and handle the configuration errors.

        Args:
            module: Module object that contains the tests. Defaults to None.
            moduletester_path: Path to the moduletester file. Defaults to None.
            _category: Test discovery category. Defaults to the value stored in
             config.PACKAGE_CONF["general"].category.
            _template_path: .moduletester template file. Defaults to "".

        Returns:
            TestManager: A new TestManager object or None if the configuration file
             contains errors.
        """
        manager = TestManager(module, moduletester_path, _category, _template_path)
        if (conf_err := manager.get_conf_conflict_err()) is not None:
            ok = self._resolve_moduletester_config_error(conf_err)
            if ok:
                return self.new_test_manager(
                    module, moduletester_path, _category, _template_path
                )
            else:
                return manager

        if (conf_err := manager.get_conf_path_val_err()) is not None:
            print("Error was not None")
            # TODO: open a conf editor to allow the user to modify the config file
            conf_file = os.path.join(
                config.MODULETESTER_CONFIG_DIR, config.MODULETESTER_CONFIG_NAME
            )
            QW.QMessageBox.critical(
                self,
                "Configuration file contains invalid values",
                f"Configuration file {conf_file} contains "
                f"invalid value:\n {conf_err.key} = {conf_err.value}",
                QW.QMessageBox.Cancel,
            )
            return None
        return manager

    def _resolve_moduletester_config_error(self, e: config.ConfigConflictError) -> bool:
        """Handle the configuration file error by opening a dialog to allow the user to
        fix the error.

        Args:
            e: The configuration error.

        Returns:
            True if the user wants to fix the error and save the file, False otherwise.
        """
        config_path = os.path.join(
            config.MODULETESTER_CONFIG_DIR, config.MODULETESTER_CONFIG_NAME
        )
        response = (
            QW.QMessageBox.critical(
                self,
                "Error in configuration file",
                f"Error in configuration file: {config_path}\n{str(e)}"
                "\nDo you want to fix the error and save the file?",
                QW.QMessageBox.Apply | QW.QMessageBox.Cancel,
            )
            == QW.QMessageBox.Apply
        )
        if response:
            config.load_package_conf(config_path, resolve=True)
            config.save_config(config.PACKAGE_CONF, config_path)
            print(config_path)
            return True
        return False

    def _handle_missing_module(self, missing_modules: list[Module]) -> None:
        """Handle the missing modules by asking the user if he wants to reimport all the
        tests and override the current file.

        Args:
            missing_modules: List of missing modules.
        """
        if self.manager is None:
            return
        missing_modules_names = ", ".join(map(lambda m: m.full_name, missing_modules))
        response = (
            QW.QMessageBox.warning(
                self,
                _("Error during moduletester file loading."),
                (
                    _("Error while parsing the .moduletester file: %s")
                    % f"{self.manager.moduletester_path}\n"
                    + _("Missing modules:")
                    + f"\n\n{missing_modules_names}\n\n"
                    + _(
                        "Do you want to reimport all tests"
                        " and override the current file?"
                    )
                ),
                buttons=QW.QMessageBox.Ok | QW.QMessageBox.Cancel,
            )
            == QW.QMessageBox.Ok
        )
        if response:
            self.manager.reload()
            self.manager.save()
            self.signals.SIG_FILE_LOADED.emit(self.manager.moduletester_path)

    def _notifiy_errored_module(self, errored_modules: list[Module]) -> None:
        """Notify the user that some modules could not be imported do to error in the
        imported file.

        Args:
            errored_modules: list of errored modules.
        """
        if self.manager is None:
            return
        errored_modules_names = ", ".join(map(lambda m: m.full_name, errored_modules))
        _response = QW.QMessageBox.warning(
            self,
            _("Error during module loading."),
            (
                _("Error while importing modules:")
                + f"\n\n{errored_modules_names}\n\n"
                + _(
                    "The modules are still visible in moduletester but should be fixed "
                    "or removed."
                )
            ),
            buttons=QW.QMessageBox.Ok,
        )

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

        vlayout.addWidget(edit, alignment=QC.Qt.AlignmentFlag.AlignRight)
        vlayout.addWidget(btn, alignment=QC.Qt.AlignmentFlag.AlignRight)

        btn.clicked.connect(lambda: self.create_template(edit.text(), dialog))

        dialog.exec()

    def clear_dock_widgets(self):
        """Remove all the dock widgets from the main window."""
        for dock in self.findChildren(QW.QDockWidget):
            self.removeDockWidget(dock)
            self.toolbar.removeAction(dock.toggleViewAction())

    def create_template(self, module_name: str, dialog: QW.QDialog):
        """Create a new template file with the given module name.

        Args:
            module_name: The name of the module.
            dialog: The dialog that contains the module name input.
        """
        try:
            module = Module(import_module(module_name))
            dialog.close()
            self.manager = self.new_test_manager(
                module, _category=config.PACKAGE_CONF["general"].category
            )
            if self.manager is None:
                return
            if len(errored_modules := self.manager.get_errored_modules()) > 0:
                self._notifiy_errored_module(errored_modules)
            self.set_central_widget(self.manager.test_suite)
            self.setup()
            self.signals.SIG_PROJECT_LOADED.emit()
            self.signals.SIG_TEMPLATE_CREATED.emit()
        except (ModuleNotFoundError, ValueError):
            QW.QMessageBox(
                QW.QMessageBox.Icon.Critical,
                "Module not found",
                f"No module named {module_name}",
            ).exec()

    def file_exists_warning(self, file_path: str) -> bool:
        """Display a warning message to the user if the file already exists.

        Args:
            file_path: The path of the file.

        Returns:
            True if the user wants to overwrite the file, False otherwise.
        """
        res = QW.QMessageBox.warning(
            self,
            "File already exists",
            f"File {file_path} already exists, do you want to overwite it?",
            buttons=QW.QMessageBox.Yes | QW.QMessageBox.No,
            defaultButton=QW.QMessageBox.No,
        )
        return res == QW.QMessageBox.Yes

    def backup_file_exists_warning(self, bkp_file_path: str) -> bool:
        """Display a warning message to the user if a backup file was found.

        Args:
            bkp_file_path: The path of the backup file.

        Returns:
            True if the user wants to import the backup file, False otherwise.
        """
        res = QW.QMessageBox.warning(
            self,
            "Backup file found",
            f"Backup file {bkp_file_path} was found which means the application may "
            "have crashed during saving. \nDo you want to import it instead?",
            buttons=QW.QMessageBox.Yes | QW.QMessageBox.No,
            defaultButton=QW.QMessageBox.No,
        )
        return res == QW.QMessageBox.Yes

    def alert_test_running(self):
        """Alert the user that a test is currently running."""
        QW.QMessageBox.warning(
            self,
            _("Test running"),
            _(
                "A test is currently running, please wait for it "
                "to finish before saving."
            ),
        )

    def save(self):
        """Save the current test_suite to the current file. If the file does not exist,
        the user is asked to select a file to save the test_suite.
        """
        if (manager := self.manager) is None:
            return

        if manager.test_suite.running_test is not None:
            self.alert_test_running()
            return

        if manager.moduletester_path is None:
            self.save_as()
        else:
            self.apply_all_changes()
            manager.save()
            self.signals.SIG_FILE_LOADED.emit(manager.moduletester_path)
            self.signals.SIG_PROJECT_SAVED.emit(manager.moduletester_path)

    def save_as(self):
        """Save the current test_suite to a new file. If the file already exists, the
        user is asked if he wants to overwrite it.
        """
        file_path = self.get_save_file_name()
        # is_save_ok = True
        if file_path == "":
            return
        # elif os.path.exists(file_path):
        #     is_save_ok = self.file_exists_warning(file_path)
        #     if is_save_ok:
        #         open(file_path, "w", encoding="utf-8").close()
        elif not os.path.exists(file_path):
            open(file_path, "w", encoding="utf-8").close()

        if self.manager is None:
            return

        if self.state_machine.running_state.active():
            self.alert_test_running()
            return

        self.apply_all_changes()
        self.manager.save_as(file_path)
        self.central_widget.moduletester_path = self.manager.moduletester_path
        self.central_widget.set_item()

        self.signals.SIG_FILE_LOADED.emit(file_path)
        self.signals.SIG_PROJECT_SAVED.emit(file_path)

    def _multi_export_callback(self, basename: str, fmts: Iterable[str]):
        """Callback function for the multi_export_async method of the TestListDocument
        and TestResultsDocument classes.

        Args:
            basename: The basename of the file that are exported.
            fmts: The formats of the files that are exported (their extensions).
        """

        for fmt in fmts:
            self.export_finished.emit(f"{basename}.{fmt}")

    def _check_exports(self, abs_out_basename: str, fmts: Iterable[str]) -> bool:
        """Check if the files already exist and ask the user if he wants to overwrite
        them.

        Args:
            abs_out_basename: The absolute path of the file to export.
            fmts: The formats of the files to export (their extensions).
        """
        files_already_exist: list[str] = [
            filename
            for fmt in fmts
            if os.path.isfile(filename := f"{abs_out_basename}.{fmt}")
        ]
        files_str = ", ".join(files_already_exist)
        if len(files_already_exist) > 0:
            res = QW.QMessageBox.warning(
                self,
                "File already exists.",
                (
                    f"The following files already exist: {files_str}.\n"
                    f"File {abs_out_basename} already exists,"
                    " do you want to overwrite it?"
                ),
                buttons=QW.QMessageBox.Yes | QW.QMessageBox.No,
                defaultButton=QW.QMessageBox.No,
            )
            return res == QW.QMessageBox.Yes

        return True

    def export(self):
        """Export both TestListDocument and TestResultsDocument files to the same
        directory. The user is asked to select the directory.
        """
        dir_name = self.get_existing_dir()

        if dir_name == "":
            return

        self.export_test_list(dir_name)
        self.export_test_results(dir_name)

    def export_test_list(self, dir_name: Optional[str] = None):
        """Exports a TestListDocument file to the given directory. If the directory is
        None, the user is asked to select a directory.

        Args:
            dir_name: Path to the export directory. Defaults to None.
        """

        if dir_name is None:
            dir_name = self.get_existing_dir()
            if dir_name == "":
                return

        self.apply_all_changes()

        model = "test_list"
        fmts = []
        abs_out_basename = os.path.join(dir_name, model)
        if self.manager is not None and self.manager.module is not None:
            abs_out_basename = os.path.join(
                dir_name, f"{model}_{self.manager.module.last_name}"
            )
            fmts.extend(config.PACKAGE_CONF["export"].export_fmts)

        else:
            raise ValueError("No manager or module loaded")

        if not self._check_exports(abs_out_basename, fmts):
            return

        self.statusbar.set_export_label(f"Exporting {abs_out_basename} to {fmts}")
        # rst2odt(source, dest)
        doc = TestListDocument(
            test_suite=self.manager.test_suite,
            reload_template=config.PACKAGE_CONF["export"].reload_templates_on_export,
            template_name=config.PACKAGE_CONF["export"].test_list_template_name,
        )
        doc.multi_exports_async(
            fmts,
            abs_out_basename,
            lambda: self._multi_export_callback(abs_out_basename, fmts),
        )

    def export_test_results(self, dir_name: Optional[str] = None):
        """Exports a TestResultsDocument file to the given directory. If the directory
        is None, the user is asked to select a directory.

        Args:
            dir_name: Path to the export directory. Defaults to None.
        """
        if dir_name is None:
            dir_name = self.get_existing_dir()
            if dir_name == "":
                return

        self.apply_all_changes()
        model = "test_results"

        fmts = []
        abs_out_basename = os.path.join(dir_name, model)
        if self.manager is not None and self.manager.module is not None:
            abs_out_basename = os.path.join(
                dir_name, f"{model}_{self.manager.module.last_name}"
            )
            fmts.extend(config.PACKAGE_CONF["export"].export_fmts)

        else:
            raise ValueError("No manager or module loaded")

        if not self._check_exports(abs_out_basename, fmts):
            return
        self.statusbar.set_export_label(f"Exporting {abs_out_basename} to {fmts}")
        doc = TestResultsDocument(
            test_suite=self.manager.test_suite,
            reload_template=config.PACKAGE_CONF["export"].reload_templates_on_export,
            template_name=config.PACKAGE_CONF["export"].test_results_template_name,
        )
        doc.multi_exports_async(
            fmts,
            abs_out_basename,
            lambda: self._multi_export_callback(abs_out_basename, fmts),
        )

    def doc_exported(self, file: str):
        self.statusbar.set_export_label("")
        odt_mb = QW.QMessageBox(
            QW.QMessageBox.NoIcon,
            "TestManager",
            f"File generated: \n{file}",
            QW.QMessageBox.StandardButtons(QW.QMessageBox.Open | QW.QMessageBox.Close),
        )
        odt_mb.accepted.connect(lambda: self.open_file(file))  # type: ignore
        odt_mb.exec_()

    def open_file(self, fname: str):
        QG.QDesktopServices.openUrl(QC.QUrl.fromLocalFile(fname))
