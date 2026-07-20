"""Regression tests for reliable installer upgrades."""

from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_windows_reinstall_forces_fresh_github_package():
    installer = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")

    assert "--upgrade --force-reinstall --no-cache-dir" in installer
    assert "estenio/archive/refs/heads/main.zip" in installer


def test_unix_reinstall_forces_fresh_github_package():
    installer = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")

    assert "--upgrade --force-reinstall --no-cache-dir" in installer
    assert "git+https://github.com/lucasrodrigges/estenio.git" in installer
