from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class CardWidget(QWidget):
    """Lightweight information card styled entirely via QSS."""

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str | None = None,
        accent_color: str = "#5C6BF5",
        parent: QWidget | None = None,
        compact: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        if accent_color != "#5C6BF5":
            self.setProperty("variant", "accent")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_Hover)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10) if compact else layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)
        self.setLayout(layout)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("CardTitle")
        layout.addWidget(self._title_label)

        self._value_label = QLabel(value)
        self._value_label.setObjectName("CardValue")
        self._value_label.setWordWrap(True)
        self._value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._value_label)
        self._default_value_font = self._value_label.font()

        self._subtitle_label: QLabel | None = None
        if subtitle is not None:
            self._subtitle_label = QLabel(subtitle)
            self._subtitle_label.setObjectName("Subtitle")
            layout.addWidget(self._subtitle_label)

        if not compact:
            layout.addStretch(1)

    # ------------------------------------------------------------------ public API
    def set_title(self, text: str) -> None:
        self._title_label.setText(text)

    def set_value(self, text: str) -> None:
        self._value_label.setText(text)
        self._value_label.setAlignment(Qt.AlignCenter)

    def set_subtitle(self, text: str | None) -> None:
        if text is None:
            if self._subtitle_label is not None:
                self._subtitle_label.hide()
        else:
            if self._subtitle_label is None:
                self._subtitle_label = QLabel(text)
                self._subtitle_label.setObjectName("Subtitle")
                self.layout().addWidget(self._subtitle_label)
            self._subtitle_label.setText(text)
            self._subtitle_label.show()

    def set_value_font(self, point_size: int) -> None:
        if point_size <= 0:
            return
        font = self._value_label.font()
        font.setPointSize(point_size)
        self._value_label.setFont(font)

    def reset_value_font(self) -> None:
        font = self._default_value_font
        if font.pointSize() <= 0:
            font = self._value_label.font()
            font.setPointSize(max(font.pointSize(), 1))
        self._value_label.setFont(font)
