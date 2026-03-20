# -*- coding: utf-8 -*-
"""
Login window - JWT authentication UI.

A self-contained PyQt6 widget that:
  1. Collects username / password.
  2. Fires an HTTP login request in a background QThread.
  3. Emits ``login_success(dict)`` on success so the caller can proceed.

Author : AHDUNYI
Version: 9.0.0
"""

import logging
from typing import Optional

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Background login thread
# ---------------------------------------------------------------------------

class _LoginThread(QThread):
    """Perform the HTTP login call off the main thread.

    Signals:
        success: Emitted with the decoded token payload on HTTP 200.
        failure: Emitted with a user-facing error string on any error.
    """

    success: pyqtSignal = pyqtSignal(dict)
    failure: pyqtSignal = pyqtSignal(str)

    def __init__(self, server_url: str, username: str, password: str) -> None:
        super().__init__()
        self._server_url = server_url.rstrip("/")
        self._username = username
        self._password = password

    def run(self) -> None:  # noqa: D102
        try:
            import requests  # local import keeps the module importable without requests

            resp = requests.post(
                f"{self._server_url}/api/auth/login",
                json={"username": self._username, "password": self._password},
                timeout=10,
            )
            if resp.status_code == 200:
                self.success.emit(resp.json())
            elif resp.status_code == 401:
                self.failure.emit("Username or password incorrect.")
            elif resp.status_code == 403:
                self.failure.emit("Account is disabled. Contact your administrator.")
            else:
                self.failure.emit(f"Server error ({resp.status_code}).")
        except requests.exceptions.ConnectionError:
            self.failure.emit(
                f"Cannot connect to server:\n{self._server_url}\n"
                "Please check network or server status."
            )
        except requests.exceptions.Timeout:
            self.failure.emit("Login request timed out (10 s). Please retry.")
        except Exception as exc:  # pylint: disable=broad-except
            self.failure.emit(f"Login error: {exc}")


# ---------------------------------------------------------------------------
# Login window
# ---------------------------------------------------------------------------

