# postmarketOS / Mainline Linux for SM-T870 — Technical Notes

## Current Status (as of 2026-06-12)

### Mainline Kernel Support

**Existing DTS:** `sm8250-samsung-gts7l.dts` in [itzreesa/sm8250-mainline](https://github.com/itzreesa/sm8250-mainline) (branch `6.13.0-gts7l`)

Working subsystems in that DTS:
- Framebuffer (simplefb, 2560x1600)
- USB dual-controller (usb_1 + usb_2, both HS)
- Touchscreen (Novatek NVT-TS on i2c5 @ 0x62)
- Bluetooth (QCA6390 on uart6)
- GPIO keys (volume up/down)
- Regulators (pm8150 LDOs)
- USB Type-C PHY (pm8150b)
- ramoops (crash logging)

NOT in the DTS yet:
- Display panel DSI node (using simplefb instead)
- WiFi (QCA6390 / ath11k) — needs PCIe + firmware DT node
- Audio (CS35L41 codec on SPI/I2C)
- GPU (Adreno 650 / freedreno) — SoC DTSI has it, just needs panel + display pipe
- S-Pen (Wacom W9021 @ i2c 0x56, IRQ gpio136) — needs custom driver extension
- Sensors (accelerometer, light)
- NFC

### Panel Driver — The Key Finding

**`panel-novatek-nt36523.c` already exists in mainline!**

File: `drivers/gpu/drm/panel/panel-novatek-nt36523.c`
DT binding: `Documentation/devicetree/bindings/display/panel/novatek,nt36523.yaml`

Currently supports:
- `lenovo,j606f-boe-nt36523w` (Lenovo Tab P11)
- `xiaomi,elish-boe-nt36523` (Mi Pad 5 Pro, BOE panel)
- `xiaomi,elish-csot-nt36523` (Mi Pad 5 Pro, CSOT panel)

To add T870 support, you need:
1. Extract the DSI init sequence from downstream kernel
2. Add a `samsung_gts7l_ppa957db1_desc` panel descriptor
3. Add a `samsung,gts7l-ppa957db1-nt36523` compatible string
4. Add mode timing (2560x1600 @ 120Hz)

### How to Extract DSI Init Sequence

The downstream kernel has the init commands in a device tree include:
```
arch/arm64/boot/dts/samsung/drivers/kona-sec-gts7l-display-r00.dtsi
```

Look for `qcom,mdss-dsi-on-command` — this is an array of DSI commands that
gets sent to the panel during power-on. Each command is:
```
{header} {payload...} {last_cmd} {wait_ms}
```

Convert these to `mipi_dsi_dcs_write_seq()` calls for the mainline driver.
The elish_boe panel has ~345 such commands — expect similar complexity.

### Panel Timing

From downstream DTS look for:
- `qcom,mdss-dsi-panel-width` = 1600 (T870 is portrait-native, so w<h)
- `qcom,mdss-dsi-panel-height` = 2560
- `qcom,mdss-dsi-panel-framerate` = 120
- `qcom,mdss-dsi-panel-clockrate` / `qcom,mdss-dsi-panel-bitclk`
- `qcom,mdss-dsi-h-*` (front/back porch, pulse width)
- `qcom,mdss-dsi-v-*` (vertical timing)

### DTS Structure (T870 Panel Node)

```dts
&dsi0 {
    status = "okay";
    
    panel@0 {
        compatible = "samsung,gts7l-ppa957db1-nt36523", "novatek,nt36523";
        reg = <0>;
        
        reset-gpios = <&tlmm XX GPIO_ACTIVE_LOW>;
        vddio-supply = <&vreg_l12a_1p8>;
        
        port {
            panel_in: endpoint {
                remote-endpoint = <&dsi0_out>;
            };
        };
    };
};
```

### WiFi DTS Node Template

```dts
&pcie0 {
    status = "okay";
    
    wifi@0 {
        compatible = "qcom,wcn6750-wifi";  /* or qca6390 */
        reg = <0x10000 0x0 0x0 0x0 0x0>;
        /* firmware: ath11k/QCA6390/hw2.0/ */
    };
};
```

### Estimated Effort

| Task | Difficulty | Time |
|------|-----------|------|
| Extract DSI init sequence from downstream | Low-Med | 2-4 hours |
| Add panel_desc to nt36523 driver | Low | 1-2 hours |
| Wire up DSI in DTS (replace simplefb) | Medium | 2-4 hours |
| Add WiFi PCIe + ath11k node | Low | 1-2 hours |
| Audio (CS35L41 codec DTS wiring) | Medium | 4-8 hours |
| S-Pen (Wacom W9021 driver + DTS) | Medium | 4-8 hours |
| pmOS APKBUILD packaging | Low | 2-3 hours |
| Testing & debugging | High | Days |

**Total realistic estimate: 2-4 weekends** assuming Droidian is already running (for comparison testing) and you can read downstream DTS fluently.

### Comparison: Effort vs Reward

| Metric | Droidian | pmOS (mainline) |
|--------|----------|-----------------|
| Time to first boot | 1 day | 2-4 weekends |
| Kernel security updates | Stuck on 4.19 | Follows upstream |
| GPU performance | Good (Android HAL) | Excellent (native freedreno) |
| App ecosystem | Debian apt (same) | Alpine apk (smaller but less) |
| Desktop environments | Phosh | Phosh / Plasma Mobile / Sway |
| Waydroid (Android apps) | Works | Works (with halium compat) |
| Long-term viability | Vendor blobs rot | Mainline tracks upstream |

### Next Steps for pmOS Path

1. Get Droidian working first (validates hardware, provides debug path)
2. Clone itzreesa/sm8250-mainline
3. Extract DSI init from downstream `kona-sec-gts7l-display-r00.dtsi`
4. Add panel variant to `panel-novatek-nt36523.c`
5. Test with pmOS rootfs (alpine + phosh)
6. Upstream the DTS + panel variant to linux-next

---

## GNOME Desktop on Wayland — Daily-Driver Feasibility (2026-06-12)

### GPU Driver (freedreno / Adreno 650)

| API | Version | Notes |
|-----|---------|-------|
| OpenGL | 4.6 | 100% complete, tied #1 among Mesa drivers |
| OpenGL ES | 3.2 | 100% complete |
| Vulkan (turnip) | 1.3 | 217/297 extensions (73%), 1.4 is a7xx-only |
| OpenCL (Rusticl) | Experimental | `RUSTICL_ENABLE=freedreno`, not conformant |
| VA-API | N/A | Does NOT exist for Qualcomm; use v4l2 (GStreamer/FFmpeg) |

**Key capabilities:**
- UBWC (bandwidth compression) — helps at 2560x1600
- Compositor-aware autotuning (`TU_AUTOTUNE_FLAGS=preempt_optimize`)
- No resolution caps; 2560x1600 @ 120Hz is hardware-supported
- Firmware needed: `a650_zap.mbn` (device-specific), `a650_sqe.fw` + `a650_gmu.bin` (linux-firmware)

**Verdict:** GPU is more than sufficient for Mutter/GNOME Shell compositing at full resolution.

### HiDPI / Fractional Scaling

At 2560x1600 on 11" (~274 PPI):
- **200%** → 1280x800 logical (usable but cramped)
- **150%** → ~1707x1067 logical (recommended sweet spot)
- **175%** → ~1463x914 logical (larger touch targets)

Enable in GNOME 47+:
```bash
gsettings set org.gnome.mutter experimental-features \
  '["scale-monitor-framebuffer", "xwayland-native-scaling"]'
```

- GTK4/Qt6 apps render natively at fractional scale (sharp)
- XWayland apps: GNOME 47 added native-scaling (less blur)
- Still marked "experimental" but stable in practice

### Touch Gestures (GNOME 45+)

| Gesture | Action |
|---------|--------|
| 3-finger swipe up | Activities Overview |
| 3-finger swipe left/right | Switch workspaces |
| Edge swipe from bottom | On-screen keyboard |
| Edge swipe from top | Exit fullscreen |
| Press and hold | Context menu |
| 2-finger pinch | Zoom |

Gestures are "fluid and interruptible" — cancel mid-swipe works.
Missing: no swipe-down for notification panel (tap only).

### On-Screen Keyboard

- Built into GNOME Shell, auto-shows on text field tap
- GNOME 46: auto-capitalization, context-specific layouts (phone, email, URL)
- IBus integration for CJK (ibus-pinyin etc.), but candidate selection UX is weak
- **Missing:** no swipe typing, no word prediction, no split keyboard for landscape
- Bottom-edge swipe up to invoke, swipe down to dismiss

### Auto-Rotation

Works via `iio-sensor-proxy` → D-Bus → GNOME Shell.
Needs: accelerometer IIO driver in kernel + DTS node.
SM-T870 has an accelerometer (LSM6DSO series likely) — needs DTS wiring.

### Suspend/Resume (SM8250 mainline)

- **s2idle** (suspend-to-idle): generally functional
- GPU resume: Adreno 6xx needs full re-init on wake (GMU firmware reload)
- Known issue: occasional GPU hang on resume (kernel 6.6+ has fixes)
- Battery drain in suspend: **5-15% per hour** (vs <1% on Android)
- Deep suspend (s2ram): unreliable, depends on PSCI firmware

**This is the single biggest blocker for daily-driver use.**

### Video Decode

- No VA-API path exists for Qualcomm hardware
- Use kernel `venus` driver (v4l2 interface) via:
  - GStreamer `v4l2codecs` plugin
  - FFmpeg `v4l2_m2m` decoder
- Hardware decode works but browser integration requires manual setup
- Firmware: `venus.mbn` from device vendor partition

### Overall Daily-Driver Assessment

| Feature | Rating | Blocker? |
|---------|--------|----------|
| GPU / compositing | Excellent | No |
| HiDPI scaling | Good | No |
| Touch gestures | Adequate | No |
| On-screen keyboard | Fair | Soft (CJK weak) |
| Auto-rotation | Good | No (needs DTS) |
| Suspend/battery | Poor | **YES** |
| Camera | Non-functional | Soft |
| Tablet UI density | Poor | Soft |

**Honest verdict:** GNOME on Wayland CAN run on SM-T870 with full GPU acceleration. The 
desktop experience works — browsing, coding, document editing. But as a grab-and-go tablet 
replacing an iPad:

- **Suspend drains battery fast** → must treat it like a laptop (close lid = shut down)
- **No polished tablet UI** → works with S-Pen/keyboard dock, awkward with just fingers
- **CJK input limited** → IBus works but not mobile-quality

**Best use case:** Linux development tablet with Book Cover keyboard + S-Pen, where you
close the lid and plug in to charge. NOT a media consumption / casual tablet.

### Alternative: Phosh (lighter, touch-first)

If pure tablet UX matters more than "full GNOME desktop", Phosh (used in Droidian) is 
actually better suited:
- Designed for touch from day one (Librem 5 / PinePhone)
- Proper mobile gestures, app drawer, notification pull-down
- Smaller resource footprint
- But: phone-oriented layout on 11" screen may waste space

### Recommended DE Combinations

| Use Case | DE | Why |
|----------|-----|-----|
| Developer tablet (keyboard dock) | GNOME | Full desktop, fractional scaling, good with physical KB |
| Casual tablet (touch only) | Phosh | Mobile-first UX, better gestures, auto-show keyboard |
| Tiling/productivity | Sway | Wayland tiling, extremely lightweight, needs keyboard |
| Compromise | Plasma Mobile | Touch-friendly + desktop features, Qt-based |
