# pylint: disable=missing-module-docstring, missing-function-docstring
# pylint: disable=missing-class-docstring

from typing import Any, Callable, Dict, Optional

from guidata.qthelpers import get_icon
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from moduletester.gui.states.signals import TMSignals
from moduletester.gui.widgets.dockable_widget import DockableQWidget
from moduletester.gui.widgets.result_comment import TestCommentWidget
from moduletester.gui.widgets.result_error_widget import ResultError
from moduletester.gui.widgets.result_output_widget import ResultOutput
from moduletester.gui.widgets.result_props_widget import ResultProps
from moduletester.model import Test


class ResultInformation(DockableQWidget):
    def __init__(
        self,
        signals: TMSignals,
        title: str = "Test Result",
        parent: Optional[QW.QWidget] = None,
    ):
        super().__init__(parent, title)
        self.signals = signals

        # Widgets
        self.tab_widget = QW.QTabWidget()

        self.prop_group = ResultProps(self)

        self.comment_widget = TestCommentWidget(self.signals)
        self.output_widget = ResultOutput()
        self.error_widget = ResultError()

        # Layouts
        self.vlayout = QW.QVBoxLayout(self)

        self.vlayout.addWidget(self.title_label)
        self.vlayout.addWidget(self.tab_widget)

        # Additional
        self._notification_icon = get_icon("notification.svg")

        self._tab_bar_connected = False

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
        """Set the item to be displayed in the widget.

        Args:
            test: The test to be displayed.
        """
        self.prop_group.set_item(test)
        self.set_tabs(test)

    def _reset_tab_icon(self, index: int):
        """Reset the icon of the tab at the given index.

        Args:
            index: The index of the tab to reset.
        """
        if index in (1, 2) and self.tab_widget.tabIcon(index) is not None:
            self.tab_widget.setTabIcon(index, QG.QIcon())

    def _remove_tab_notif(self, test: Test) -> Callable[[int], None]:
        """Create a callback to remove the notification icon from the tab.

        Args:
            test: The test to remove the notification from.

        Returns:
            The callback function that encapsulate the given test.
        """

        def callback(index: int):
            self.tab_widget.setTabIcon(index, QG.QIcon())
            if index == 1:
                test.set_message_state(False)
            elif index == 2:
                test.set_error_state(False)

            if not (test.is_message_new() or test.is_error_new()):
                self.tab_widget.currentChanged.disconnect(callback)

        return callback

    def set_tabs(self, test: Test):
        """Set the tabs of the widget.

        Args:
            test: The test to display in the tabs.
        """
        self.comment_widget.set_item(test)

        current_tab_ind = self.tab_widget.currentIndex()

        self.output_widget.set_item(test)

        self.error_widget.set_item(test)

        self.tab_widget.clear()

        self.tab_widget.insertTab(0, self.comment_widget, "Comment")
        self.tab_widget.insertTab(1, self.output_widget, "Output message")
        self.tab_widget.insertTab(2, self.error_widget, "Error message")

        if test.is_message_new():
            self.tab_widget.setTabIcon(1, self._notification_icon)

        if test.is_error_new():
            self.tab_widget.setTabIcon(2, self._notification_icon)

        self.tab_widget.currentChanged.connect(self._remove_tab_notif(test))

        self.tab_widget.setCurrentIndex(current_tab_ind)
