"""Interactive prompt steps for Estenio."""

import questionary


def ask_source() -> str:
    """Ask which platform to download from."""
    return questionary.select(
        "O que você quer baixar?",
        choices=[
            questionary.Choice("YouTube", value="youtube"),
            questionary.Choice("Instagram", value="instagram"),
        ],
    ).unsafe_ask()


def ask_type(source: str) -> str:
    """Ask what type of media to download. Options depend on the source."""
    if source == "instagram":
        return questionary.select(
            "Tipo de download:",
            choices=[
                questionary.Choice("Reels (link único)", value="reels"),
                questionary.Choice("Stories (link do perfil)", value="stories"),
            ],
        ).unsafe_ask()

    # YouTube
    return questionary.select(
        "Tipo de download:",
        choices=[
            questionary.Choice("Apenas áudio", value="audio"),
            questionary.Choice("Vídeo (MP4 com áudio)", value="video"),
            questionary.Choice("Ambos (vídeo + áudio separados)", value="both"),
        ],
    ).unsafe_ask()


def ask_format(download_type: str) -> str:
    """Ask the output format.

    For 'video' and Instagram types, format is implicit — skipped by caller.
    For 'audio' and 'both', we ask the audio format.

    Returns the format string: 'mp3', 'wav', or 'mp4'.
    """
    if download_type in ("video", "reels", "stories"):
        return "mp4"

    return questionary.select(
        "Formato do áudio:",
        choices=[
            questionary.Choice("MP3", value="mp3"),
            questionary.Choice("WAV", value="wav"),
        ],
    ).unsafe_ask()


def ask_url(source: str, download_type: str) -> str:
    """Ask for the media URL. Prompt text adapts to source and type."""
    if source == "instagram":
        if download_type == "reels":
            prompt = "Link do Reels:"
        else:
            prompt = "Link do perfil:"
    else:
        prompt = "Link do YouTube:"

    return questionary.text(
        prompt,
        validate=lambda text: True if text.strip() else "Digite um link válido",
    ).unsafe_ask()
