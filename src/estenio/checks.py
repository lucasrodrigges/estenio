"""Pre-flight dependency checks for Estenio."""

import shutil
from dataclasses import dataclass

from estenio import _get_ffmpeg_path


@dataclass
class Dependency:
    name: str          # display name
    binary: str        # executable to look for
    install_cmd: str   # how to install it
    bundled: bool = False  # True if bundled with the app


DEPENDENCIES = [
    Dependency(
        name="yt-dlp",
        binary="yt-dlp",
        install_cmd="pip install yt-dlp",
    ),
    Dependency(
        name="ffmpeg",
        binary="ffmpeg",
        install_cmd="sudo apt install ffmpeg   # Ubuntu/Debian\n"
                     "brew install ffmpeg        # macOS",
    ),
]


@dataclass
class CheckResult:
    name: str          # dependency display name
    present: bool      # True if found
    install_cmd: str   # install instructions
    bundled: bool = False  # True if using bundled version


def check_dependencies() -> list[CheckResult]:
    """Check all required external dependencies.

    Checks bundled ffmpeg first (via _get_ffmpeg_path), then falls back
    to the system PATH. This allows PyInstaller bundles to ship their
    own ffmpeg while also supporting pip-installed usage.

    Returns:
        List of CheckResult, one per dependency.
        Caller should check .present on each.
    """
    results: list[CheckResult] = []
    for dep in DEPENDENCIES:
        if dep.name == "ffmpeg":
            # Check bundled ffmpeg first
            bundled_path = _get_ffmpeg_path()
            if bundled_path:
                results.append(CheckResult(
                    name=dep.name,
                    present=True,
                    install_cmd=dep.install_cmd,
                    bundled=True,
                ))
                continue
            # Fallback to system PATH
            found = shutil.which(dep.binary) is not None
            results.append(CheckResult(
                name=dep.name,
                present=found,
                install_cmd=dep.install_cmd,
            ))
        else:
            found = shutil.which(dep.binary) is not None
            results.append(CheckResult(
                name=dep.name,
                present=found,
                install_cmd=dep.install_cmd,
            ))
    return results


def all_present(results: list[CheckResult]) -> bool:
    """Return True if every dependency is present."""
    return all(r.present for r in results)
