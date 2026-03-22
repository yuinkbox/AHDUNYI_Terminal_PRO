# -*- coding: utf-8 -*-
"""
QWebChannel bridge - exposes Python state to the Vue frontend.

Protocol
--------
* JS calls bridge.getRoomId()        -> Python returns current room ID.
* JS calls bridge.getSystemStatus()  -> Python returns a JSON string.
* Python emits roomIdChanged(str)    -> JS listener updates UI.
* Python emits systemStatusChanged(str) -> JS listener updates UI.

Author : AHDUNYI
Version: 9.0.0
"""

import json
from typing import Optional
import logging

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)


class AppBridge(QObject):
    """Qt object exposed to JavaScript via QWebChannel.

    All public pyqtSlot methods are callable from Vue components.
    All pyqtSignal signals can be subscribed to from JavaScript.

    Args:
        parent: Optional QObject parent.
    """

    # Signals emitted to JavaScript
    roomIdChanged       = pyqtSignal(str, name="roomIdChanged")
    roomInfoChanged     = pyqtSignal(str, name="roomInfoChanged")
    systemStatusChanged = pyqtSignal(str, name="systemStatusChanged")
    tokenInfoChanged    = pyqtSignal(str, name="tokenInfoChanged")

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._room_id: Optional[str] = None
        self._user_id: Optional[str] = None
        self._token_info: dict = {}
        self._monitor_running: bool = False

    # ------------------------------------------------------------------
    # Slots callable from JavaScript
    # ------------------------------------------------------------------

    @pyqtSlot(result=str)
    def getRoomId(self) -> str:
        """Return the currently monitored room ID, or empty string."""
        return self._room_id or ""

    @pyqtSlot(result=str)
    def getRoomInfo(self) -> str:
        """Return JSON with both room_id and user_id."""
        return json.dumps({
            "room_id": self._room_id or "",
            "user_id": self._user_id or "",
        }, ensure_ascii=False)

    @pyqtSlot(result=str)
    def getSystemStatus(self) -> str:
        """Return a JSON-encoded system status snapshot."""
        status = {
            "room_id": self._room_id,
            "monitor_running": self._monitor_running,
            "token_info": self._token_info,
        }
        return json.dumps(status, ensure_ascii=False)

    @pyqtSlot(result=str)
    def getTokenInfo(self) -> str:
        """Return the current login token payload as a JSON string."""
        return json.dumps(self._token_info, ensure_ascii=False)

    @pyqtSlot(str)
    def logFromJS(self, message: str) -> None:
        """Receive a log message forwarded from the Vue console."""
        logger.info("[JS] %s", message)

    @pyqtSlot(bool)
    def setAlwaysOnTop(self, enabled: bool) -> None:
        """Toggle window-stays-on-top flag from JavaScript."""
        win = self.parent()
        if win and hasattr(win, "set_always_on_top"):
            win.set_always_on_top(enabled)
            logger.info("Bridge: alwaysOnTop -> %s", enabled)

    @pyqtSlot(bool)
    def setMiniMode(self, enabled: bool) -> None:
        """Switch between mini-float and normal window size from JavaScript."""
        win = self.parent()
        if win and hasattr(win, "set_mini_mode"):
            win.set_mini_mode(enabled)
            logger.info("Bridge: miniMode -> %s", enabled)

    # ------------------------------------------------------------------
    # Python-side setters (called by main application logic)
    # ------------------------------------------------------------------

    def update_room_id(self, room_id: Optional[str]) -> None:
        """Backward-compat: update room_id only."""
        self._room_id = room_id
        self.roomIdChanged.emit(room_id or "")
        logger.debug("Bridge: roomIdChanged -> %s", room_id)

    def update_room_info(
        self, room_id: Optional[str], user_id: Optional[str]
    ) -> None:
        """Update both room_id and user_id, notify JavaScript."""
        self._room_id = room_id
        self._user_id = user_id
        self.roomIdChanged.emit(room_id or "")
        info = json.dumps({
            "room_id": room_id or "",
            "user_id": user_id or "",
        }, ensure_ascii=False)
        self.roomInfoChanged.emit(info)
        logger.debug("Bridge: roomInfoChanged -> room=%s user=%s", room_id, user_id)

    def update_token_info(self, token_info: dict) -> None:
        """Store login token payload and notify JavaScript.

        Args:
            token_info: Decoded JWT payload dict from the login response.
        """
        self._token_info = token_info
        self.tokenInfoChanged.emit(
            json.dumps(token_info, ensure_ascii=False)
        )
        logger.debug(
            "Bridge: tokenInfoChanged -> user=%s role=%s",
            token_info.get("username"),
            token_info.get("role"),
        )

    def update_monitor_status(self, running: bool) -> None:
        """Update the RoomMonitor running state and push to JavaScript.

        Args:
            running: True if the monitor thread is active.
        """
        self._monitor_running = running
        self.systemStatusChanged.emit(self.getSystemStatus())
        logger.debug("Bridge: monitorRunning -> %s", running)
