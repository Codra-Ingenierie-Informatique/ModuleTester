# pylint: disable=missing-class-docstring, missing-module-docstring
# pylint: disable=missing-function-docstring

from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from moduletester.gui.states.signals import TMSignals
from moduletester.gui.widgets.tab_image_widget import TabImageWidget
from moduletester.gui.widgets.test_description_widget import TestDescriptionWidget
from moduletester.gui.widgets.test_prop_widget import TestProps
from moduletester.model import Test


class TestInformation(QW.QWidget):
    def __init__(
        self,
        signals: TMSignals,
        parent: QW.QWidget,
    ):
        super().__init__(parent)
        self.props = {
            "name": "",
            "source": "",
            "path": "",
            "args": "",
            "timeout": 0,
        }
        self.test = None
        self.signals = signals
        # Widgets
        self.tab_widget = QW.QTabWidget(parent=self)
        self.description_tab = TestDescriptionWidget(self)
        self.table_group = TestProps()

        # Layouts
        self.vlayout = QW.QVBoxLayout(self)
        self.vlayout.addWidget(self.tab_widget)

        self.table_group.setup()

    def set_item(self, test: Test, origin_path: str):
        """Set the item to be displayed in the description and properties widgets.

        Args:
            test: The test to be displayed.
            origin_path: _description_
        """

        current_tab_ind = self.tab_widget.currentIndex()

        self.description_tab.set_item(test)

        new_tab_widget = TabImageWidget(origin_path)
        new_tab_widget.create_tab(test)
        new_tab_widget.insertTab(0, self.description_tab, test.package.last_name)
        new_tab_widget.menu.open_image.triggered.connect(  # type: ignore
            self.open_image
        )
        self.vlayout.removeWidget(self.tab_widget)

        self.vlayout.insertWidget(0, new_tab_widget)

        new_tab_widget.setCurrentIndex(current_tab_ind)
        self.table_group.set_props(test)

        self.tab_widget = new_tab_widget

    def has_test_changed(self, test: Test):
        """Check if the current test has changed.

        Args:
            test: The test to check.

        Returns:
            True if the test has changed, False otherwise.
        """
        if test.package.last_name == self.props["name"]:
            return False

        return True

    def open_image(self):
        """Open the image in the current tab if the tab is a TabImageWidget."""
        if not isinstance(self.tab_widget, TabImageWidget):
            return
        tab_index = self.tab_widget.currentIndex() - 1  # Compensate for test desc
        image = self.tab_widget.images[tab_index]
        QG.QDesktopServices.openUrl(QC.QUrl.fromLocalFile(image))

    def update_command(self, test: Test):
        """Update the test command arguments of the given test.

        Args:
            test: The test to update.
        """
        info_dataset = self.table_group.dataset_gbox.dataset
        test.command_args = info_dataset.args  # type: ignore
        test.command_timeout = info_dataset.timeout  # type: ignore

        for s in test.run_opts:
            value = self.table_group.props.get(s, None)
            is_zero_value = value in ("", "0", 0)

            if not is_zero_value and value in test.run_opts:
                opt_index = test.run_opts.index(s)
                test.run_opts[opt_index + 1] = value
            elif not is_zero_value:
                test.run_opts.extend((s, value))
            elif is_zero_value and value in test.run_opts:
                opt_index = test.run_opts.index(s)
                test.run_opts.remove(test.run_opts[opt_index + 1])
                test.run_opts.remove(s)

        self.validate_command(test)

    def validate_command(self, test: Test) -> bool:
        """Validate the command line arguments of the given test. If the command line
        arguments are invalid, a message box will be shown to the user."""
        try:
            test.build_command()
            return True
        except ValueError as e:
            QW.QMessageBox(
                QW.QMessageBox.NoIcon,
                "Command Error",
                "The following error occured while parsing the "
                "command line arguments:"
                f"\n\n\t{str(e)}\n\n"
                "Please check the command line arguments.",
            ).exec()
            return False
