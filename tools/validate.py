#!/usr/bin/env python3
"""Validate plugins/* listings and registry/v1/index.json before merge."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA_RE = re.compile(r"^[a-fA-F0-9]{64}$")
RESERVED = {"orion-stt", "orion-tts", "orion-core", "orion-agent", "orion-voice"}


def load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def download_url(v: Dict[str, Any]) -> str:
    arts = v.get("artifacts") or []
    first = arts[0] if arts else {}
    return str(
        v.get("download_url")
        or v.get("downloadUrl")
        or first.get("url")
        or ""
    )


def sha256_of(v: Dict[str, Any]) -> str:
    arts = v.get("artifacts") or []
    first = arts[0] if arts else {}
    return str(v.get("sha256") or first.get("sha256") or "")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: List[str] = []
    reserved: Set[str] = set(RESERVED)
    reserved_file = root / "policy" / "reserved-ids.json"
    if reserved_file.is_file():
        reserved.update(load(reserved_file).get("reserved") or [])

    plugin_ids: List[str] = []
    for plug in sorted((root / "plugins").glob("*")):
        if not plug.is_dir():
            continue
        meta_p = plug / "plugin.json"
        if not meta_p.is_file():
            errors.append(f"{plug.name}: missing plugin.json")
            continue
        meta = load(meta_p)
        pid = meta.get("id") or plug.name
        plugin_ids.append(str(pid))
        if pid != plug.name:
            errors.append(f"{plug.name}: id {pid!r} != folder name")
        if not ID_RE.match(str(pid)):
            errors.append(f"{pid}: bad id")
        if pid in reserved:
            errors.append(f"{pid}: reserved id")
        for key in ("name", "summary", "license", "repository"):
            if not meta.get(key):
                errors.append(f"{pid}: missing {key}")
        repo = str(meta.get("repository") or "")
        if repo and not repo.startswith("https://"):
            errors.append(f"{pid}: repository must be https://")

        versions = list((plug / "versions").glob("*.json")) if (plug / "versions").is_dir() else []
        if not versions:
            errors.append(f"{pid}: no versions/")
        for vp in versions:
            v = load(vp)
            if str(v.get("version") or "") and str(v.get("version")) != vp.stem:
                errors.append(f"{pid}@{vp.stem}: version field != filename")
            if v.get("staging"):
                continue
            sha = sha256_of(v)
            if not SHA_RE.match(sha):
                errors.append(f"{pid}@{vp.stem}: non-staging without valid sha256")
            url = download_url(v)
            if not url.startswith("https://"):
                errors.append(f"{pid}@{vp.stem}: need https download url")
            if ".orionplugin" not in url and not url.endswith(".zip"):
                errors.append(f"{pid}@{vp.stem}: download should be .orionplugin or .zip")

    index_path = root / "registry" / "v1" / "index.json"
    if not index_path.is_file():
        errors.append("registry/v1/index.json missing — run tools/build-index.py")
    else:
        index = load(index_path)
        if index.get("schema") != "orion.registry.index/1":
            errors.append("index: bad schema id")
        listed = {p.get("id") for p in (index.get("plugins") or []) if p.get("id")}
        source = set(plugin_ids)
        for missing in sorted(source - listed):
            errors.append(f"index missing plugin {missing!r} — run tools/build-index.py")
        for extra in sorted(listed - source):
            errors.append(f"index has orphan plugin {extra!r} (no plugins/{extra}/)")
        for row in index.get("plugins") or []:
            pid = row.get("id")
            if row.get("staging"):
                continue
            if not SHA_RE.match(str(row.get("sha256") or "")):
                errors.append(f"index {pid}: bad sha256")
            url = str(row.get("downloadUrl") or "")
            if not url.startswith("https://"):
                errors.append(f"index {pid}: bad downloadUrl")

    # Legacy product-brand scrub (does not match astral.sh / uv)
    token = "ast" + "ra"
    banned = re.compile(rf"(?i)\b{token}(?:-registry)?\b")
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".toml"}:
            continue
        if path.name in {"validate.py"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if banned.search(text):
            errors.append(f"banned brand token in {path.relative_to(root)}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(f"OK: registry listings valid ({len(plugin_ids)} plugins)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
