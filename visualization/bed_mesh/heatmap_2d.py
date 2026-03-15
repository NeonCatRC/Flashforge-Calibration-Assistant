#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Модуль для визуализации 2D тепловой карты стола принтера

from typing import Callable, Optional

import numpy as np
from matplotlib import patheffects
from matplotlib.artist import setp as _mpl_setp
from matplotlib.figure import Figure

Translator = Callable[[str, Optional[str]], str]


def _noop_translator(key: str, default: Optional[str] = None) -> str:
    return default if default is not None else key


class BedMeshHeatmap:
    # Класс для отображения 2D тепловой карты стола

    def __init__(self, is_dark_theme: bool = False, translator: Optional[Translator] = None):
        self.mesh_data = None
        self.max_delta = None
        self.is_dark_theme = is_dark_theme
        self.figsize = (6.5, 5.0)
        self._translator: Translator = translator or _noop_translator

    # ------------------------------------------------------------------ service helpers
    def set_translator(self, translator: Optional[Translator]) -> None:
        # Устанавливает функцию перевода, совместимую с LocalizationService
        if translator is None:
            self._translator = _noop_translator
        else:
            self._translator = translator

    def _tr(self, key: str, default: Optional[str] = None) -> str:
        return self._translator(key, default)
        
    def set_mesh_data(self, mesh_data: np.ndarray) -> None:
        # Установка данных сетки и расчет максимального отклонения
        self.mesh_data = mesh_data
        self.max_delta = float(np.max(self.mesh_data) - np.min(self.mesh_data))
        
    def set_theme(self, is_dark_theme: bool) -> None:
        # Установка темы
        self.is_dark_theme = is_dark_theme

    def set_figsize(self, width: float, height: float) -> None:
        # Override default figure size (in inches)
        if width > 0 and height > 0:
            self.figsize = (width, height)

    def create_2d_figure(self) -> Figure:
        # Создание фигуры с 2D тепловой картой
        if self.mesh_data is None:
            return None

        fig = Figure(figsize=self.figsize, dpi=100)
        fig.subplots_adjust(left=0.06, bottom=0.05, right=0.82, top=0.86)

        ax = fig.add_subplot(111)
        fig.patch.set_alpha(0.0)
        ax.set_facecolor('none')

        text_color = 'white' if self.is_dark_theme else 'black'

        rows, cols = self.mesh_data.shape
        Z = np.flipud(self.mesh_data)
        im = ax.imshow(Z, cmap='coolwarm_r', aspect='equal', interpolation='nearest')

        cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.04)
        cbar.set_label(self._tr("visualization.height_mm"), color=text_color)
        cbar.ax.yaxis.set_tick_params(color=text_color)
        _mpl_setp(cbar.ax.get_yticklabels(), color=text_color)

        for i in range(rows):
            for j in range(cols):
                val = Z[i, j]
                brightness = im.norm(val)
                cell_color = 'white' if brightness < 0.5 else 'black'
                ax.text(j, i, f"{val:.3f}", ha='center', va='center',
                        color=cell_color, fontweight='bold')

        max_deviation = float(np.max(self.mesh_data) - np.min(self.mesh_data))
        title = self._tr("visualization.bed_mesh_title").format(max_deviation)
        ax.text(
            0.5,
            1.12,
            title,
            color=text_color,
            fontsize=11,
            fontweight='semibold',
            ha='center',
            va='bottom',
            transform=ax.transAxes,
        )

        ax.axis('off')

        outline = [patheffects.withStroke(linewidth=2, foreground=('black' if text_color == 'white' else 'white'))]
        pad = 0.028
        ax.text(
            0.0,
            1.0 + pad,
            self._tr("visual_rec.back_left"),
            color=text_color,
            fontsize=9,
            ha='left',
            va='bottom',
            path_effects=outline,
            transform=ax.transAxes,
        )
        ax.text(
            1.0,
            1.0 + pad,
            self._tr("visual_rec.back_right"),
            color=text_color,
            fontsize=9,
            ha='right',
            va='bottom',
            path_effects=outline,
            transform=ax.transAxes,
        )
        ax.text(
            0.0,
            -pad,
            self._tr("visual_rec.front_left"),
            color=text_color,
            fontsize=9,
            ha='left',
            va='top',
            path_effects=outline,
            transform=ax.transAxes,
        )
        ax.text(
            1.0,
            -pad,
            self._tr("visual_rec.front_right"),
            color=text_color,
            fontsize=9,
            ha='right',
            va='top',
            path_effects=outline,
            transform=ax.transAxes,
        )

        return fig

