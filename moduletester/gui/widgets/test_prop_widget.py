# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Any, Dict, Optional

from guidata.dataset import DataSet
from guidata.dataset.dataitems import IntItem, StringItem
from guidata.dataset.qtwidgets import DataSetEditGroupBox
from qtpy import QtWidgets as QW

from moduletester.gui.widgets.dockable_widget import DockableQWidget
from moduletester.model import Test


class _PropertiesDataSet(DataSet):
    name = StringItem("Name").set_prop("display", active=False)
    source = StringItem("Source").set_prop("display", active=False)
    path = StringItem("Path").set_prop("display", active=False)
    args = StringItem("Args").set_prop("display", placeholder="No args")
    timeout = IntItem("Timeout", default=0)


class TestProps(DockableQWidget):
    """Widget to display the properties of a test.

    Args:
        title: Title of the widget. Defaults to "Test Properties".
        parent: Parent widget. Defaults to None.
    """

    def __init__(self, title="Test Properties", parent: Optional[QW.QWidget] = None):
        super().__init__(parent, title)
        self.props: Dict[str, Any] = {}

        # Widgets
        self.dataset_gbox = DataSetEditGroupBox(None, _PropertiesDataSet)
        # Layout
        self.vlayout = QW.QVBoxLayout(self)
        self.vlayout.addWidget(self.title_label)
        self.vlayout.addWidget(self.dataset_gbox)

        self.props = {}

    def setup(self):
        """Setup the widget. Empty."""
        pass

    def set_props(self, test: Test):
        """Set the widget properties from a test.

        Args:
            test: Test to set the properties from.
        """
        self.props.update(
            {
                "name": test.package.last_name,
                "source": test.package.full_name.split(".")[0],
                "path": test.package.root_path,
                "args": test.command_args,
                "timeout": test.command_timeout,
            }
        )
        dataset = self.dataset_gbox.dataset
        dataset.name = test.package.last_name
        dataset.source = test.package.full_name.split(".")[0]
        dataset.path = test.package.root_path
        dataset.args = test.command_args
        dataset.timeout = test.command_timeout

        self.dataset_gbox.get()
        self.dataset_gbox.set_apply_button_state(False)
