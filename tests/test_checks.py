"""Tests for dependency checks."""

from unittest.mock import patch

from estenio.checks import check_dependencies, all_present


def test_all_dependencies_present():
    """When both yt-dlp and ffmpeg are found, all results are present."""
    with patch("estenio.checks.shutil.which", return_value="/usr/bin/found"):
        results = check_dependencies()
        assert len(results) == 2
        assert all_present(results)
        assert all(r.present for r in results)


def test_ytdlp_missing():
    """When yt-dlp is missing, it's flagged."""
    def mock_which(cmd):
        if cmd == "ffmpeg":
            return "/usr/bin/ffmpeg"
        return None

    with patch("estenio.checks.shutil.which", side_effect=mock_which):
        results = check_dependencies()
        ytdl = next(r for r in results if r.name == "yt-dlp")
        ffmpeg_r = next(r for r in results if r.name == "ffmpeg")
        assert not ytdl.present
        assert ffmpeg_r.present
        assert not all_present(results)


def test_ffmpeg_missing():
    """When ffmpeg is missing, it's flagged."""
    def mock_which(cmd):
        if cmd == "yt-dlp":
            return "/usr/bin/yt-dlp"
        return None

    with patch("estenio.checks.shutil.which", side_effect=mock_which):
        results = check_dependencies()
        ytdl = next(r for r in results if r.name == "yt-dlp")
        ffmpeg_r = next(r for r in results if r.name == "ffmpeg")
        assert ytdl.present
        assert not ffmpeg_r.present
        assert not all_present(results)


def test_both_missing():
    """When neither is found, both are flagged."""
    with patch("estenio.checks.shutil.which", return_value=None):
        results = check_dependencies()
        assert len(results) == 2
        assert not all_present(results)
        assert not any(r.present for r in results)
