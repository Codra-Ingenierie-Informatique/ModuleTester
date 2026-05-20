from __future__ import annotations

from typing import Optional

import qtpy.QtCore as QC
import qtpy.QtWidgets as QW
from guidata.configtools import get_icon

from moduletester.gui.widgets import test_list_widget
from moduletester.gui.widgets.dockable_widget import DockableQWidget
from moduletester.model import Test


class TestListComponent(DockableQWidget):
    """Wrapper for the TestListWidget and the additional butons and search bar.

    Args:
        tests: List of Test objects. Defaults to None.
        title: Title of the widget (and dock widget). Defaults to "Tests".
        parent: Parent widget. Defaults to None.
    """

    def __init__(
        self,
        tests: Optional[list[Test]] = None,
        title: str = "Tests",
        parent: Optional[QW.QWidget] = None,
    ) -> None:
        super().__init__(parent, title)

        self.test_list_widget = test_list_widget.TestListWidget(tests, self)
        self.list_layout = QW.QVBoxLayout()
        self.collapse_all_btn = QW.QPushButton("Collapse all", self)
        self.expand_all_btn = QW.QPushButton("Expand all", self)
        self.search_bar = QW.QLineEdit(self)
        self.search_bar.setPlaceholderText("Search test...")
        self.run_btn = QW.QPushButton(get_icon("apply.png"), "Run Script", self)

        self.setup()

    def setup(self):
        """Setup the layout and signal connections for the widget."""
        self.list_layout = QW.QGridLayout()
        top_controls_layout = QW.QHBoxLayout()
        top_controls_layout.addWidget(self.collapse_all_btn)
        top_controls_layout.addWidget(self.expand_all_btn)
        top_controls_layout.addWidget(self.search_bar)
        self.list_layout.addLayout(top_controls_layout, 0, 0, 1, 1)
        self.list_layout.addWidget(self.test_list_widget, 1, 0, 7, 1)
        self.list_layout.addWidget(self.run_btn, 8, 0, 1, 1)
        self.setLayout(self.list_layout)

        self.collapse_all_btn.clicked.connect(self.test_list_widget.collapseAll)
        self.expand_all_btn.clicked.connect(self.test_list_widget.expandAll)
        self.search_bar.textChanged.connect(self.test_list_widget.filter_items)
