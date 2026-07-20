"""Tests for interactive prompt steps.

These tests validate the structure of the questionary prompts —
choices, values, and conditional behavior. We mock questionary.select
and questionary.text to return inspectable result objects instead of
triggering real interactive prompts.
"""

import pytest

from estenio.steps import (
    ask_source,
    ask_type,
    ask_format,
    ask_url,
    ask_youtube_download_scope,
    ask_channel_download_confirmation,
)


# ── helpers ──────────────────────────────────────────────────────────────────

class _SelectResult:
    """Mimics a questionary.select(...).unsafe_ask() result."""
    def __init__(self, choices, message):
        self.choices = choices
        self.message = message


class _TextResult:
    """Mimics a questionary.text(...).unsafe_ask() result."""
    def __init__(self, message, validate):
        self.message = message
        self._validate = validate


def _mock_select(message, choices):
    """Return a mock that has .unsafe_ask() returning our inspectable result."""
    result = _SelectResult(choices, message)

    class MockQuestion:
        def unsafe_ask(self):
            return result

    return MockQuestion()


def _mock_text(message, validate):
    """Return a mock that has .unsafe_ask() returning our inspectable result."""
    result = _TextResult(message, validate)

    class MockQuestion:
        def unsafe_ask(self):
            return result

    return MockQuestion()


# ── ask_source ───────────────────────────────────────────────────────────────

def test_ask_source_choices(monkeypatch):
    """ask_source offers YouTube and Instagram as active choices."""
    monkeypatch.setattr("estenio.steps.questionary.select", _mock_select)
    result = ask_source()
    values = [c.value for c in result.choices if hasattr(c, 'value')]
    assert "youtube" in values
    assert "instagram" in values


# ── ask_type ─────────────────────────────────────────────────────────────────

def test_ask_type_youtube(monkeypatch):
    """YouTube source returns only audio/video."""
    monkeypatch.setattr("estenio.steps.questionary.select", _mock_select)
    result = ask_type("youtube")
    values = [c.value for c in result.choices if hasattr(c, 'value')]
    assert "audio" in values
    assert "video" in values
    assert "both" not in values
    assert "reels" not in values
    assert "stories" not in values


def test_ask_type_instagram(monkeypatch):
    """Instagram source returns reels/stories."""
    monkeypatch.setattr("estenio.steps.questionary.select", _mock_select)
    result = ask_type("instagram")
    values = [c.value for c in result.choices if hasattr(c, 'value')]
    assert "reels" in values
    assert "stories" in values
    assert "audio" not in values
    assert "video" not in values
    assert "both" not in values


# ── ask_format ───────────────────────────────────────────────────────────────

def test_ask_format_video_returns_mp4():
    """Video type returns mp4 without prompting."""
    assert ask_format("video") == "mp4"


def test_ask_format_reels_returns_mp4():
    """Reels type returns mp4 without prompting."""
    assert ask_format("reels") == "mp4"


def test_ask_format_stories_returns_mp4():
    """Stories type returns mp4 without prompting."""
    assert ask_format("stories") == "mp4"


def test_ask_format_audio_prompts(monkeypatch):
    """Audio type shows mp3/wav choices."""
    monkeypatch.setattr("estenio.steps.questionary.select", _mock_select)
    result = ask_format("audio")
    values = [c.value for c in result.choices if hasattr(c, 'value')]
    assert "mp3" in values
    assert "wav" in values


# ── conditional YouTube prompts ─────────────────────────────────────────────

def test_ask_youtube_download_scope_defaults_to_single(monkeypatch):
    monkeypatch.setattr("estenio.steps.questionary.select", _mock_select)
    result = ask_youtube_download_scope()
    values = [choice.value for choice in result.choices]
    assert values == ["single", "playlist"]
    assert "playlist" in result.message.lower()


def test_ask_channel_confirmation_defaults_to_continue(monkeypatch):
    monkeypatch.setattr("estenio.steps.questionary.select", _mock_select)
    result = ask_channel_download_confirmation()
    values = [choice.value for choice in result.choices]
    assert values == [True, False]
    assert "todos os vídeos" in result.message.lower()


def test_ask_channel_section_confirmation_uses_section_text(monkeypatch):
    monkeypatch.setattr("estenio.steps.questionary.select", _mock_select)
    result = ask_channel_download_confirmation(is_section=True)
    assert "seção" in result.message.lower()


# ── ask_url ──────────────────────────────────────────────────────────────────

def test_ask_url_youtube(monkeypatch):
    """YouTube prompt says 'Link do YouTube'."""
    monkeypatch.setattr("estenio.steps.questionary.text", _mock_text)
    result = ask_url("youtube", "video")
    assert "YouTube" in result.message


def test_ask_url_instagram_reels(monkeypatch):
    """Instagram Reels prompt says 'Link do Reels'."""
    monkeypatch.setattr("estenio.steps.questionary.text", _mock_text)
    result = ask_url("instagram", "reels")
    assert "Reels" in result.message


def test_ask_url_instagram_stories(monkeypatch):
    """Instagram Stories prompt says 'Link do perfil'."""
    monkeypatch.setattr("estenio.steps.questionary.text", _mock_text)
    result = ask_url("instagram", "stories")
    assert "perfil" in result.message.lower()
