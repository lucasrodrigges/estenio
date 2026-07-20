"""Tests for conditional orchestration in the interactive main loop."""

import importlib

import pytest

main_module = importlib.import_module("estenio.main")


def _prepare_main(monkeypatch, first_source="youtube"):
    sources = iter([first_source])

    def ask_source():
        try:
            return next(sources)
        except StopIteration:
            raise KeyboardInterrupt

    monkeypatch.setattr(main_module, "check_dependencies", lambda: [])
    monkeypatch.setattr(main_module, "all_present", lambda results: True)
    monkeypatch.setattr(main_module, "show_banner", lambda: None)
    monkeypatch.setattr(main_module.console, "print", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module.sys, "argv", ["estenio"])
    monkeypatch.setattr(main_module, "ask_source", ask_source)
    monkeypatch.setattr(main_module, "ask_type", lambda source: "video")
    monkeypatch.setattr(main_module, "ask_format", lambda download_type: "mp4")


def test_update_flag_starts_update_before_dependency_checks(monkeypatch):
    monkeypatch.setattr(main_module.sys, "argv", ["estenio", "--update"])
    monkeypatch.setattr(main_module, "start_update", lambda: None, raising=False)
    monkeypatch.setattr(
        main_module,
        "check_dependencies",
        lambda: pytest.fail("dependency checks must not run during update"),
    )
    monkeypatch.setattr(main_module.console, "print", lambda *args, **kwargs: None)

    with pytest.raises(SystemExit) as exc:
        main_module.main()

    assert exc.value.code == 0


def test_channel_cancellation_returns_to_start_without_download(monkeypatch):
    _prepare_main(monkeypatch)
    monkeypatch.setattr(
        main_module,
        "ask_url",
        lambda source, download_type: "https://youtube.com/@creator?list=PL123",
    )
    monkeypatch.setattr(
        main_module,
        "ask_channel_download_confirmation",
        lambda is_section=False: False,
    )

    def unexpected_download(*args, **kwargs):
        pytest.fail("download must not run after channel cancellation")

    monkeypatch.setattr(main_module, "download", unexpected_download)

    with pytest.raises(SystemExit) as exc:
        main_module.main()
    assert exc.value.code == 0


def test_hybrid_link_scope_reaches_downloader(monkeypatch):
    _prepare_main(monkeypatch)
    monkeypatch.setattr(
        main_module,
        "ask_url",
        lambda source, download_type: (
            "https://youtube.com/watch?v=abc&list=PL123"
        ),
    )
    monkeypatch.setattr(main_module, "ask_youtube_download_scope", lambda: "single")
    captured = {}

    def fake_download(*args):
        captured["args"] = args
        return None

    monkeypatch.setattr(main_module, "download", fake_download)

    with pytest.raises(SystemExit):
        main_module.main()

    assert captured["args"][-1] == "single"


def test_playlist_only_link_uses_playlist_scope_without_scope_prompt(monkeypatch):
    _prepare_main(monkeypatch)
    monkeypatch.setattr(
        main_module,
        "ask_url",
        lambda source, download_type: "https://youtube.com/playlist?list=PL123",
    )
    monkeypatch.setattr(
        main_module,
        "ask_youtube_download_scope",
        lambda: pytest.fail("playlist-only links must not ask single versus playlist"),
    )
    captured = {}

    def fake_download(*args):
        captured["args"] = args
        return None

    monkeypatch.setattr(main_module, "download", fake_download)

    with pytest.raises(SystemExit):
        main_module.main()

    assert captured["args"][-1] == "playlist"
