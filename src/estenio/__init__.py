"""Estenio — interactive media downloader."""

import os
import sys
from pathlib import Path


def _get_ffmpeg_path() -> str | None:
    """Return the path to the bundled ffmpeg binary, or None if not bundled.

    When running from a PyInstaller bundle (sys.frozen), looks inside the
    temp extraction directory (sys._MEIPASS). Otherwise, looks in the
    package's own bin/ directory.

    Platform-appropriate binary names:
        Linux:   ffmpeg-linux
        macOS:   ffmpeg-macos
        Windows: ffmpeg-windows.exe

    Returns:
        Absolute path to ffmpeg binary, or None if not found.
    """
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).parent

    if sys.platform == 'win32':
        binary = 'ffmpeg-windows.exe'
    elif sys.platform == 'darwin':
        binary = 'ffmpeg-macos'
    else:
        binary = 'ffmpeg-linux'

    candidate = base / 'bin' / binary
    if candidate.exists():
        os.chmod(candidate, 0o755)
        return str(candidate)
    return None
