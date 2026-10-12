#!/usr/bin/env bash
# Commit the work in ~/resonance-build/src/flycast (branch ps4) and export it as
# patches/flycast-ps4.patch against the upstream base recorded in patches/BASE.txt.
#   save-patch.sh "commit message"
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="${FLYCAST_SRC:-$HOME/resonance-build/src/flycast}"
BASE="$(awk '/^base:/{print $2}' "$HERE/../patches/BASE.txt")"
git -C "$SRC" add -A
git -C "$SRC" diff --cached --quiet || git -C "$SRC" commit -q -m "${1:-PS4 port work}"
git -C "$SRC" diff "$BASE" HEAD > "$HERE/../patches/flycast-ps4.patch"
echo "patches/flycast-ps4.patch: $(grep -c '^diff --git' "$HERE/../patches/flycast-ps4.patch") files"
