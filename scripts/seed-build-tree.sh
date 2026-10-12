#!/usr/bin/env bash
# One-time: create ~/resonance-build from copies of Crema's build tree (libc++ 21 sysroot with the
# libc overlay and prebuilt libraries, and the RADV/GNM Mesa build), so this port never writes
# into ~/cemups4-build or ~/dolphinps4-build.
set -euo pipefail
CRM="${CRM:-$HOME/cemups4-build}"
PSB="${PSB:-$HOME/resonance-build}"
mkdir -p "$PSB/src" "$PSB/build" "$PSB/out" "$PSB/logs" "$PSB/oelf"
[ -d "$PSB/sysroot" ] || cp -a "$CRM/sysroot" "$PSB/sysroot"
[ -d "$PSB/host-compat" ] || cp -a "$CRM/host-compat" "$PSB/host-compat"
# Mesa: the whole build directory (its static libraries are thin archives)
[ -d "$PSB/build/mesa" ] || cp -a "$CRM/build/mesa" "$PSB/build/mesa"
# Space-free path to this repo: toolchain flags (linker script paths) break on "PS4 Projects".
REPO="$(cd "$(dirname "$0")/.." && pwd)"
[ -e "$HOME/resonance" ] || ln -s "$REPO" "$HOME/resonance"
du -sh "$PSB"/* 2>/dev/null
find "$PSB/build/mesa" -name '*.a' | wc -l
