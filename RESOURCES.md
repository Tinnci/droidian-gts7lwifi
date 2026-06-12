# SM-T870 (Galaxy Tab S7 Wi-Fi) Droidian Port — Resource Inventory

## Target Device
- **Model:** Samsung Galaxy Tab S7 Wi-Fi (SM-T870)
- **Codename:** `gts7lwifi`
- **SoC:** Qualcomm SM8250 "kona" (Snapdragon 865+)
- **Display:** 11" 2560×1600 LCD (NT36523 TDDI panel)
- **Touch IC:** Novatek NT36523 (integrated with panel)
- **Audio:** Cirrus CS35L41 × 4 speakers
- **S-Pen:** Wacom W9021
- **Keyboard:** STM32 POGO (Book Cover)
- **WiFi:** QCA6390
- **USB-C DP:** PS5169 redriver (same as T970)

## Source Port (reference)
- **Device:** SM-T970 (Galaxy Tab S7+ Wi-Fi, `gts7xlwifi`)
- **Repo:** https://github.com/mukahraman/galaxy-tab-s7-plus-droidian
- **Status:** Fully working (Phosh, touch, cameras, BT, DP, etc.)

## Upstream Repositories

### Kernel (mukahraman, branch: droidian)
- **Repo:** https://github.com/mukahraman/kernel_samsung_sm8250/tree/droidian
- **T870 support confirmed:**
  - Config fragment: `arch/arm64/configs/vendor/samsung/gts7lwifi.config`
  - Device tree overlays: `arch/arm64/boot/dts/samsung/gts7l/kona-sec-gts7lwifi-eur-overlay-r0{2..7}.dts`
  - Pinctrl: `kona-sec-gts7lwifi-pinctrl-r0{2..7}.dtsi`
  - PM: `kona-sec-gts7lwifi-pm-r02.dtsi`
  - Board includes: `kona-sec-gts7lwifi-r0{2..7}.dtsi`
  - Firmware: `firmware/abov/a96t356_gts7lwifi_{main1,wifi1}.bin`
- **CI:** GitHub Actions produces .deb packages (currently only gts7xlwifi target)
- **What to change:** `debian/kernel-info.mk` → point to gts7lwifi

### Adaptation (mukahraman)
- **Repo:** https://github.com/mukahraman/adaptation-samsung-gts7xlwifi
- **Contents:** udev rules, PulseAudio config, libinput quirks, Phosh config, BT address script, audio HAL overlay, Firefox video pref
- **What to change:** Global rename gts7xlwifi→gts7lwifi, touch calibration params, udev sysfs paths

### Recipes (mukahraman)
- **Repo:** https://github.com/mukahraman/droidian-recipes
- **Purpose:** Builds flashable rootfs image incorporating kernel .deb + adaptation .deb

### Flashing Tools (mukahraman)
- **Repo:** https://github.com/mukahraman/galaxy-tab-s7-plus-droidian
- **Key files:** `tools/build-bootimg.py`, `tools/make-touchpad-dtbo.py`, `testkey_rsa4096.pem`, `vbmeta-disabled.img`

## LineageOS (official, maintained)
- **Device tree:** https://github.com/LineageOS/android_device_samsung_gts7lwifi (branch: lineage-23.2)
  - Contains: mixer_paths.xml (150KB, T870-specific audio routing), BoardConfig.mk, init.gts7lwifi.rc, sensor configs, overlays
  - Partition sizes: boot=71303168, recovery=86888448, dtbo=10485760, cache=629145600, super=10171187200
- **Common:** https://github.com/LineageOS/android_device_samsung_gts7l (shared base with LTE variant)
- **Vendor blobs:** https://github.com/TheMuppets/proprietary_vendor_samsung_gts7lwifi (lineage-23.2)
  - Contains: ACDB audio calibration files (Speaker_cal.acdb, Headset_cal.acdb, etc.)

## TWRP Recovery
- **Device tree:** https://github.com/ShionKanagawa/android_device_samsung_gts7lwifi-twrp (updated 2026-05)
  - Has prebuilt: Image.gz, dtb.img, dtbo.img
  - Touch firmware: novatek_nt36523_k82_fw01.bin, fw02.bin
  - Boot header v2, page_size=4096, kernel_offset=0x00008000, ramdisk_offset=0x02000000, dtb_offset=0x01f00000
- **Alternative:** https://github.com/GT642/twrp_gts7lwifi (2024)

## Other Community Kernel Sources
- https://github.com/ianmacd/gts7l — ianmacd's kernel (LineageOS-based, has caliban defconfig)
- https://github.com/Official-Ayrton990/android_kernel_samsung_sm8250 — has T870 defconfig
- https://github.com/ShionKanagawa/android_kernel_samsung_gts7l — has T870 defconfig

## Key Hardware Differences from T970 (Port Impact)

| Component | T870 (ours) | T970 (source) | Port Impact |
|-----------|-------------|---------------|-------------|
| Display panel | NT36523 LCD (CONFIG_PANEL_NT36523_PPA957DB1_WQXGA) | S6E3 AMOLED (CONFIG_PANEL_S6TUUM0..3) | Kernel config swap (already done in gts7lwifi.config) |
| Touch IC | NT36523 TDDI (CONFIG_TOUCHSCREEN_NOVATEK_NT36523) | STM FTS1BA90A (CONFIG_TOUCHSCREEN_FTS1BA90A) | Kernel config swap + udev calibration rules |
| Resolution | 2560×1600 | 2800×1752 | Phosh/compositor auto-detects; S-Pen calibration may need rescale |
| Light sensor | VEML3235 | VEML3328 | Kernel config swap |
| Camera sensor | GW3X | GW9558X | Kernel config swap; camera app should work via libcamera/android HAL |
| DDIC regulator | none (LCD) | S2DOS06 (AMOLED) | Not needed for T870 |
| Project flag | CONFIG_SEC_GTS7L_PROJECT | CONFIG_SEC_GTS7XL_PROJECT | Kernel config swap |
| MACH flag | CONFIG_MACH_GTS7LWIFI_EUR_OPEN | CONFIG_MACH_GTS7XLWIFI_EUR_OPEN | Kernel config swap |
| Fingerprint | Goodix (optical under-display) | Goodix (optical under-display) | Same — likely works as-is |

## What's NOT Missing (good news)
- Kernel source: complete T870 support in mukahraman's droidian branch
- Device tree: all overlays/pinctrl/PM dtsi present
- Config fragment: gts7lwifi.config exists
- TWRP: prebuilt available
- Audio ACDB: available via TheMuppets vendor blobs
- Vendor blobs: available via TheMuppets (lineage-23.2)
- Community maintenance: LineageOS official device, actively maintained

## What Needs To Be Done
1. Fork kernel → modify `debian/kernel-info.mk` → push → CI builds T870 .deb
2. Fork adaptation → global rename + touch/epen calibration + udev paths
3. Adapt flashing tools (build-bootimg.py cmdline, dtbo script)
4. Get TWRP .img (build from ShionKanagawa tree or find prebuilt .tar)
5. Flash and debug
