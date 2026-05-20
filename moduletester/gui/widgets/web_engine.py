from __future__ import annotations

from typing import Optional

import qtpy.QtWebEngineCore as QWEBC
import qtpy.QtWebEngineWidgets as QWEB
from qtpy.QtWidgets import QAction, QMenu


class UrlBloquer(QWEBC.QWebEngineUrlRequestInterceptor):
    """Simple Url blocker for QWebEngineView."""

    def interceptRequest(self, info: QWEBC.QWebEngineUrlRequestInfo) -> None:
        """Intercept the request and block it if it is a url.

        Args:
            info: Request info.
        """
        scheme = info.requestUrl().scheme()
        navigation_type = info.navigationType()
        ressource_type = info.resourceType()

        block = not (
            (scheme == "data")
            or (
                navigation_type
                == QWEBC.QWebEngineUrlRequestInfo.NavigationType.NavigationTypeLink
                and ressource_type
                == QWEBC.QWebEngineUrlRequestInfo.ResourceType.ResourceTypeImage
            )
        )

        return info.block(block)


class SimpleWebViewer(QWEB.QWebEngineView):  # type: ignore
    """Simplified QWebEngineView web viewer.

    Args:
        web_actions: List of QAction or QWebEnginePage.WebAction to add to the context
         menu.
        *arhs: Arguments to pass to the parent QWebEngineView class.
    """

    def __init__(
        self,
        *args,
        web_actions: Optional[list[QAction | QWEB.QWebEnginePage.WebAction]] = None,  # type: ignore
    ):
        super().__init__(*args)
        self.protect_settings()
        self.protect_profile()

        self.menu = self.setup_menu(web_actions or [])

    def protect_settings(self):
        """Creates new settings for the QWebEngineView. These settings are meant to
        protect the user from malicious content."""
        WebAttribute = QWEB.QWebEngineSettings.WebAttribute  # type: ignore
        new_settings = {
            WebAttribute.AutoLoadImages: True,
            WebAttribute.JavascriptEnabled: False,
            WebAttribute.JavascriptCanOpenWindows: False,
            WebAttribute.JavascriptCanAccessClipboard: False,
            WebAttribute.LinksIncludedInFocusChain: False,
            WebAttribute.LocalStorageEnabled: False,
            WebAttribute.LocalContentCanAccessRemoteUrls: False,
            WebAttribute.XSSAuditingEnabled: True,
            WebAttribute.SpatialNavigationEnabled: False,
            WebAttribute.LocalContentCanAccessFileUrls: False,
            WebAttribute.HyperlinkAuditingEnabled: False,
            WebAttribute.ScrollAnimatorEnabled: False,
            WebAttribute.ErrorPageEnabled: False,
            WebAttribute.PluginsEnabled: False,
            WebAttribute.FullScreenSupportEnabled: False,
            WebAttribute.ScreenCaptureEnabled: False,
            WebAttribute.WebGLEnabled: True,
            WebAttribute.Accelerated2dCanvasEnabled: True,
            WebAttribute.AutoLoadIconsForPage: False,
            WebAttribute.TouchIconsEnabled: False,
            WebAttribute.FocusOnNavigationEnabled: False,
            WebAttribute.PrintElementBackgrounds: True,
            WebAttribute.AllowRunningInsecureContent: False,
            WebAttribute.AllowGeolocationOnInsecureOrigins: False,
            WebAttribute.AllowWindowActivationFromJavaScript: False,
            WebAttribute.ShowScrollBars: True,
            WebAttribute.PlaybackRequiresUserGesture: True,
            WebAttribute.WebRTCPublicInterfacesOnly: True,
            WebAttribute.JavascriptCanPaste: False,
            WebAttribute.DnsPrefetchEnabled: False,
            WebAttribute.PdfViewerEnabled: True,
        }

        settings = self.page().settings()
        for setting, value in new_settings.items():
            settings.setAttribute(setting, value)

    def protect_profile(self):
        """Protect the profile of the QWebEngineView. This is done by setting a
        UrlRequestInterceptor that will block any request that is not a data url or a
        link to an image.
        """
        self.page().profile().setUrlRequestInterceptor(UrlBloquer(self))

    def setup_menu(
        self,
        web_actions: list[QWEB.QWebEnginePage.WebAction],  # type: ignore
    ) -> QMenu:
        """Setup the context menu.

        Args:
            web_actions: List of QAction or QWebEnginePage.WebAction to add to the
             context menu.

        Returns:
            The context menu.
        """
        menu = QMenu()
        for action in web_actions:
            if isinstance(action, QWEB.QWebEnginePage.WebAction):  # type: ignore
                action = self.pageAction(action)
            menu.addAction(action)
        return menu

    def contextMenuEvent(self, event):
        """Show the context menu.

        Args:
            event: Context menu event to get the position from.
        """
        self.menu.exec_(event.globalPos())
