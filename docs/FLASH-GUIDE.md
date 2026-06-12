# Droidian on Samsung Galaxy Tab S7 Wi-Fi (SM-T870) — Flash Guide

## Prerequisites

### Hardware
- Samsung Galaxy Tab S7 Wi-Fi (SM-T870) with **unlocked bootloader**
- USB-C cable (data-capable)
- PC running Linux (or WSL2 with USB passthrough)

### Software (on PC)
```bash
sudo apt install heimdall-flash android-tools-adb android-sdk-libsparse-utils \
    python3 device-tree-compiler binutils unzip
pip3 install avbtool   # or build from AOSP source
```

### Downloads
1. **Kernel .deb** — from your fork's GitHub Actions CI release:
   `linux-bootimage-4.19-325-samsung-gts7lwifi_*.deb`
2. **Droidian rootfs** — nightly from https://images.droidian.org/:
   `droidian-rootfs-api30-arm64-nightly_YYYYMMDD.zip`
3. **TWRP recovery** — build from `ShionKanagawa/android_device_samsung_gts7lwifi-twrp`
   or get a prebuilt `twrp-gts7lwifi.img.tar`
4. **vbmeta-disabled.img** — from this repo or the source repo (64KB, flags=0x02)
5. **testkey_rsa4096.pem** — AOSP AVB test key (from this repo)

## Step 0: Unlock Bootloader

> **WARNING: This trips Knox and voids warranty permanently.**

1. Enable Developer Options → OEM Unlocking
2. Power off → hold Vol-Down + Vol-Up + connect USB → Download Mode
3. Long-press Vol-Up to unlock
4. Device factory-resets and reboots
5. **Wait 7 days** then re-enable OEM Unlocking (VaultKeeper requirement)
6. Repeat step 2-3 to finalize unlock

## Step 1: Extract Kernel Boot Image

```bash
# Extract the .deb
ar x linux-bootimage-4.19-325-samsung-gts7lwifi_*.deb
tar xf data.tar.* ./boot/
# The raw boot.img is at:
ls boot/boot.img-4.19-325-samsung-gts7lwifi
```

## Step 2: Build Samsung-Acceptable Boot Image

```bash
python3 tools/build-bootimg.py \
    boot/boot.img-4.19-325-samsung-gts7lwifi \
    boot-tab.img

# For first-boot debugging (drops to telnet rescue shell):
python3 tools/build-bootimg.py \
    boot/boot.img-4.19-325-samsung-gts7lwifi \
    boot-rescue.img --rescue
```

## Step 3: Patch DTBO (Book Cover Trackpad Fix)

Skip this if you don't have a Book Cover Keyboard, but recommended:

```bash
# Extract dtbo from the kernel .deb
tar xf data.tar.* ./boot/dtbo.img-4.19-325-samsung-gts7lwifi
python3 tools/make-touchpad-dtbo.py \
    boot/dtbo.img-4.19-325-samsung-gts7lwifi \
    dtbo-tab.img
```

## Step 4: Prepare Rootfs

```bash
unzip droidian-rootfs-api30-arm64-nightly_*.zip
# Produces: droidian-rootfs-api30-arm64.img (sparse image)
simg2img droidian-rootfs-api30-arm64.img droidian-rootfs.raw
```

## Step 5: Flash TWRP + vbmeta (Download Mode)

1. Power off tablet
2. Enter Download Mode: Vol-Down + Vol-Up + connect USB
3. Flash:

```bash
heimdall flash \
    --VBMETA vbmeta-disabled.img \
    --RECOVERY twrp-gts7lwifi.img \
    --no-reboot
```

4. Unplug USB, hold Power + Vol-Down to power off
5. Boot to TWRP: hold Vol-Up + Power until Samsung logo, release Power

## Step 6: Write Rootfs to userdata (in TWRP)

```bash
# On PC, with tablet in TWRP and USB connected:
adb shell "dd if=/dev/zero of=/dev/block/by-name/userdata bs=4096 count=1024"
adb push droidian-rootfs.raw /tmp/
adb shell "dd if=/tmp/droidian-rootfs.raw of=/dev/block/by-name/userdata bs=4096"

# Alternative (pipe method, saves space on device):
cat droidian-rootfs.raw | adb shell -T "dd of=/dev/block/by-name/userdata bs=4096"
```

## Step 7: Flash Kernel + DTBO (Download Mode)

1. Power off tablet
2. Enter Download Mode again
3. Flash everything:

```bash
heimdall flash \
    --VBMETA vbmeta-disabled.img \
    --BOOT boot-tab.img \
    --DTBO dtbo-tab.img \
    --no-reboot
```

> **IMPORTANT:** Always include `--VBMETA` on every flash — single-image flashes
> commit unreliably on SM8250 Samsung devices.

4. Unplug, hold Power to boot

## Step 8: First Boot

- First boot takes 2-3 minutes (Halium init, LVM setup, filesystem resize)
- You should see the Phosh lock screen
- Default credentials: `droidian` / `1234`

### If boot fails (black screen / reboot loop)

1. Flash the `--rescue` boot image instead
2. Connect USB, check `dmesg | grep usb` for RNDIS interface
3. Configure host: `ip addr add 192.168.2.1/24 dev <iface>`
4. Telnet in: `telnet 192.168.2.15`
5. Check `dmesg` and `/proc/last_kmsg` for kernel panics

## Post-Install

### Install adaptation package
```bash
# SSH or telnet into the device, then:
sudo dpkg -i adaptation-samsung-gts7lwifi*.deb
sudo apt -f install
```

### WiFi
Should work out of the box via NetworkManager. If routes are missing:
```bash
sudo /usr/lib/adaptation-samsung-gts7lwifi/wlan-routes-fix
```

### Audio
```bash
systemctl --user restart pulseaudio
pactl list sinks  # should show droid card
```

## Partition Map (SM-T870)

| Partition | Size | Notes |
|-----------|------|-------|
| BOOT | 71303168 (68MB) | Kernel + ramdisk + dtb |
| RECOVERY | 86888448 (83MB) | TWRP |
| DTBO | 10485760 (10MB) | Device tree overlays |
| VBMETA | 65536 (64KB) | Verification disabled |
| userdata | ~113GB | Droidian rootfs (f2fs/ext4) |
| super | ~10GB | Android system/vendor/product (keep intact!) |

## Troubleshooting

### "Heimdall ERROR: Protocol initialisation failed!"
- Try a different USB port (USB-2.0 hubs sometimes work better)
- On Linux: `sudo` or add udev rule for Samsung

### Boot loops after flash
- Always include `--VBMETA` in every heimdall flash command
- Check if boot.img fits: must be < 71303168 bytes with AVB footer

### No display after boot
- Try rescue image, telnet in, check `/sys/class/drm/card0-DSI-1/status`
- The NT36523 panel needs the vendor partition's display HAL — don't wipe vendor/super

### Touch not working
- Check `cat /proc/bus/input/devices` for `sec_touchscreen`
- Verify udev rules are installed: `ls /etc/udev/rules.d/98-touch-calib.rules`
