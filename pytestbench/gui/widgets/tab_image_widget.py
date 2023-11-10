# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring

# guitest: skip
import os
from typing import List, Optional

from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from pytestbench.model import Test
from pytestbench.python_helpers import image_walker


class TabImageWidget(QW.QTabWidget):
    def __init__(self, origin_path: str, parent: Optional[QW.QWidget] = None) -> None:
        super().__init__(parent)
        self.images: List[str] = []
        self.tabs: List[QW.QLabel] = []
        self.menu = ImageContextMenu()

        self.origin_path = origin_path

        self.image_dirs = image_walker(self.origin_path)

    def create_tab(self, test: Test):
        self.images = test.get_images(self.image_dirs)

        if len(self.images) == 0:
            return

        if len(self.tabs) != 0:
            self.clear()
            self.tabs = []

        for image in self.images:
            tab = QW.QLabel()
            tab.setPixmap(QG.QPixmap(image))
            tab.setAlignment(QC.Qt.AlignCenter)
            tab.setContextMenuPolicy(QC.Qt.CustomContextMenu)
            tab.customContextMenuRequested.connect(self.run_menu)  # type: ignore
            self.tabs.append(tab)
            self.addTab(tab, os.path.basename(image))

    def run_menu(self, point: QC.QPoint):
        self.menu.exec_(self.mapToGlobal(point))


class ImageContextMenu(QW.QMenu):
    def __init__(self, parent: Optional[QW.QWidget] = None) -> None:
        super().__init__(parent)
        # Actions
        self.open_image = QW.QAction("Open Image")

        self.addAction(self.open_image)
