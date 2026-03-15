<div align="center">

<img src="flashforge_app/ui/assets/icons/app.svg" width="92" alt="Flashforge Calibration Assistant logo" />

# Flashforge Calibration Assistant

A helper tool for Flashforge Adventurer 5M/X calibration: visual leveling guidance, bed mesh visualization, quick Input Shaper utilities.

</div>

---

## Features

- **Visual Leveling Guidance**
  A three-step workflow (Z-rods, screws, tape) with automatic rotation direction hints and visual feedback. The visualization is available in 2D, 3D, and animated screw rotation modes.

- **Input Shaper**
  Import CSV logs, compute optimal shapers, generate `printer.cfg` commands, and view amplitude plots.

- **SSH Tools**
  Connect to your printer, download `printer.cfg` and shaper files directly from the interface.

- **Themes and Localization**
  Light and dark themes, with instant language switching between Russian and English.

- **Settings**
  Screw-mode toggle ("screw vs. nut" logic), threshold controls, and thermal drift presets.

---

## How to Get Bed Mesh on Stock Firmware (No SSH)

If you have stock firmware you need to download printer config using the **service menu** and a **flash drive**.

1. Insert your flash drive into the printer.
2. Press the **(i)** icon to open the *Machine Info* screen.
3. Press and hold the "Machine Info" text for about **10 seconds** until the service menu appears.
4. Go to the **Test** tab (top of the screen), then inside the box **"Change printer.base.cfg"** press **[get]**.
5. Remove the flash drive and insert it into your computer.
6. Open `printer.cfg` from the flash drive in the Calibration Assistant.

<div align="center">
  <img src="pics/m1.jpg" width="240" />
  <img src="pics/m2.jpg" width="240" />
  <img src="pics/m3.jpg" width="240" />
</div>

---

## Dependencies

See `requirements.txt`. Requires Python >= 3.9.

```
PySide6        # GUI
numpy          # matrix and mesh calculations
matplotlib     # charts and animations
scipy          # interpolation and smoothing
paramiko       # SSH
python-scp     # file transfer from printer
```

---

## Quick Start

```bash
git clone https://github.com/lDOCI/Flashforge-Calibration-Assistant-v2.git
cd Flashforge-Calibration-Assistant-v2
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Interface Overview

| Section | Description |
|----------|-------------|
| **Bed Leveling** | 2D/3D mesh maps, status cards, visual leveling hints. |
| **Input Shaper** | Load CSV, analyze X/Y axes, recommended shapers. |
| **SSH** | Printer connection, download `printer.cfg` and shaper files. |
| **Settings** | Equipment setup, thresholds, thermal presets, about. |

---

## Project Structure

```
flashforge_app/
 ├─ services/         # settings, localization, state
 ├─ ui/
 │   ├─ dialogs/      # visual guides, author dialog
 │   ├─ views/        # main UI tabs
 │   ├─ widgets/      # topbar, sidebar, cards
 │   ├─ theme/        # palette, QSS template, loader
 │   └─ assets/       # icons and images
 └─ ...
