#!/usr/bin/env python3
"""Reject floating or unowned direct source and Action dependencies."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "dependencies.lock.json").read_text())
allowed = set()
for dependency in lock["sources"].values():
    assert dependency["repository"].startswith("https://github.com/Tinnci/")
    assert re.fullmatch(r"[0-9a-f]{40}", dependency["commit"])
for dependency in lock["actions"].values():
    assert dependency["repository"].startswith("Tinnci/")
    assert re.fullmatch(r"[0-9a-f]{40}", dependency["commit"])
    allowed.add(f'{dependency["repository"]}@{dependency["commit"]}')
for workflow in (ROOT / ".github/workflows").glob("*.y*ml"):
    for action in re.findall(r"uses:\s*([^\s]+)", workflow.read_text()):
        assert action in allowed, f"unlocked Action in {workflow}: {action}"
for image in lock["images"].values():
    assert re.search(r"@sha256:[0-9a-f]{64}$", image), image
print(f'Checked {len(lock["sources"])} source forks, {len(allowed)} Action forks and pinned bootstrap images')
