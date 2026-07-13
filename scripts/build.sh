#!/usr/bin/env bash
# build.sh — Build Estenio standalone executable for the current platform.
#
# Usage:
#   bash scripts/build.sh              # build for current platform
#   bash scripts/build.sh --clean      # clean + rebuild
#
# Prerequisites: Python 3.10+, pip
#
# Output: dist/estenio (or dist/estenio.exe on Windows)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[BUILD]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }

# ── Parse args ───────────────────────────────────────────────────────────────
DO_CLEAN=false
for arg in "$@"; do
    case "$arg" in
        --clean|-c) DO_CLEAN=true ;;
    esac
done

# ── Detect platform ─────────────────────────────────────────────────────────
case "$(uname -s)" in
    Linux)  PLATFORM="linux";   BINARY_NAME="estenio" ;;
    Darwin) PLATFORM="macos";   BINARY_NAME="estenio" ;;
    MINGW*|MSYS*|CYGWIN*)
            PLATFORM="windows"; BINARY_NAME="estenio.exe" ;;
    *)
        echo "ERRO: sistema não suportado: $(uname -s)" >&2
        exit 1
        ;;
esac

info "Plataforma: $PLATFORM"

# ── Clean ───────────────────────────────────────────────────────────────────
if $DO_CLEAN; then
    info "Limpando builds anteriores..."
    rm -rf build/ dist/ __pycache__/ src/estenio/__pycache__/
    success "Limpeza concluída."
fi

# ── Python check ────────────────────────────────────────────────────────────
PYTHON=""
for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" &>/dev/null; then
        ver=$("$candidate" -c 'import sys; v=sys.version_info; print(f"{v.major}.{v.minor}")' 2>/dev/null || true)
        major="${ver%%.*}"
        minor="${ver##*.}"
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ] 2>/dev/null; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERRO: Python 3.10+ não encontrado. Instale e tente novamente." >&2
    exit 1
fi
success "Python: $($PYTHON --version)"

# ── Install deps ────────────────────────────────────────────────────────────
info "Instalando dependências..."
"$PYTHON" -m pip install --upgrade pip --quiet 2>&1 | tail -1 || true
"$PYTHON" -m pip install -e ".[dev]" --quiet
success "Dependências instaladas."

# ── Bundle ffmpeg ───────────────────────────────────────────────────────────
info "Baixando ffmpeg ($PLATFORM)..."
bash "$SCRIPT_DIR/bundle-ffmpeg.sh" "$PLATFORM"

# ── Build with PyInstaller ──────────────────────────────────────────────────
info "Compilando com PyInstaller..."
"$PYTHON" -m PyInstaller estenio.spec

info "Verificando binário..."
OUTPUT="$ROOT_DIR/dist/$BINARY_NAME"
if [ -f "$OUTPUT" ]; then
    chmod +x "$OUTPUT" 2>/dev/null || true
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    success "Binário compilado: $OUTPUT ($SIZE)"
else
    echo "ERRO: binário não encontrado em $OUTPUT" >&2
    exit 1
fi

# ── Quick smoke test ────────────────────────────────────────────────────────
info "Teste rápido..."
"$OUTPUT" --version 2>&1 | head -3 || true
"$OUTPUT" --help 2>&1 | head -1 || true

echo ""
success "Build concluído!"
echo ""
echo "Binário: $OUTPUT"
echo ""
echo "Para publicar uma release:"
echo "  bash scripts/release.sh <versão>"
echo "  Ex: bash scripts/release.sh v0.3.0"
