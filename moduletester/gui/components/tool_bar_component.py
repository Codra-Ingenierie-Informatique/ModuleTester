# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable= missing-function-docstring

from typing import List, Optional

from guidata.configtools import get_icon  # type: ignore
from qtpy import QtCore as QC
from qtpy import QtWidgets as QW
from qtpy.QtWidgets import QAction

CTRL = QC.Qt.Modifier.CTRL
SHIFT = QC.Qt.Modifier.SHIFT


class TestManagerToolbar(QW.QToolBar):
    def __init__(self, parent: Optional[QW.QWidget] = None):
        """Top toolbar.

        Args:
            parent: Parent widget. Defaults to None.
        """
        super().__init__(parent)
        # Fields
        self.file_actions: List[QAction] = []
        self.test_actions: List[QAction] = []

        # File Actions
        self.save_action = QAction(get_icon("libre-gui-save.svg"), "Save")
        self.save_as_action = QAction(get_icon("libre-gui-save-as.svg"), "Save As")
        self.open_action = QAction(get_icon("libre-gui-folder-open.svg"), "Open")
        self.update_action = QAction(get_icon("libre-gui-refresh.svg"), "Reload tests")
        self.new_file_action = QAction(
            get_icon("libre-gui-new-file-document.svg"), "New"
        )

        # Expt action
        self.export_menu = QW.QMenu()
        self.export_action = QAction("Export all documents")
        self.export_test_list_action = QAction("Export Test List Document")
        self.export_test_results_action = QAction("Export Test Results Document")
        self.export_tool_btn = QW.QToolButton()

        # Test Actions
        self.run_action = QAction("Run")
        self.stop_action = QAction("Stop")
        self.restart_action = QAction("Restart")

        # Other actions
        self.view_menu = QW.QMenu("View")
        self.view_tool_btn = QW.QToolButton()
        self.view_tool_btn.setIcon(get_icon("dock.svg"))
        self.view_tool_btn.setDisabled(True)

        self.setContextMenuPolicy(QC.Qt.ContextMenuPolicy.PreventContextMenu)
        # Setup
        self.setup()

    def setup(self):
        """Setup the toolbar menus and actions."""
        self.setup_export()
        # Actions
        self.file_actions = [
            self.new_file_action,
            self.open_action,
            self.update_action,
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
        self.addSeparator()
        self.addWidget(self.view_tool_btn)

    def setup_view(self, view_menu: QW.QMenu) -> None:
        """Setup the view (docks) menu for the toolbar.

        Args:
            view_menu: The view menu to be added to the toolbar.
        """
        self.view_menu = view_menu
        self.view_tool_btn.setMenu(self.view_menu)
        self.view_tool_btn.setPopupMode(QW.QToolButton.InstantPopup)

    def setup_export(self):
        """Setup the export menu for the toolbar."""
        self.export_menu.addAction(self.export_action)
        self.export_menu.addSeparator()
        self.export_menu.addActions(
            [self.export_test_list_action, self.export_test_results_action]
        )
        self.export_tool_btn.setMenu(self.export_menu)
        self.export_tool_btn.setPopupMode(QW.QToolButton.InstantPopup)
        self.export_tool_btn.setIcon(get_icon("libre-gui-export-doc.svg"))

    def setup_shortcuts(self):
        """Setup the shortcuts for the toolbar actions."""
        self.new_file_action.setShortcut(CTRL + QC.Qt.Key.Key_N)
        self.save_action.setShortcut(CTRL + QC.Qt.Key.Key_S)
        self.open_action.setShortcut(CTRL + QC.Qt.Key.Key_O)
        self.update_action.setShortcut(CTRL + QC.Qt.Key.Key_R)
        self.save_as_action.setShortcut(CTRL + SHIFT + QC.Qt.Key.Key_S)

        self.export_action.setShortcut(CTRL + QC.Qt.Key.Key_E)
        self.export_test_list_action.setShortcut(CTRL + QC.Qt.Key.Key_D)
        self.export_test_results_action.setShortcut(CTRL + QC.Qt.Key.Key_R)

        self.run_action.setShortcut(QC.Qt.Key.Key_F5)
        self.stop_action.setShortcut(SHIFT + QC.Qt.Key.Key_F5)
        self.restart_action.setShortcut(CTRL + SHIFT + QC.Qt.Key.Key_F5)

    def setup_tooltips(self):
        """Setup the tooltips for the toolbar actions."""
        for action in [*self.file_actions, *self.test_actions]:
            tooltip = f"{action.text()} ({action.shortcut().toString()})"
            action.setToolTip(tooltip)
