# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Any, Dict, Optional

from qtpy import QtWidgets as QW

from pytestbench.model import ResultEnum, Test


class ResultProps(QW.QGroupBox):
    def __init__(self, parent: Optional[QW.QWidget] = None):
        super().__init__(parent)
        self.props: Dict[str, Any] = {}

        # Widgets
        self.result_enum = QW.QComboBox()
        self.table = QW.QTreeWidget()

        # Layouts
        self.vlayout = QW.QVBoxLayout(self)
        self.vlayout.addWidget(self.result_enum)
        self.vlayout.addWidget(self.table)

        # Config
        result_value = [result.value for result in ResultEnum]
        self.result_enum.addItems(result_value)

        self.table.setHeaderLabels(["Property", "Value"])
        self.table.setAlternatingRowColors(True)
        self.table.setIndentation(False)
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 200)

    def set_item(self, test: Test):
        self.set_props(test)
        result_value = "no result"
        if test.result is not None:
            result_value = test.result.result.value

        if test.result is None:
            self.result_enum.setEnabled(False)
        else:
            self.result_enum.setEnabled(True)

        self.result_enum.blockSignals(True)
        self.result_enum.setCurrentText(result_value)
        self.result_enum.blockSignals(False)

    def set_props(self, test: Test):
        if test.result is not None:
            self.props = {
                "return code": test.result.error_code,
                "execution duration": test.result.execution_duration,
                "last run": test.result.last_run,
                "status": test.result.status.value,
            }

            if self.props["execution duration"] is not None:
                self.props["execution duration"] = round(
                    self.props["execution duration"], 3
                )
        else:
            self.props = {}

        for _ in range(self.table.topLevelItemCount()):
            self.table.takeTopLevelItem(0)

        for key, value in self.props.items():
            item = QW.QTreeWidgetItem((str(key), str(value)))
            tooltip = f"{key}: {value}"
            self.set_tool_tips(item, tooltip)
            self.table.addTopLevelItem(item)

    def set_tool_tips(self, item: QW.QTreeWidgetItem, tooltip: str):
        for col_index in range(item.columnCount()):
            item.setToolTip(col_index, tooltip)
