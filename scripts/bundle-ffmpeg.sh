#!/usr/bin/env bash
# bundle-ffmpeg.sh — Download static ffmpeg binaries for all platforms.
#
# Usage:   bash scripts/bundle-ffmpeg.sh
# Output:  src/estenio/bin/ffmpeg-linux
#          src/estenio/bin/ffmpeg-macos
#          src/estenio/bin/ffmpeg-windows.exe
#
# Sources:  Official static builds from ffmpeg.org / BtbN / gyan.dev
#            (these are the same builds yt-dlp recommends)

set -euo pipefail

BIN_DIR="$(cd "$(dirname "$0")/../src/estenio/bin" && pwd)"
mkdir -p "$BIN_DIR"

# ── Linux (amd64) ────────────────────────────────────────────────────────────
# BtbN static build — widely used, updated regularly
LINUX_URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
LINUX_TARBALL="/tmp/ffmpeg-linux.tar.xz"

echo "⬇  Baixando ffmpeg Linux..."
curl -sSL --retry 3 -o "$LINUX_TARBALL" "$LINUX_URL"

echo "   Extraindo..."
tar -xf "$LINUX_TARBALL" -C /tmp/
# The tarball contains: ffmpeg-master-latest-linux64-gpl/bin/ffmpeg
cp "/tmp/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg" "$BIN_DIR/ffmpeg-linux"
chmod +x "$BIN_DIR/ffmpeg-linux"
rm -rf "/tmp/ffmpeg-master-latest-linux64-gpl" "$LINUX_TARBALL"
echo "   ✅ ffmpeg-linux ($(du -h "$BIN_DIR/ffmpeg-linux" | cut -f1))"

# ── macOS (amd64) ────────────────────────────────────────────────────────────
# BtbN also has a macOS build, but evermeet/FFmpeg static is more reliable.
# Using the "ffmpeg" standalone binary from evermeet.
MACOS_URL="https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
MACOS_ZIP="/tmp/ffmpeg-macos.zip"

echo "⬇  Baixando ffmpeg macOS..."
curl -sSL --retry 3 -o "$MACOS_ZIP" "$MACOS_URL"

echo "   Extraindo..."
unzip -oq "$MACOS_ZIP" -d /tmp/ffmpeg-macos-extract/
# evermeet zip contains just "ffmpeg"
cp "/tmp/ffmpeg-macos-extract/ffmpeg" "$BIN_DIR/ffmpeg-macos"
chmod +x "$BIN_DIR/ffmpeg-macos"
rm -rf "/tmp/ffmpeg-macos-extract" "$MACOS_ZIP"
echo "   ✅ ffmpeg-macos ($(du -h "$BIN_DIR/ffmpeg-macos" | cut -f1))"

# ── Windows (amd64) ─────────────────────────────────────────────────────────
# gyan.dev essential build — most widely recommended for Windows
WINDOWS_URL="https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
WINDOWS_ZIP="/tmp/ffmpeg-windows.zip"

echo "⬇  Baixando ffmpeg Windows..."
curl -sSL --retry 3 -o "$WINDOWS_ZIP" "$WINDOWS_URL"

echo "   Extraindo..."
unzip -oq "$WINDOWS_ZIP" -d /tmp/ffmpeg-windows-extract/
# gyan.dev: ffmpeg-release-essentials/bin/ffmpeg.exe inside a versioned folder
WIN_EXTRACT_DIR=$(ls -d /tmp/ffmpeg-windows-extract/ffmpeg-* 2>/dev/null | head -1)
cp "$WIN_EXTRACT_DIR/bin/ffmpeg.exe" "$BIN_DIR/ffmpeg-windows.exe"
chmod +x "$BIN_DIR/ffmpeg-windows.exe" 2>/dev/null || true
rm -rf "/tmp/ffmpeg-windows-extract" "$WINDOWS_ZIP"
echo "   ✅ ffmpeg-windows.exe ($(du -h "$BIN_DIR/ffmpeg-windows.exe" | cut -f1))"

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "✅ Todos os binários ffmpeg foram baixados para: $BIN_DIR"
ls -lh "$BIN_DIR/"