class LoginWindow(QWidget):
    """Standalone login widget.

    Emits ``login_success(token_info)`` on successful authentication.
    The caller is responsible for hiding/showing windows in response.

    Args:
        server_url: Backend origin, e.g. ``http://127.0.0.1:8000``.
        parent: Optional parent widget.
    """

    login_success: pyqtSignal = pyqtSignal(dict)

    # Colour palette
    _C_BG      = "#0d0f1a"
    _C_CARD    = "#13162b"
    _C_ACCENT  = "#4f8ef7"
    _C_ACCENT2 = "#6ba3ff"
    _C_TEXT    = "#e2e8f0"
    _C_MUTED   = "#64748b"
    _C_BORDER  = "#1e2440"
    _C_ERROR   = "#f87171"
    _C_OK      = "#4ade80"
    _C_INPUT   = "#1a1f3a"

    def __init__(self, server_url: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._server_url = server_url
        self._thread: Optional[_LoginThread] = None
        self._build_window()
        self._build_ui()
        self._apply_styles()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_window(self) -> None:
        self.setWindowTitle("AHDUNYI Terminal PRO  -  Login")
        self.setFixedSize(440, 540)
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint
        )
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2,
        )

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        outer = QWidget()
        outer.setObjectName("outer")
        root.addWidget(outer)

        ol = QVBoxLayout(outer)
        ol.setContentsMargins(44, 52, 44, 36)
        ol.setSpacing(0)
        ol.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Brand
        brand = QLabel("AHDUNYI")
        brand.setObjectName("brand")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ol.addWidget(brand)

        sub = QLabel("Terminal PRO")
        sub.setObjectName("sub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ol.addWidget(sub)
        ol.addSpacing(40)

        # Card
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 28, 28, 28)
        cl.setSpacing(14)
        ol.addWidget(card)

        title = QLabel("Sign in to your account")
        title.setObjectName("card_title")
        cl.addWidget(title)
        cl.addSpacing(2)

        # Username
        lbl_u = QLabel("Username")
        lbl_u.setObjectName("field_label")
        cl.addWidget(lbl_u)

        self._inp_user = QLineEdit()
        self._inp_user.setObjectName("field_input")
        self._inp_user.setPlaceholderText("Enter username")
        self._inp_user.returnPressed.connect(self._on_login)
        cl.addWidget(self._inp_user)

        # Password
        lbl_p = QLabel("Password")
        lbl_p.setObjectName("field_label")
        cl.addWidget(lbl_p)

        self._inp_pass = QLineEdit()
        self._inp_pass.setObjectName("field_input")
        self._inp_pass.setPlaceholderText("Enter password")
        self._inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_pass.returnPressed.connect(self._on_login)
        cl.addWidget(self._inp_pass)

        cl.addSpacing(6)

        # Login button
        self._btn = QPushButton("Sign In")
        self._btn.setObjectName("btn_login")
        self._btn.setFixedHeight(46)
        self._btn.clicked.connect(self._on_login)
        cl.addWidget(self._btn)

        # Status label
        self._status = QLabel("")
        self._status.setObjectName("status_lbl")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status.setWordWrap(True)
        self._status.hide()
        cl.addWidget(self._status)

        ol.addStretch()

        # Server info footer
        footer = QLabel(f"Server: {self._server_url}")
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ol.addWidget(footer)

    def _apply_styles(self) -> None:
        self.setStyleSheet(f"""
            QWidget#outer {{ background: {self._C_BG}; }}
            LoginWindow   {{ background: {self._C_BG}; }}

            QLabel#brand {{
                color: {self._C_ACCENT};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 34px;
                font-weight: 800;
                letter-spacing: 7px;
            }}
            QLabel#sub {{
                color: {self._C_MUTED};
                font-size: 12px;
                letter-spacing: 3px;
            }}
            QFrame#card {{
                background: {self._C_CARD};
                border: 1px solid {self._C_BORDER};
                border-radius: 14px;
            }}
            QLabel#card_title {{
                color: {self._C_TEXT};
                font-size: 17px;
                font-weight: 600;
            }}
            QLabel#field_label {{
                color: {self._C_MUTED};
                font-size: 12px;
            }}
            QLineEdit#field_input {{
                background: {self._C_INPUT};
                color: {self._C_TEXT};
                border: 1px solid {self._C_BORDER};
                border-radius: 7px;
                padding: 9px 13px;
                font-size: 14px;
            }}
            QLineEdit#field_input:focus {{
                border: 1px solid {self._C_ACCENT};
            }}
            QPushButton#btn_login {{
                background: {self._C_ACCENT};
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 1px;
            }}
            QPushButton#btn_login:hover  {{ background: {self._C_ACCENT2}; }}
            QPushButton#btn_login:pressed {{ background: #3a6fd8; }}
            QPushButton#btn_login:disabled {{
                background: #1e2440;
                color: {self._C_MUTED};
            }}
            QLabel#status_lbl {{ font-size: 13px; padding: 4px; }}
            QLabel#footer     {{ color: {self._C_MUTED}; font-size: 11px; }}
        """)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_login(self) -> None:
        username = self._inp_user.text().strip()
        password = self._inp_pass.text()

        if not username:
            self._show_status("Please enter your username.", self._C_ERROR)
            self._inp_user.setFocus()
            return
        if not password:
            self._show_status("Please enter your password.", self._C_ERROR)
            self._inp_pass.setFocus()
            return

        self._set_loading(True)
        self._show_status("Signing in...", self._C_MUTED)

        self._thread = _LoginThread(self._server_url, username, password)
        self._thread.success.connect(self._on_success)
        self._thread.failure.connect(self._on_failure)
        self._thread.start()

    def _on_success(self, token_info: dict) -> None:
        logger.info(
            "Login success: user=%s role=%s",
            token_info.get("username", "?"),
            token_info.get("role", "?"),
        )
        self._show_status("Login successful. Loading workspace...", self._C_OK)
        self._set_loading(False)
        QTimer.singleShot(600, lambda: self.login_success.emit(token_info))

    def _on_failure(self, msg: str) -> None:
        logger.warning("Login failed: %s", msg)
        self._show_status(msg, self._C_ERROR)
        self._set_loading(False)
        self._inp_pass.clear()
        self._inp_pass.setFocus()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_loading(self, loading: bool) -> None:
        self._btn.setEnabled(not loading)
        self._inp_user.setEnabled(not loading)
        self._inp_pass.setEnabled(not loading)
        self._btn.setText("Signing in..." if loading else "Sign In")

    def _show_status(self, msg: str, colour: str) -> None:
        self._status.setText(msg)
        self._status.setStyleSheet(
            f"font-size: 13px; color: {colour}; padding: 4px;"
        )
        self._status.show()
