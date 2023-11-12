# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Optional

from guidata.qthelpers import get_std_icon  # type: ignore
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from moduletester.model import Test


class ResultOutput(QW.QWidget):
    def __init__(self, parent: Optional[QW.QWidget] = None):
        super().__init__(parent)

        # Widgets
        self.icon = QW.QLabel()
        self.label = QW.QTextEdit()

        # Layouts
        self.hlayout = QW.QHBoxLayout(self)
        self.hlayout.addWidget(self.icon)
        self.hlayout.addWidget(self.label)

        # Config
        self.label.setWordWrapMode(QG.QTextOption.WordWrap)
        self.label.setTextInteractionFlags(QC.Qt.TextSelectableByMouse)
        self.label.setFrameStyle(0)
        self.label.setAlignment(QC.Qt.AlignTop)
        self.icon.setFixedWidth(32)
        self.icon.setAlignment(QC.Qt.AlignTop)

    def set_item(self, test: Test):
        if test.result is None:
            text = "No result yet"
        elif test.result.output_msg is None or test.result.output_msg == "":
            text = "No output message"
        else:
            text = test.result.output_msg

        self.icon.setPixmap(get_std_icon("MessageBoxInformation").pixmap(24, 24))
        self.label.setPlainText(text)
