# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Flashforge Calibration Assistant — single .exe."""

import os
from pathlib import Path

block_cipher = None
ROOT = os.path.abspath(".")

a = Analysis(
    ["main.py"],
    pathex=[ROOT],
    binaries=[],
    datas=[
        # UI assets (icons, images)
        ("flashforge_app/ui/assets", "flashforge_app/ui/assets"),
        # QSS theme template
        ("flashforge_app/ui/theme/style_template.qss", "flashforge_app/ui/theme"),
        # Language files
        ("languages", "languages"),
        # Input Shaper analysis modules (added to sys.path at runtime)
        ("input_shaper", "input_shaper"),
    ],
    hiddenimports=[
        # Matplotlib backends
        "matplotlib.backends.backend_qtagg",
        "matplotlib.backends.backend_agg",
        # 3D toolkit
        "mpl_toolkits.mplot3d",
        "mpl_toolkits.axes_grid1",
        "mpl_toolkits.axes_grid1.inset_locator",
        # PySide6 plugins
        "PySide6.QtSvg",
        "PySide6.QtSvgWidgets",
        # SSH/SCP
        "paramiko",
        "scp",
        # Scipy sub-modules used by interpolation
        "scipy.interpolate",
        "scipy.ndimage",
        "scipy.signal",
        # Input shaper analysis (dynamically loaded)
        "input_shaper.analysis.calibrate_shaper",
        "input_shaper.analysis.extras.shaper_calibrate",
        "input_shaper.analysis.extras.shaper_defs",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "tk",
        "_tkinter",
        "tkinterdnd2",
        # Heavy ML/GPU packages not used by this app
        "torch",
        "torchvision",
        "torchaudio",
        "xformers",
        "bitsandbytes",
        "triton",
        "transformers",
        "accelerate",
        "diffusers",
        "safetensors",
        "huggingface_hub",
        "tokenizers",
        "sentencepiece",
        "onnx",
        "onnxruntime",
        "tensorflow",
        "keras",
        "cv2",
        "IPython",
        "notebook",
        "jupyter",
        "pytest",
        "sphinx",
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FlashforgeCalibrationAssistant",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
