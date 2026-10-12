#!/usr/bin/env bash
# Configure Flycast for PS4 (Resonance): no SDL/X11/desktop audio, the PS4 frontend (shell/ps4) and
# Vulkan on DolphinPS4's RADV port. Run through ~/resonance (no space in the path).
#   configure-flycast.sh [extra cmake args...]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/ps4-env.sh"
SRC="${FLYCAST_SRC:-$PS4_BUILD_ROOT/src/flycast}"
BUILD="$PS4_BUILD_ROOT/build/flycast"
export PKG_CONFIG_LIBDIR="$PS4_BUILD_ROOT/sysroot/lib/pkgconfig"
unset PKG_CONFIG_PATH
ps4_cmake -S "$SRC" -B "$BUILD" -G Ninja \
    -DCMAKE_TOOLCHAIN_FILE="$HERE/../toolchain/ps4-resonance.cmake" \
    "-DCMAKE_PROJECT_flycast_INCLUDE=$HERE/../toolchain/ps4-love-style.cmake" \
    -DPS4_PAID="${PS4_PAID:-0x3800000000000035}" \
    -DUSE_VULKAN=ON -DUSE_OPENGL=OFF -DUSE_HOST_SDL=OFF -DUSE_BREAKPAD=OFF -DUSE_LUA=OFF \
    -DUSE_OPENMP=OFF -DUSE_ALSA=OFF -DUSE_LIBAO=OFF -DUSE_PULSEAUDIO=OFF -DUSE_HOST_LIBZIP=OFF \
    "$@"
