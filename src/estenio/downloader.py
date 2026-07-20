"""YouTube and Instagram download orchestration via yt-dlp subprocess."""

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse


# ---------------------------------------------------------------------------
# Error mapping — yt-dlp stderr patterns → user-friendly Portuguese messages
# ---------------------------------------------------------------------------

ERROR_MAP: list[tuple[str, str]] = [
    # YouTube
    ("Video unavailable", "Este vídeo está indisponível (pode ter sido removido ou ser privado)."),
    ("Private video", "Este vídeo é privado e não pode ser baixado."),
    ("This video is not available", "Este vídeo não está disponível."),
    ("This video has been removed", "Este vídeo foi removido do YouTube."),
    ("Sign in", "Este vídeo exige login (conteúdo restrito por idade ou privado)."),
    ("Incomplete YouTube ID", "Link inválido — o ID do vídeo está incompleto."),
    ("HTTP Error 403", "Acesso negado (403). O conteúdo pode estar bloqueado."),
    ("HTTP Error 404", "Conteúdo não encontrado (404). Verifique o link."),
    ("unable to download video", "Não foi possível baixar o vídeo. Verifique sua conexão."),
    ("Requested format is not available", "O formato solicitado não está disponível para este vídeo."),
    ("This video is only available for registered users", "Este vídeo exige que você esteja logado no YouTube."),
    # Instagram
    ("This page requires login", "Este conteúdo exige login no Instagram."),
    ("login required", "Este conteúdo exige login no Instagram. Faça login no navegador e tente novamente."),
    ("Private account", "Este perfil é privado — não é possível acessar os stories."),
    ("This account is private", "Este perfil é privado — não é possível acessar o conteúdo."),
    ("No valid URL", "Link inválido. Cole o link completo do Reels ou do perfil."),
    ("Unsupported URL", "Link não reconhecido. Certifique-se de que é um link válido do Instagram."),
    ("Story unavailable", "Este story não está mais disponível (expirou ou foi removido)."),
    ("No stories found", "Nenhum story encontrado para este perfil."),
    ("not found", "Conteúdo não encontrado. O link pode estar incorreto ou o conteúdo foi removido."),
    ("secretstorage", "Módulo secretstorage não instalado. Execute: pip install secretstorage"),
    ("ERROR:", None),  # catch-all — handled after specific patterns
]


def translate_error(stderr: str) -> str:
    """Map yt-dlp stderr to a user-friendly Portuguese error message."""
    for pattern, message in ERROR_MAP:
        if message is None:
            continue
        if pattern.lower() in stderr.lower():
            return message

    # Catch-all: if stderr has "ERROR:", extract first meaningful line
    for line in stderr.splitlines():
        if "ERROR:" in line:
            return f"Erro ao baixar: {line.strip()}"
    return "Ocorreu um erro inesperado ao baixar. Tente novamente."


# ---------------------------------------------------------------------------
# Browser detection for Instagram cookies
# ---------------------------------------------------------------------------

BROWSER_CANDIDATES = ["chrome", "chromium", "firefox", "brave", "edge", "opera", "vivaldi"]


