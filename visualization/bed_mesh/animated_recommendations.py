#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Визуализации рекомендаций по регулировке стола для Qt-интерфейса.

Модуль реализует две фигуры matplotlib:
* ScrewAdjustmentVisualizer — анимация регулировки винтов с подсказками
* TapeLayoutVisualizer — схема наклейки скотча с легендой и инструкциями
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import numpy as np
import matplotlib.animation as animation
import matplotlib.patches as patches
from matplotlib.figure import Figure

from calibration.hardware.screw import RotationDirection
from flashforge_app.ui.theme.palette import mpl_colors

Translator = Callable[[str, Optional[str]], str]

DEGREES_PER_TOOTH = 22.5
_BED_SIZE = 70.0
_OK_COLOR = '#7f8c8d'
_CW_COLOR = '#fb7185'
_CCW_COLOR = '#34d399'


def _noop_tr(key: str, default: Optional[str] = None) -> str:
    return default or key


# ── Shared drawing helpers ──────────────────────────────────────────


def _draw_ok_marker(ax, x: float, y: float, bed_size: float, text: str) -> None:
    """Draw a ✓ checkmark and label at (x, y)."""
    ax.text(x, y, "✓", ha='center', va='center',
            fontsize=20, fontweight='bold', color=_OK_COLOR)
    ax.text(x, y + bed_size / 6, text, ha='center', va='center',
            fontsize=9, color=_OK_COLOR)


def _draw_corner_label(ax, x: float, y: float, label: str, bed_size: float,
                       text_color: str, panel_bg: str) -> None:
    ax.text(x, y - bed_size / 6, label.replace(" ", "\n"),
            ha='center', va='center', fontsize=10, fontweight='bold',
            color=text_color, bbox=dict(facecolor=panel_bg, alpha=0.7, boxstyle='round'))


def _draw_info_panel(ax, x: float, y: float, lines: List[str], bed_size: float,
                     color: str, panel_bg: str, edge_color: str) -> None:
    info_offset = bed_size / 2.6
    info_x = x + (info_offset if x >= 0 else -info_offset)
    info_align = 'left' if x >= 0 else 'right'
    ax.text(info_x, y, "\n".join(lines),
            ha=info_align, va='center', fontsize=9, linespacing=1.25,
            color=color,
            bbox=dict(facecolor=panel_bg, edgecolor=edge_color,
                      linewidth=0.8, alpha=0.9))


def _create_wedge(ax, x: float, y: float, bed_size: float,
                  start_angle: float, color: str) -> patches.Wedge:
    wedge = patches.Wedge((x, y), bed_size / 8, start_angle, start_angle,
                          color=color, alpha=0.5, zorder=3)
    ax.add_patch(wedge)
    return wedge


def _finalize_axes(ax, fig, bed_size: float, margin: float = 4.0) -> None:
    info_offset = bed_size / 2.6
    x_extent = bed_size / 2 + margin + info_offset + 0.8
    ax.set_xlim(-x_extent, x_extent)
    ax.set_ylim(-bed_size / 2 - margin, bed_size / 2 + margin)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.subplots_adjust(left=0.08, right=0.92, top=0.86, bottom=0.08)


# ── ScrewAdjustmentVisualizer ───────────────────────────────────────


