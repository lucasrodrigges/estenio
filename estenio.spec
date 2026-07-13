# -*- mode: python ; coding: utf-8 -*-
# Estenio — PyInstaller spec file
#
# Generates a standalone executable that bundles:
#   - Python runtime
#   - All Python dependencies (questionary, rich, yt-dlp, etc.)
#   - Platform-specific ffmpeg binary (from src/estenio/bin/)
#
# Build:  pyinstaller estenio.spec
# Output: dist/estenio (or dist/estenio.exe on Windows)

import os
import sys
from pathlib import Path

# ── Hidden imports ──────────────────────────────────────────────────────────
# yt-dlp uses lazy imports extensively; we must force them.
yt_dlp_imports = [
    'yt_dlp',
    'yt_dlp.extractor',
    'yt_dlp.downloader',
    'yt_dlp.postprocessor',
    'yt_dlp.utils',
    'yt_dlp.compat',
    'yt_dlp.cookies',
]

hiddenimports = [
    'questionary',
    'rich',
    'rich.console',
    'rich.panel',
    'rich.text',
    'rich.style',
    *yt_dlp_imports,
]

# ── Data files ──────────────────────────────────────────────────────────────
# Bundle only the platform-relevant ffmpeg binary to keep the package small.
bin_dir = Path('src/estenio/bin')
if sys.platform == 'win32':
    ffmpeg_name = 'ffmpeg-windows.exe'
elif sys.platform == 'darwin':
    ffmpeg_name = 'ffmpeg-macos'
else:
    ffmpeg_name = 'ffmpeg-linux'

datas = []
ffmpeg_src = bin_dir / ffmpeg_name
if ffmpeg_src.exists():
    datas.append((str(ffmpeg_src), f'estenio/bin'))
else:
    print(f'WARNING: {ffmpeg_src} not found — run scripts/bundle-ffmpeg.sh first')

# ── Analysis ────────────────────────────────────────────────────────────────
a = Analysis(
    ['src/estenio/main.py'],
    pathex=['src'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'cv2',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

# ── Executable ──────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='estenio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
