# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring
from __future__ import annotations

from typing import Any, Dict, Optional

from guidata.configtools import get_icon
from guidata.dataset import DataSet
from guidata.dataset.dataitems import StringItem
from guidata.dataset.qtwidgets import DataSetEditGroupBox
from qtpy import QtWidgets as QW

from moduletester.config import _
from moduletester.gui.widgets.dockable_widget import DockableQWidget
from moduletester.model import ResultEnum, Test


class _PropertiesDataSet(DataSet):
    return_code = StringItem("Return code").set_prop("display", active=False)
    execution_duration = StringItem("Execution duration").set_prop(
        "display", active=False
    )
    last_run = StringItem("Last run").set_prop("display", active=False)
    status = StringItem("Status").set_prop("display", active=False)


class ResultProps(DockableQWidget):
    """Widget to display the properties of a test result.

    Args:
        parent: Parent widget. Defaults to None.
    """

    def __init__(self, parent: Optional[QW.QWidget] = None):
        super().__init__(parent, title="Test Execution")
        self.props: Dict[str, Any] = {}

        # Widgets
        self.result_enum = QW.QComboBox()
        # self.table = QW.QTreeWidget()
        self.dataset_gbox = DataSetEditGroupBox(
            "", _PropertiesDataSet, show_button=False
        )
        self.dataset_gbox.updateGeometry()
        self.dataset_gbox.get()
        # Layouts
        self.vlayout = QW.QVBoxLayout(self)
        self.vlayout.addWidget(self.title_label)
        self.vlayout.addWidget(self.result_enum)
        self.vlayout.addWidget(self.dataset_gbox)
        self.dataset_gbox.update()

        # Config
        for i, result in enumerate(ResultEnum):
            self.result_enum.addItem(result.format(), result)  # noqa: F821
            self.result_enum.setItemIcon(i, get_icon(result.icon_path))

    def set_item(self, test: Test):
        """Set the test to display the properties of.

        Args:
            test: Test to display the properties of.
        """
        self.set_props(test)
        result = ResultEnum.NO_RESULT
        if test.result is not None:
            result = test.result.result

        if test.result is None or test.is_running():
            self.result_enum.setEnabled(False)
        else:
            self.result_enum.setEnabled(True)

        self.result_enum.blockSignals(True)
        self.result_enum.setCurrentText(result.format())
        self.result_enum.blockSignals(False)

    def set_props(self, test: Test):
        """Set the properties displayed in the widget using the given test.

        Args:
            test: Test to display the properties of.
        """
        if test.result is not None:
            self.props.update(
                {
                    "return code": test.result.error_code,
                    "execution duration": test.result.execution_duration,
                    "last run": test.result.last_run,
                    "status": test.result.status.value,
                }
            )

            if self.props["execution duration"] is not None:
                self.props["execution duration"] = round(
                    self.props["execution duration"], 3
                )
        else:
            self.props.clear()

        dataset = self.dataset_gbox.dataset
        dataset.return_code = self.props.get("return code", "")
        dataset.execution_duration = self.props.get("execution duration", "")
        dataset.last_run = self.props.get("last run", "")
        dataset.status = self.props.get("status", "")

        self.dataset_gbox.updateGeometry()
        self.dataset_gbox.get()
