# -*- coding: utf-8 -*-
"""
RoomMonitor - UI Automation room-ID probe.

Monitors a target Windows process via UIAutomation and extracts the
current live-room ID from its window tree.  Runs as a daemon thread so
the main thread (GUI) is never blocked.

Author : AHDUNYI
Version: 9.0.0
"""

import re
import time
import threading
from typing import Callable, Optional

import psutil

try:
    import uiautomation as auto  # type: ignore
    WINDOWS_AVAILABLE: bool = True
except ImportError:
    auto = None  # type: ignore
    WINDOWS_AVAILABLE = False

import logging

logger = logging.getLogger(__name__)


class RoomMonitor(threading.Thread):
    """Daemon thread that polls a target process and extracts its room ID.

    Args:
        callback: Optional callable invoked with the new room-ID string
            (or ``None`` when the room is exited) on every state change.
        heartbeat_interval: Seconds between each poll cycle.  Default 2.
        max_depth: Maximum UI-tree traversal depth.  Default 8.
    """

    # Target process name (lower-cased for comparison)
    TARGET_PROCESS_NAME: str = "small_dimple.exe"

    # Matches 3-10 digit IDs, optionally prefixed with a pretty-number marker
    ID_PATTERN: re.Pattern = re.compile(r'(?:\u9765\s*|ID[::\uff1a]\s*)?(\d{3,10})')

    def __init__(
        self,
        callback: Optional[Callable[[Optional[str]], None]] = None,
        heartbeat_interval: float = 2.0,
        max_depth: int = 8,
    ) -> None:
        super().__init__(daemon=True)
        self.callback = callback
        self.heartbeat_interval = heartbeat_interval
        self.max_depth = max_depth

        self._running: bool = False
        self._current_room_id: Optional[str] = None
        self._target_pid: Optional[int] = None
        self.stats: dict = {
            "total_scans": 0,
            "room_changes": 0,
            "last_error": None,
        }

        logger.info(
            "RoomMonitor initialised: interval=%.1fs, depth=%d",
            heartbeat_interval,
            max_depth,
        )

    # ------------------------------------------------------------------
    # Thread lifecycle
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Thread entry point.  Blocks until :meth:`stop` is called."""
        if WINDOWS_AVAILABLE:
            # Initialise COM for this thread
            _initialiser = auto.UIAutomationInitializerInThread()  # noqa: F841

        self._running = True
        logger.info("RoomMonitor thread started (target: %s)", self.TARGET_PROCESS_NAME)

        while self._running:
            try:
                self._monitor_cycle()
                time.sleep(self.heartbeat_interval)
            except Exception as exc:  # pylint: disable=broad-except
                logger.error("Monitor cycle error: %s", exc)
                self.stats["last_error"] = str(exc)
                time.sleep(self.heartbeat_interval * 2)

        logger.info("RoomMonitor thread stopped.")

    def stop(self) -> None:
        """Signal the thread to exit on its next cycle."""
        self._running = False

    # ------------------------------------------------------------------
    # Internal logic
    # ------------------------------------------------------------------

    def _monitor_cycle(self) -> None:
        """Single poll iteration: find PID -> scan UI tree -> emit changes."""
        self.stats["total_scans"] += 1

        target_pid: Optional[int] = None
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["name"].lower() == self.TARGET_PROCESS_NAME.lower():
                    target_pid = proc.info["pid"]
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if target_pid is None:
            self._target_pid = None
            self._handle_room_id_change(None)
            return

        self._target_pid = target_pid

        if not WINDOWS_AVAILABLE:
            return

        root = auto.GetRootControl()
        current_found_id: Optional[str] = None

        for window in root.GetChildren():
            try:
                if window.ProcessId != target_pid:
                    continue

                def _quick_find(control: object, depth: int = 0) -> None:  # noqa: E306
                    nonlocal current_found_id
                    if depth > self.max_depth or current_found_id:
                        return
                    try:
                        for element in control.GetChildren():  # type: ignore[attr-defined]
                            name: str = element.Name or ""
                            if name and "." not in name:
                                match = self.ID_PATTERN.search(name)
                                if match:
                                    potential_id = match.group(1)
                                    # Accept 4+ digit IDs or short IDs preceded
                                    # by the pretty-number keyword (\u9765)
                                    if "\u9765" in name or len(potential_id) >= 4:
                                        current_found_id = potential_id
                                        return
                            _quick_find(element, depth + 1)
                    except Exception:  # pylint: disable=broad-except
                        pass

                _quick_find(window)
                if current_found_id:
                    break
            except Exception:  # pylint: disable=broad-except
                continue

        self._handle_room_id_change(current_found_id)

    def _handle_room_id_change(self, new_id: Optional[str]) -> None:
        """Emit a callback when the detected room ID changes."""
        if new_id == self._current_room_id:
            return

        self._current_room_id = new_id

        if new_id:
            self.stats["room_changes"] += 1
            label = "[pretty]" if len(new_id) < 6 else ""
            logger.info("Room captured: %s %s", new_id, label)
        else:
            logger.info("Room exited.")

        if self.callback:
            try:
                self.callback(new_id)
            except Exception as exc:  # pylint: disable=broad-except
                logger.error("Callback error: %s", exc)

    # ------------------------------------------------------------------
    # Public accessors (used by bridge layer)
    # ------------------------------------------------------------------

    def get_current_room_id(self) -> Optional[str]:
        """Return the most recently detected room ID, or None."""
        return self._current_room_id

    def get_stats(self) -> dict:
        """Return a copy of the internal statistics dictionary."""
        return self.stats.copy()

    def is_running(self) -> bool:
        """Return True if the monitor thread is active."""
        return self._running

    def is_target_running(self) -> bool:
        """Return True if the target process is currently detected."""
        return self._target_pid is not None


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_room_monitor(
    callback: Optional[Callable[[Optional[str]], None]] = None,
    target_process: Optional[str] = None,  # kept for API compat
    heartbeat_interval: float = 2.0,
    max_depth: int = 8,
    room_id_pattern: Optional[str] = None,  # kept for API compat
) -> Optional[RoomMonitor]:
    """Instantiate a :class:`RoomMonitor`.

    Returns ``None`` on non-Windows platforms where UIAutomation is
    unavailable.

    Args:
        callback: State-change callback.
        target_process: Target process name (informational; the class
            constant is used for matching).
        heartbeat_interval: Seconds between polls.
        max_depth: UI-tree traversal depth limit.
        room_id_pattern: Regex pattern override (informational).

    Returns:
        A :class:`RoomMonitor` instance, or ``None``.
    """
    if not WINDOWS_AVAILABLE:
        logger.warning("Windows UIAutomation unavailable; RoomMonitor disabled.")
        return None

    monitor = RoomMonitor(
        callback=callback,
        heartbeat_interval=heartbeat_interval,
        max_depth=max_depth,
    )
    logger.info(
        "RoomMonitor created: target=%s, interval=%.1f, depth=%d",
        target_process or monitor.TARGET_PROCESS_NAME,
        heartbeat_interval,
        max_depth,
    )
    return monitor
