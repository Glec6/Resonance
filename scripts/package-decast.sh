#!/usr/bin/env bash
# Package the PS4 Flycast build (after configure-flycast.sh + build-flycast.sh) as Resonance (the
# app's name on the PS4; the project is DeCast-S4), DCST00001 (IV0000-DCST00001_00-DECASTS400000000.pkg:
# the IDs stay, so an update installs over the earlier builds and keeps /data/DeCast-S4).
#   DECAST_VERSION=01.00 package-decast.sh [upload]
# upload: puts the pkg in the console's /data/pkg (install it with GoldHEN's Package Installer).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/ps4-env.sh"
BUILD="$PS4_BUILD_ROOT/build/flycast"
EBOOT="$BUILD/shell/ps4/flycast_eboot/eboot.bin"
VERSION="${DECAST_VERSION:-01.00}"
HOST="ftp://${PS4_HOST:-192.168.0.90}:${PS4_FTP_PORT:-2121}"

[ -f "$EBOOT" ] || { echo "missing $EBOOT: build first" >&2; exit 1; }
[[ "$VERSION" =~ ^[0-9][0-9]\.[0-9][0-9]$ ]] || { echo "version must look like 01.00" >&2; exit 1; }
STAGE="$PS4_BUILD_ROOT/build/decast-stage"
rm -rf "$STAGE"
mkdir -p "$STAGE/sce_sys"
cp "$EBOOT" "$STAGE/eboot.bin"
cp "$HERE/../sce_sys/icon0.png" "$HERE/../sce_sys/pic1.png" "$STAGE/sce_sys/"
echo "$VERSION" > "$STAGE/version.txt"
# the home screen's fonts, menu sounds, CA bundle and opening pictures (launcher-assets/launcher)
cp -r "$HERE/../launcher-assets/launcher" "$STAGE/"
# PkgTool's pkg_build crashes ("Sequence contains no elements") on empty folders.
find "$STAGE" -type d -empty -delete
# Vulkan (RADV on GNM) runs under the plain homebrew identity (4.5 GiB of direct memory).
PKG="$(SFO_STYLE=plain NO_RIGHT_SPRX=1 DOLPHIN_PS4_MODULES_DIR=/nonexistent "$HERE/make-pkg.sh" "$STAGE" DCST00001 "Resonance" "$VERSION" DECASTS4 "$PS4_BUILD_ROOT/out" | tail -1)"
ls -la "$PKG"
# a copy next to the repo (E:\PS4 Projects\DeCast-S4\out), easy to find from Windows; *.pkg is ignored by git
mkdir -p "$HERE/../out"
cp "$PKG" "$HERE/../out/Resonance-v$VERSION.pkg"
# Keep the symbols of every packaged build: crash logs must be symbolized against the exact binary.
mkdir -p "$PS4_BUILD_ROOT/oelf"
cp "$BUILD/shell/ps4/flycast_eboot/flycast.oelf" "$PS4_BUILD_ROOT/oelf/v$VERSION.oelf"
cp "$BUILD/flycast" "$PS4_BUILD_ROOT/oelf/v$VERSION.elf"
if [ "${1:-}" = upload ]; then
    curl -sS -T "$PKG" "$HOST/data/pkg/"
    echo "uploaded $(basename "$PKG")"
fi
