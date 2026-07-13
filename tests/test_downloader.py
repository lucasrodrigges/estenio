"""Tests for downloader: command building, error mapping, browser detection, URL conversion."""

import subprocess

import pytest

from estenio.downloader import (
    build_command,
    translate_error,
    download,
    detect_browser,
    convert_stories_url,
)


# ── build_command ────────────────────────────────────────────────────────────

def test_build_audio_mp3():
    cmd = build_command("youtube", "audio", "mp3", "https://youtube.com/watch?v=abc")
    assert cmd[0] == "yt-dlp"
    assert "-x" in cmd
    assert "--audio-format" in cmd
    assert "mp3" in cmd
    assert "--audio-quality" in cmd
    assert "0" in cmd
    assert cmd[-1] == "https://youtube.com/watch?v=abc"


def test_build_audio_wav():
    cmd = build_command("youtube", "audio", "wav", "https://youtube.com/watch?v=abc")
    assert "wav" in cmd


def test_build_video():
    cmd = build_command("youtube", "video", None, "https://youtube.com/watch?v=abc")
    assert cmd[0] == "yt-dlp"
    assert "-f" in cmd
    assert "--merge-output-format" in cmd
    assert "mp4" in cmd
    assert cmd[-1] == "https://youtube.com/watch?v=abc"


def test_build_both():
    cmd = build_command("youtube", "both", "mp3", "https://youtube.com/watch?v=abc")
    assert ";;;" in cmd
    sep = cmd.index(";;;")
    video_cmd = cmd[:sep]
    audio_cmd = cmd[sep + 1:]
    assert video_cmd[0] == "yt-dlp"
    assert "-f" in video_cmd
    assert audio_cmd[0] == "yt-dlp"
    assert "-x" in audio_cmd
    assert "mp3" in audio_cmd
    assert audio_cmd[-1] == "https://youtube.com/watch?v=abc"


# ── build_command: Instagram ─────────────────────────────────────────────────

def test_build_instagram_reels():
    cmd = build_command(
        "instagram", "reels", None,
        "https://instagram.com/reel/abc123/",
        browser="firefox",
    )
    assert cmd[0] == "yt-dlp"
    assert "--cookies-from-browser" in cmd
    assert "firefox" in cmd
    assert cmd[-1] == "https://instagram.com/reel/abc123/"


def test_build_instagram_stories():
    cmd = build_command(
        "instagram", "stories", None,
        "https://instagram.com/stories/fulano/",
        browser="chrome",
    )
    assert cmd[0] == "yt-dlp"
    assert "--cookies-from-browser" in cmd
    assert "chrome" in cmd
    assert cmd[-1] == "https://instagram.com/stories/fulano/"


def test_build_instagram_no_browser():
    """If browser is None, --cookies-from-browser is omitted."""
    cmd = build_command(
        "instagram", "reels", None,
        "https://instagram.com/reel/abc123/",
        browser=None,
    )
    assert "--cookies-from-browser" not in cmd


# ── translate_error ──────────────────────────────────────────────────────────

def test_translate_video_unavailable():
    msg = translate_error("ERROR: [youtube] abc: Video unavailable")
    assert "indisponível" in msg.lower()


def test_translate_private_video():
    msg = translate_error("ERROR: Private video. Sign in if you've been granted access")
    assert "privado" in msg.lower()


def test_translate_404():
    msg = translate_error("HTTP Error 404: Not Found")
    assert "404" in msg.lower() or "não encontrado" in msg.lower()


def test_translate_invalid_id():
    msg = translate_error("ERROR: Incomplete YouTube ID")
    assert "inválido" in msg.lower() or "incompleto" in msg.lower()


def test_translate_generic_error():
    msg = translate_error("ERROR: Something unexpected happened")
    assert "erro" in msg.lower()


def test_translate_empty_stderr():
    msg = translate_error("")
    assert "inesperado" in msg.lower()


# ── translate_error: Instagram ───────────────────────────────────────────────

def test_translate_instagram_login_required():
    msg = translate_error("ERROR: This page requires login")
    assert "login" in msg.lower()


def test_translate_instagram_private_account():
    msg = translate_error("ERROR: This account is private")
    assert "privado" in msg.lower()


def test_translate_instagram_story_unavailable():
    msg = translate_error("Story unavailable")
    assert "story" in msg.lower() or "disponível" in msg.lower()


def test_translate_instagram_no_stories():
    msg = translate_error("No stories found")
    assert "story" in msg.lower() or "encontrado" in msg.lower()


def test_translate_instagram_invalid_url():
    msg = translate_error("No valid URL")
    assert "inválido" in msg.lower()


