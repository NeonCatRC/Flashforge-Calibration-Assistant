# Frozen-app path resolution helpers for PyInstaller

from __future__ import annotations

import sys
from pathlib import Path


# Return True when running inside a PyInstaller bundle
def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


# Root of the extracted bundle (sys._MEIPASS) or project root
def bundle_dir() -> Path:
    if is_frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[1]


# Directory containing the .exe (or project root in dev mode)
# Writable paths (config/) live here
def app_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]