class ScrewAdjustmentVisualizer:
    """Создает фигуру с визуализацией винтов и анимацией дуг."""

    def __init__(
        self,
        *,
        translator: Optional[Translator],
        is_dark_theme: bool,
        show_minutes: bool,
        show_degrees: bool,
        screw_mode: str = "hold_nut",
    ) -> None:
        self._tr = translator or _noop_tr
        self.is_dark_theme = is_dark_theme
        self.show_minutes = show_minutes
        self.show_degrees = show_degrees
        self.screw_mode = screw_mode
        self._corner_positions: Dict[str, Tuple[float, float]] = {}
        self._belt_positions: Dict[str, Tuple[float, float]] = {}
        self.animation: Optional[animation.FuncAnimation] = None

    def set_mode(self, screw_mode: str) -> None:
        self.screw_mode = screw_mode

    def _mode_caption(self) -> str:
        if self.screw_mode == "hold_screw":
            mode_text = self._tr("settings_tab.screw_mode_hold_screw", "Turn nuts, hold screws")
        else:
            mode_text = self._tr("settings_tab.screw_mode_hold_nut", "Turn screws, hold nuts")
        template = self._tr("visual_rec.screw_mode_caption", "Mode: {mode}")
        try:
            return template.format(mode=mode_text)
        except (KeyError, IndexError, ValueError):
            return f"{template} {mode_text}"

    def _setup_axes(self) -> Tuple[Figure, object, str, str, str]:
        """Create figure and axes with theme colours. Returns (fig, ax, text_color, panel_bg, edge_color)."""
        mc = mpl_colors("dark" if self.is_dark_theme else "light")

        fig = Figure(figsize=(12.0, 9.6), dpi=110)
        ax = fig.add_subplot(111)

        fig.patch.set_facecolor(mc["bg"])
        ax.set_facecolor(mc["bg"])

        text_color = mc["text"]
        panel_bg = mc["panel"]
        edge_color = mc["edge"]

        offset = _BED_SIZE / 3.0
        self._corner_positions = {
            'front_left': (-offset, -offset),
            'front_right': (offset, -offset),
            'back_left': (-offset, offset),
            'back_right': (offset, offset),
        }
        self._belt_positions = {
            'front_left': self._corner_positions['front_left'],
            'front_right': self._corner_positions['front_right'],
            'back': (0.0, offset),
        }

        accent_color = edge_color
        bed = patches.Rectangle(
            (-_BED_SIZE / 2, -_BED_SIZE / 2), _BED_SIZE, _BED_SIZE,
            fill=True, facecolor=panel_bg, edgecolor=edge_color, linewidth=2)
        ax.add_patch(bed)
        return fig, ax, text_color, panel_bg, edge_color

    # ── public API ──

    def create_adjustment_figure(
        self,
        adjustments: Dict[str, Tuple[float, RotationDirection]],
    ) -> Figure:
        """Builds screw-adjustment figure with wedge animations."""
        fig, ax, text_color, panel_bg, edge_color = self._setup_axes()
        ax.set_title(self._mode_caption(), color=text_color,
                     fontsize=12, fontweight='bold', pad=12)

        animation_data: List[Dict[str, object]] = []
        ok_text = self._tr("visual_rec.normal", "Normal")

        for corner, (x, y) in self._corner_positions.items():
            # base circle
            ax.add_patch(patches.Circle(
                (x, y), _BED_SIZE / 10, fill=True,
                facecolor=panel_bg, edgecolor=edge_color,
                linewidth=1, alpha=0.55, zorder=1))

            corner_label = self._tr(f"neo_ui.visual.corners.{corner}",
                                    corner.replace("_", " ").title())
            _draw_corner_label(ax, x, y, corner_label, _BED_SIZE, text_color, panel_bg)

            data = adjustments.get(corner)
            minutes = float(data[0]) if data else 0.0
            if not data or minutes <= 0.0:
                _draw_ok_marker(ax, x, y, _BED_SIZE, ok_text)
                continue

            _, direction = data
            actual_clockwise = direction == RotationDirection.CLOCKWISE
            user_clockwise = actual_clockwise if self.screw_mode != "hold_screw" else not actual_clockwise
            wedge_color = _CW_COLOR if user_clockwise else _CCW_COLOR
            start_angle = 90.0
            total_degrees = minutes * 6.0
            end_angle = start_angle - total_degrees if user_clockwise else start_angle + total_degrees

            wedge = _create_wedge(ax, x, y, _BED_SIZE, start_angle, wedge_color)
            animation_data.append({
                'wedge': wedge, 'start_angle': start_angle,
                'end_angle': end_angle, 'clockwise': user_clockwise})

            rotation_symbol = '↻' if user_clockwise else '↺'
            ax.text(x, y, rotation_symbol, ha='center', va='center',
                    fontsize=22, fontweight='bold', color=wedge_color)

            info_lines: List[str] = []
            if self.show_minutes:
                info_lines.append(self._tr("visual_rec.minutes_short", "{value:.0f} мин").format(value=minutes))
            if self.show_degrees:
                info_lines.append(self._tr("visual_rec.degrees_short", "{value:.0f}°").format(value=total_degrees))
            dir_key = "visual_rec.clockwise" if user_clockwise else "visual_rec.counterclockwise"
            info_lines.append(self._tr(dir_key, "Clockwise" if user_clockwise else "Counterclockwise"))
            _draw_info_panel(ax, x, y, info_lines, _BED_SIZE, wedge_color, panel_bg, edge_color)

        if animation_data:
            anim = _build_animation(fig, animation_data, frames=60, interval=60, repeat_delay=2000)
            if anim:
                fig.animation = anim
                self.animation = anim

        _finalize_axes(ax, fig, _BED_SIZE)
        return fig

    def create_belt_animation_figure(
        self,
        adjustments: Dict[str, Dict[str, object]],
    ) -> Figure:
        """Builds belt shaft adjustment figure with wedge animations."""
        fig, ax, text_color, panel_bg, edge_color = self._setup_axes()
        ax.set_title("", color=text_color)

        animation_data: List[Dict[str, object]] = []
        ok_text = self._tr("visual_rec.belt_action_ok", "In tolerance")

        for corner, (x, y) in self._belt_positions.items():
            # gear + hub
            ax.add_patch(patches.RegularPolygon(
                (x, y), numVertices=12, radius=_BED_SIZE / 10,
                orientation=np.deg2rad(15.0), facecolor=panel_bg,
                edgecolor=edge_color, linewidth=1.2, alpha=0.8, zorder=1))
            ax.add_patch(patches.Circle(
                (x, y), _BED_SIZE / 20, facecolor=panel_bg,
                edgecolor=edge_color, linewidth=1.0, zorder=2))

            label_key = 'back_center' if corner == 'back' else corner
            corner_label = self._tr(f"visual_rec.{label_key}", None)
            if not corner_label or corner_label == f"visual_rec.{label_key}":
                corner_label = self._tr(f"neo_ui.visual.corners.{label_key}",
                                        label_key.replace("_", " ").title())
            _draw_corner_label(ax, x, y, corner_label, _BED_SIZE, text_color, panel_bg)

            data = adjustments.get(corner)
            teeth = int(abs(int(data.get('teeth', 0) or 0))) if data else 0
            if not data or teeth <= 0:
                _draw_ok_marker(ax, x, y, _BED_SIZE, ok_text)
                continue

            direction_token = str(data.get('direction', 'counterclockwise')).lower()
            clockwise = direction_token in {'clockwise', 'down', 'cw'}

            wedge_color = _CW_COLOR if clockwise else _CCW_COLOR
            start_angle = 90.0
            total_degrees = min(float(teeth) * DEGREES_PER_TOOTH, 270.0)
            end_angle = start_angle - total_degrees if clockwise else start_angle + total_degrees

            wedge = _create_wedge(ax, x, y, _BED_SIZE, start_angle, wedge_color)
            animation_data.append({
                'wedge': wedge, 'start_angle': start_angle,
                'end_angle': end_angle, 'clockwise': clockwise})

            ax.text(x, y, str(teeth), ha='center', va='center',
                    fontsize=18, fontweight='bold', color=wedge_color)

            info_lines: List[str] = []
            info_lines.append(self._tr("visual_rec.belt_teeth_count",
                                       "Teeth to move: {count}").format(count=teeth))
            delta_mm = float(data.get('delta_mm') or 0.0)
            if delta_mm > 0.0:
                info_lines.append(self._tr("visual_rec.spot_height_diff",
                                           "{value:.2f} mm").format(value=delta_mm))
            dir_key = "visual_rec.belt_action_loosen" if clockwise else "visual_rec.belt_action_tighten"
            info_lines.append(self._tr(dir_key, "Rotate clockwise" if clockwise else "Rotate counterclockwise"))
            _draw_info_panel(ax, x, y, info_lines, _BED_SIZE, wedge_color, panel_bg, edge_color)

        if animation_data:
            anim = _build_animation(fig, animation_data, frames=60, interval=120, repeat_delay=2000)
            if anim:
                fig.animation = anim
                self.animation = anim

        _finalize_axes(ax, fig, _BED_SIZE)
        return fig


