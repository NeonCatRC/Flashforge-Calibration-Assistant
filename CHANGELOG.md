# Changelog

## v2.1.0 — UI Overhaul (2026-03-15)

Major UI refactoring focused on code simplification, deduplication, and theme centralization.
Mathematical and calibration modules are untouched.

### Removed (~5,200 lines of dead / legacy code)

- **Legacy tkinter UI** (`app/` folder) — entire directory removed
- **`visual_recommendations_original.py`** — legacy standalone script
- **`flashforge_app/ui/views/dashboard.py`** — unused view, never imported
- **`visualization/widgets/custom_toolbars.py`** — tkinter-only toolbar
- **`visualization/shapers/shaper_visualization.py`** — empty placeholder
- **`style_dark.qss` / `style_light.qss`** — replaced by unified QSS template
- Tkinter-only methods `display_in_frame()` / `display_in_window()` from `heatmap_2d.py` and `surface_3d.py`
- Unused `create_teeth_figure()` from `animated_recommendations.py`

### Changed — Theme System

- **Centralized color palette** (`palette.py`): `DARK` and `LIGHT` frozen dataclass palettes as single source of truth for all colors
- **QSS template** (`style_template.qss`): single file with `{variable}` placeholders, auto-filled from palette — replaces two separate, inconsistent QSS files
- **`mpl_colors()` helper**: provides matplotlib-safe hex colors derived from palette — no more hardcoded color blocks per theme
- All inline `setStyleSheet()` color overrides replaced with QSS object names and palette references
- Typography standardized via QSS classes (`#ViewHeader`, `#SectionTitle`, `#SubsectionTitle`, `#Subtitle`)

### Changed — Widget Simplification

- **`CardWidget`** (139 → 83 lines): removed custom `QPainter` hover animation, replaced with pure QSS `:hover` selector
- **`AnimatedStackedWidget`** (78 → 64 lines): replaced `try/except TypeError` reconnection pattern with a clean state machine (`idle → fade_out → fade_in`)

### Changed — Visualization Deduplication

- **`animated_recommendations.py`** (988 → 453 lines): extracted shared helpers (`_draw_ok_marker`, `_draw_corner_label`, `_draw_info_panel`, `_create_wedge`, `_finalize_axes`, `_build_animation`), module-level constants, and theme via `mpl_colors()`
- **`visual_recommendations.py`** (999 → 926 lines): extracted `_format_thermal_lines()` shared helper, `_make_visualizer()` factory, `_finalize_fig()`, simplified `_start_animation()`

### Changed — View Simplification

- **`InputShaperView`** (597 → 586 lines): extracted `_clear_contents()` in `_AxisInfo`, theme colors from palette, added public `load_csv_files()` API
- **`SettingsView`** (437 → 433 lines): deduplicated preset sync logic by reusing `_populate_environment_from_preset()`
- **`MainWindow`** (358 → 350 lines): uses `InputShaperView.load_csv_files()` instead of calling private methods

### Fixed

- **Matplotlib figure memory leaks**: added `plt.close(fig)` in `leveling.py`, `visual_recommendations.py`, and `input_shaper.py` before canvas disposal
- **Light theme crash in tape visualization**: `p.border` contained CSS `rgba()` format incompatible with matplotlib — replaced with hex-safe `edge_color` from `mpl_colors()`

### Added

- `flashforge_app/ui/constants.py` — named constants for sidebar width, spacing, margins, DPI, animation duration
- `flashforge_app/ui/theme/style_template.qss` — unified QSS template

### Dependencies

- Removed `tkinterdnd2` and `sv-ttk` from requirements (legacy tkinter deps)

---

### Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Dead / legacy code | ~5,200 lines | 0 | -5,200 |
| Live UI + viz code | ~5,700 lines | ~3,500 lines | -2,200 (-38%) |
| Color source files | 10+ | 1 (`palette.py`) | unified |
| QSS files | 2 (inconsistent) | 1 template | consistent |
| Files > 500 lines | 3 | 0 | all under 500 |
