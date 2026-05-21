"""Toolbox widget for collapsible sections."""

from __future__ import annotations

from PyQt5.QtWidgets import QWidget
from qtpy import QtWidgets as QW

from moduletester.gui.states.signals import TMSignals
from moduletester.gui.widgets.config_editor import ConfigEditor
from moduletester.gui.widgets.dockable_widget import DockableQWidget


class Toolbox(DockableQWidget):
    """A toolbox widget to hold various tools.

    Args:
        parent: Parent widget. Defaults to None.
        signals: Signals object that contains shared global ModuleTester signals.
        title: Title of the widget. Defaults to "Toolbox".
    """

    def __init__(
        self,
        parent: QWidget | None,
        signals: TMSignals,
        title: str = "Toolbox",
    ) -> None:
        super().__init__(parent, title)
        self.signals = signals

        self.vlayout = QW.QVBoxLayout(self)

        self.tbx = QW.QToolBox()

        self.config_editor = ConfigEditor(
            self,
            self.signals,
            "Config Editor",
        )
        self.tbx.addItem(self.config_editor, "Config editor")

        self.vlayout.addWidget(self.tbx)

        self.setup()
        self.setLayout(self.vlayout)

    def setup(self) -> None:
        """Setup the widget. Empty."""
        pass
