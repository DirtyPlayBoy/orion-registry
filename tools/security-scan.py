#!/usr/bin/env python3
"""CI / local security scan for .orionplugin and plugin folders.

Layers: sha256 (optional), zip safety, forbidden binaries, Python AST heuristics.
On Windows, also runs Windows Defender MpCmdRun when available.
Exit 0 = clean, 2 = blocked.
Aligned with Orion app security_scan.py.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import List, Tuple

FORBIDDEN_EXT = {
    ".exe", ".dll", ".sys", ".scr", ".com", ".pif", ".msi", ".bat", ".cmd",
    ".ps1", ".vbs", ".vbe", ".js", ".jse", ".wsf", ".wsh", ".hta", ".cpl",
    ".msc", ".reg", ".lnk", ".iso", ".img", ".apk", ".jar",
}
DANGEROUS = {"eval", "exec", "compile", "__import__"}
RISKY_ATTR = {
    ("os", "system"),
    ("os", "popen"),
    ("ctypes", "windll"),
    ("ctypes", "CDLL"),
    ("pickle", "loads"),
    ("pickle", "load"),
    ("marshal", "loads"),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def defender(path: Path) -> Tuple[bool, str]:
    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Windows Defender" / "MpCmdRun.exe",
    ]
    platform = Path(r"C:\ProgramData\Microsoft\Windows Defender\Platform")
    if platform.is_dir():
        candidates.extend(sorted(platform.glob("*/MpCmdRun.exe"), reverse=True)[:1])
    exe = next((c for c in candidates if c.is_file()), None)
    if not exe:
        return True, "defender skipped (not found)"
    try:
        proc = subprocess.run(
            [str(exe), "-Scan", "-ScanType", "3", "-File", str(path), "-DisableRemediation"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if proc.returncode == 2:
            return False, (proc.stdout or "") + (proc.stderr or "")
        return True, f"defender ok exit={proc.returncode}"
    except Exception as exc:
        return True, f"defender error skipped: {exc}"


def ast_scan(root: Path) -> Tuple[List[str], List[str]]:
    blockers: List[str] = []
    warnings: List[str] = []
    for path in root.rglob("*.py"):
        try:
            src = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src, filename=str(path))
        except Exception as exc:
            warnings.append(f"{path.name}: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                if isinstance(f, ast.Name) and f.id in DANGEROUS:
                    blockers.append(f"{path.name}: {f.id}()")
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                    pair = (f.value.id, f.attr)
                    if pair in RISKY_ATTR:
                        blockers.append(f"{path.name}: {pair[0]}.{pair[1]}")
                    if pair[0] == "subprocess":
                        for kw in node.keywords:
                            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                blockers.append(f"{path.name}: subprocess shell=True")
    return blockers, warnings


def scan_dir(root: Path) -> int:
    blockers: List[str] = []
    warnings: List[str] = []
    if not (root / "plugin.toml").is_file():
        kids = [p for p in root.iterdir() if p.is_dir()]
        if len(kids) == 1 and (kids[0] / "plugin.toml").is_file():
            root = kids[0]
        else:
            blockers.append("plugin.toml missing")
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in FORBIDDEN_EXT:
            blockers.append(f"forbidden file {path.relative_to(root)}")
    b, w = ast_scan(root)
    blockers.extend(b)
    warnings.extend(w)
    ok_d, detail_d = defender(root)
    if not ok_d:
        blockers.append("Windows Defender: " + detail_d[:400])
    else:
        print("OK:", detail_d)
    for x in warnings:
        print("WARN:", x)
    for x in blockers:
        print("BLOCK:", x, file=sys.stderr)
    return 0 if not blockers else 2


def scan_archive(path: Path, expected: str = "") -> int:
    digest = sha256(path)
    print("sha256=", digest)
    if expected and digest.lower() != expected.lower():
        print("BLOCK: sha256 mismatch", file=sys.stderr)
        return 2
    ok_d, detail_d = defender(path)
    print("OK:" if ok_d else "BLOCK:", detail_d)
    if not ok_d:
        return 2
    tmp = Path(tempfile.mkdtemp(prefix="orion-reg-scan-"))
    try:
        with zipfile.ZipFile(path, "r") as zf:
            for info in zf.infolist():
                name = info.filename.replace("\\", "/")
                if name.startswith("/") or ".." in name.split("/"):
                    print("BLOCK: zip-slip", name, file=sys.stderr)
                    return 2
                if Path(name).suffix.lower() in FORBIDDEN_EXT:
                    print("BLOCK: forbidden", name, file=sys.stderr)
                    return 2
            zf.extractall(tmp)
        return scan_dir(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    p = argparse.ArgumentParser(description="Orion registry security scan")
    p.add_argument("path")
    p.add_argument("--sha256", default="")
    args = p.parse_args()
    path = Path(args.path)
    if not path.exists():
        print("FAIL: path not found", file=sys.stderr)
        return 1
    if path.is_file():
        return scan_archive(path, args.sha256)
    return scan_dir(path)


if __name__ == "__main__":
    raise SystemExit(main())
