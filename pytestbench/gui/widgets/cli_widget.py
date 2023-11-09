# pylint: disable=missing-module-docstring, missing-class-docstring,
# pylint: disable=missing-function-docstring

from typing import Optional

from click import Context
from PyQt5 import QtCore as QC
from PyQt5 import QtWidgets as QW

from pytestbench.bench import cli, run
from pytestbench.model import Test


class CLIWidget(QW.QGroupBox):
    def __init__(self, parent: Optional[QW.QWidget] = None):
        super().__init__(parent)
        self.setTitle("Command line")
        self.menu = CLIContextMenu()

        self.command_label = QW.QLabel()
        self.command_label.setTextInteractionFlags(QC.Qt.TextSelectableByMouse)
        self.command_label.setWordWrap(True)

        self.vlayout = QW.QVBoxLayout(self)
        self.vlayout.addWidget(self.command_label)
        self.get_help()

        self.menu.copy_cli_action.triggered.connect(  # type: ignore
            self.copy_command_line
        )

    @property
    def command(self):
        text = self.command_label.text()
        command_txt = text.splitlines()[0]
        return command_txt

    def set_item(self, test: Test):
        if test.command != "":
            self.command_label.setText(test.command)
        else:
            self.command_label.setText("No command line available")

        self.command_label.setContextMenuPolicy(QC.Qt.CustomContextMenu)
        self.command_label.customContextMenuRequested.connect(  # type: ignore
            self.run_menu
        )

    def run_menu(self, point: QC.QPoint):
        self.menu.exec_(self.command_label.mapToGlobal(point))

    def get_help(self):
        ctx = Context(cli)
        run_help = run.get_help(ctx)
        options = run_help.split("Options:\n")[-1]
        options_no_help = options.split("\n  --help")[0]
        return options_no_help

    def get_run_options(self, test: Test):
        ctx = Context(cli)
        run_params = run.get_params(ctx)
        run_options = ""
        for param in run_params:
            if param.name in test.run_opts:
                opt_index = test.run_opts.index(param.name)
                opt_str = f"{param.opts[0]} {test.run_opts[opt_index + 1]} "
                run_options += opt_str
        return run_options

    def copy_command_line(self):
        app = QW.QApplication.instance()
        clipboard = app.clipboard()
        clipboard.setText(self.command)


class CLIContextMenu(QW.QMenu):
    def __init__(self, parent: Optional[QW.QWidget] = None) -> None:
        super().__init__(parent)
        # Actions
        self.copy_cli_action = QW.QAction("Copy Command Line")

        self.addAction(self.copy_cli_action)