# ── Animation builder ───────────────────────────────────────────────


def _build_animation(
    fig: Figure,
    entries: Iterable[Dict[str, object]],
    *,
    frames: int = 20,
    interval: int = 50,
    repeat_delay: int = 1000,
) -> Optional[animation.FuncAnimation]:
    items = list(entries)
    if not items:
        return None
    total_frames = max(frames, 2)

    def init():
        result = []
        for data in items:
            wedge: patches.Wedge = data['wedge']  # type: ignore[assignment]
            start = float(data['start_angle'])     # type: ignore[arg-type]
            wedge.set_theta1(start)
            wedge.set_theta2(start)
            result.append(wedge)
        return result

    def update(frame: int):
        progress = frame / max(total_frames - 1, 1)
        result = []
        for data in items:
            wedge: patches.Wedge = data['wedge']  # type: ignore[assignment]
            start = float(data['start_angle'])     # type: ignore[arg-type]
            end = float(data['end_angle'])         # type: ignore[arg-type]
            clockwise = bool(data['clockwise'])
            current = start + (end - start) * progress
            if clockwise:
                wedge.set_theta1(current)
            else:
                wedge.set_theta2(current)
            result.append(wedge)
        return result

    return animation.FuncAnimation(
        fig, update, init_func=init, frames=total_frames,
        interval=interval, blit=False, repeat=True, repeat_delay=repeat_delay)


# ── TapeLayoutVisualizer ────────────────────────────────────────────


@dataclass(frozen=True)
class TapeCell:
    row: int
    col: int
    layers: int
    delta: float


