#!/usr/bin/env bash
# Clone upstream Flycast (with submodules) into the WSL build tree and link the repo space-free.
set -euo pipefail
ln -sfn "/mnt/e/PS4 Projects/DeCast-S4" "$HOME/decast"
mkdir -p "$HOME/decast-build/src" "$HOME/decast-build/logs"
cd "$HOME/decast-build/src"
[ -d flycast ] || git clone --recursive https://github.com/flyinghead/flycast.git flycast
cd flycast && git log -1 --format='%h %ci %s' && git submodule status
