# -*- coding: utf-8 -*-
"""
Main application window - PyQt6 WebEngine container.

Loads the compiled Vue frontend from client/web/dist/index.html and
exposes AppBridge via QWebChannel so Vue communicates with Python
without any HTTP server.

Token injection strategy
------------------------
The Python LoginWindow authenticates BEFORE the Vue page loads.
QWebChannel signals fired before page-load are missed by JS listeners.
Instead, on ``loadFinished`` we inject the full login response directly
into ``localStorage`` via ``runJavaScript``, then dispatch a custom
``ahdunyi:token-ready`` event so Vue can react immediately.

Author : AHDUNYI
Version: 9.0.0
"""

import json
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
    """Extract a field from token_info, checking user sub-dict then top-level."""
    user_sub = token_info.get("user") or {}
    return user_sub.get(field) or token_info.get(field) or default


class MainWindow(QMainWindow):
    """Primary application window hosting the Vue WebEngine frontend."""

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
        """Return the AppBridge instance."""
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

        # Inject token into localStorage once the page has fully loaded
        self._view.loadFinished.connect(self._on_load_finished)

        # Load frontend
        index_html = self._settings.web_client_dist / "index.html"
        if index_html.exists():
            self._view.load(QUrl.fromLocalFile(str(index_html)))
            logger.info("WebEngine loading: %s", index_html)
        else:
            self._show_build_error(self._settings.web_client_dist)

    def _on_load_finished(self, ok: bool) -> None:
        """Called by WebEngine after every page load.

        Injects the JWT token and user info directly into localStorage so
        the Vue app can read them synchronously before any route guard runs.
        Also dispatches ``ahdunyi:token-ready`` so Vue can react instantly.

        Args:
            ok: True if the page loaded successfully.
        """
        if not ok:
            logger.warning("WebEngine page load failed.")
            return

        token = self._token_info.get("access_token", "")
        user = self._token_info.get("user") or {}
        permissions = self._token_info.get("permissions") or []
        role_meta = self._token_info.get("role_meta") or {}
        role = user.get("role") or self._token_info.get("role", "")

        if not token:
            logger.warning("_on_load_finished: no access_token in token_info")
            return

        # Serialise payloads for JS injection
        token_json = json.dumps(token)
        user_json = json.dumps(user)
        perm_data = json.dumps({
            "role": role,
            "permissions": permissions,
            "role_meta": role_meta,
        })

        js = f"""
(function() {{
  try {{
    localStorage.setItem('ahdunyi_access_token', {token_json});
    localStorage.setItem('ahdunyi_user_info',   {user_json});
    localStorage.setItem('ahdunyi_permissions', {perm_data});
    console.info('[PyBridge] Token injected into localStorage for user: ' +
      ({user_json}.username || '?'));
    window.dispatchEvent(new CustomEvent('ahdunyi:token-ready', {{
      detail: {{
        access_token: {token_json},
        user: {user_json},
        permissions: {perm_data}
      }}
    }}));
  }} catch(e) {{
    console.error('[PyBridge] Token injection failed:', e);
  }}
}})();
"""
        self._view.page().runJavaScript(js)
        logger.info(
            "Token injected into WebEngine localStorage: user=%s role=%s",
            user.get("username", "?"),
            role,
        )

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
