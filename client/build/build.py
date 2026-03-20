# -*- coding: utf-8 -*-
"""
AHDUNYI Terminal PRO - one-click build script.

Steps:
  1. Build Vue frontend (npm run build inside web_client/).
  2. Clean previous PyInstaller artifacts.
  3. Check Python environment.
  4. Run PyInstaller with build/AHDUNYI.spec.
  5. Report output EXE path and size.

GBK-safe: zero emoji, all print() output is pure ASCII/CJK text,
subprocess uses errors='replace'.

Author : AHDUNYI
Version: 9.0.0
"""

import locale
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.resolve()  # client/build/ -> client/ -> repo root
WEB_CLIENT = ROOT / "client" / "web"
DIST_DIR = ROOT / "dist"
BUILD_WORK = ROOT / "client" / "build" / "_pyinstaller"
SPEC_FILE = ROOT / "client" / "build" / "AHDUNYI.spec"


def _sep() -> None:
    print("-" * 60)


def _run(cmd: list, cwd: Path, label: str, timeout: int = 600) -> bool:
    print("[CMD] " + " ".join(str(c) for c in cmd))
    try:
        proc = subprocess.Popen(
            [str(c) for c in cmd],
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for line in proc.stdout:  # type: ignore[union-attr]
            line = line.rstrip()
            if line:
                # Strip non-ASCII chars that crash GBK terminals
                safe = line.encode("gbk", errors="replace").decode("gbk", errors="replace")
                print("    " + safe)
        proc.wait(timeout=timeout)
        if proc.returncode != 0:
            print("[ERR] " + label + " failed (exit " + str(proc.returncode) + ")")
            return False
        print("[OK]  " + label)
        return True
    except subprocess.TimeoutExpired:
        proc.kill()  # type: ignore[possibly-undefined]
        print("[ERR] " + label + " timed out (" + str(timeout) + "s)")
        return False
    except Exception as exc:  # pylint: disable=broad-except
        print("[ERR] " + label + ": " + str(exc))
        return False


def step_build_frontend() -> bool:
    print()
    print("[STEP 1] Building Vue frontend")
    _sep()
    if not WEB_CLIENT.exists():
        print("[ERR] web_client/ not found: " + str(WEB_CLIENT))
        return False
    npm = shutil.which("npm")
    if not npm:
        print("[ERR] npm not found in PATH. Install Node.js >= 18.")
        return False
    print("[OK]  npm: " + npm)
    if not _run([npm, "install"], WEB_CLIENT, "npm install"):
        return False
    if not _run([npm, "run", "build"], WEB_CLIENT, "npm run build"):
        return False
    index = WEB_CLIENT / "dist" / "index.html"
    if not index.exists():
        print("[ERR] dist/index.html missing after build")
        return False
    print("[OK]  dist ready: " + str(index.parent))
    return True


def step_clean() -> None:
    print()
    print("[STEP 2] Cleaning artifacts")
    _sep()
    for d in (DIST_DIR, BUILD_WORK):
        if d.exists():
            shutil.rmtree(d)
            print("[OK]  Removed: " + str(d))
        else:
            print("[--]  Skip (not found): " + str(d))


def step_check_env() -> bool:
    print()
    print("[STEP 3] Checking Python environment")
    _sep()
    v = sys.version_info
    print("[OK]  Python " + str(v.major) + "." + str(v.minor) + "." + str(v.micro))
    deps = [
        ("pyinstaller",     ["PyInstaller"]),
        ("PyQt6",           ["PyQt6.QtWidgets"]),
        ("PyQt6-WebEngine", ["PyQt6.QtWebEngineWidgets"]),
        ("psutil",          ["psutil"]),
        ("requests",        ["requests"]),
        ("uiautomation",    ["uiautomation"]),
    ]
    missing = []
    for display, mods in deps:
        found = False
        for m in mods:
            try:
                __import__(m)
                found = True
                break
            except ImportError:
                pass
        tag = "[OK] " if found else "[MISS]"
        print(tag + " " + display)
        if not found:
            missing.append(display)
    if missing:
        print()
        print("[ERR] Missing: " + ", ".join(missing))
        print("      pip install " + " ".join(missing))
        return False
    return True


def step_pyinstaller() -> bool:
    print()
    print("[STEP 4] Running PyInstaller")
    _sep()
    if not SPEC_FILE.exists():
        print("[ERR] Spec not found: " + str(SPEC_FILE))
        return False
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(SPEC_FILE),
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_WORK),
        "--clean",
        "--noconfirm",
    ]
    return _run(cmd, ROOT, "PyInstaller", timeout=600)


def step_report() -> None:
    print()
    print("[STEP 5] Report")
    _sep()
    if not DIST_DIR.exists():
        print("[WARN] dist/ directory not found")
        return
    exes = list(DIST_DIR.rglob("*.exe"))
    if exes:
        for exe in exes:
            mb = exe.stat().st_size / (1024 * 1024)
            print("[OUT]  " + exe.name + "  (" + str(round(mb, 1)) + " MB)")
            print("       " + str(exe))
    else:
        print("[WARN] No .exe files found under dist/")


def main() -> int:
    print("=" * 60)
    print("AHDUNYI Terminal PRO  -  automated build  v9.0.0")
    print("=" * 60)

    if not step_build_frontend():
        return 1
    step_clean()
    if not step_check_env():
        return 1
    if not step_pyinstaller():
        return 1
    step_report()

    print()
    print("=" * 60)
    print("[OK]  Build complete!")
    print("=" * 60)
    print("Run : dist\\AHDUNYI_Terminal_PRO\\AHDUNYI_Terminal_PRO.exe")
    print("Cfg : config.json  (place next to the .exe)")
    print("Logs: logs\\client.log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
