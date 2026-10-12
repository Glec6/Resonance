#!/usr/bin/env bash
# libnfs and libsmb2 (Ronnie Sahlberg's user-space NFS and SMB2/3 clients, LGPL-2.1) for PS4,
# static, into the sysroot: Resonance reads games from network shares through them
# (shell/ps4/netfs.cpp). Sources in ~/resonance-build/src/{libnfs,libsmb2} (git clone of
# github.com/sahlberg/libnfs and libsmb2; the commits used are in patches/BASE.txt).
#   build-netfs.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/ps4-env.sh"
SRC="$PS4_BUILD_ROOT/src"
SYSROOT="$PS4_BUILD_ROOT/sysroot"
TOOLCHAIN="$HERE/../toolchain/ps4-deps.cmake"

build() {
    local name="$1"; shift
    local dir="$PS4_BUILD_ROOT/build/$name"
    rm -rf "$dir"
    env -u CFLAGS -u CXXFLAGS -u CPPFLAGS -u LDFLAGS -u LIBS \
        cmake -S "$SRC/$name" -B "$dir" -G Ninja -DCMAKE_TOOLCHAIN_FILE="$TOOLCHAIN" \
        -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$SYSROOT" -DBUILD_SHARED_LIBS=OFF "$@"
    ninja -C "$dir"
    ninja -C "$dir" install
}

# libsmb2's PS4 branch sets CMAKE_C_FLAGS to "-funwind-tables", dropping the toolchain's sysroot
# flags: append instead
sed -i 's|set(CMAKE_C_FLAGS "-funwind-tables")|set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -funwind-tables")|' "$SRC/libsmb2/CMakeLists.txt"
# ... and its PS4 code uses the Sony SDK's __bswap_16/32: clang's builtins on OpenOrbis
grep -q "__bswap_32=__builtin_bswap32" "$SRC/libsmb2/CMakeLists.txt" ||
    sed -i 's|      add_definitions(-DPS4_PLATFORM)|      add_definitions(-DPS4_PLATFORM -D__bswap_16=__builtin_bswap16 -D__bswap_32=__builtin_bswap32 -D__bswap_64=__builtin_bswap64)|' \
        "$SRC/libsmb2/CMakeLists.txt"

build libnfs -DENABLE_TESTS=OFF -DENABLE_EXAMPLES=OFF -DENABLE_UTILS=OFF -DENABLE_DOCUMENTATION=OFF
build libsmb2 -DENABLE_EXAMPLES=OFF -DENABLE_LIBKRB5=OFF -DENABLE_GSSAPI=OFF
ls -la "$SYSROOT/lib/libnfs.a" "$SYSROOT/lib/libsmb2.a"
