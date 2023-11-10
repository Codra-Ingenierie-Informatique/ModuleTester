# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

import sys
from importlib import import_module
from typing import Optional

from qtpy import QtWidgets as QW

from pytestbench.gui.states.bench_signals import TMSignals
from pytestbench.gui.states.bench_state_machine import TMStateMachine
from pytestbench.gui.window import TMWindow
from pytestbench.model import Module


class TestBenchMain:
    """TestBench Main class

    This class manages the state machines transitions and effect on window
    """

    def __init__(self, package: Optional[Module] = None, path: Optional[str] = None):
        # Fields
        self.package = package
        self.path = path

        self.signals = TMSignals()
        self.state_machine = TMStateMachine(self.signals)

        self.setup((self.path is not None))

        self.window = TMWindow(
            self.signals, self.state_machine, self.package, self.path
        )

        if self.path is not None:
            self.window.statusbar.set_path_label(self.path)
        self.signals.benchSaved.connect(self.window.statusbar.set_path_label)
        self.signals.testbenchLoaded.connect(self.window.statusbar.set_path_label)

    def setup(self, has_save_path: bool = False):
        """Main class setup: state entries and starting state machine"""
        self.add_entry_handlers()
        self.state_machine.start_machine(has_save_path)

    def add_entry_handlers(self):
        """Connect state entries to handlers"""
        self.state_machine.started_state.entered.connect(self.start_handler)
        self.state_machine.loaded_states.entered.connect(self.loaded_handler)

        self.state_machine.up_to_date_state.entered.connect(self.up_to_date_handler)
        self.state_machine.modified_state.entered.connect(self.modified_handler)

        self.state_machine.has_file_state.entered.connect(self.has_file_handler)
        self.state_machine.no_file_state.entered.connect(self.no_file_handler)

        self.state_machine.running_state.entered.connect(self.running_handler)
        self.state_machine.waiting_run_state.entered.connect(self.waiting_handler)
        self.state_machine.paused_state.entered.connect(self.paused_handler)

    def start_handler(self):
        """Started_state entry handler"""
        enabled_actions = [
            self.window.toolbar.new_file_action,
            self.window.toolbar.open_action,
        ]
        for action in self.window.toolbar.actions():
            if action not in enabled_actions:
                action.setEnabled(False)
            else:
                action.setEnabled(True)

        if self.window.bench is not None:
            self.signals.benchLoaded.emit()

    def loaded_handler(self):
        """Loaded_state entry handler"""
        for action in self.window.toolbar.actions():
            if action in self.window.toolbar.test_actions:
                action.setEnabled(False)
            else:
                action.setEnabled(True)

    def up_to_date_handler(self):
        """Up_to_date_state entry handler"""
        self.window.statusbar.set_state_label("Up to date")
        self.window.toolbar.save_action.setEnabled(False)
        self.window.is_file_saved = True

        title = self.window.windowTitle()
        if title.endswith("*"):
            title = title[:-1]
            self.window.setWindowTitle(title)

    def modified_handler(self):
        """Modified_state entry handler"""
        self.window.statusbar.set_state_label("Modified")
        self.window.toolbar.save_action.setEnabled(True)
        self.window.is_file_saved = False

        title = self.window.windowTitle()
        if not title.endswith("*"):
            title += "*"
            self.window.setWindowTitle(title)

    def has_file_handler(self):
        """has_file_state entry handler"""
        self.window.toolbar.run_action.setEnabled(True)
        self.window.central_widget.run_btn.setEnabled(True)
        self.window.central_widget.test_list.menu.run_script.setEnabled(True)

    def no_file_handler(self):
        """no_file_state entry handler"""
        self.window.statusbar.set_path_label("No save file")
        self.window.toolbar.run_action.setEnabled(False)
        self.window.central_widget.run_btn.setEnabled(False)
        self.window.central_widget.test_list.menu.run_script.setEnabled(False)

    def running_handler(self):
        """running_state entry handler"""
        self.window.toolbar.run_action.setEnabled(False)
        self.window.central_widget.run_btn.setEnabled(False)
        self.window.central_widget.test_list.menu.run_script.setEnabled(False)

        self.window.toolbar.stop_action.setEnabled(
            self.window.bench.test_suite.running_test.is_running()
        )
        self.window.toolbar.restart_action.setEnabled(True)

    def waiting_handler(self):
        """waiting_run entry handler"""
        if not self.state_machine.no_file_state.active():
            self.window.toolbar.run_action.setEnabled(True)
            self.window.central_widget.run_btn.setEnabled(True)
            self.window.central_widget.test_list.menu.run_script.setEnabled(True)

        self.window.toolbar.stop_action.setEnabled(False)
        self.window.toolbar.restart_action.setEnabled(False)

    def paused_handler(self):
        """paused_run entry handler"""
        self.window.toolbar.run_action.setEnabled(False)
        self.window.central_widget.run_btn.setEnabled(False)
        self.window.central_widget.test_list.menu.run_script.setEnabled(False)

        self.window.toolbar.stop_action.setEnabled(True)
        self.window.toolbar.restart_action.setEnabled(True)


def run(package: Optional[str] = None, path: Optional[str] = None) -> TestBenchMain:
    main = None
    if package is not None and path is None:
        module = Module(import_module(package))
        main = TestBenchMain(package=module)
    elif path is not None and package is None:
        main = TestBenchMain(path=path)
    else:
        main = TestBenchMain()

    return main


if __name__ == "__main__":
    # import faulthandler
    # faulthandler.enable()
    # faulthandler.dump_traceback_later(60, False, exit=True)

    PATH = r"C:\_projets\pytestbench\DataLab\run.testbench"
    PACKAGE = "cdl"
    app = QW.QApplication.instance()
    if not app:
        app = QW.QApplication(sys.argv)

    # run(package=PACKAGE)
    # run(path=PATH)
    pytestbench = run()
    pytestbench.window.show()

    app.exec_()
