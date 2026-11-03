#!/bin/bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "$0")/.." && pwd)
PACKAGES=$(realpath "${1:?directory containing kernel, adaptation and camera debs}")
OUTPUT=${2:-"$ROOT/out/rootfs"}
mkdir -p "$OUTPUT"
OUTPUT=$(realpath "$OUTPUT")
ENGINE=${CONTAINER_ENGINE:-docker}
ARCH=$(uname -m)
case "$ARCH" in
    x86_64) IMAGE_KEY=rootfs_amd64 ;;
    aarch64) IMAGE_KEY=rootfs_arm64 ;;
    *) echo "Unsupported builder architecture: $ARCH" >&2; exit 1 ;;
esac
IMAGE=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["images"][sys.argv[2]])' "$ROOT/dependencies.lock.json" "$IMAGE_KEY")
python3 "$ROOT/tools/fetch-dependencies.py" --destination "$OUTPUT/sources" --only droidian-recipes
SOURCE="$OUTPUT/sources/droidian-recipes"
git -C "$SOURCE" submodule update --init --recursive --depth 1
mkdir -p "$SOURCE/apt"
cp "$PACKAGES"/*.deb "$SOURCE/apt/"
mkdir -p "$SOURCE/pre-overlay/etc/apt/preferences.d"
PREFERENCES="$SOURCE/pre-overlay/etc/apt/preferences.d/t870-local-packages"
: > "$PREFERENCES"
for file in "$SOURCE/apt"/*.deb; do
    printf 'Package: %s\nPin: version %s\nPin-Priority: 1001\n\n' \
        "$(dpkg-deb -f "$file" Package)" "$(dpkg-deb -f "$file" Version)" >> "$PREFERENCES"
done
for package in linux-image-4.19-325-samsung-gts7lwifi linux-bootimage-4.19-325-samsung-gts7lwifi adaptation-samsung-gts7lwifi adaptation-samsung-gts7lwifi-configs droidian-camera; do
    found=no
    for file in "$SOURCE/apt"/*.deb; do
        [ "$(dpkg-deb -f "$file" Package)" != "$package" ] || found=yes
    done
    [ "$found" = yes ] || { echo "Missing package: $package" >&2; exit 1; }
done
"$ENGINE" run --rm --privileged --network host --cgroupns=host \
    -e T870_UID="$(id -u)" -e T870_GID="$(id -g)" \
    -v /dev:/host-dev -v "$SOURCE:/buildd/sources" \
    "$IMAGE" /bin/bash -c '
      set -euo pipefail
      trap '\''chown -R "$T870_UID:$T870_GID" /buildd/sources'\'' EXIT
      mountpoint -q /proc/sys/fs/binfmt_misc || { mkdir -p /proc/sys/fs/binfmt_misc; mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc; }
      update-binfmts --enable
      cd /buildd/sources
      dpkg-scanpackages --multiversion apt /dev/null > apt/Packages
      # A file: repository needs paths relative to its own root.
      sed -i '\''s|^Filename: apt/|Filename: |'\'' apt/Packages
      DROIDIAN_VERSION=current python3 generate_device_recipe.py gts7lwifi-phosh arm64 phosh tablet 30
      debos --disable-fakemachine generated/droidian.yaml
    '
mkdir -p "$OUTPUT/images"
cp "$SOURCE"/out/* "$OUTPUT/images/"
cp "$ROOT/dependencies.lock.json" "$OUTPUT/images/"
(cd "$OUTPUT/images" && sha256sum ./* > SHA256SUMS)