class TapeLayoutVisualizer:
    """Визуализация схемы наклейки скотча."""

    def __init__(self, *, translator: Optional[Translator], is_dark_theme: bool) -> None:
        self._tr = translator or _noop_tr
        self.is_dark_theme = is_dark_theme

    def create_tape_figure(
        self,
        mesh: np.ndarray,
        cells: Iterable[TapeCell],
        *,
        threshold_mm: Optional[float] = None,
        tape_thickness: Optional[float] = None,
    ) -> Figure:
        cells = [cell for cell in cells if cell.layers > 0]
        rows, cols = mesh.shape

        mc = mpl_colors("dark" if self.is_dark_theme else "light")

        fig = Figure(figsize=(8.0, 6.0), dpi=110)
        fig.patch.set_facecolor(mc["bg"])
        text_color = mc["text"]
        panel_bg = mc["panel"]
        edge_color = mc["edge"]

        ax = fig.add_subplot(111)
        ax.set_facecolor(panel_bg)
        ax.axis('off')
        ax.set_aspect('equal')

        # grid background + outline
        ax.add_patch(patches.Rectangle(
            (-0.55, -0.55), cols + 0.1, rows + 0.1,
            linewidth=0, facecolor=panel_bg, alpha=0.95))
        ax.add_patch(patches.Rectangle(
            (-0.5, -0.5), cols, rows,
            linewidth=1.6, edgecolor=edge_color, facecolor='none'))

        for i in range(rows + 1):
            ax.axhline(i - 0.5, linestyle=':', linewidth=0.8, color=edge_color, alpha=0.55)
        for j in range(cols + 1):
            ax.axvline(j - 0.5, linestyle=':', linewidth=0.8, color=edge_color, alpha=0.55)

        # row/col labels
        for r in range(rows):
            ax.text(-0.9, r, str(r + 1), ha='center', va='center', fontsize=9, color=text_color)
        for c in range(cols):
            ax.text(c, -0.9, chr(65 + c), ha='center', va='center', fontsize=9, color=text_color)

        color_palette = {1: '#fde047', 2: '#fb923c', 3: '#f97316'}
        legend_entries: list[str] = []

        for cell in cells:
            face = color_palette.get(min(cell.layers, 3), '#EA580C')
            alpha = min(0.35 + 0.15 * cell.layers, 0.92)
            ax.add_patch(patches.Rectangle(
                (cell.col - 0.4, cell.row - 0.4), 0.8, 0.8,
                facecolor=face, edgecolor='#EA580C', linewidth=1.4, alpha=alpha))
            ax.text(cell.col, cell.row, str(cell.layers),
                    ha='center', va='center', fontsize=12, fontweight='bold', color=text_color)
            coords = f"{cell.row + 1}{chr(65 + cell.col)}"
            info = (f"{coords} • "
                    + self._tr("visual_rec.tape_layers_short", "{value}×").format(value=cell.layers)
                    + " • "
                    + self._tr("neo_ui.visual.delta", "Δ {value:.3f} mm").format(value=float(cell.delta)))
            legend_entries.append(info)

        # corner labels
        lbl = dict(fontsize=8, color=text_color)
        ax.text(-0.45, -0.55, self._tr("neo_ui.visual.corners.front_left", "Front left"),
                ha='right', va='top', **lbl)
        ax.text(cols - 0.05, -0.55, self._tr("neo_ui.visual.corners.front_right", "Front right"),
                ha='left', va='top', **lbl)
        ax.text(-0.45, rows - 0.05, self._tr("neo_ui.visual.corners.back_left", "Back left"),
                ha='right', va='bottom', **lbl)
        ax.text(cols - 0.05, rows - 0.05, self._tr("neo_ui.visual.corners.back_right", "Back right"),
                ha='left', va='bottom', **lbl)

        if not cells:
            ax.text(cols / 2, rows / 2,
                    self._tr("visual_rec.tape_no_adjustment", "No tape correction required"),
                    ha='center', va='center', fontsize=12, fontweight='bold', color=text_color)

        # legend sidebar
        pad = max(0.8, cols * 0.08)
        if legend_entries:
            info_padding = 0.4
            legend_width = max(2.6, max(len(e) for e in legend_entries) * 0.18 + 1.2)
            legend_height = len(legend_entries) * 0.85 + 0.6
            ax.add_patch(patches.Rectangle(
                (cols - 0.5 + pad + info_padding, (rows - legend_height) / 2),
                legend_width, legend_height,
                linewidth=1.0, edgecolor=edge_color, facecolor=panel_bg, alpha=0.95))
            ax.text(cols - 0.5 + pad + info_padding + 0.3,
                    (rows - legend_height) / 2 + 0.3,
                    "\n".join(legend_entries),
                    ha='left', va='top', fontsize=10, color=text_color, linespacing=1.35)

        ax.set_xlim(-0.5 - pad, cols - 0.5 + pad)
        ax.set_ylim(-0.5 - pad, rows - 0.5 + pad)
        fig.subplots_adjust(left=0.08, right=0.94, top=0.9, bottom=0.08)
        return fig
