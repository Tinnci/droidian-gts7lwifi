#!/bin/bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
[ "$(uname -m)" = aarch64 ] || { echo "Camera build requires an arm64 runner" >&2; exit 1; }
OUTPUT=${1:-"$ROOT/out/camera"}
mkdir -p "$OUTPUT"
OUTPUT=$(realpath "$OUTPUT")
ENGINE=${CONTAINER_ENGINE:-docker}
python3 "$ROOT/tools/fetch-dependencies.py" --destination "$OUTPUT/sources" --only \
    droidian-camera linux-packaging-snippets releng-tools docker-images
mkdir -p "$OUTPUT/builder-context"
for dependency in linux-packaging-snippets releng-tools; do
    cp -a "$OUTPUT/sources/$dependency" "$OUTPUT/builder-context/"
done
IMAGE=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["images"]["build_arm64"])' "$ROOT/dependencies.lock.json")
"$ENGINE" build --network host -t t870-camera-builder --build-arg BASE_IMAGE="$IMAGE" \
    -f "$OUTPUT/sources/docker-images/Dockerfile.t870-builder" "$OUTPUT/builder-context"
"$ENGINE" run --rm --network host --cpus "${BUILD_JOBS:-4}" \
    -e T870_UID="$(id -u)" -e T870_GID="$(id -g)" \
    -v "$OUTPUT:/build" t870-camera-builder /bin/bash -c '
      set -euo pipefail
      trap '\''chown -R "$T870_UID:$T870_GID" /build'\'' EXIT
      cd /build/sources/droidian-camera
      apt-get update
      apt-get build-dep -y .
      dpkg-buildpackage -us -uc -b
      find /build/sources -maxdepth 1 -type f -exec mv -t /build {} +
    '
