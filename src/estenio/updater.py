"""Self-update orchestration for an installed Estenio environment."""

import os
import subprocess
import sys


PACKAGE_URL = "https://github.com/lucasrodrigges/estenio/archive/refs/heads/main.zip"

_UPDATE_HELPER = r'''
import os
import subprocess
import sys
import time

parent_pid = int(sys.argv[1])
package_url = sys.argv[2]


def parent_is_running():
    if os.name == "nt":
        import ctypes

        synchronize = 0x00100000
        handle = ctypes.windll.kernel32.OpenProcess(synchronize, False, parent_pid)
        if not handle:
            return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True

    try:
        os.kill(parent_pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


while parent_is_running():
    time.sleep(0.2)

print("\nAtualizando o Estenio...", flush=True)
command = [
    sys.executable,
    "-m",
    "pip",
    "install",
    "--upgrade",
    "--force-reinstall",
    "--no-cache-dir",
    package_url,
]
result = subprocess.run(command)
if result.returncode == 0:
    version_result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from importlib.metadata import version; print(version('estenio'))",
        ],
        capture_output=True,
        text=True,
    )
    installed_version = version_result.stdout.strip()
    print("\nEstenio atualizado com sucesso!", flush=True)
    if installed_version:
        print(f"Versão instalada: {installed_version}", flush=True)
else:
    print("\nNão foi possível atualizar o Estenio.", flush=True)
    print("Execute novamente com uma conexão ativa ou use o instalador oficial.", flush=True)
'''


def build_update_command(
    parent_pid: int | None = None,
    python_executable: str | None = None,
) -> list[str]:
    """Build the detached helper command that updates after this process exits."""
    return [
        python_executable or sys.executable,
        "-c",
        _UPDATE_HELPER,
        str(parent_pid or os.getpid()),
        PACKAGE_URL,
    ]


def start_update() -> str | None:
    """Start the update helper, returning a readable error or None."""
    try:
        subprocess.Popen(build_update_command())
    except OSError as error:
        return f"Não foi possível iniciar a atualização: {error}"
    return None
