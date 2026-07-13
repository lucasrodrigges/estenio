#!/usr/bin/env bash
# bundle-ffmpeg.sh — Download static ffmpeg binaries.
#
# Usage:
#   bash scripts/bundle-ffmpeg.sh              # current platform only
#   bash scripts/bundle-ffmpeg.sh --all        # all platforms
#   bash scripts/bundle-ffmpeg.sh linux        # specific platform
#   bash scripts/bundle-ffmpeg.sh macos windows
#
# Sources:  Official static builds (same ones yt-dlp recommends)

set -euo pipefail

BIN_DIR="$(cd "$(dirname "$0")/../src/estenio/bin" && pwd)"
mkdir -p "$BIN_DIR"

# ── Parse args ───────────────────────────────────────────────────────────────
PLATFORMS=()

if [ $# -eq 0 ]; then
    # Default: current platform
    case "$(uname -s)" in
        Linux)  PLATFORMS=(linux) ;;
        Darwin) PLATFORMS=(macos) ;;
        MINGW*|MSYS*|CYGWIN*) PLATFORMS=(windows) ;;
        *) echo "ERRO: sistema não reconhecido" >&2; exit 1 ;;
    esac
else
    for arg in "$@"; do
        case "$arg" in
            --all) PLATFORMS=(linux macos windows); break ;;
            linux|macos|windows) PLATFORMS+=("$arg") ;;
            *) echo "ERRO: plataforma inválida '$arg'. Use: linux, macos, windows, --all" >&2; exit 1 ;;
        esac
    done
fi

# ── Download functions ───────────────────────────────────────────────────────

_download_linux() {
    local url="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
    local tarball="/tmp/ffmpeg-linux.tar.xz"

    echo "⬇  Baixando ffmpeg Linux..."
    curl -sSL --retry 3 -o "$tarball" "$url"

    echo "   Extraindo..."
    tar -xf "$tarball" -C /tmp/
    cp "/tmp/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg" "$BIN_DIR/ffmpeg-linux"
    chmod +x "$BIN_DIR/ffmpeg-linux"
    rm -rf "/tmp/ffmpeg-master-latest-linux64-gpl" "$tarball"
    echo "   ✅ ffmpeg-linux ($(du -h "$BIN_DIR/ffmpeg-linux" | cut -f1))"
}

_download_macos() {
    local url="https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
    local zipfile="/tmp/ffmpeg-macos.zip"

    echo "⬇  Baixando ffmpeg macOS..."
    curl -sSL --retry 3 -o "$zipfile" "$url"

    echo "   Extraindo..."
    unzip -oq "$zipfile" -d /tmp/ffmpeg-macos-extract/
    cp "/tmp/ffmpeg-macos-extract/ffmpeg" "$BIN_DIR/ffmpeg-macos"
    chmod +x "$BIN_DIR/ffmpeg-macos"
    rm -rf "/tmp/ffmpeg-macos-extract" "$zipfile"
    echo "   ✅ ffmpeg-macos ($(du -h "$BIN_DIR/ffmpeg-macos" | cut -f1))"
}

_download_windows() {
    local url="https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    local zipfile="/tmp/ffmpeg-windows.zip"

    echo "⬇  Baixando ffmpeg Windows..."
    curl -sSL --retry 3 -o "$zipfile" "$url"

    echo "   Extraindo..."
    unzip -oq "$zipfile" -d /tmp/ffmpeg-windows-extract/
    local extract_dir
    extract_dir=$(ls -d /tmp/ffmpeg-windows-extract/ffmpeg-* 2>/dev/null | head -1)
    cp "$extract_dir/bin/ffmpeg.exe" "$BIN_DIR/ffmpeg-windows.exe"
    rm -rf "/tmp/ffmpeg-windows-extract" "$zipfile"
    echo "   ✅ ffmpeg-windows.exe ($(du -h "$BIN_DIR/ffmpeg-windows.exe" | cut -f1))"
}

# ── Execute ──────────────────────────────────────────────────────────────────
for plat in "${PLATFORMS[@]}"; do
    case "$plat" in
        linux)   _download_linux ;;
        macos)   _download_macos ;;
        windows) _download_windows ;;
    esac
done

echo ""
echo "✅ Binários ffmpeg em: $BIN_DIR"
ls -lh "$BIN_DIR/"
