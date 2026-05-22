# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring

from typing import Optional

from guidata.qthelpers import get_std_icon  # type: ignore
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from moduletester.model import Test


class ResultError(QW.QWidget):
    """Widget to display the error message of a test result (stderr).

    Args:
        parent: Parent widget. Defaults to None.
    """

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
        self.label.setTextInteractionFlags(
            QC.Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.label.setAlignment(QC.Qt.AlignmentFlag.AlignTop)
        self.label.setFrameStyle(0)
        self.label.setFont(QG.QFontDatabase.systemFont(QG.QFontDatabase.FixedFont))
        self.icon.setFixedWidth(32)
        self.icon.setAlignment(QC.Qt.AlignmentFlag.AlignTop)

    def set_item(self, test: Test):
        """Set the test to display the error message of."""
        if test.result is None:
            text_level = "Information"
            text = "No result yet"
        elif test.result.error_msg is None or test.result.error_msg == "":
            text_level = "Information"
            text = "No error message"
        else:
            text_level = "Critical"
            text = test.result.error_msg

        self.icon.setPixmap(get_std_icon(f"MessageBox{text_level}").pixmap(24, 24))
        self.label.setText(text)
