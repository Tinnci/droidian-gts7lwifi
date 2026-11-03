#!/usr/bin/env python3
"""Check out the exact source commits from dependencies.lock.json."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    subprocess.run(["git", *map(str, args)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=ROOT / "out/sources")
    parser.add_argument("--only", nargs="+")
    args = parser.parse_args()
    sources = json.loads((ROOT / "dependencies.lock.json").read_text())["sources"]
    for name in args.only or sources:
        dependency = sources[name]
        path = args.destination.resolve() / name
        if not (path / ".git").exists():
            path.mkdir(parents=True, exist_ok=True)
            git("init", path)
            git("-C", path, "remote", "add", "origin", dependency["repository"])
        status = subprocess.check_output(["git", "-C", str(path), "status", "--porcelain"], text=True)
        if status:
            raise SystemExit(f"refusing to replace modified dependency: {path}")
        git("-C", path, "fetch", "--depth", "1", "origin", dependency["commit"])
        git("-C", path, "checkout", "--detach", "FETCH_HEAD")


if __name__ == "__main__":
    main()