def detect_browser() -> str | None:
    """Detect an installed browser with Instagram cookies.

    Priority: $BROWSER → xdg-settings → fallback candidates (Chrome first).

    Returns the yt-dlp browser name (e.g. 'chrome', 'firefox') or None.
    """
    # 1. $BROWSER environment variable
    browser_env = os.environ.get("BROWSER", "")
    if browser_env:
        for candidate in BROWSER_CANDIDATES:
            if candidate in browser_env.lower():
                if _find_browser_binary(candidate):
                    return candidate

    # 2. xdg-settings (freedesktop)
    try:
        result = subprocess.run(
            ["xdg-settings", "get", "default-web-browser"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            desktop = result.stdout.strip().lower()
            # Extract browser name directly from .desktop filename
            name = _resolve_from_desktop(desktop)
            if name:
                return name
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 3. Fallback: first installed among candidates (Chrome first)
    for candidate in BROWSER_CANDIDATES:
        if _find_browser_binary(candidate):
            return candidate

    return None


def _find_browser_binary(ytdlp_name: str) -> bool:
    """Check if a browser is installed, trying multiple binary names.

    yt-dlp browser names don't always match the binary name on PATH
    (e.g. yt-dlp uses 'chrome' but the binary is 'google-chrome-stable').
    """
    aliases: dict[str, list[str]] = {
        "chrome": ["google-chrome-stable", "google-chrome", "chrome"],
        "chromium": ["chromium-browser", "chromium"],
        "brave": ["brave-browser", "brave"],
        "edge": ["microsoft-edge", "edge"],
        "firefox": ["firefox"],
        "opera": ["opera"],
        "vivaldi": ["vivaldi"],
    }
    for candidate in aliases.get(ytdlp_name, [ytdlp_name]):
        if shutil.which(candidate):
            return True
    return False


def _resolve_from_desktop(desktop: str) -> str | None:
    """Extract yt-dlp browser name from a .desktop filename.

    Examples:
        google-chrome.desktop → chrome
        firefox.desktop → firefox
        chromium-browser.desktop → chromium
    """
    # Remove .desktop suffix if present
    name = desktop.replace(".desktop", "").strip()

    # Map known desktop names to yt-dlp names
    mapping = {
        "google-chrome": "chrome",
        "chromium-browser": "chromium",
        "brave-browser": "brave",
        "microsoft-edge": "edge",
        "opera": "opera",
        "vivaldi": "vivaldi",
    }

    browser = mapping.get(name, name)

    # Verify the browser is actually installed (checks multiple binary names)
    if _find_browser_binary(browser):
        return browser
    # Full desktop name partial match (e.g. google-chrome-stable.desktop)
    for key in mapping:
        if key in name and _find_browser_binary(mapping[key]):
            return mapping[key]
    return None


# ---------------------------------------------------------------------------
# URL classification and conversion
# ---------------------------------------------------------------------------

def _is_official_youtube_host(hostname: str | None) -> bool:
    """Return whether hostname belongs to YouTube without network access."""
    if not hostname:
        return False

    host = hostname.lower().rstrip(".")
    return host == "youtu.be" or host == "youtube.com" or host.endswith(".youtube.com")


def has_youtube_playlist_reference(url: str) -> bool:
    """Return whether an official YouTube URL has a non-empty ``list`` query."""
    parsed = urlparse(url.strip())
    if not _is_official_youtube_host(parsed.hostname):
        return False

    return any(value.strip() for value in parse_qs(
        parsed.query, keep_blank_values=True
    ).get("list", []))


def is_youtube_video_url(url: str) -> bool:
    """Return whether an official YouTube URL identifies a specific video."""
    parsed = urlparse(url.strip())
    if not _is_official_youtube_host(parsed.hostname):
        return False

    query = parse_qs(parsed.query, keep_blank_values=True)
    if any(value.strip() for value in query.get("v", [])):
        return True

    path_parts = [part for part in parsed.path.split("/") if part]
    host = (parsed.hostname or "").lower().rstrip(".")
    if host == "youtu.be":
        return bool(path_parts)

    return (
        len(path_parts) >= 2
        and path_parts[0].lower() in {"shorts", "live"}
        and bool(path_parts[1].strip())
    )


def is_youtube_video_with_playlist(url: str) -> bool:
    """Return whether URL identifies both one video and a playlist."""
    return is_youtube_video_url(url) and has_youtube_playlist_reference(url)


def get_youtube_channel_link_kind(url: str) -> str | None:
    """Classify an official YouTube channel URL as ``channel`` or ``section``."""
    parsed = urlparse(url.strip())
    if not _is_official_youtube_host(parsed.hostname):
        return None

    host = (parsed.hostname or "").lower().rstrip(".")
    if host == "youtu.be":
        return None

    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return None

    section_index: int | None = None
    if parts[0].startswith("@") and len(parts[0]) > 1:
        section_index = 1
    elif parts[0].lower() in {"channel", "c", "user"} and len(parts) >= 2:
        section_index = 2
    else:
        return None

    if len(parts) == section_index:
        return "channel"
    if (
        len(parts) == section_index + 1
        and parts[section_index].lower() in {"videos", "shorts", "streams"}
    ):
        return "section"
    return None


def convert_stories_url(url: str) -> str:
    """Convert a plain Instagram profile URL to the stories endpoint.

    instagram.com/fulano → instagram.com/stories/fulano/
    instagram.com/fulano/ → instagram.com/stories/fulano/
    Already a stories URL → return as-is.
    """
    # Already a stories URL
    if "/stories/" in url:
        return url

    # Strip trailing slash and path, then append /stories/username/
    cleaned = url.rstrip("/")
    # Extract username: last path segment after instagram.com/
    match = re.search(r"instagram\.com/([^/?]+)", cleaned)
    if match:
        username = match.group(1)
        return f"https://www.instagram.com/stories/{username}/"

    return url


# ---------------------------------------------------------------------------
# Command building
# ---------------------------------------------------------------------------

def build_command(
    source: str,
    download_type: str,
    audio_format: str | None,
    url: str,
    browser: str | None = None,
    download_scope: str | None = None,
) -> list[str]:
    """Build the yt-dlp command args for the given options.

    Args:
        source: Platform identifier ('youtube' or 'instagram').
        download_type: 'audio', 'video', 'reels', or 'stories'.
        audio_format: 'mp3' or 'wav' (ignored for video/reels/stories).
        url: The media URL.
        browser: Browser name for --cookies-from-browser (Instagram only).
        download_scope: YouTube scope: ``single``, ``playlist``, or None.

    Returns:
        Command as a list of strings ready for subprocess.run.
    """
    # --- Instagram ---
    if source == "instagram":
        cmd: list[str] = ["yt-dlp"]
        if browser:
            cmd.extend(["--cookies-from-browser", browser])
        cmd.append(url)
        return cmd

    # --- YouTube ---
    cmd = ["yt-dlp"]
    if download_scope == "single":
        cmd.append("--no-playlist")
    elif download_scope == "playlist":
        cmd.append("--yes-playlist")

    if download_type == "audio":
        cmd.extend([
            "-x",
            "--audio-format", audio_format or "mp3",
            "--audio-quality", "0",
        ])
        cmd.append(url)

    elif download_type == "video":
        cmd.extend([
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
        ])
        cmd.append(url)

    return cmd


# ---------------------------------------------------------------------------
# Download execution
# ---------------------------------------------------------------------------

def download(
    source: str,
    download_type: str,
    audio_format: str | None,
    url: str,
    browser: str | None = None,
    download_scope: str | None = None,
) -> str | None:
    """Execute the full download and return an error message or None on success.

    Returns:
        None if download succeeded, or a Portuguese error message string.
    """
    cmd = build_command(
        source, download_type, audio_format, url, browser, download_scope
    )

    # Show native progress and capture stderr for translated errors
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return translate_error(result.stderr)

    return None
