# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring

# guitest: skip

from typing import Optional

from guidata.qthelpers import get_std_icon  # type: ignore
from PyQt5 import QtCore as QC
from PyQt5 import QtGui as QG
from PyQt5 import QtWidgets as QW

from pytestbench.gui.states.bench_signals import TMSignals
from pytestbench.model import Test


class TestCommentWidget(QW.QWidget):
    def __init__(self, signals: TMSignals, parent: Optional[QW.QWidget] = None):
        super().__init__(parent)
        self.signals = signals

        # Widgets
        self.lbl_icon = QW.QLabel()
        self.lbl_icon.setFixedWidth(32)

        self.comment_label = QW.QTextEdit()
        self.comment_label.setWordWrapMode(QG.QTextOption.WordWrap)
        self.comment_label.setFrameStyle(0)

        for label in (self.comment_label, self.lbl_icon):
            label.setAlignment(QC.Qt.AlignTop)

        # Event Handlers
        self.comment_label.textChanged.connect(self.text_changed)  # type: ignore

        # Layouts
        self.hlayout = QW.QHBoxLayout(self)
        self.hlayout.addWidget(self.lbl_icon)
        self.hlayout.addWidget(self.comment_label)

    def set_item(self, test: Test):
        if test.result is not None:
            text = test.result.comment
            self.comment_label.setTextInteractionFlags(QC.Qt.TextEditorInteraction)
        else:
            text = "No result yet"
            self.comment_label.setTextInteractionFlags(QC.Qt.TextSelectableByMouse)

        self.lbl_icon.setPixmap(get_std_icon("MessageBoxInformation").pixmap(24, 24))

        self.comment_label.blockSignals(True)
        self.comment_label.setText(text)
        self.comment_label.blockSignals(False)

    def text_changed(self):
        self.signals.benchModified.emit()