# ── download (integration with mock) ─────────────────────────────────────────

def test_download_audio_success(monkeypatch):
    def mock_run(cmd, stderr, text):
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)
    error = download("youtube", "audio", "mp3", "https://youtube.com/watch?v=abc")
    assert error is None


def test_download_video_failure(monkeypatch):
    def mock_run(cmd, stderr, text):
        return subprocess.CompletedProcess(
            args=cmd, returncode=1, stdout="",
            stderr="ERROR: [youtube] abc: Video unavailable"
        )

    monkeypatch.setattr(subprocess, "run", mock_run)
    error = download("youtube", "video", None, "https://youtube.com/watch?v=abc")
    assert error is not None
    assert "indisponível" in error.lower()


def test_download_both_success(monkeypatch):
    def mock_run(cmd, stderr, text):
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)
    error = download("youtube", "both", "mp3", "https://youtube.com/watch?v=abc")
    assert error is None


def test_download_both_first_fails(monkeypatch):
    call_count = [0]

    def mock_run(cmd, stderr, text):
        call_count[0] += 1
        if call_count[0] == 1:
            return subprocess.CompletedProcess(
                args=cmd, returncode=1, stdout="",
                stderr="ERROR: Private video"
            )
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)
    error = download("youtube", "both", "mp3", "https://youtube.com/watch?v=abc")
    assert error is not None
    assert "privado" in error.lower()
    assert call_count[0] == 1


def test_download_instagram_reels_success(monkeypatch):
    def mock_run(cmd, stderr, text):
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)
    error = download(
        "instagram", "reels", None,
        "https://instagram.com/reel/abc/",
        browser="firefox",
    )
    assert error is None


def test_download_instagram_stories_failure(monkeypatch):
    def mock_run(cmd, stderr, text):
        return subprocess.CompletedProcess(
            args=cmd, returncode=1, stdout="",
            stderr="This page requires login",
        )

    monkeypatch.setattr(subprocess, "run", mock_run)
    error = download(
        "instagram", "stories", None,
        "https://instagram.com/stories/fulano/",
        browser="firefox",
    )
    assert error is not None
    assert "login" in error.lower()


# ── detect_browser ───────────────────────────────────────────────────────────

def test_detect_browser_from_env(monkeypatch):
    """$BROWSER=firefox + firefox in PATH → returns 'firefox'."""
    monkeypatch.setenv("BROWSER", "firefox")
    monkeypatch.setattr(subprocess, "run", _no_xdg_found)  # block xdg-settings
    import shutil as shutil_mod
    monkeypatch.setattr(shutil_mod, "which", lambda name: name if name == "firefox" else None)
    assert detect_browser() == "firefox"


def test_detect_browser_fallback_first_installed(monkeypatch):
    """No env, no xdg → first candidate on PATH wins."""
    monkeypatch.delenv("BROWSER", raising=False)
    monkeypatch.setattr(subprocess, "run", _no_xdg_found)
    import shutil as shutil_mod
    monkeypatch.setattr(
        shutil_mod, "which",
        lambda name: name if name in ("chrome", "chromium") else None,
    )
    # firefox not found, chrome found → chrome
    assert detect_browser() == "chrome"


def test_detect_browser_none_found(monkeypatch):
    """No browsers installed → None."""
    monkeypatch.delenv("BROWSER", raising=False)
    monkeypatch.setattr(subprocess, "run", _no_xdg_found)
    import shutil as shutil_mod
    monkeypatch.setattr(shutil_mod, "which", lambda name: None)
    assert detect_browser() is None


def _no_xdg_found(*args, **kwargs):
    raise FileNotFoundError("xdg-settings not found")


# ── convert_stories_url ──────────────────────────────────────────────────────

def test_convert_plain_profile():
    result = convert_stories_url("https://instagram.com/fulano")
    assert result == "https://www.instagram.com/stories/fulano/"


def test_convert_profile_with_trailing_slash():
    result = convert_stories_url("https://instagram.com/fulano/")
    assert result == "https://www.instagram.com/stories/fulano/"


def test_convert_already_stories():
    result = convert_stories_url("https://instagram.com/stories/fulano/")
    assert result == "https://instagram.com/stories/fulano/"


def test_convert_with_query_params():
    result = convert_stories_url("https://instagram.com/fulano?utm=something")
    assert result == "https://www.instagram.com/stories/fulano/"


def test_convert_www_variant():
    result = convert_stories_url("https://www.instagram.com/fulano/")
    assert result == "https://www.instagram.com/stories/fulano/"
