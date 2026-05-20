from typing import Optional

import qtpy.QtWidgets as QW

from moduletester.gui.widgets.abstract_widget import AbstractQWidget


class DockableQWidget(AbstractQWidget):
    def __init__(self, parent: Optional[QW.QWidget], title: str = "") -> None:
        """Normal QWidget with a title and a label. This class is meant to be used as a
        base class for optionnally dockable widgets by being wrapped into a
        QDockWrapper object.

        Args:
            parent: Parent widget. Defaults to None.
            title: Widget title. Defaults to "".
        """
        super().__init__(parent)
        self.title = title
        self.title_label = QW.QLabel(self.title)
