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


class TestDescriptionWidget(QW.QWidget):
    def __init__(self, signals: TMSignals, parent: Optional[QW.QWidget] = None):
        super().__init__(parent)
        self.test: Optional[Test] = None
        self.signals = signals

        # Widgets
        self.lbl_icon = QW.QLabel()
        self.lbl_icon.setFixedWidth(32)

        self.desc_label = QW.QTextEdit()
        self.desc_label.setWordWrapMode(QG.QTextOption.WordWrap)
        self.desc_label.setFrameStyle(0)

        for label in (self.desc_label, self.lbl_icon):
            label.setAlignment(QC.Qt.AlignTop)

        # Layouts
        self.hlayout = QW.QHBoxLayout(self)
        self.hlayout.addWidget(self.lbl_icon)
        self.hlayout.addWidget(self.desc_label)

        self.desc_label.textChanged.connect(self.text_changed)  # type: ignore

    def text_changed(self):
        self.signals.benchModified.emit()

    def set_item(self, test: Test):
        self.test = test
        text_level = "Information" if test.is_valid else "Critical"
        self.lbl_icon.setPixmap(get_std_icon(f"MessageBox{text_level}").pixmap(24, 24))

        self.desc_label.blockSignals(True)
        self.desc_label.setText(test.description)
        self.desc_label.blockSignals(False)
