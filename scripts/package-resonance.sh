#!/usr/bin/env bash
# Package the PS4 Flycast build (after configure-flycast.sh + build-flycast.sh) as Resonance (formerly
# DeCast-S4), DCST00001 (IV0000-DCST00001_00-DECASTS400000000.pkg:
# the IDs stay, so an update installs over the earlier builds and keeps /data/Resonance).
#   RESONANCE_VERSION=01.00 package-resonance.sh [upload]
# upload: puts the pkg in the console's /data/pkg as Resonance-vXX.YY.pkg (install it with GoldHEN's
# Package Installer). Older builds of this app are deleted, on the PC (out/) and on the console
# (Resonance-v*, the old DeCast-S4-v*, IV0000-DCST00001*); other apps' packages are left alone.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/ps4-env.sh"
BUILD="$PS4_BUILD_ROOT/build/flycast"
EBOOT="$BUILD/shell/ps4/flycast_eboot/eboot.bin"
VERSION="${RESONANCE_VERSION:-01.00}"
HOST="ftp://${PS4_HOST:-192.168.0.90}:${PS4_FTP_PORT:-2121}"

[ -f "$EBOOT" ] || { echo "missing $EBOOT: build first" >&2; exit 1; }
[[ "$VERSION" =~ ^[0-9][0-9]\.[0-9][0-9]$ ]] || { echo "version must look like 01.00" >&2; exit 1; }
STAGE="$PS4_BUILD_ROOT/build/resonance-stage"
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
PKG="$(SFO_STYLE=plain NO_RIGHT_SPRX=1 DOLPHIN_PS4_MODULES_DIR=/nonexistent "$HERE/make-pkg.sh" "$STAGE" DCST00035 "Ready 2 Rumble Boxing" "$VERSION" R2RB "$PS4_BUILD_ROOT/out" | tail -1)"
ls -la "$PKG"
# a copy next to the repo (E:\PS4 Projects\Resonance\out), easy to find from Windows; *.pkg is ignored by git
mkdir -p "$HERE/../out"
NAME="Resonance-v$VERSION.pkg"
cp "$PKG" "$HERE/../out/$NAME"
# the update archive for a GitHub release (shell/ps4/updater.cpp): the installed app runs it from
# /data/Resonance/app; ustar, which the updater unpacks
UPDATE="Resonance-v$VERSION-update.tar"
tar --format=ustar -C "$STAGE" -cf "$HERE/../out/$UPDATE" eboot.bin version.txt launcher
find "$HERE/../out" -maxdepth 1 \( -name '*.pkg' -o -name '*-update.tar' \) ! -name "$NAME" ! -name "$UPDATE" -print -delete | sed 's|^|removed old |'
rm -f /tmp/DeCast-S4-v*.pkg /tmp/Resonance-v*.pkg
# Keep the symbols of every packaged build: crash logs must be symbolized against the exact binary.
mkdir -p "$PS4_BUILD_ROOT/oelf"
cp "$BUILD/shell/ps4/flycast_eboot/flycast.oelf" "$PS4_BUILD_ROOT/oelf/v$VERSION.oelf"
cp "$BUILD/flycast" "$PS4_BUILD_ROOT/oelf/v$VERSION.elf"
if [ "${1:-}" = upload ]; then
    listing() { curl -sS --list-only "$HOST/data/pkg/" | tr -d '\r'; }
    # The console's FTP server (GoldHEN v2.2) loses a big upload when a delete follows it within
    # seconds (the old file comes back, the new one goes, even after a listing showed them right):
    # the new build first, the old ones only once it has stood for 30 s, then 45 s more of checks
    SIZE="$(stat -c %s "$HERE/../out/$NAME")"
    # Windows' curl when there is one: uploads sent from WSL have been the ones the console lost
    upload() {
        if command -v curl.exe > /dev/null; then curl.exe -sS -T "$(wslpath -w "$(realpath "$1")")" "$HOST/data/pkg/"; else curl -sS -T "$1" "$HOST/data/pkg/"; fi
    }
    present() { curl -sS "$HOST/data/pkg/" | tr -d '\r' | awk -v n="$NAME" -v s="$SIZE" '$NF == n && $5 == s { f = 1 } END { exit !f }'; }
    settled() { for _ in 1 2 3; do sleep 10; present || return 1; done; }
    for try in 1 2 3; do
        upload "$HERE/../out/$NAME"
        echo "uploaded $NAME"
        settled && break
        echo "console: $NAME didn't stay, uploading again"
    done
    for old in $(listing | grep -E '^(Resonance-v[0-9.]+|DeCast-S4-v[0-9.]+|IV0000-DCST00001_00-[A-Z0-9]+)[.]pkg$' | grep -vx "$NAME"); do
        if curl -sS "$HOST/" -Q "DELE /data/pkg/$old" > /dev/null; then echo "console: removed old $old"; else echo "console: could not remove $old"; fi
        sleep 15
    done
    for try in 1 2 3; do
        sleep 15
        settled && break
        echo "console: $NAME went missing after the cleanup, uploading again"
        upload "$HERE/../out/$NAME"
        sleep 30
    done
    listing | grep -E '^(Resonance|DeCast)' | sed 's/^/console has: /'
fi
