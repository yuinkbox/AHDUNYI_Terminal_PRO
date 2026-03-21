# -*- coding: utf-8 -*-
"""
Main application window - PyQt6 WebEngine container.

Loads the compiled Vue frontend from client/web/dist/index.html and
exposes AppBridge via QWebChannel so Vue communicates with Python
without any HTTP server.

Author : AHDUNYI
Version: 9.0.0
"""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget

from client.desktop.app.bridge.web_channel import AppBridge
from client.desktop.config.settings import AppSettings

logger = logging.getLogger(__name__)


def _extract_user_field(token_info: dict, field: str, default: str = "") -> str:
    """Extract a field from token_info, checking both top-level and user sub-dict.

    Server response structure::

        {
            "access_token": "...",
            "user": {"username": "...", "role": "...", ...},
            "permissions": [...],
            "role_meta": {...}
        }

    Args:
        token_info: The full login response dict.
        field:      Field name to look up (e.g. ``"username"``).
        default:    Fallback value if field is not found.

    Returns:
        String value or *default*.
    """
    user_sub = token_info.get("user") or {}
    return (
        user_sub.get(field)
        or token_info.get(field)
        or default
    )


class MainWindow(QMainWindow):
    """Primary application window hosting the Vue WebEngine frontend.

    Args:
        settings:   Application settings dataclass.
        token_info: Full login response dict from the Python login step.
        parent:     Optional parent widget.
    """

    def __init__(
        self,
        settings: AppSettings,
        token_info: dict,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings
        self._token_info = token_info

        self._bridge = AppBridge(parent=self)
        self._bridge.update_token_info(token_info)

        self._setup_window()
        self._setup_webengine()

        username = _extract_user_field(token_info, "username", "?")
        role = _extract_user_field(token_info, "role", "?")
        logger.info("MainWindow ready: user=%s role=%s", username, role)

    @property
    def bridge(self) -> AppBridge:
        """Return the AppBridge instance for wiring external data sources."""
        return self._bridge

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        username = _extract_user_field(self._token_info, "username", "user")
        role = _extract_user_field(self._token_info, "role", "UNKNOWN")
        self.setWindowTitle(f"AHDUNYI Terminal PRO  -  {username}  ({role})")
        self.resize(self._settings.gui.window_width, self._settings.gui.window_height)
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    def _setup_webengine(self) -> None:
        self._view = QWebEngineView(self)
        self.setCentralWidget(self._view)

        # Register bridge with QWebChannel
        channel = QWebChannel(self._view.page())
        channel.registerObject("bridge", self._bridge)
        self._view.page().setWebChannel(channel)

        # WebEngine settings
        ws = self._view.page().settings()
        ws.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        ws.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        ws.setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
        )

        # Load frontend
        index_html = self._settings.web_client_dist / "index.html"
        if index_html.exists():
            self._view.load(QUrl.fromLocalFile(str(index_html)))
            logger.info("WebEngine loading: %s", index_html)
        else:
            self._show_build_error(self._settings.web_client_dist)

    def _show_build_error(self, dist_path: Path) -> None:
        logger.error("Frontend dist not found: %s", dist_path)
        self._view.setHtml(
            '<!DOCTYPE html><html lang="en">'
            '<head><meta charset="utf-8">'
            "<style>"
            "body{margin:0;background:#0d0f1a;color:#e2e8f0;"
            "font-family:Consolas,monospace;"
            "display:flex;align-items:center;justify-content:center;"
            "height:100vh;flex-direction:column;gap:16px}"
            "h2{color:#f87171}"
            "code{background:#1e2440;padding:4px 10px;border-radius:6px;color:#4f8ef7}"
            "</style></head>"
            "<body>"
            "<h2>Frontend not built</h2>"
            "<p>Build the Vue frontend first:</p>"
            "<code>cd client/web &amp;&amp; npm install &amp;&amp; npm run build</code>"
            "<p>Or use the automated build script:</p>"
            "<code>python client/build/build.py</code>"
            "</body></html>"
        )

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Close AHDUNYI Terminal PRO?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("MainWindow closing.")
            event.accept()
        else:
            event.ignore()
