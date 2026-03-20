# -*- coding: utf-8 -*-
"""
File and path utilities.

Provides PyInstaller _MEIPASS-aware path resolution, log-directory
creation, and safe file-read helpers used across the application.

Author : AHDUNYI
Version: 9.0.0
"""

import sys
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def resource_path(relative: str) -> Path:
    """Resolve a path relative to the application resource root.

    Handles both normal execution and PyInstaller one-file bundles where
    resources are extracted to a temporary ``_MEIPASS`` directory.

    Args:
        relative: Path relative to the project/bundle root.

    Returns:
        Absolute Path object.
    """
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        # src/utils/file_helper.py -> project root is three levels up
        base = Path(__file__).parent.parent.parent
    return base / relative


def ensure_directory(path: Path) -> Path:
    """Create *path* (and parents) if it does not exist.

    Args:
        path: Directory path to create.

    Returns:
        The same Path object (for chaining).

    Raises:
        OSError: If the directory cannot be created.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def setup_logging(
    log_dir: Path,
    log_file: str,
    level: str = "INFO",
    enable_console: bool = True,
) -> None:
    """Configure the root logging system.

    Always writes UTF-8 encoded log files to prevent GBK encoding errors
    on Chinese Windows systems.

    Args:
        log_dir: Directory that will contain the log file.
        log_file: File name (not full path) for the rotating log.
        level: Logging level string, e.g. ``"INFO"``.
        enable_console: Whether to add a StreamHandler to stdout.
    """
    ensure_directory(log_dir)
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handlers: list = [
        logging.FileHandler(
            log_dir / log_file,
            encoding="utf-8",   # explicit UTF-8 - prevents GBK UnicodeEncodeError
        )
    ]
    if enable_console:
        stream_handler = logging.StreamHandler()
        # Force UTF-8 on the stream as well
        if hasattr(stream_handler.stream, "reconfigure"):
            try:
                stream_handler.stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
            except Exception:  # pylint: disable=broad-except
                pass
        handlers.append(stream_handler)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=handlers,
        force=True,
    )
    logger.info("Logging initialised: level=%s, file=%s", level, log_dir / log_file)


def read_text(path: Path, encoding: str = "utf-8") -> Optional[str]:
    """Safely read a text file, returning None on any error.

    Args:
        path: File to read.
        encoding: File encoding.  Defaults to ``utf-8``.

    Returns:
        File contents as a string, or None if the file cannot be read.
    """
    try:
        return path.read_text(encoding=encoding)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Cannot read %s: %s", path, exc)
        return None
