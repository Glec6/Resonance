#!/usr/bin/env bash
# Build Flycast for PS4 (run scripts/configure-flycast.sh first). Extra args go to ninja.
#   build-flycast.sh [ninja args...]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/ps4-env.sh"  # also puts PacBrew ld.lld's libxml2 compat link on LD_LIBRARY_PATH
ninja -C "$PS4_BUILD_ROOT/build/flycast" -j"${JOBS:-12}" "$@"
