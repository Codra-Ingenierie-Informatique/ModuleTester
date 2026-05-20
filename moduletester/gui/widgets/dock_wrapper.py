from __future__ import annotations

from typing import Generic, Optional, TypeVar

import qtpy.QtCore as QC
import qtpy.QtWidgets as QW

from moduletester.gui.widgets.dockable_widget import DockableQWidget

STR_TO_DOCK_AREA: dict[str, QC.Qt.DockWidgetArea] = {
    "left": QC.Qt.DockWidgetArea.LeftDockWidgetArea,
    "right": QC.Qt.DockWidgetArea.RightDockWidgetArea,
    "top": QC.Qt.DockWidgetArea.TopDockWidgetArea,
    "bottom": QC.Qt.DockWidgetArea.BottomDockWidgetArea,
}

AnyDockableWidget = TypeVar("AnyDockableWidget", bound=DockableQWidget)


class QDockWrapper(QW.QDockWidget, Generic[AnyDockableWidget]):
    def __init__(
        self,
        parent: Optional[QW.QWidget],
        widget: AnyDockableWidget,
        title: Optional[str] = None,
    ) -> None:
        """Wrapper for DockableQWidget to transform it into a usable QDockWidget.

        Args:
            parent: Parent widget. Defaults to None.
            widget: DockableQWidget to wrap into a QDockWidget.
            title: Dock widget title. If None, will default to the given widget title.
             Defaults to None.
        """
        widget_title_label: QW.QLabel | None = getattr(widget, "title_label", None)
        if widget_title_label is not None:
            widget_title_label.hide()
        title = title or widget_title_label.text() if widget_title_label else ""

        super().__init__(title, parent)
        self.setWidget(widget)
        self.setFeatures(QW.QDockWidget.DockWidgetFeature.AllDockWidgetFeatures)
        # self.setFloating(False)
        # self.setContextMenuPolicy(QC.Qt.ContextMenuPolicy.CustomContextMenu)

    @staticmethod
    def get_area_from_str(area: str) -> QC.Qt.DockWidgetArea:
        """Get the QDockWidgetArea from a string.

        Args:
            area: String representation of the dock area.

        Returns:
            The QDockWidgetArea corresponding to the given string.
        """
        return STR_TO_DOCK_AREA.get(area, QC.Qt.DockWidgetArea.RightDockWidgetArea)
