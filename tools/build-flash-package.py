#!/usr/bin/env python3
"""Build and verify a T870 flash package from a local kernel .deb."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def field(package, name):
    return subprocess.check_output(["dpkg-deb", "-f", str(package), name], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kernel-deb", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "out/flash")
    args = parser.parse_args()
    args.kernel_deb = args.kernel_deb.resolve()
    args.output = args.output.resolve()
    expected = "linux-bootimage-4.19-325-samsung-gts7lwifi"
    if field(args.kernel_deb, "Package") != expected or field(args.kernel_deb, "Architecture") != "arm64":
        parser.error(f"expected arm64 package {expected}")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("output directory must be empty")
    for tool in ("avbtool", "dtc", "dpkg-buildpackage", "dh", "openssl"):
        if not shutil.which(tool):
            parser.error(f"missing build dependency: {tool}")
    with tempfile.TemporaryDirectory(prefix="t870-build-") as directory:
        work = Path(directory)
        image_dir = work / "flash"
        image_dir.mkdir()
        run("dpkg-deb", "-x", args.kernel_deb, work / "kernel")
        boot = list((work / "kernel/boot").glob("boot.img-*"))
        dtbo = list((work / "kernel/boot").glob("dtbo.img-*"))
        if len(boot) != 1 or len(dtbo) != 1:
            raise ValueError("kernel package must contain exactly one boot image and DTBO")
        key = ROOT / "testkey_rsa4096.pem"
        for name, flags in (("boot.img", []), ("boot-rescue.img", ["--rescue"])):
            run("python3", ROOT / "tools/build-bootimg.py", boot[0], image_dir / name, *flags)
        run("python3", ROOT / "tools/make-touchpad-dtbo.py", dtbo[0], image_dir / "dtbo.img")
        for name in ("boot.img", "boot-rescue.img"):
            verify_dir = work / f"verify-{name}"
            verify_dir.mkdir()
            shutil.copy2(image_dir / name, verify_dir / "boot.img")
            run("avbtool", "verify_image", "--image", verify_dir / "boot.img", "--key", key)
        shutil.copy2(ROOT / "vbmeta-disabled.img", image_dir)
        info = subprocess.check_output(["avbtool", "info_image", "--image",
                                        str(image_dir / "vbmeta-disabled.img")], text=True)
        if not any(line.split() == ["Flags:", "2"] for line in info.splitlines()):
            raise ValueError("vbmeta must use flags=2")
        source = work / "adaptation"
        shutil.copytree(ROOT / "adaptation", source, ignore=shutil.ignore_patterns(".git"))
        run("dpkg-buildpackage", "-us", "-uc", "-b", cwd=source)
        for package in work.glob("adaptation-*.deb"):
            shutil.copy2(package, image_dir)
        configs = list(image_dir.glob("adaptation-*-configs_*.deb"))
        if len(configs) != 1:
            raise ValueError("missing adaptation configs package")
        run("dpkg-deb", "-x", configs[0], work / "installed")
        installed = work / "installed"
        for path in ("usr/lib/systemd/system/wlan-routes.service",
                     "usr/lib/droid-vendor-overlay/etc/init/android.hardware.audio.service.rc",
                     "usr/lib/droid-vendor-overlay/lib64/hw/audio.primary.kona.so"):
            if not (installed / path).is_file():
                raise ValueError(f"adaptation payload missing: {path}")
        for path in ("usr/bin/droid/droid-get-bt-address.sh",
                     "etc/systemd/system/multi-user.target.wants/wlan-routes.service"):
            if not (installed / path).is_symlink():
                raise ValueError(f"adaptation link missing: {path}")
        shutil.copy2(ROOT / "QUICK-FLASH.md", image_dir)
        manifest = {
            "kernel_package": args.kernel_deb.name,
            "kernel_sha256": hashlib.sha256(args.kernel_deb.read_bytes()).hexdigest(),
            "kernel_version": field(args.kernel_deb, "Version"),
            "source_commit": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
            "source_dirty": bool(subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain"], text=True).strip()),
            "adaptation_commit": subprocess.check_output(["git", "-C", str(ROOT / "adaptation"), "rev-parse", "HEAD"], text=True).strip(),
        }
        lock = ROOT / "dependencies.lock.json"
        if lock.exists():
            manifest["dependencies"] = json.loads(lock.read_text())
        (image_dir / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        checksums = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
                            for path in sorted(image_dir.iterdir()) if path.is_file())
        (image_dir / "SHA256SUMS").write_text(checksums)
        shutil.copytree(image_dir, args.output, dirs_exist_ok=True)
    print(f"Verified flash package: {args.output}")


if __name__ == "__main__":
    main()
