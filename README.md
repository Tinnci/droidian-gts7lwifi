# Droidian for Galaxy Tab S7 Wi-Fi (SM-T870)

T870 device build maintained under [Tinnci](https://github.com/Tinnci).
The source forks, Actions commits and bootstrap image digests are fixed in
[`dependencies.lock.json`](dependencies.lock.json).

The port uses the Samsung/LineageOS 4.19 kernel, Halium API 30, Debian and Phosh.
The hardware target is **SM-T870 / gts7lwifi**. S7+ (T970) images use a different
panel and device tree.

## Build locally

Initialize the adaptation submodule:

```sh
git clone --recurse-submodules https://github.com/Tinnci/droidian-gts7lwifi.git
cd droidian-gts7lwifi
```

Build the kernel on an x86_64 Linux/WSL host with Docker or Podman:

```sh
BUILD_JOBS=8 tools/build-kernel.sh
# For rootless Podman: CONTAINER_ENGINE=podman BUILD_JOBS=8 tools/build-kernel.sh
```

This builds our container overlay, compiles the kernel, and produces Debian
packages in `out/kernel/`. It uses our forks of the kernel configuration
fragments, packaging snippets and release tools. The compiler and generic
Halium initramfs are distro packages; their exact versions are recorded in
`.buildinfo`. Their closest source/build repositories are also forked for
maintenance. Bootstrap containers are pinned by digest.

Build the flash bundle in the pinned Droidian container:

```sh
tools/build-flash-in-container.sh out/kernel out/flash
```

Ubuntu 24.04 does not provide `avbtool` in its standard package archive. The
container installs it from the Droidian archive. With the required tools
already installed, the direct `tools/build-flash-package.py --kernel-deb ...`
entry point is also available.

The output contains boot and rescue images, DTBO, vbmeta, both adaptation
packages, `build-manifest.json` and `SHA256SUMS`. It verifies image signatures,
DTBO properties and required adaptation payloads before copying the output.
An existing kernel `.deb` can also be passed to the same command.

Build the camera package on an arm64 host, or use the native arm64 CI job:

```sh
tools/build-camera.sh
```

To build the LVM userdata image, collect the kernel packages, both adaptation
packages and camera package in one directory, then run:

```sh
tools/build-rootfs.sh /absolute/path/to/packages
```

The rootfs builder supports native arm64 and x86_64 with binfmt emulation.
It needs privileged container access for debootstrap, loop devices and LVM.
The image includes the device packages before first boot. The base system uses
Droidian's `current` snapshot; `.buildinfo` and the dependency lock record the
build inputs, while the distro archive remains an external dependency.

## CI and maintenance

Run **Build T870 from source** in Actions. A normal source push builds the kernel
and verified flash bundle. Manual dispatch with `rootfs=true` also builds the
camera and userdata image on native arm64 runners. All active Actions come from
Tinnci forks and use full commit hashes. No GitHub Pages setup is required.
Use **Package and rebuild T870 rootfs** with an existing run ID to reuse
its kernel and camera packages and regenerate the flash bundle and rootfs.

[`adaptation/`](adaptation/) is a pinned submodule of
[Tinnci/adaptation-samsung-gts7lwifi](https://github.com/Tinnci/adaptation-samsung-gts7lwifi).
Change device configuration there, then update this submodule and the dependency
lock together. Change other source pins explicitly after reviewing their diffs.
The kernel signing helpers are mirrored under `debian/samsung` in the kernel
fork; update both copies together.

See [the build comparison](docs/BUILD-COMPARISON.md),
[dependency inventory](docs/DEPENDENCIES.md), and
[flash instructions](QUICK-FLASH.md).

## Hardware status

The inherited T870 port has not recorded a successful first boot. Local/CI
build verification covers generated files and package contents. T870 display,
touch, S-Pen, audio, Wi-Fi, suspend and charging still need device testing.
The original S7+ port and history remain linked in the dependency inventory.
