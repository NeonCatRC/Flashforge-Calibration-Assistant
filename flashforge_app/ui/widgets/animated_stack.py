from __future__ import annotations

from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QStackedWidget, QWidget


class AnimatedStackedWidget(QStackedWidget):
    """
    QStackedWidget with cross-fade animation between pages.

    The QGraphicsOpacityEffect is only enabled during transitions.
    Keeping it enabled permanently would force Qt to render every child
    widget into an offscreen pixmap, which blocks mouse events on
    interactive controls (QCheckBox, QRadioButton, QComboBox, etc.).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_opacity = 1.0
        self._pending_index: int | None = None
        self._phase = "idle"  # "fade_out" | "fade_in" | "idle"

        self._fade_effect = QGraphicsOpacityEffect(self)
        self._fade_effect.setOpacity(1.0)
        self._fade_effect.setEnabled(False)
        self.setGraphicsEffect(self._fade_effect)

        self._animation = QPropertyAnimation(self, b"opacity", self)
        self._animation.setDuration(240)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._animation.finished.connect(self._on_animation_finished)

    def setCurrentIndex(self, index: int) -> None:
        if index == self.currentIndex():
            return
        self._pending_index = index
        self._phase = "fade_out"
        self._fade_effect.setEnabled(True)
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.start()

    def _on_animation_finished(self) -> None:
        if self._phase == "fade_out":
            if self._pending_index is not None:
                super().setCurrentIndex(self._pending_index)
            self._phase = "fade_in"
            self._animation.setStartValue(0.0)
            self._animation.setEndValue(1.0)
            self._animation.start()
        elif self._phase == "fade_in":
            self._phase = "idle"
            self._pending_index = None
            self._fade_effect.setOpacity(1.0)
            self._fade_effect.setEnabled(False)

    def getOpacity(self) -> float:
        return self._current_opacity

    def setOpacity(self, value: float) -> None:
        self._current_opacity = value
        self._fade_effect.setOpacity(value)

    opacity = Property(float, getOpacity, setOpacity)
