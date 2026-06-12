# Droidian on Galaxy Tab S7 Wi-Fi (SM-T870) — Quick Flash Guide

## You Need

- This flash package (boot.img, dtbo.img, vbmeta-disabled.img, adaptation .deb)
- Droidian rootfs: download `droidian-rootfs-api30-arm64-nightly_*.zip` from https://images.droidian.org/
- TWRP recovery for gts7lwifi (build from ShionKanagawa/android_device_samsung_gts7lwifi-twrp)
- PC with `heimdall-flash` and `adb` installed
- USB-C data cable
- **Bootloader must be unlocked** (Settings → Developer Options → OEM Unlock → Download Mode → Vol-Up)

## Flash Steps

### 1. Enter Download Mode

Power off → hold **Vol-Down + Vol-Up** → connect USB cable

### 2. Flash vbmeta + TWRP

```bash
heimdall flash --VBMETA vbmeta-disabled.img --RECOVERY twrp.img --no-reboot
```

### 3. Boot into TWRP

Unplug → hold **Vol-Up + Power** until Samsung logo → release Power (keep Vol-Up)

### 4. Write Droidian rootfs to userdata

```bash
# On PC:
unzip droidian-rootfs-api30-arm64-nightly_*.zip
simg2img droidian-rootfs-api30-arm64.img rootfs.raw
adb push rootfs.raw /tmp/
adb shell "dd if=/tmp/rootfs.raw of=/dev/block/by-name/userdata bs=4096"
```

### 5. Flash kernel + DTBO (Download Mode)

Power off → Download Mode again:

```bash
heimdall flash --VBMETA vbmeta-disabled.img --BOOT boot.img --DTBO dtbo.img --no-reboot
```

### 6. First Boot

Unplug → Power on. Wait 2-3 minutes. Login: `droidian` / `1234`

### 7. Install Adaptation (after boot, via USB/SSH)

```bash
adb push adaptation-samsung-gts7lwifi-configs_0.0.1_all.deb /tmp/
adb shell
sudo dpkg -i /tmp/adaptation-samsung-gts7lwifi-configs_0.0.1_all.deb
sudo reboot
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Heimdall connection error | Try USB 2.0 port, run as root |
| Boot loops | Flash `boot-rescue.img` instead, telnet to 192.168.2.15 |
| Black screen after boot | Don't wipe super/vendor partition — display HAL lives there |
| Touch not working | Install adaptation .deb (step 7), reboot |
| WiFi not connecting | Run: `sudo /usr/lib/adaptation-samsung-gts7lwifi/wlan-routes-fix` |

## Important Notes

- **Always include `--VBMETA`** in every heimdall command
- **Never wipe the `super` partition** — it contains the Android vendor HAL that Droidian needs
- boot.img must be < 68MB (partition limit: 71303168 bytes)
- Default SSH is disabled; use `adb shell` or enable via Settings after boot
