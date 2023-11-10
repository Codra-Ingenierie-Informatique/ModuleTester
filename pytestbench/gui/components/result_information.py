# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=missing-class-docstring

from typing import Any, Dict, Optional

from qtpy import QtWidgets as QW

from pytestbench.gui.states.bench_signals import TMSignals
from pytestbench.gui.widgets.result_comment import TestCommentWidget
from pytestbench.gui.widgets.result_error_widget import ResultError
from pytestbench.gui.widgets.result_output_widget import ResultOutput
from pytestbench.gui.widgets.result_props_widget import ResultProps
from pytestbench.model import Test


class ResultInformation(QW.QGroupBox):
    def __init__(self, signals: TMSignals, parent: Optional[QW.QWidget] = None):
        super().__init__("Results", parent)
        self.signals = signals

        # Widgets
        self.tab_widget = QW.QTabWidget()

        self.prop_group = ResultProps("Properties")
        self.comment_widget = TestCommentWidget(self.signals)

        # Layouts
        self.vlayout = QW.QHBoxLayout(self)

        self.vlayout.addWidget(self.tab_widget)
        self.vlayout.addWidget(self.prop_group)

        # Config
        self.prop_group.setFixedWidth(350)

    @property
    def comment(self) -> str:
        return self.comment_widget.comment_label.toPlainText()

    @property
    def result_enum(self) -> QW.QComboBox:
        return self.prop_group.result_enum

    @property
    def props(self) -> Dict[str, Any]:
        return self.prop_group.props

    def set_item(self, test: Test):
        self.prop_group.set_item(test)
        self.set_tabs(test)

    def set_tabs(self, test: Test):
        self.comment_widget = TestCommentWidget(self.signals)
        self.comment_widget.set_item(test)

        current_tab_ind = self.tab_widget.currentIndex()

        output_widget = ResultOutput()
        output_widget.set_item(test)

        error_widget = ResultError()
        error_widget.set_item(test)

        for _index in range(self.tab_widget.count()):
            self.tab_widget.removeTab(0)

        self.tab_widget.insertTab(0, self.comment_widget, "Comment")
        self.tab_widget.insertTab(1, output_widget, "Output message")
        self.tab_widget.insertTab(2, error_widget, "Error message")

        self.tab_widget.setCurrentIndex(current_tab_ind)
