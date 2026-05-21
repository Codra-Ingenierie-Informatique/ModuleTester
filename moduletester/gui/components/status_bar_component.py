# pylint: disable=missing-module-docstring, missing-class-docstring
# pylint: disable=missing-function-docstring
from qtpy import QtCore as QC
from qtpy import QtGui as QG
from qtpy import QtWidgets as QW

from moduletester.gui.external.pyqtspinner import WaitingSpinner


class TMStatusBar(QW.QStatusBar):
    def __init__(self, parent: QW.QWidget = None):
        super().__init__(parent)

        self.state_label = QW.QLabel()
        self.path_label = QW.QLabel()
        self.export_label = QW.QLabel()

        self.export_widget = QW.QWidget()
        export_layout = QW.QHBoxLayout()
        export_layout.setAlignment(QC.Qt.AlignmentFlag.AlignHCenter)
        export_layout.setContentsMargins(0, 0, 0, 0)
        self.export_spinner = WaitingSpinner(
            self.export_widget,
            False,
            radius=4,
            roundness=0,
            lines=25,
            line_length=4,
            line_width=2,
            fade=100,
            speed=3.1415 / 4,
            color=QG.QColor("#0671D5"),
        )

        export_layout.addWidget(self.export_label)
        export_layout.addWidget(self.export_spinner)
        self.export_widget.setLayout(export_layout)

        if parent is not None:
            self.setFont(parent.font())

        self.addWidget(self.state_label)
        self.addWidget(self.path_label)
        self.addWidget(self.export_widget)

    def set_state_label(self, state_name: str):
        """Set the state label text and visibility.

        Args:
            state_name: The state name to set.
        """
        if state_name != "":
            self.state_label.setVisible(True)
            self.state_label.setText(state_name)
        else:
            self.state_label.setVisible(False)

    def set_path_label(self, path: str):
        """Set the path label text and visibility.

        Args:
            path: The path to set.
        """
        if path and path != "":
            self.path_label.setVisible(True)
            self.path_label.setText(path)
        else:
            self.path_label.setVisible(False)

    def set_export_label(self, export: str):
        """Set the export label text and spinner visibility.

        Args:
            export: The export label text to set (path and formats).
        """
        if export and export != "":
            self.export_label.setText(export)
            self.export_spinner.start()
            self.export_widget.setVisible(True)
        else:
            self.export_widget.setVisible(False)
            self.export_spinner.stop()
