#!/bin/bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
PACKAGES=$(realpath "${1:-$ROOT/out/kernel}")
OUTPUT=${2:-"$ROOT/out/flash"}
mkdir -p "$OUTPUT"
OUTPUT=$(realpath "$OUTPUT")
ENGINE=${CONTAINER_ENGINE:-docker}
IMAGE=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["images"]["build_amd64"])' "$ROOT/dependencies.lock.json")
"$ENGINE" run --rm --network host \
    -e T870_UID="$(id -u)" -e T870_GID="$(id -g)" \
    -v "$ROOT:/work:ro" -v "$PACKAGES:/input:ro" -v "$OUTPUT:/output" \
    "$IMAGE" /bin/bash -c '
      set -euo pipefail
      trap '\''chown -R "$T870_UID:$T870_GID" /output'\'' EXIT
      apt-get update
      apt-get install -y --no-install-recommends debhelper device-tree-compiler avbtool python3-pycryptodome
      git config --global --add safe.directory /work
      git config --global --add safe.directory /work/adaptation
      kernel=(/input/linux-bootimage-4.19-325-samsung-gts7lwifi_*.deb)
      [ "${#kernel[@]}" = 1 ]
      python3 /work/tools/build-flash-package.py --kernel-deb "${kernel[0]}" --output /output
    '
