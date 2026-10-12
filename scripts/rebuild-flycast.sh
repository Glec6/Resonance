#!/usr/bin/env bash
# Configure + build with logs (~/resonance-build/logs/{configure,build}.log) and an error summary.
#   rebuild-flycast.sh [clean]
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ "${1:-}" = clean ] && rm -rf "$HOME/resonance-build/build/flycast"
bash "$HERE/logrun.sh" configure bash "$HERE/configure-flycast.sh" || { tail -30 "$HOME/resonance-build/logs/configure.log"; exit 1; }
bash "$HERE/logrun.sh" build bash "$HERE/build-flycast.sh" -k 0
L="$HOME/resonance-build/logs/build.log"
tail -1 "$L"; echo "errors: $(grep -c 'error:' "$L")"
grep "error:" "$L" | sed 's/.*src\/flycast\///' | sort | uniq -c | sort -rn | head -${TOP:-60}
