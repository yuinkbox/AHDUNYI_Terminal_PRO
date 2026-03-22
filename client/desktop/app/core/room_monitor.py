# -*- coding: utf-8 -*-
"""
RoomMonitor - UI Automation room-ID & user-ID probe.

Monitors a target Windows process via UIAutomation and extracts the
current live-room ID and user ID from its window tree.  Runs as a
daemon thread so the main thread (GUI) is never blocked.

Author : AHDUNYI
Version: 9.1.0
"""

import re
import time
import threading
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Tuple

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
    """Daemon thread that polls a target process and extracts room/user IDs.

    The callback receives ``(room_id, user_id)`` on every state change.
    Either value can be ``None`` when not detected.
    """

    TARGET_PROCESS_NAME: str = "small_dimple.exe"

    # Matches 3-10 digit IDs with optional ID: / ID： / 靓 prefix
    ID_PATTERN: re.Pattern = re.compile(r'(?:\u9765\s*|ID[::\uff1a]\s*)?(\d{3,10})')

    # UI 文本关键词：用于在只能扫到一个节点时区分房间号 / 用户资料 ID
    _ROOM_HINT_TOKENS: Tuple[str, ...] = (
        "\u623f\u95f4",  # 房间
        "\u76f4\u64ad\u95f4",  # 直播间
        "\u76f4\u64ad",  # 直播
        "Live",
        "live",
    )
    _USER_HINT_TOKENS: Tuple[str, ...] = (
        "\u4e3b\u64ad",  # 主播
        "\u7528\u6237",  # 用户
        "\u8fbe\u4eba",  # 达人
        "\u6296\u97f3\u53f7",  # 抖音号
        "UID",
        "uid",
    )
    # 仅出现一个 ID 且深度大于该阈值时，若与上次稳定房间号不同，则视为资料页用户 ID（保留房间号）
    _DEEP_SINGLE_ID_DEPTH: int = 2

    def __init__(
        self,
        callback: Optional[Callable[[Optional[str], Optional[str]], None]] = None,
        heartbeat_interval: float = 2.0,
        max_depth: int = 8,
    ) -> None:
        super().__init__(daemon=True)
        self.callback = callback
        self.heartbeat_interval = heartbeat_interval
        self.max_depth = max_depth

        self._running: bool = False
        self._current_room_id: Optional[str] = None
        self._current_user_id: Optional[str] = None
        self._sticky_room_id: Optional[str] = None
        self._target_pid: Optional[int] = None
        self.stats: dict = {
            "total_scans": 0,
            "room_changes": 0,
            "user_changes": 0,
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
        if WINDOWS_AVAILABLE:
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
        self._running = False

    # ------------------------------------------------------------------
    # Internal logic
    # ------------------------------------------------------------------

    def _monitor_cycle(self) -> None:
        """Single poll: find PID -> scan UI tree -> collect all IDs -> emit."""
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
            self._sticky_room_id = None
            self._handle_info_change(None, None)
            return

        self._target_pid = target_pid

        if not WINDOWS_AVAILABLE:
            return

        root = auto.GetRootControl()
        # (id_value, depth_of_control_where_name_was_read, control_name)
        collected_ids: List[Tuple[str, int, str]] = []

        for window in root.GetChildren():
            try:
                if window.ProcessId != target_pid:
                    continue

                def _collect(control: object, depth: int = 0) -> None:
                    if depth > self.max_depth:
                        return
                    try:
                        for element in control.GetChildren():  # type: ignore[attr-defined]
                            name: str = element.Name or ""
                            if name and "." not in name:
                                match = self.ID_PATTERN.search(name)
                                if match:
                                    potential_id = match.group(1)
                                    if "\u9765" in name or len(potential_id) >= 4:
                                        collected_ids.append((potential_id, depth, name))
                            _collect(element, depth + 1)
                    except Exception:  # pylint: disable=broad-except
                        pass

                _collect(window)
            except Exception:  # pylint: disable=broad-except
                continue

        room_id, user_id = self._classify_collected_ids(collected_ids)
        self._handle_info_change(room_id, user_id)

    def _classify_collected_ids(
        self, collected_ids: List[Tuple[str, int, str]]
    ) -> Tuple[Optional[str], Optional[str]]:
        """Aggregate by id (min depth + name text), then infer room vs user."""
        if not collected_ids:
            return None, None

        agg: Dict[str, List] = defaultdict(lambda: [999, []])  # min_depth, name_parts

        for id_val, depth, name in collected_ids:
            slot = agg[id_val]
            slot[0] = min(slot[0], depth)
            if name:
                slot[1].append(name)

        # Sort unique ids by shallowest occurrence (title / chrome first)
        ranked: List[Tuple[str, int, str]] = [
            (iid, int(meta[0]), "".join(meta[1])) for iid, meta in agg.items()
        ]
        ranked.sort(key=lambda x: x[1])

        if len(ranked) >= 2:
            room_id, user_id = ranked[0][0], ranked[1][0]
            if room_id != user_id:
                self._sticky_room_id = room_id
                return room_id, user_id

        id_val, min_depth, blob = ranked[0]

        def _has_any(tokens: Tuple[str, ...], text: str) -> bool:
            return any(t in text for t in tokens)

        if _has_any(self._ROOM_HINT_TOKENS, blob):
            self._sticky_room_id = id_val
            return id_val, None

        if _has_any(self._USER_HINT_TOKENS, blob):
            sticky = self._sticky_room_id
            return sticky, id_val

        # 资料页常只剩深层用户 ID，避免覆盖标题栏扫到的房间号
        if (
            self._sticky_room_id
            and id_val != self._sticky_room_id
            and min_depth > self._DEEP_SINGLE_ID_DEPTH
        ):
            return self._sticky_room_id, id_val

        # 浅层 lone id：视为房间标题区域
        if min_depth <= self._DEEP_SINGLE_ID_DEPTH:
            self._sticky_room_id = id_val
            return id_val, None

        self._sticky_room_id = id_val
        return id_val, None

    def _handle_info_change(
        self, new_room: Optional[str], new_user: Optional[str]
    ) -> None:
        """Emit callback when either room_id or user_id changes."""
        if new_room == self._current_room_id and new_user == self._current_user_id:
            return

        if new_room != self._current_room_id:
            self._current_room_id = new_room
            self.stats["room_changes"] += 1
            if new_room:
                logger.info("Room captured: %s", new_room)
            else:
                logger.info("Room exited.")

        if new_user != self._current_user_id:
            self._current_user_id = new_user
            self.stats["user_changes"] += 1
            if new_user:
                logger.info("User captured: %s", new_user)

        if self.callback:
            try:
                self.callback(self._current_room_id, self._current_user_id)
            except Exception as exc:  # pylint: disable=broad-except
                logger.error("Callback error: %s", exc)

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

    def get_current_room_id(self) -> Optional[str]:
        return self._current_room_id

    def get_current_user_id(self) -> Optional[str]:
        return self._current_user_id

    def get_stats(self) -> dict:
        return self.stats.copy()

    def is_running(self) -> bool:
        return self._running

    def is_target_running(self) -> bool:
        return self._target_pid is not None


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_room_monitor(
    callback: Optional[Callable[[Optional[str], Optional[str]], None]] = None,
    target_process: Optional[str] = None,
    heartbeat_interval: float = 2.0,
    max_depth: int = 8,
    room_id_pattern: Optional[str] = None,
) -> Optional[RoomMonitor]:
    """Create a RoomMonitor. Returns None on non-Windows platforms."""
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
