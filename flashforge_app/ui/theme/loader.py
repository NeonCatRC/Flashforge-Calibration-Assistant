from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from .palette import get_palette

THEME_DIR = Path(__file__).resolve().parent
_TEMPLATE_PATH = THEME_DIR / "style_template.qss"
_template_cache: str | None = None


def apply_theme(app: QApplication, theme: str = "dark") -> None:
    # Generate QSS from the palette template and apply it
    _load_fonts()
    if theme not in {"dark", "light"}:
        theme = "dark"

    global _template_cache
    if _template_cache is None:
        if _TEMPLATE_PATH.exists():
            _template_cache = _TEMPLATE_PATH.read_text(encoding="utf-8")
        else:
            _template_cache = ""

    palette = get_palette(theme)
    stylesheet = _template_cache.format(**asdict(palette))
    app.setStyleSheet(stylesheet)
    app.setProperty("currentTheme", theme)


def _load_fonts() -> None:
    # Attempt to load bundled fonts; quietly ignore if unavailable
    fonts_dir = THEME_DIR / "fonts"
    if not fonts_dir.exists():
        return
    for font_file in fonts_dir.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font_file))
