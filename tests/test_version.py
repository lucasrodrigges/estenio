"""Tests for the user-visible package version."""

from estenio import __version__
from estenio.main import VERSION


def test_cli_version_uses_package_version():
    assert __version__ == "0.3.0"
    assert VERSION == __version__
