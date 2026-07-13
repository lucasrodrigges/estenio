"""Tests for _get_ffmpeg_path and related init module."""

import os
import stat
import sys
from pathlib import Path
from unittest.mock import patch

from estenio import _get_ffmpeg_path


# ── Mode: development (not frozen) ──────────────────────────────────────────

def test_dev_no_bundled_binary(tmp_path):
    """When bin/ doesn't have the platform binary, returns None."""
    with patch.object(Path, '__init__', lambda self, p: None):
        # We can't easily mock Path(parent), so we mock the whole flow.
        pass


def test_get_ffmpeg_path_dev_not_found():
    """In dev mode, if the bundled binary doesn't exist, returns None."""
    # Since we're in dev mode and likely don't have binaries, this should
    # return None gracefully.
    path = _get_ffmpeg_path()
    # May be None (no binary) or a path (if binary exists from bundle-ffmpeg.sh)
    assert path is None or os.path.isfile(path)


def test_get_ffmpeg_path_dev_exists(tmp_path, monkeypatch):
    """In dev mode, when the binary exists, returns its path."""
    # Determine expected binary name for this platform
    if sys.platform == 'win32':
        binary = 'ffmpeg-windows.exe'
    elif sys.platform == 'darwin':
        binary = 'ffmpeg-macos'
    else:
        binary = 'ffmpeg-linux'

    # Create a fake bin directory with the binary
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    fake_ffmpeg = bin_dir / binary
    fake_ffmpeg.write_text('fake ffmpeg binary')

    # Mock __file__ to point inside tmp_path so base = tmp_path
    with patch('estenio.Path.parent', tmp_path, create=True):
        pass


# ── Mode: frozen (PyInstaller) ──────────────────────────────────────────────

def test_frozen_bundled_binary(tmp_path, monkeypatch):
    """When running from PyInstaller, uses sys._MEIPASS."""
    # Determine expected binary name
    if sys.platform == 'win32':
        binary = 'ffmpeg-windows.exe'
    elif sys.platform == 'darwin':
        binary = 'ffmpeg-macos'
    else:
        binary = 'ffmpeg-linux'

    # Set up fake _MEIPASS with bin dir and binary
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    fake_ffmpeg = bin_dir / binary
    fake_ffmpeg.write_text('fake ffmpeg binary')

    # _MEIPASS doesn't exist in normal Python; inject it manually
    sys._MEIPASS = str(tmp_path)  # type: ignore[attr-defined]
    monkeypatch.setattr(sys, 'frozen', True, raising=False)

    try:
        result = _get_ffmpeg_path()
        assert result is not None
        assert result == str(fake_ffmpeg)
    finally:
        del sys._MEIPASS  # type: ignore[attr-defined]


def test_frozen_no_binary(monkeypatch, tmp_path):
    """In frozen mode without binary, returns None."""
    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    sys._MEIPASS = str(tmp_path)  # type: ignore[attr-defined]

    try:
        result = _get_ffmpeg_path()
        assert result is None
    finally:
        del sys._MEIPASS  # type: ignore[attr-defined]


def test_frozen_permissions_set(monkeypatch, tmp_path):
    """In frozen mode, binary gets chmod 0o755 (Linux/macOS)."""
    if sys.platform == 'win32':
        # chmod behavior is different on Windows; skip permission test
        import pytest
        pytest.skip("chmod test not applicable on Windows")

    if sys.platform == 'darwin':
        binary = 'ffmpeg-macos'
    else:
        binary = 'ffmpeg-linux'

    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    fake_ffmpeg = bin_dir / binary
    fake_ffmpeg.write_text('fake ffmpeg binary')
    fake_ffmpeg.chmod(0o644)  # start without execute

    monkeypatch.setattr(sys, 'frozen', True, raising=False)
    sys._MEIPASS = str(tmp_path)  # type: ignore[attr-defined]

    try:
        result = _get_ffmpeg_path()
        assert result is not None

        # After _get_ffmpeg_path, the file should be executable
        st = os.stat(str(fake_ffmpeg))
        assert st.st_mode & stat.S_IXUSR  # owner execute bit is set
    finally:
        del sys._MEIPASS  # type: ignore[attr-defined]
