# -*- coding: utf-8 -*-
"""
AHDUNYI Terminal PRO - unified application entry point.

Startup sequence
----------------
1. Load configuration (config.json or built-in defaults).
2. Initialise logging (UTF-8 safe, GBK-proof).
3. Check runtime dependencies.
4. Launch GUI event loop:
   a. Show LoginWindow.
   b. On login_success -> hide login, show MainWindow (WebEngine).
   c. Start RoomMonitor, wire callbacks to AppBridge.
5. On GUI exit: stop RoomMonitor, flush logs.

Author : AHDUNYI
Version: 9.0.0
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Monorepo root: client/desktop/ -> client/ -> repo_root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from client.desktop.config.settings import ConfigManager, AppSettings
from client.desktop.utils.file_helper import setup_logging

logger = logging.getLogger(__name__)


def _try_import(module: str) -> bool:
    """Return True if module can be imported without error."""
    try:
        __import__(module)
        return True
    except ImportError:
        return False


def _check_dependencies() -> list:
    """Return a list of missing package display-names."""
    required = [
        ("psutil",          ["psutil"]),
        ("uiautomation",    ["uiautomation"]),
        ("PyQt6",           ["PyQt6.QtWidgets"]),
        ("PyQt6-WebEngine", ["PyQt6.QtWebEngineWidgets"]),
        ("requests",        ["requests"]),
    ]
    missing = []
    for display, imports in required:
        if not any(_try_import(m) for m in imports):
            missing.append(display)
    return missing


def _start_room_monitor(settings: AppSettings, bridge) -> Optional[object]:
    """Start RoomMonitor and wire its callback to the AppBridge.

    Args:
        settings: Application settings.
        bridge: AppBridge instance to receive room-ID updates.

    Returns:
        Running RoomMonitor, or None on failure.
    """
    try:
        from client.desktop.app.core.room_monitor import create_room_monitor

        def _on_room_change(room_id: Optional[str]) -> None:
            bridge.update_room_id(room_id)

        monitor = create_room_monitor(
            callback=_on_room_change,
            target_process=settings.room_monitor.target_process,
            heartbeat_interval=settings.room_monitor.heartbeat_interval,
            max_depth=settings.room_monitor.max_search_depth,
        )
        if monitor:
            monitor.start()
            bridge.update_monitor_status(True)
            logger.info("RoomMonitor started.")
        return monitor
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("RoomMonitor startup failed: %s", exc)
        return None


def _run_gui(settings: AppSettings) -> int:
    """Create QApplication and run the main event loop.

    Returns:
        Process exit code.
    """
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtGui import QPalette, QColor

    app = QApplication(sys.argv)
    app.setApplicationName("AHDUNYI Terminal PRO")
    app.setOrganizationName("AHDUNYI")

    # Global dark palette
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,          QColor("#0d0f1a"))
    pal.setColor(QPalette.ColorRole.WindowText,      QColor("#e2e8f0"))
    pal.setColor(QPalette.ColorRole.Base,            QColor("#13162b"))
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor("#1a1f3a"))
    pal.setColor(QPalette.ColorRole.Text,            QColor("#e2e8f0"))
    pal.setColor(QPalette.ColorRole.Button,          QColor("#13162b"))
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor("#e2e8f0"))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor("#4f8ef7"))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)

    try:
        from client.desktop.app.ui.login_window import LoginWindow
        from client.desktop.app.ui.main_window import MainWindow
    except ImportError as exc:
        logger.error("UI import failed: %s", exc)
        QMessageBox.critical(None, "Startup Error", f"Failed to load UI:\n{exc}")
        return 1

    _main_windows: list = []
    _monitors: list = []

    login_win = LoginWindow(server_url=settings.server.url)

    def _on_login_success(token_info: dict) -> None:
        login_win.hide()
        try:
            main_win = MainWindow(settings=settings, token_info=token_info)
            _main_windows.append(main_win)
            if settings.features.auto_start_monitor:
                mon = _start_room_monitor(settings, main_win.bridge)
                if mon:
                    _monitors.append(mon)
            main_win.show()
            logger.info("MainWindow displayed.")
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed to open MainWindow: %s", exc, exc_info=True)
            QMessageBox.critical(
                None, "Error", f"Could not open main window:\n{exc}"
            )
            login_win.show()

    login_win.login_success.connect(_on_login_success)
    login_win.show()
    logger.info("LoginWindow displayed.")

    exit_code = app.exec()

    for mon in _monitors:
        try:
            mon.stop()
        except Exception:  # pylint: disable=broad-except
            pass
    logger.info("Application exited (code=%d).", exit_code)
    return exit_code


def main() -> int:
    """Application entry point. Returns integer exit code."""
    print("AHDUNYI Terminal PRO  -  starting...")

    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    settings: AppSettings = ConfigManager(config_path).load()

    setup_logging(
        log_dir=Path(settings.paths.logs_directory),
        log_file=settings.logging.file,
        level=settings.logging.level,
        enable_console=settings.debug.enable_console,
    )
    logger.info("Settings loaded: server=%s", settings.server.url)

    missing = _check_dependencies()
    if missing:
        msg = "Missing dependencies: " + ", ".join(missing)
        logger.error(msg)
        print("[ERROR] " + msg)
        print("Run: pip install " + " ".join(missing))
        return 1

    return _run_gui(settings)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python -m client.desktop.main [config_file]")
        sys.exit(0)

    try:
        sys.exit(main())
    except Exception as exc:  # pylint: disable=broad-except
        print("[FATAL] " + str(exc))
        import traceback
        traceback.print_exc()
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            _a = QApplication.instance() or QApplication([])
            QMessageBox.critical(
                None, "Fatal Error",
                "AHDUNYI Terminal PRO encountered a fatal error:\n\n"
                + str(exc)
                + "\n\nPlease check the log file."
            )
        except Exception:  # pylint: disable=broad-except
            pass
        input("Press Enter to exit...")
        sys.exit(1)
