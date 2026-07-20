"""Tests for the self-update command."""

from estenio import updater


def test_build_update_command_uses_current_python_and_parent_pid():
    command = updater.build_update_command(
        parent_pid=1234,
        python_executable="C:/Estenio/venv/Scripts/python.exe",
    )

    assert command[0] == "C:/Estenio/venv/Scripts/python.exe"
    assert command[1] == "-c"
    assert command[-2] == "1234"
    assert command[-1] == updater.PACKAGE_URL
    assert '"--upgrade"' in command[2]
    assert '"--force-reinstall"' in command[2]
    assert '"--no-cache-dir"' in command[2]


def test_start_update_spawns_helper(monkeypatch):
    captured = {}

    class FakeProcess:
        pass

    def fake_popen(command):
        captured["command"] = command
        return FakeProcess()

    monkeypatch.setattr(updater.subprocess, "Popen", fake_popen)

    error = updater.start_update()

    assert error is None
    assert captured["command"][0] == updater.sys.executable


def test_start_update_returns_readable_error(monkeypatch):
    def fake_popen(command):
        raise OSError("blocked")

    monkeypatch.setattr(updater.subprocess, "Popen", fake_popen)

    assert updater.start_update() == "Não foi possível iniciar a atualização: blocked"
