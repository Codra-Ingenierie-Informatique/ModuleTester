# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Any, Dict, Optional

from qtpy import QtCore as QC
from qtpy import QtWidgets as QW

from moduletester.model import Test


class TestProps(QW.QGroupBox):
    def __init__(self, parent: Optional[QW.QWidget] = None):
        super().__init__(parent)
        self.props: Dict[str, Any] = {}

        # Widgets
        self.table = QW.QTreeWidget()

        # Layout
        self.vlayout = QW.QVBoxLayout(self)
        self.vlayout.addWidget(self.table)

    def setup(self):
        self.setTitle("Properties")

        self.table.setHeaderLabels(["Property", "Value"])
        self.table.setIndentation(False)
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 200)
        self.table.setAlternatingRowColors(True)

        self.table.setEditTriggers(QW.QAbstractItemView.NoEditTriggers)

        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)

    def set_props(self, test: Test):
        self.props = {
            "name": test.package.last_name,
            "source": test.package.full_name.split(".")[0],
            "path": test.package.root_path,
            "args": test.command_args if test.command_args != "" else "No args",
            "timeout": test.command_timeout if test.command_timeout != 86400 else 0,
        }

        for _ in range(self.table.topLevelItemCount()):
            self.table.takeTopLevelItem(0)

        for key, value in self.props.items():
            item = QW.QTreeWidgetItem((str(key), str(value)))
            if key not in ("name", "source", "path"):
                item.setFlags(
                    QC.Qt.ItemIsEditable | QC.Qt.ItemIsSelectable | QC.Qt.ItemIsEnabled
                )

            tooltip = f"{key}: {value}"
            self.set_tool_tips(item, tooltip)
            self.table.addTopLevelItem(item)

    def set_tool_tips(self, item: QW.QTreeWidgetItem, tooltip: str):
        for col_index in range(item.columnCount()):
            item.setToolTip(col_index, tooltip)

    def on_item_double_clicked(self, item: QW.QTreeWidgetItem, column: int):
        if column == 1 and item.flags() & QC.Qt.ItemIsEditable:
            self.table.editItem(item, column)
