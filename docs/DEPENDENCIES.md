# Maintained dependency forks

The complete exact revision inventory is in `../dependencies.lock.json`.

| Tinnci repository | Upstream | Purpose |
|---|---|---|
| droidian-gts7lwifi | iridite/droidian-gts7lwifi | Device coordinator, build scripts and CI |
| galaxy-tab-s7-plus-droidian | mukahraman/galaxy-tab-s7-plus-droidian | Preserve the original port status, signing tools and bring-up guide |
| kernel_samsung_sm8250 | iridite/kernel_samsung_sm8250; mukahraman/kernel_samsung_sm8250 | T870 kernel and Samsung image packaging |
| adaptation-samsung-gts7lwifi | mukahraman/adaptation-samsung-gts7xlwifi | T870 configuration package, audio and services |
| droidian-recipes | mukahraman/droidian-recipes | Device image recipe |
| droidian-camera | mukahraman/droidian-camera | Camera orientation support |
| rootfs-templates | ArchieMeng/rootfs-templates | debos recipes and image generation |
| android-image-flashing-template | droidian-releng/android-image-flashing-template | Image ZIP layout |
| android-recovery-flashing-template | droidian-releng/android-recovery-flashing-template | Recovery ZIP template |
| common_fragments | droidian-devices/common_fragments | Kernel configuration fragments |
| linux-packaging-snippets | droidian/linux-packaging-snippets | Kernel Debian packaging |
| releng-tools | droidian-releng/releng-tools | Build dependency installation and release metadata |
| docker-images | droidian-releng/docker-images | Owned build-container overlay and upstream definitions |
| initramfs-tools-halium | droidian/initramfs-tools-halium | Maintain the source for the distro Halium initramfs package |
| build-snippets | droidian-releng/build-snippets | Preserve the upstream CI helper definitions |
| checkout | actions/checkout | Pinned source checkout Action |
| upload-artifact | actions/upload-artifact | Pinned build artifact upload Action |
| download-artifact | actions/download-artifact | Pinned build artifact download Action |
| setup-qemu-action | docker/setup-qemu-action | Maintained for emulated builds; native arm64 jobs are the default |
| action-gh-release | softprops/action-gh-release | Maintained release helper; the coordinator currently uploads artifacts |

Direct source and Action references used by the coordinator point to these
forks. The base distro, compiler packages, package archive and digest-pinned
bootstrap images remain distribution inputs. Successful kernel `.buildinfo`
files record the installed package versions. The initramfs source fork is
available for maintenance; the current kernel build consumes the distro's
prebuilt `linux-initramfs-halium-generic:arm64` package.

Upstream changes can be fetched into separate remotes and compared before
merging. Update submodule gitlinks, source locks and mirrored signing helpers
in the same maintenance change. Do not use scheduled rebases on the device
branch. `tools/check-dependencies.py` rejects floating or unowned active Actions.
