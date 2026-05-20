# pylint: disable=missing-class-docstring, missing-function-docstring
# pylint: disable=missing-module-docstring

# guitest: skip

from typing import Optional

from qtpy import QtWidgets as QW
from qtpy.QtWebEngineWidgets import QWebEnginePage  # type: ignore

from moduletester.gui.widgets.web_engine import SimpleWebViewer
from moduletester.model import Test


class TestDescriptionWidget(QW.QWidget):
    """Widget to display the description of a test. Includes a SimpleWebViewer to
    display the HTML description of the test.

    Args:
        parent: Parent widget. Defaults to None.
    """

    def __init__(self, parent: Optional[QW.QWidget] = None):
        super().__init__(parent)
        self.test: Optional[Test] = None

        # Widgets
        self.web_view = SimpleWebViewer(web_actions=[QWebEnginePage.WebAction.Reload])  # type: ignore
        self.web_view.pageAction(QWebEnginePage.WebAction.Reload).triggered.connect(
            self.force_reload
        )

        # Layouts
        self.hlayout = QW.QHBoxLayout(self)
        self.hlayout.addWidget(self.web_view)

    def force_reload(self):
        """Force the web view to reload the content."""
        if self.test is not None:
            self.set_item(self.test, use_cached=False)

    def set_item(self, test: Test, use_cached: bool = True):
        """Set the test to display the description of.
        Args:
            test: Test to display the description of.
            use_cached: Whether to use the cached HTML description or not.
             Defaults to True.
        """
        self.test = test
        self.web_view.setHtml(
            test.get_html_description(
                standalone=True, embeded=True, apply_style=True, use_cached=use_cached
            )
        )
