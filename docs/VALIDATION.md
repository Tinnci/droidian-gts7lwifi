# Validation — 2026-11-03

## Local source build

The Tinnci kernel source at `7eb0630e74457b83abf224ba15d869db2786bdbf`
compiled successfully under Debian 13 / WSL2 on x86_64 using an eight-CPU Podman
container. All six kernel Debian packages were generated. The build ran the
owned `linux-packaging-snippets` version `43+t870.1` and owned release tools.

The resulting T870 bootimage package is 66,348,364 bytes with SHA256:

```text
c4f99809efed7b830bbe51b51a3d03e188800983aadcee4c8890d83ae63ca9cd
```

The `.buildinfo` records Android Clang `14.0-r450784d`, packaged as
`13.0.0+r2+z1+git20250320231423.c8ca1b2.next.production`, and Halium initramfs
`2025.04.11.0+git20250411210410.e515727.next.production` for arm64.

Direct verification of images extracted from this `.deb` succeeded:

| Image | Size in bytes | Verification |
|---|---:|---|
| boot | 71,303,168 | AVB RSA4096 signature and content hash |
| recovery | 86,888,448 | AVB RSA4096 signature and content hash |
| DTBO | 10,485,760 | AVB signature/hash; six already-correct board overlays |
| vbmeta | 4,096 | Flags equal 2 |

The maintained flash-package script also completed successfully with this
self-built kernel package. It built both adaptation `.deb` packages, verified
all required files and symbolic links, verified boot/rescue/DTBO signatures,
and generated checksums and a build manifest. Every `SHA256SUMS` entry passed.
The coordinator worktree was clean when this flash package was generated.

The complete arm64 rootfs recipe also passed `debos --dry-run --print-recipe`
in the pinned amd64 rootfs-builder container, with our local packages present.

Four regression tests pass, covering boot header validation, extended command
line clearing, DTBO idempotence and rejection of missing/unexpected properties
or truncated tables. Shell syntax and source/Action lock checks pass.

Local outputs:

- `/home/enterp/dev/t870/build/kernel-local/`
- `/home/enterp/dev/t870/build/flash-local/`
- `/home/enterp/dev/t870/build/kernel-source.log`

## GitHub Actions

The owned native arm64 camera build has succeeded. End-to-end build tracking:
[Build T870 from source](https://github.com/Tinnci/droidian-gts7lwifi/actions/runs/41619666783).
The kernel, flash bundle and rootfs results are being verified in that run.

## Device validation

First boot and the T870 display, touch, S-Pen, audio, wireless, suspend and
charging behavior still require testing on a physical SM-T870.