calibration/          # leveling algorithms
data_processing/      # mesh parsing and interpolation
visualization/        # matplotlib visualizations
input_shaper/         # shaper analysis modules
languages/            # localization JSONs
```

---

## Developer Notes

- **Localization** — all strings are in `languages/*.json`. Add your language and register keys in `LocalizationService`.
- **Visual Guides** — generation logic is in `visualization/bed_mesh/animated_recommendations.py`.
- **Themes** — centralized palette in `flashforge_app/ui/theme/palette.py`, single QSS template with variable substitution.

---

## FAQ

**My `config/` files disappeared — is that normal?**
Yes. The app recreates `config/app_settings.json` automatically.

**Can I use it without SSH?**
Yes, all visualization functions work with local files. SSH is just a convenience.

---

## Feedback

Author — [@I_DOC_I](https://t.me/I_DOC_I).
For all questions — only in the community chat.

---

Good calibration and perfect first layers!

---

# 🇷🇺 Русская версия

<div align="center">

<img src="flashforge_app/ui/assets/icons/app.svg" width="92" alt="Flashforge Calibration Assistant logo" />

# Flashforge Calibration Assistant

Помощник по калибровке принтера Flashforge Adventurer 5M/X: наглядные рекомендации, визуализация сеток, быстрая работа с Input Shaper.

</div>

---

## Что умеет приложение

- **Визуальные рекомендации по выравниванию**
  Пошаговый workflow из трёх этапов (Z-валы, винты, скотч) с автоматическим вычислением направлений вращения и подсказками. Визуализация в 2D, 3D и анимации вращения винтов.

- **Input Shaper**
  Импорт CSV-логов, вычисление оптимальных шейперов, генерация команд для printer.cfg и графики амплитуд.

- **SSH-инструменты**
  Подключение к принтеру, скачивание `printer.cfg` и файлов шейпера прямо из интерфейса.

- **Темы и локализация**
  Светлая и тёмная темы + переключение языков без перезапуска.

- **Настройки**
  Screw-mode (логика «винт или гайка»), контроль порогов и термопресеты.

---

## Как снять карту стола на стоковой прошивке (без SSH)

1. Вставьте флешку в принтер.
2. Нажмите на иконку **(i)** → экран *Machine Info*.
3. Удерживайте надпись **Machine Info** ~10 секунд → сервисное меню.
4. Вкладка **Test** → блок **"Change printer.base.cfg"** → **[get]**.
5. Флешку в компьютер → откройте `printer.cfg` в приложении.

<div align="center">
  <img src="pics/m1.jpg" width="240" />
  <img src="pics/m2.jpg" width="240" />
  <img src="pics/m3.jpg" width="240" />
</div>

---

## Зависимости

См. `requirements.txt`. Нужен Python >= 3.9.

```
PySide6        # GUI
numpy          # расчёты матриц и сеток
matplotlib     # графики и анимации
scipy          # интерполяция и сглаживание
paramiko       # SSH
python-scp     # загрузка файлов с принтера
```

---

## Быстрый старт

```bash
git clone https://github.com/lDOCI/Flashforge-Calibration-Assistant-v2.git
cd Flashforge-Calibration-Assistant-v2
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Навигация по интерфейсу

| Раздел | Описание |
|--------|----------|
| **Bed Leveling** | 2D/3D карты сетки, карточки статуса, визуальные рекомендации. |
| **Input Shaper** | Загрузка CSV, анализ осей X/Y, рекомендуемые шейперы. |
| **SSH** | Подключение к принтеру, скачивание файлов. |
| **Settings** | Оборудование, пороги, термопресеты, о программе. |

---

## Структура проекта

```
flashforge_app/
 ├─ services/         # настройки, локализация, состояние
 ├─ ui/
 │   ├─ dialogs/      # визуальные рекомендации, авторский диалог
 │   ├─ views/        # основные вкладки
 │   ├─ widgets/      # topbar, сайдбар, карточки
 │   ├─ theme/        # палитра, QSS-шаблон, загрузчик
 │   └─ assets/       # иконки, картинки
 └─ ...
calibration/          # алгоритмы выравнивания
data_processing/      # парсинг и интерполяция сеток
visualization/        # matplotlib-визуализации
input_shaper/         # модули анализа шейперов
languages/            # json-файлы локализации
```

---

## Советы разработчикам

- **Локализация** — строки в `languages/*.json`. Добавьте язык и ключи в `LocalizationService`.
- **Визуальные рекомендации** — логика в `visualization/bed_mesh/animated_recommendations.py`.
- **Темы** — централизованная палитра в `flashforge_app/ui/theme/palette.py`, единый QSS-шаблон с подстановкой переменных.

---

## FAQ

**Файлы в `config/` пропали — это нормально?**
Да. Приложение пересоздаст `config/app_settings.json` автоматически.

**Можно ли работать без SSH?**
Да, все функции визуализации работают с локальными файлами.

---

## Обратная связь

Автор — [@I_DOC_I](https://t.me/I_DOC_I).
По вопросам — только в общий чат сообщества.

---

Удачной калибровки и ровных первых слоёв!
