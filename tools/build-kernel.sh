#!/bin/bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
OUTPUT=${1:-"$ROOT/out/kernel"}
mkdir -p "$OUTPUT"
OUTPUT=$(realpath "$OUTPUT")
ENGINE=${CONTAINER_ENGINE:-docker}
python3 "$ROOT/tools/fetch-dependencies.py" --destination "$OUTPUT/sources" --only \
    kernel_samsung_sm8250 linux-packaging-snippets releng-tools docker-images
SOURCE="$OUTPUT/sources/kernel_samsung_sm8250"
git -C "$SOURCE" submodule update --init --recursive --depth 1
mkdir -p "$OUTPUT/builder-context"
for dependency in linux-packaging-snippets releng-tools; do
    cp -a "$OUTPUT/sources/$dependency" "$OUTPUT/builder-context/"
done
"$ENGINE" build --network host -t t870-kernel-builder \
    -f "$OUTPUT/sources/docker-images/Dockerfile.t870-builder" "$OUTPUT/builder-context"
"$ENGINE" run --rm --network host --cpus "${BUILD_JOBS:-8}" \
    -e RELENG_JOBS="${BUILD_JOBS:-8}" \
    -e T870_UID="$(id -u)" -e T870_GID="$(id -g)" \
    -v "$OUTPUT:/build" t870-kernel-builder /bin/bash -c '
      set -euo pipefail
      trap '\''chown -R "$T870_UID:$T870_GID" /build'\'' EXIT
      cd /build/sources/kernel_samsung_sm8250
      # Packages are emitted next to the source directory by dpkg-buildpackage.
      RELENG_HOST_ARCH=arm64 releng-build-package
      find /build/sources -maxdepth 1 -type f -exec mv -t /build {} +
    '
