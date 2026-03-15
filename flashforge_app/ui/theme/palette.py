from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    # Centralised theme colours — the single source of truth for the entire app

    # Background hierarchy
    background: str
    surface: str
    surface_alt: str
    surface_hover: str
    border: str
    border_subtle: str

    # Accents
    accent_primary: str
    accent_secondary: str
    accent_success: str
    accent_warning: str
    accent_error: str

    # CTA (call-to-action) button
    cta_bg: str
    cta_bg_hover: str
    cta_bg_pressed: str
    cta_text: str

    # Text
    text_primary: str
    text_secondary: str
    text_muted: str

    # Matplotlib-specific
    mpl_bg: str
    mpl_text: str

    # TopBar
    topbar_bg: str
    topbar_border: str

    # Misc
    shadow: str
    outline_glow: str


DARK = Palette(
    background="#0F111A",
    surface="#161925",
    surface_alt="#1D2132",
    surface_hover="#22283D",
    border="#2B324A",
    border_subtle="rgba(255, 255, 255, 0.05)",
    accent_primary="#5C6BF5",
    accent_secondary="#FF6EA1",
    accent_success="#42C29E",
    accent_warning="#F5A45C",
    accent_error="#F55C6B",
    cta_bg="#F97316",
    cta_bg_hover="#fb8a35",
    cta_bg_pressed="#d85f0b",
    cta_text="#0F111A",
    text_primary="#F7F9FF",
    text_secondary="#B5BAD6",
    text_muted="#707897",
    mpl_bg="#0f172a",
    mpl_text="#F8FAFC",
    topbar_bg="rgba(22, 25, 37, 200)",
    topbar_border="none",
    shadow="#000000",
    outline_glow="#5C6BF533",
)

LIGHT = Palette(
    background="#F5F7FB",
    surface="#FFFFFF",
    surface_alt="#FFFFFF",
    surface_hover="#F0F0F5",
    border="rgba(28, 30, 36, 0.12)",
    border_subtle="rgba(28, 30, 36, 0.08)",
    accent_primary="#5C6BF5",
    accent_secondary="#FF6EA1",
    accent_success="#42C29E",
    accent_warning="#F5A45C",
    accent_error="#F55C6B",
    cta_bg="#5C6BF5",
    cta_bg_hover="#6f79f7",
    cta_bg_pressed="#4a5de5",
    cta_text="#FFFFFF",
    text_primary="#1C1E24",
    text_secondary="#5D6476",
    text_muted="#8E92A3",
    mpl_bg="#f8fafc",
    mpl_text="#1e293b",
    topbar_bg="rgba(255, 255, 255, 0.85)",
    topbar_border="1px solid rgba(28, 30, 36, 0.08)",
    shadow="#00000020",
    outline_glow="#5C6BF533",
)


# Return the palette for the given theme name
def get_palette(theme: str = "dark") -> Palette:
    return DARK if theme == "dark" else LIGHT


# Return a dict of matplotlib-compatible colour strings
def mpl_colors(theme: str = "dark") -> dict[str, str]:
    p = get_palette(theme)
    return {
        "bg": p.mpl_bg,
        "text": p.mpl_text,
        "face": p.mpl_bg,
        "panel": p.surface_alt,
        "accent": p.accent_primary,
        "edge": p.text_muted,
    }
