"""Pre-flight dependency checks for Estenio."""

import shutil
from dataclasses import dataclass


@dataclass
class Dependency:
    name: str          # display name
    binary: str        # executable to look for
    install_cmd: str   # how to install it


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


def check_dependencies() -> list[CheckResult]:
    """Check all required external dependencies on the system PATH.

    Returns:
        List of CheckResult, one per dependency.
        Caller should check .present on each.
    """
    return [
        CheckResult(
            name=dep.name,
            present=shutil.which(dep.binary) is not None,
            install_cmd=dep.install_cmd,
        )
        for dep in DEPENDENCIES
    ]


def all_present(results: list[CheckResult]) -> bool:
    """Return True if every dependency is present."""
    return all(r.present for r in results)
