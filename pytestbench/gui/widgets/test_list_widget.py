# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring

# guitest: skip

from datetime import datetime
from typing import List, Optional

from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from pytestbench.model import Test

GREY = "#F5F5F5"


class TestListWidget(QW.QTreeWidget):
    def __init__(self, tests: List[Test], parent: Optional[QW.QWidget] = None):
        super().__init__(parent)
        # Fields
        self.tests = tests
        self.menu = TestContextMenu(self)

        # Config
        self.setHeaderLabels(["Name", "Status", "Last run"])
        self.setSelectionMode(QW.QAbstractItemView.SingleSelection)
        self.setup_list(None)
        self.setCurrentItem(self.topLevelItem(0))
        self.installEventFilter(self)
        self.setAlternatingRowColors(True)
        self.setIndentation(False)

    @property
    def current_item(self):
        return self.selectedItems()[0]

    def setup_list(self, current_item: Optional[QW.QTreeWidgetItem]):
        current_row = self.get_current_row(current_item)
        self.blockSignals(True)
        self.clear_widget()

        for test in self.tests:
            item = QW.QTreeWidgetItem(self.get_cols(test))
            for col in range(item.columnCount()):
                item.setSizeHint(col, QC.QSize(1, 25))
            self.addTopLevelItem(item)
            item_ind = self.topLevelItemCount()

            test = self.tests[item_ind - 1]

            if not test.is_valid:
                item.setForeground(0, QG.QColor("#FF3333"))

        self.setCurrentItem(self.topLevelItem(current_row))

        self.blockSignals(False)

    def get_cols(self, test: Test) -> List[str]:
        cols = [test.package.name_from_source]
        if test.result is None:
            cols.extend(["NOT EXECUTED", ""])
        elif test.result.last_run is None:
            cols.extend([test.result.result_name, ""])
        else:
            if isinstance(test.result.last_run, datetime):
                last_run = test.result.last_run.strftime("%d/%m/%y %H:%M:%S.%f")
            else:
                last_run = test.result.last_run
            cols.extend([test.result.result_name, last_run])
        return cols

    def clear_widget(self):
        for _ in range(self.topLevelItemCount()):
            self.takeTopLevelItem(0)

    def set_row_background(self, item: QW.QTreeWidgetItem):
        for col in range(item.columnCount()):
            item.setBackground(col, QG.QColor(GREY))

    def get_selected_test(self) -> Test:
        item = self.selectedItems()[0]
        test_index = self.get_current_row(item)
        return self.tests[test_index]

    def get_current_row(self, current_item: Optional[QW.QTreeWidgetItem]) -> int:
        if current_item is None:
            return 0

        test_name = current_item.text(0)
        for ind, test in enumerate(self.tests):
            if test.package.name_from_source == test_name:
                return ind
        return 0

    def eventFilter(  # pylint: disable=invalid-name
        self, source: QC.QObject, event: QC.QEvent
    ) -> bool:
        if event.type() == QC.QEvent.ContextMenu and source is self:
            self.menu.run(event)

            return True
        return super(TestListWidget, self).eventFilter(source, event)


class TestContextMenu(QW.QMenu):
    def __init__(self, parent: Optional[QW.QWidget] = None) -> None:
        super().__init__(parent)
        # Actions
        self.run_script = QW.QAction("Run script")
        self.code_snippet = QW.QAction("Show code snippet")

        self.addAction(self.run_script)
        self.addAction(self.code_snippet)

    def run(self, event: QC.QEvent):
        super().exec_(event.globalPos())
