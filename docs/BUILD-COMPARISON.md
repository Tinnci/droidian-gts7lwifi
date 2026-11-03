# T870 build comparison — 2026-11-03

Initial snapshots: device repository `iridite/droidian-gts7lwifi@313134d`,
T870 kernel `iridite/kernel_samsung_sm8250@e17bc7259`, S7+ kernel
`mukahraman/kernel_samsung_sm8250@97e4a5b90`, S7+ adaptation `a508236`,
S7+ recipes `7037853`.

## T870 versus the original S7+ implementation

The initial T870 kernel has two extra commits and five changed paths versus the
S7+ kernel. It changes package/device names, selects `gts7lwifi.config`, switches
the overlay directory from `gts7xl` to `gts7l`, and restricts model metadata to
T870. The effective extra Kconfig assignments match the S7+ port.

The T870 adaptation changes S-Pen resolution hints from `100x100` to `97x97`,
changes the X11/Wayland nested output modes to `1280x800`, and renames device
paths. The original port also omitted the Wi-Fi boot service, audio vendor
service override and `audio.primary.kona.so` bridge; these are now restored
from the S7+ fork history. The generic Qualcomm udev permissions are retained.
These device configuration choices need T870 hardware validation.

## Build pipeline changes

| Area | Original T870 repository | Maintained build |
|---|---|---|
| Kernel | Downloaded a recent Actions artifact | Build pinned Tinnci source in a digest-pinned container overlay |
| Artifact lookup | Selected the latest run, without checking build success/expiry | Source build; a local `.deb` is accepted for packaging |
| Adaptation | Handwritten `dpkg-deb` payload skipped `debian/*.links` and the metapackage | Standard `dpkg-buildpackage`, both packages and links verified |
| Wi-Fi/audio | Missing service and audio bridge payloads | Restored in the owned adaptation fork |
| Kernel upgrades | Kernel `.deb` contained raw boot images; Samsung wrapping was a separate step | Kernel packaging signs boot/recovery and DTBO; vbmeta flags fixed to 2 |
| Kernel cmdline | Rescue console and historical sleep-disable token in the raw package | Normal boot console and the tested S7+ wrapper command line |
| DTBO | Silent zero-edit success and unchecked dtc failures | Accept already-correct properties; reject missing/unexpected properties and invalid tables |
| Rootfs | Separately downloaded generic rootfs, adaptation installed after first boot | T870 tablet recipe with local packages installed during image creation |
| Dependencies | Personal upstream URLs and moving Action tags | Owned source/Action forks with explicit commit pins |
| Updates | Inherited scheduled automatic kernel rebase | Deliberate dependency updates reviewed before pin changes |
| Publishing | Kernel job included mandatory GitHub Pages deployment | Build artifacts independent of Pages |
| Provenance | Minimal checksums | Source lock, package hashes, image verification and Debian build metadata |

The June kernel workflow's overall failure came from **Pages deployment**.
Its build job succeeded and published a T870 bootimage `.deb` with SHA256
`5b223d9d4f5556b8a2df8c10ee01f8a6e9aa6a185cea5848e9ec9b83b625d2b8`.
The Actions artifacts have expired, while the Release package remains available.

The Release DTBO contains six board revisions, r02–r07, already using
`touchpad,invert = <0 0 0>`. The old tool's “patched 0 FDTs” was an idempotent
result. The maintained tool reports all six as already correct and verifies
its signed output.

## Local environment

Debian 13 under WSL2, x86_64; 20 logical CPUs, 27 GiB RAM, 32 GiB swap and
approximately 215 GiB free at initial inspection. The host already provided
cross-binutils/GCC and dtc. Debhelper and Podman were added for these builds.
The Android Clang/GCC toolchain is installed inside the build container.

Validation evidence and current CI links are recorded in `VALIDATION.md`.
