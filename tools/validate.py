#!/usr/bin/env python3
"""Validate plugins/* listings before merge."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESERVED = {"orion-stt", "orion-tts", "orion-core", "orion-agent", "orion-voice"}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = []
    reserved_file = root / "policy" / "reserved-ids.json"
    reserved = set(RESERVED)
    if reserved_file.is_file():
        reserved.update(json.loads(reserved_file.read_text(encoding="utf-8")).get("reserved") or [])

    for plug in sorted((root / "plugins").glob("*")):
        if not plug.is_dir():
            continue
        meta_p = plug / "plugin.json"
        if not meta_p.is_file():
            errors.append(f"{plug.name}: missing plugin.json")
            continue
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        pid = meta.get("id") or plug.name
        if pid != plug.name:
            errors.append(f"{plug.name}: id {pid!r} != folder name")
        if not ID_RE.match(str(pid)):
            errors.append(f"{pid}: bad id")
        if pid in reserved:
            errors.append(f"{pid}: reserved id")
        for key in ("name", "summary", "license", "repository"):
            if not meta.get(key):
                errors.append(f"{pid}: missing {key}")
        versions = list((plug / "versions").glob("*.json")) if (plug / "versions").is_dir() else []
        if not versions:
            errors.append(f"{pid}: no versions/")
        for vp in versions:
            v = json.loads(vp.read_text(encoding="utf-8"))
            if v.get("staging"):
                continue
            if not (v.get("sha256") or (v.get("artifacts") or [{}])[0].get("sha256")):
                errors.append(f"{pid}@{vp.stem}: non-staging without sha256")
            url = v.get("download_url") or v.get("downloadUrl") or ((v.get("artifacts") or [{}])[0].get("url"))
            if not url or not str(url).startswith("https://"):
                errors.append(f"{pid}@{vp.stem}: need https download url")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print("OK: registry listings valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
