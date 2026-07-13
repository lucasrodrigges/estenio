#!/usr/bin/env bash
# release.sh — Create a GitHub Release with local binaries.
#
# Usage:
#   bash scripts/release.sh <version>              # current platform binary
#   bash scripts/release.sh <version> --draft       # draft release
#
# Examples:
#   bash scripts/release.sh v0.3.0
#   bash scripts/release.sh v0.3.0 --draft
#
# Uses gh CLI if available, otherwise curl + GITHUB_TOKEN.
# Requires GITHUB_TOKEN env var when using curl.
#
# For multi-platform releases:
#   1. Build on each platform (Linux, macOS, Windows)
#   2. Copy all binaries into dist/
#   3. Run release.sh once — it uploads everything in dist/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[RELEASE]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}      $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}    $*"; }

# ── Parse args ───────────────────────────────────────────────────────────────
if [ $# -lt 1 ]; then
    echo "Uso: bash scripts/release.sh <versão> [--draft] [--prerelease] [--notes <arquivo>]"
    echo "Ex:  bash scripts/release.sh v0.3.0"
    echo "     bash scripts/release.sh v0.3.0 --draft"
    echo ""
    echo "Coloque os binários em dist/ antes de executar:"
    echo "  dist/estenio          (Linux)"
    echo "  dist/estenio          (macOS)"
    echo "  dist/estenio.exe      (Windows)"
    exit 1
fi

VERSION="$1"
shift

DRAFT=false
PRERELEASE=false
NOTES_FILE=""

while [ $# -gt 0 ]; do
    case "$1" in
        --draft) DRAFT=true ;;
        --prerelease) PRERELEASE=true ;;
        --notes) NOTES_FILE="$2"; shift ;;
        *) echo "ERRO: argumento inválido: $1" >&2; exit 1 ;;
    esac
    shift
done

cd "$ROOT_DIR"

# ── Find binaries in dist/ ─────────────────────────────────────────────────
declare -A ASSETS

DIST_DIR="$ROOT_DIR/dist"
if [ ! -d "$DIST_DIR" ]; then
    echo "ERRO: diretório dist/ não encontrado. Execute 'bash scripts/build.sh' primeiro." >&2
    exit 1
fi

# Map platform → file in dist/
for entry in "$DIST_DIR"/*; do
    [ -f "$entry" ] || continue
    name=$(basename "$entry")
    case "$name" in
        estenio.exe)   ASSETS[windows]="$entry" ;;
        estenio)       # Check if it's Linux or macOS
            file "$entry" | grep -qi "mach-o" && ASSETS[macos]="$entry" || ASSETS[linux]="$entry"
            ;;
    esac
done

if [ ${#ASSETS[@]} -eq 0 ]; then
    echo "ERRO: Nenhum binário encontrado em dist/" >&2
    echo "Execute 'bash scripts/build.sh' primeiro." >&2
    exit 1
fi

echo ""
info "Preparando release $VERSION"
echo ""
echo "Plataformas detectadas em dist/:"
for plat in "${!ASSETS[@]}"; do
    size=$(du -h "${ASSETS[$plat]}" | cut -f1)
    echo "  $plat  →  ${ASSETS[$plat]} ($size)"
done
echo ""

# ── Changelog ───────────────────────────────────────────────────────────────
CHANGELOG="Release $VERSION"
if [ -f "$ROOT_DIR/CHANGELOG.md" ]; then
    info "Usando CHANGELOG.md..."
    CHANGELOG=$(cat "$ROOT_DIR/CHANGELOG.md")
elif [ -n "$NOTES_FILE" ] && [ -f "$NOTES_FILE" ]; then
    info "Usando notas de $NOTES_FILE..."
    CHANGELOG=$(cat "$NOTES_FILE")
fi

# ── GitHub Release ──────────────────────────────────────────────────────────
REPO="lucasrodrigges/estenio"

# Try gh CLI first, then curl
if command -v gh &>/dev/null; then
    # ── Using gh CLI ────────────────────────────────────────────────────────
    info "Usando gh CLI..."

    FLAGS="--title \"Estenio $VERSION\" --notes \"$CHANGELOG\""
    $DRAFT && FLAGS="$FLAGS --draft"
    $PRERELEASE && FLAGS="$FLAGS --prerelease"

    for plat in "${!ASSETS[@]}"; do
        FLAGS="$FLAGS ${ASSETS[$plat]}#estenio-${plat}"
    done

    eval "gh release create \"$VERSION\" $FLAGS"
    success "Release $VERSION criada com sucesso!"

elif [ -n "${GITHUB_TOKEN:-}" ]; then
    # ── Using curl ──────────────────────────────────────────────────────────
    info "Usando curl (GITHUB_TOKEN)..."

    # Create release
    DRAFT_JSON="false"
    PRERELEASE_JSON="false"
    $DRAFT && DRAFT_JSON="true"
    $PRERELEASE && PRERELEASE_JSON="true"

    RESPONSE=$(curl -sS -H "Authorization: token $GITHUB_TOKEN" \
        -H "Content-Type: application/json" \
        "https://api.github.com/repos/$REPO/releases" \
        -d "{
            \"tag_name\": \"$VERSION\",
            \"name\": \"Estenio $VERSION\",
            \"body\": $(echo "$CHANGELOG" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'),
            \"draft\": $DRAFT_JSON,
            \"prerelease\": $PRERELEASE_JSON
        }")

    RELEASE_ID=$(echo "$RESPONSE" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])' 2>/dev/null || true)

    if [ -z "$RELEASE_ID" ]; then
        echo "ERRO: Falha ao criar release. Resposta da API:" >&2
        echo "$RESPONSE" >&2
        exit 1
    fi
    success "Release criada (ID: $RELEASE_ID)"

    # Upload assets
    for plat in "${!ASSETS[@]}"; do
        asset_path="${ASSETS[$plat]}"
        asset_name="estenio-${plat}"
        [ "$plat" = "windows" ] && asset_name="estenio-windows.exe"

        info "Enviando $asset_name ($(du -h "$asset_path" | cut -f1))..."
        curl -sS -H "Authorization: token $GITHUB_TOKEN" \
            -H "Content-Type: application/octet-stream" \
            --data-binary "@$asset_path" \
            "https://uploads.github.com/repos/$REPO/releases/$RELEASE_ID/assets?name=$asset_name" \
            -o /dev/null
        success "$asset_name enviado."
    done

else
    echo "ERRO: Nem gh CLI nem GITHUB_TOKEN disponível." >&2
    echo "" >&2
    echo "Opções:" >&2
    echo "  1. Instale gh CLI:  https://cli.github.com" >&2
    echo "  2. Defina um token:  export GITHUB_TOKEN=ghp_..." >&2
    exit 1
fi

echo ""
success "Release $VERSION publicada!"
echo "  https://github.com/$REPO/releases/tag/$VERSION"
