# pylint: disable=missing-module-docstring, missing-class-docstring,
# pylint: disable=missing-function-docstring

from typing import Optional

from click import Context
from guidata.config import CONF
from guidata.configtools import get_font
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW
from qtpy.QtWidgets import QAction

from moduletester.gui.widgets.dockable_widget import DockableQWidget
from moduletester.model import Test


class CLIWidget(DockableQWidget):
    def __init__(
        self, parent: Optional[QW.QWidget] = None, title: str = "Command Line"
    ) -> None:
        super().__init__(parent=parent, title=title)

        self.menu = CLIContextMenu()

        self.command_label = QW.QLabel()
        self.command_label.setTextInteractionFlags(
            QC.Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.command_label.setWordWrap(True)
        font = get_font(CONF, "codeeditor")
        self.command_label.setFont(font)

        self.vlayout = QW.QVBoxLayout(self)
        self.vlayout.addWidget(self.title_label)
        self.vlayout.addWidget(self.command_label)

        self.menu.copy_cli_action.triggered.connect(  # type: ignore
            self.copy_command_line
        )

    @property
    def command(self):
        text = self.command_label.text()
        command_txt = text.splitlines()[0]
        return command_txt

    def set_item(self, test: Test):
        """Set the current test to display its command line.

        Args:
            test: Test from which to display the command line.
        """
        if test.command != "":
            self.command_label.setText(test.command)
        else:
            self.command_label.setText("No command line available")

        self.command_label.setContextMenuPolicy(
            QC.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.command_label.customContextMenuRequested.connect(  # type: ignore
            self.run_menu
        )

    def run_menu(self, point: QC.QPoint):
        """Run the context menu.

        Args:
            point: Point where the context menu was requested.
        """
        self.menu.exec_(self.command_label.mapToGlobal(point))

    def get_run_options(self, test: Test):
        """Get the run options for the current test.

        Args:
            test: Test for which to get the run options.

        Returns:
            str: The run options for the current test.
        """
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
        """Copy the command line to the clipboard."""
        app = QW.QApplication.instance()
        clipboard = app.clipboard()
        clipboard.setText(self.command)


class CLIContextMenu(QW.QMenu):
    """Context menu for the command line widget."""

    def __init__(self, parent: Optional[QW.QWidget] = None) -> None:
        super().__init__(parent)
        # Actions
        self.copy_cli_action = QAction("Copy Command Line")

        self.addAction(self.copy_cli_action)
        self.addAction(self.copy_cli_action)
