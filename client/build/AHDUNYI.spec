# -*- mode: python ; coding: utf-8 -*-
"""
AHDUNYI Terminal PRO - PyInstaller spec (Monorepo layout).

Packs:
  - client/desktop/main.py   (entry point)
  - client/web/dist/**       (compiled Vue frontend)
  - shared/**                (shared schemas/constants)
  - config.json              (optional, repo root)

Author : AHDUNYI
Version: 9.0.0
"""

import os
import sys
from pathlib import Path

SPEC_DIR   = Path(SPECPATH)        # noqa: F821  client/build/
CLIENT_DIR = SPEC_DIR.parent       # client/
PROJECT    = CLIENT_DIR.parent     # repo root

print("[SPEC] repo root   : " + str(PROJECT))
print("[SPEC] client dir  : " + str(CLIENT_DIR))
print("[SPEC] python      : " + sys.executable)

MAIN = str(CLIENT_DIR / "desktop" / "main.py")
assert os.path.exists(MAIN), "Entry point not found: " + MAIN

# Data files
datas = []

WEB_DIST = CLIENT_DIR / "web" / "dist"
if WEB_DIST.exists():
    datas.append((str(WEB_DIST), "client/web/dist"))
    print("[SPEC] client/web/dist included")
else:
    print("[WARN] client/web/dist missing - run npm run build first")

CFG = PROJECT / "config.json"
if CFG.exists():
    datas.append((str(CFG), "."))
    print("[SPEC] config.json included")

SHARED = PROJECT / "shared"
if SHARED.exists():
    datas.append((str(SHARED), "shared"))
    print("[SPEC] shared/ included")

hiddenimports = [
    "PyQt6", "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
    "PyQt6.QtWebChannel", "PyQt6.QtWebEngineWidgets",
    "PyQt6.QtWebEngineCore", "PyQt6.sip",
    "psutil", "uiautomation", "comtypes", "comtypes.client",
    "requests", "urllib3", "urllib3.util.retry", "cachetools",
    "client.desktop.main", "client.desktop.config.settings",
    "client.desktop.utils.file_helper", "client.desktop.utils.network_client",
    "client.desktop.app.bridge.web_channel",
    "client.desktop.app.core.room_monitor",
    "client.desktop.app.ui.login_window", "client.desktop.app.ui.main_window",
    "shared.constants.api_paths",
    "shared.schemas.token", "shared.schemas.audit",
    "shared.patterns.room_id",
]

excludes = [
    "tkinter", "unittest", "test", "pytest", "doctest",
    "numpy", "pandas", "matplotlib", "scipy", "sklearn",
    "torch", "tensorflow", "keras", "PIL", "cv2",
    "setuptools", "pip", "wheel", "distutils",
]

a = Analysis(        # noqa: F821
    [MAIN],
    pathex=[str(PROJECT), str(PROJECT / "shared")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)  # noqa: F821

exe = EXE(            # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AHDUNYI_Terminal_PRO",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(       # noqa: F821
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AHDUNYI_Terminal_PRO",
)

print("[SPEC] done - hidden imports: " + str(len(hiddenimports)))
print("[SPEC] done - datas         : " + str(len(datas)))
