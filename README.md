# Droidian Port for Samsung Galaxy Tab S7 Wi-Fi (SM-T870 / gts7lwifi)

Ported from [mukahraman/galaxy-tab-s7-plus-droidian](https://github.com/mukahraman/galaxy-tab-s7-plus-droidian) (SM-T970 / gts7xlwifi).

## Quick Start

### 1. Fork & Patch Kernel
```bash
gh repo fork mukahraman/kernel_samsung_sm8250 --clone
cd kernel_samsung_sm8250
git checkout droidian
cp /path/to/tabs7-roms/kernel-patches/kernel-info.mk debian/kernel-info.mk
cp /path/to/tabs7-roms/kernel-patches/extra.config droidian/extra.config
git add -A && git commit -m "Port to gts7lwifi (SM-T870)"
git push origin droidian
# GitHub Actions will build linux-bootimage-*-samsung-gts7lwifi.deb
```

### 2. Build Adaptation Package
```bash
cd /path/to/tabs7-roms/adaptation
dpkg-buildpackage -us -uc -b
# Or push to GitHub and let Droidian CI build it
```

### 3. Flash
See [docs/FLASH-GUIDE.md](docs/FLASH-GUIDE.md) for the full step-by-step.

## Project Structure

```
tabs7-roms/
├── README.md
├── RESOURCES.md              # Full resource inventory & links
├── kernel-patches/
│   ├── kernel-info.mk        # Drop-in replacement for debian/kernel-info.mk
│   └── extra.config          # Droidian kconfig fragment (drop into droidian/)
├── adaptation/               # Full adaptation-samsung-gts7lwifi Debian package
│   ├── debian/
│   ├── etc/                  # udev, phosh, pulse, libinput, bluetooth configs
│   └── usr/                  # scripts, device flags, audio HAL overlay
├── tools/
│   ├── build-bootimg.py      # Patch boot.img header + AVB footer for T870
│   └── make-touchpad-dtbo.py # Fix Book Cover trackpad orientation
└── docs/
    └── FLASH-GUIDE.md        # Complete flashing instructions
```

## What's Different from T970 Port

| Area | Change |
|------|--------|
| kernel-info.mk | DEVICE_MODEL, cmdline buildproduct, DTBO path, FLASH_INFO |
| extra.config | Comment header only (all kconfig identical) |
| phoc.ini | Scale comment (2560x1600 vs 2800x1752) |
| libinput quirks | S-Pen resolution 97x97 (vs 100x100 for larger panel) |
| debian/ | Package names gts7xlwifi → gts7lwifi |
| Partition sizes | boot=71303168 (same), dtbo=10485760 (same) |

## Status

- [x] Kernel config verified (gts7lwifi.config exists in upstream)
- [x] Device tree overlays verified (kona-sec-gts7lwifi-eur-overlay-r02..r07)
- [x] TWRP available (ShionKanagawa/android_device_samsung_gts7lwifi-twrp)
- [x] Vendor blobs available (TheMuppets/proprietary_vendor_samsung_gts7lwifi)
- [x] Audio ACDB calibration available (in vendor blobs)
- [ ] First boot (pending hardware flash)
- [ ] Touch verification
- [ ] Audio verification
- [ ] Camera verification
