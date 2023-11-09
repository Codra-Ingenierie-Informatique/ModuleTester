# pylint: disable=missing-class-docstring, missing-module-docstring
# pylint: disable=missing-function-docstring
from typing import Optional

from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

from pytestbench.gui.states.bench_signals import TMSignals
from pytestbench.gui.widgets.tab_image_widget import TabImageWidget
from pytestbench.gui.widgets.test_description_widget import TestDescriptionWidget
from pytestbench.gui.widgets.test_prop_widget import TestProps
from pytestbench.model import Test


class TestInformation(QW.QGroupBox):
    def __init__(self, signals: TMSignals, parent: Optional[QW.QWidget] = None):
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
        self.tab_widget = QW.QTabWidget()
        self.table_group = TestProps()
        self.description_tab = TestDescriptionWidget(self.signals)

        # Layouts
        self.hlayout = QW.QHBoxLayout(self)

        self.hlayout.addWidget(self.tab_widget)
        self.hlayout.addWidget(self.table_group)

        self.table_group.setFixedWidth(350)
        self.table_group.setup()

    @property
    def description(self) -> str:
        return self.description_tab.desc_label.toPlainText()

    def set_item(self, test: Test, origin_path: str):
        self.setTitle(test.package.full_name)
        text = self.description

        current_tab_ind = self.tab_widget.currentIndex()

        self.hlayout.removeWidget(self.tab_widget)

        self.description_tab = TestDescriptionWidget(self.signals)
        self.description_tab.set_item(test)

        if not self.has_test_changed(test):
            self.description_tab.desc_label.setText(text)

        self.tab_widget = TabImageWidget(origin_path)
        self.tab_widget.create_tab(test)
        self.tab_widget.insertTab(0, self.description_tab, "Test description")
        self.tab_widget.setCurrentIndex(0)
        self.tab_widget.menu.open_image.triggered.connect(  # type: ignore
            self.open_image
        )

        self.hlayout.insertWidget(0, self.tab_widget)

        self.tab_widget.setCurrentIndex(current_tab_ind)
        self.table_group.set_props(test)

    def has_test_changed(self, test: Test):
        if test.package.last_name == self.props["name"]:
            return False

        return True

    def open_image(self):
        tab_index = self.tab_widget.currentIndex() - 1  # Compensate for test desc
        image = self.tab_widget.images[tab_index]
        QG.QDesktopServices.openUrl(QC.QUrl.fromLocalFile(image))

    def update_command(self, item: QW.QTreeWidgetItem, test: Test):
        if item.text(0) == "args":
            test.command_args = item.text(1)
        elif item.text(0) == "timeout":
            try:
                if item.text(1) != "0":
                    test.command_timeout = int(item.text(1))
                else:
                    test.command_timeout = 86400
            except ValueError:
                item.setText(1, str(test.command_timeout))

        if item.text(0) in (
            "timeout",
            "category",
            "save_path",
            "pattern",
        ) and item.text(1) not in ("", "0"):
            if item.text(0) in test.run_opts:
                opt_index = test.run_opts.index(item.text(0))
                test.run_opts[opt_index + 1] = item.text(1)
            else:
                test.run_opts.extend([item.text(0), item.text(1)])
        elif item.text(0) in ("timeout", "category", "save_path", "pattern"):
            if item.text(0) in test.run_opts:
                opt_index = test.run_opts.index(item.text(0))
                test.run_opts.remove(test.run_opts[opt_index + 1])
                test.run_opts.remove(item.text(0))
