"""Regression coverage for image corruption and silent DTBO patch failures."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dtbo = load("make-touchpad-dtbo")
boot = load("build-bootimg")


class ImageTests(unittest.TestCase):
    def test_stock_touchpad_and_idempotence(self):
        fixed, changes = dtbo.patch_dts("touchpad,invert = <0 1 1>;")
        self.assertEqual(changes, 1)
        self.assertEqual(dtbo.patch_dts(fixed), (fixed, 0))

    def test_missing_or_unknown_touchpad_rejected(self):
        for source in ("/ {};", "touchpad,invert = <1 1 0>;", "touchpad,invert = <0 0>;"):
            with self.assertRaises(ValueError):
                dtbo.patch_dts(source)

    def test_truncated_table_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                dtbo.patch_table(b"short", Path(directory))

    def test_boot_header_and_extended_cmdline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "boot.img"
            data = bytearray(8192)
            data[:8] = b"ANDROID!"
            marker = b"SEANDROIDENFORCE"
            struct.pack_into("<I", data, 8, len(marker))
            struct.pack_into("<I", data, 36, 4096)
            struct.pack_into("<I", data, 40, 2)
            data[608:1632] = b"x" * 1024
            data[4096:4096 + len(marker)] = marker
            path.write_bytes(data)
            boot.patch_header(path, boot.CMDLINE_REAL)
            result = path.read_bytes()
            self.assertEqual(result[608:1632], b"\x00" * 1024)
            self.assertEqual(result[64:64 + len(boot.CMDLINE_REAL)], boot.CMDLINE_REAL.encode())
            data[40] = 3
            path.write_bytes(data)
            with self.assertRaises(ValueError):
                boot.patch_header(path, boot.CMDLINE_REAL)


if __name__ == "__main__":
    unittest.main()
