# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable= missing-function-docstring

from typing import List, Optional

from guidata.configtools import get_icon  # type: ignore
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

CTRL = QC.Qt.CTRL
SHIFT = QC.Qt.SHIFT


class TestManagerToolbar(QW.QToolBar):
    def __init__(self, parent: Optional[QW.QWidget] = None):
        super().__init__(parent)
        # Fields
        self.file_actions: List[QW.QAction] = []
        self.test_actions: List[QW.QAction] = []

        # File Actions
        self.save_action = QW.QAction(get_icon("filesave.png"), "Save")
        self.save_as_action = QW.QAction(get_icon("filesaveas.png"), "Save As")
        self.open_action = QW.QAction(get_icon("fileopen.png"), "Open")
        self.new_file_action = QW.QAction(get_icon("filenew.png"), "New")

        # Expt action
        self.export_menu = QW.QMenu()
        self.export_action = QW.QAction("Export")
        self.export_dtv_action = QW.QAction("Export dtv")
        self.export_rtv_action = QW.QAction("Export rtv")
        self.export_tool_btn = QW.QToolButton()

        # Test Actions
        self.run_action = QW.QAction("Run")
        self.stop_action = QW.QAction("Stop")
        self.restart_action = QW.QAction("Restart")

        # Setup
        self.setup()

    def setup(self):
        self.setup_export()
        # Actions
        self.file_actions = [
            self.new_file_action,
            self.open_action,
            self.save_action,
            self.save_as_action,
        ]
        self.test_actions = [
            self.run_action,
            self.restart_action,
            self.stop_action,
        ]

        # Setup
        self.setup_shortcuts()
        self.setup_tooltips()

        # ToolBar
        self.addActions(self.file_actions)
        self.addWidget(self.export_tool_btn)
        self.addSeparator()
        self.addActions(self.test_actions)

    def setup_export(self):
        self.export_menu.addAction(self.export_action)
        self.export_menu.addSeparator()
        self.export_menu.addActions([self.export_dtv_action, self.export_rtv_action])
        self.export_tool_btn.setMenu(self.export_menu)
        self.export_tool_btn.setPopupMode(QW.QToolButton.InstantPopup)
        self.export_tool_btn.setIcon(get_icon("edit.png"))

    def setup_shortcuts(self):
        self.new_file_action.setShortcut(CTRL + QC.Qt.Key_N)
        self.save_action.setShortcut(CTRL + QC.Qt.Key_S)
        self.open_action.setShortcut(CTRL + QC.Qt.Key_O)
        self.save_as_action.setShortcut(CTRL + SHIFT + QC.Qt.Key_S)

        self.export_action.setShortcut(CTRL + QC.Qt.Key_E)
        self.export_dtv_action.setShortcut(CTRL + QC.Qt.Key_D)
        self.export_rtv_action.setShortcut(CTRL + QC.Qt.Key_R)

        self.run_action.setShortcut(QC.Qt.Key_F5)
        self.stop_action.setShortcut(SHIFT + QC.Qt.Key_F5)
        self.restart_action.setShortcut(CTRL + SHIFT + QC.Qt.Key_F5)

    def setup_tooltips(self):
        for action in [*self.file_actions, *self.test_actions]:
            tooltip = f"{action.text()} ({action.shortcut().toString()})"
            action.setToolTip(tooltip)
