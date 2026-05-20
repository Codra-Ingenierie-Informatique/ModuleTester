# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring

# guitest: skip
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, List, Optional

from guidata.configtools import get_icon
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from moduletester.gui.external.pyqtspinner import WaitingSpinner
from moduletester.model import (
    ModuleErrorType,
    ModuleInternalErrorType,
    ModuleNotFoundType,
    Test,
)

GREY = "#F5F5F5"
# BLUE = "#0060C6"
BLUE = "#007BFF"
# TREE_STYLESHEET = """
#     QTreeWidget::item:selected {
#         background-color: #007BFF;
#     }
# """
TREE_STYLESHEET = ""


class TestListWidget(QW.QTreeWidget):
    """Widget to display the list of tests and some result/status information.

    Args:
        tests: List of tests to display. Defaults to None.
        parent: Parent widget. Defaults to None.
    """

    def __init__(
        self, tests: Optional[List[Test]], parent: Optional[QW.QWidget] = None
    ) -> None:
        super().__init__(parent)
        # Fields
        tests = tests or []
        self.tests: dict[str, Test] = {}
        self._setup_tests(tests)
        self.test_items: dict[str, QW.QTreeWidgetItem] = {}
        self.menu = TestContextMenu(self)

        # Config
        self.setHeaderLabels(["Name", "Status", "Last run"])
        self.setSelectionMode(QW.QAbstractItemView.SingleSelection)
        self.bold_font = QG.QFont()
        self.bold_font.setBold(True)
        self.bold_font.setUnderline(True)
        # self.bold_font.setCapitalization(QG.QFont.Capitalization.Capitalize)
        # self.setCurrentItem(self.topLevelItem(0))
        self.installEventFilter(self)
        self.setAlternatingRowColors(True)
        self.setIndentation(15)
        self.setColumnWidth(0, 250)
        self.setStyleSheet(TREE_STYLESHEET)
        self.currentItemChanged.connect(self._select_item)

        self.build_tree()

    def _setup_tests(self, tests: List[Test]) -> None:
        """Set the tests list.

        Args:
            tests: List of tests.
        """
        self.tests.clear()
        self.tests.update(
            {t.package.name_from_source.rsplit(".", 1)[-1]: t for t in tests}
        )

    def reset_widget(self, tests: List[Test]) -> None:
        """Reset the widget with the given tests. Avoids creating a new widget.
        Args:
            tests: List of tests to display.
        """
        self._setup_tests(tests)
        self.build_tree()

    def start_test_spinner(self, test_item: QW.QTreeWidgetItem) -> None:
        """Start a spinner for the given test item.

        Args:
            test_item: Test item to start the spinner for.
        """
        spinner = WaitingSpinner(
            self,
            False,
            radius=5,
            roundness=0,
            lines=50,
            line_length=5,
            line_width=1,
            fade=100,
            speed=3.1415 / 4,
            color=QG.QColor("#0671D5"),
        )

        spinner.start()
        test_item.setText(1, "")
        test_item.setIcon(1, QG.QIcon())
        self.setItemWidget(test_item, 1, spinner)

    def stop_test_spinner(self, test_item: QW.QTreeWidgetItem) -> None:
        """Stop the spinner for the given test item.

        Args:
            test_item: Test item to stop the spinner for.
        """
        spinner = self.itemWidget(test_item, 1)
        self.removeItemWidget(test_item, 1)
        if isinstance(spinner, WaitingSpinner):
            spinner.stop()
            del spinner

    @property
    def current_item(self) -> QW.QTreeWidgetItem | None:
        return self.currentItem()

    def _select_item(
        self,
        current_item: QW.QTreeWidgetItem,
        previous_item: Optional[QW.QTreeWidgetItem],
    ) -> None:
        """Select the given item and reset the icon of the previous item. Implements
        some logic to avoid selecting non-selectable items (items can correspond to
        tests or directory in the package).

        Args:
            current_item: Current item.
            previous_item: Previous item.
        """
        if QC.Qt.ItemFlag.ItemIsSelectable & current_item.flags():  # type: ignore
            current_item.setSelected(True)
            self._reset_item_icon(current_item, None)
            if previous_item is not None:
                self._reset_item_icon(previous_item, None)

        elif (
            previous_item is not None
            and QC.Qt.ItemFlag.ItemIsSelectable & previous_item.flags()  # type: ignore
        ):
            self.setCurrentItem(previous_item)

    def _reset_item_icon(
        self, item: Optional[QW.QTreeWidgetItem], test: Optional[Test]
    ) -> None:
        """Reset the icon of the given item. If no item is given, the current item is
        used. One or both of the arguments must be set.

        Args:
            item: Item to reset the icon of.
            test: Test to reset the icon of.
        """
        if isinstance(item, QW.QTreeWidgetItem) and isinstance(test, Test):
            pass
        elif item is None and test is None:
            item, test = self.current_item, self.get_selected_test()
        elif item is None and isinstance(test, Test):
            item = self.test_items.get(test.package.last_name, None)
        elif test is None and isinstance(item, QW.QTreeWidgetItem):
            test = self.tests.get(item.text(0), None)

        if item is None or test is None or item.text(0) != test.package.last_name:
            return

        if isinstance(test.package.module, ModuleErrorType) or (
            test.is_error_new() or test.is_message_new()
        ):
            new_icon = get_icon("file-notify.svg")
        elif item is self.current_item and item.childCount() == 0:
            new_icon = get_icon("file-selected.svg")
        elif item.childCount() == 0:
            new_icon = get_icon("file.svg")
        else:
            new_icon = get_icon("libre-gui-folder-open.svg")

        item.setIcon(0, new_icon)

    def set_test_icon(self, test: Test, icon: str | QG.QIcon) -> None:
        """Set the icon of the given test.

        Args:
            test: Test to set the icon of.
            icon: icon to set.
        """
        item = self.test_items.get(test.package.last_name, None)
        if item is None:
            return
        icon = icon if isinstance(icon, QG.QIcon) else get_icon(icon)
        item.setIcon(0, icon)

    def select_first_test_item_from(
        self, root: Optional[QW.QTreeWidgetItem] = None
    ) -> Optional[QW.QTreeWidgetItem]:
        """Select the first test item from the given root. If no root is given, the
        invisible root item is used.

        Args:
            root: Root QTreeWidgetItem. Defaults to None.

        Returns:
            The first test item from the given root.
        """
        item = self.invisibleRootItem() if root is None else root
        if item is None:
            return None

        while item.childCount() > 0:  # type: ignore
            item = item.child(0)  # type: ignore

        if item is not None:
            self.setCurrentItem(item)

        return item

    def _set_result_icon(self, item: QW.QTreeWidgetItem, test: Test) -> None:
        """Set the result icon of the given item depending on the test result.

        Args:
            item: Item to set the result icon of.
            test: Test to get the result from.
        """
        if test.result is None:
            item.setIcon(1, get_icon("unknown.svg"))
        else:
            item.setIcon(1, get_icon(test.result.result.icon_path))

    def update_result(self, test: Optional[Test]) -> None:
        """Update the result of the given test. If no test is given, the selected test
        is used.

        Args:
            test: Test to update the result of. Defaults to None.
        """
        test = test or self.get_selected_test()
        if test is None:
            return

        item = self.test_items.get(test.package.last_name, None)

        if item is None:
            return

        test_columns = self.get_cols(test)

        if not test.is_running():
            self.stop_test_spinner(item)
            item.setText(1, test_columns[1])
            self._set_result_icon(item, test)
            self._reset_item_icon(item, test)
        item.setText(2, test_columns[2])

    def build_tree(self) -> None:
        """Build the tree widget with the tests. The tree is built using the tests
        list.
        """
        self.clear_widget()
        tree_dict = self._build_submodules_tree_dict(self.tests.values())
        self._build_tree_widget(self, tree_dict)

        for test in self.tests.values():
            self.update_result(test)

        self.select_first_test_item_from()

    def _build_submodules_tree_dict(self, tests: Iterable[Test]) -> dict[str, Any]:
        """Build a dictionary with the tests and their submodules. The dictionary is
        used to build the tree widget. This is done by calling
        self._build_submodules_tree_dict_step recursively.

        Args:
            tests: Tests to build the dictionary from.

        Returns:
            Dictionary with the tests and their submodules.
        """
        rows = [self.get_cols(test) for test in tests]
        # T = Union[str, dict[str, "T"]]
        grouped_elements: dict[str, Any] = {}
        for row in rows:
            self._build_submodules_tree_dict_step(grouped_elements, row)
        return grouped_elements

    def _build_submodules_tree_dict_step(
        self, current_dict: dict[str, Any], submodule_row: list[str]
    ) -> None:
        """Helper function to build the dictionary with the tests and their submodules.

        Args:
            current_dict: Current dictionary.
            submodule_row: Submodule row.
        """
        submodules = submodule_row[0].split(".", 1)

        if len(submodules) == 1:
            submodule, status, last_run = submodule_row
            current_dict[submodule] = submodule, status, last_run
            return

        submodule, submodule_row[0] = submodules
        next_level: dict[str, Any] = current_dict.setdefault(submodule, {})
        self._build_submodules_tree_dict_step(next_level, submodule_row)
        return

    def _build_tree_widget(
        self,
        parent: QW.QTreeWidgetItem | QW.QTreeWidget,
        level: dict[str, dict] | dict[str, tuple[str, str, str]] | tuple[str, str, str],
    ) -> Optional[QW.QTreeWidgetItem]:
        """Build the tree widget using the given level information.

        Args:
            parent: Parent QTreeWidgetItem or QTreeWidget.
            level: Level to build the tree widget with.
        """
        if isinstance(level, dict):
            for key, next_level in level.items():
                if isinstance(next_level, tuple):
                    self._build_tree_widget(parent, next_level)
                    continue
                new_parent_item = QW.QTreeWidgetItem(parent, (key, "", ""))
                new_parent_item.setFont(0, self.bold_font)
                new_parent_item.setExpanded(True)
                new_parent_item.setFlags(
                    QC.Qt.ItemFlag(
                        new_parent_item.flags() & ~QC.Qt.ItemFlag.ItemIsSelectable
                    )
                )
                new_parent_item.setIcon(0, get_icon("libre-gui-folder-open.svg"))

                self._build_tree_widget(new_parent_item, next_level)
        elif isinstance(level, tuple):
            new_leaf_item = QW.QTreeWidgetItem(parent, level)
            if isinstance(
                self.tests[level[0]].package.module,
                (ModuleNotFoundType, ModuleInternalErrorType),
            ):
                new_leaf_item.setForeground(0, QG.QColor("red"))
                new_leaf_item.setIcon(0, get_icon("file-notify.svg"))
            else:
                new_leaf_item.setIcon(0, get_icon("file.svg"))
            self.test_items[level[0]] = new_leaf_item

    def get_cols(self, test: Test) -> List[str]:
        """Get the columns for the given test.

        Args:
            test: Test to get the columns for.

        Returns:
            Columns for the given test.
        """
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

    def clear_widget(self) -> None:
        """Clear the widget."""
        for __ in range(self.topLevelItemCount()):
            self.takeTopLevelItem(0)

    def get_selected_test(self) -> Test | None:
        """Return the currently selected test.

        Returns:
            Currently selected test.
        """
        item = self.current_item
        assert isinstance(item, QW.QTreeWidgetItem)
        if item.childCount() > 0:
            return None
        test_name = item.text(0)
        return self.tests[test_name]

    def get_current_row(self, current_item: Optional[QW.QTreeWidgetItem]) -> int:
        """Return the row of the given item. If no item is given, the current item is
        used.

        Args:
            current_item: Current item. Defaults to None.
        """

        if current_item is None:
            return 0
        test_name = current_item.text(0)
        return tuple(self.tests.keys()).index(test_name, 0)

    def filter_items(self, search_str: str) -> None:
        """Filter the items in the tree widget using the given search string.

        Args:
            search_str: Search string.
        """
        # Hide items that don't contain the text
        search_str = search_str.lower()
        for i in range(self.topLevelItemCount()):
            self._filter(self.topLevelItem(i), search_str)  # type: ignore

    def _filter(self, item: QW.QTreeWidgetItem, search_str: str) -> bool:
        """Recursively filter the items in the tree widget using the given search.

        Args:
            item: Current item to check.
            search_str: Search string.

        Returns:
            Whether the item is enabled or not.
        """
        is_enabled = search_str in item.text(0).lower()
        for i in range(item.childCount()):
            child_item = item.child(i)
            is_enabled = child_item is not None and (
                is_enabled | self._filter(child_item, search_str)
            )

        item.setHidden(not is_enabled)
        return is_enabled

    def eventFilter(  # pylint: disable=invalid-name  # noqa: N802 #type: ignore
        self, source: QC.QObject, event: QC.QEvent
    ) -> bool:
        """Custom event filter to handle the context menu event.

        Args:
            source: Source of the event.
            event: Event to handle.

        Returns:
            Whether the event was handled or not.
        """
        if event.type() == QC.QEvent.Type.ContextMenu and source is self:
            self.menu.run(event)

            return True
        return super().eventFilter(source, event)


class TestContextMenu(QW.QMenu):
    """Context menu for the test list widget.

    Args:
        parent: Parent widget. Defaults to None.
    """

    def __init__(self, parent: Optional[QW.QWidget] = None) -> None:
        super().__init__(parent)
        # Actions
        self.run_script = QW.QAction("Run script")
        self.code_snippet = QW.QAction("Show code snippet")

        self.addAction(self.run_script)
        self.addAction(self.code_snippet)

    def run(self, event: QC.QEvent) -> None:
        """Run the context menu.

        Args:
            event: Event used to get context menu position.
        """
        super().exec_(event.globalPos())
