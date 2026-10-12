#!/usr/bin/env python3
"""Rename APKs to release-safe asset names before uploading to GitHub.

GitHub silently rewrites asset names containing spaces or parentheses
(e.g. ``smart_launcher-...-v6.6 build 020.apk`` is stored with dots), so the
uploaded name would no longer match the keep-list given to
cleanup_old_apks.py, which would then delete the APK it just uploaded, or
the ``apk`` names recorded in manifest.json. This applies the same renaming
as the GitLab publisher (gitlab_api.safe_filename) and patches manifest.json
to match. The manifest's resolved_version is left untouched so incremental
planning still compares real app versions.

Usage: python scripts/safe_asset_names.py --apks-dir ./release-apks
"""
import argparse
import json
import sys
from pathlib import Path


def safe_filename(name: str) -> str:
    # Keep in sync with src/gitlab_api.py:safe_filename (not imported to
    # avoid pulling the builder's dependencies into the release job).
    name = name.replace("(", "-").replace(")", "")
    safe = "".join(c for c in name if c.isascii() and (c.isalnum() or c in "._-"))
    return safe or "file"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apks-dir", default=".", help="directory holding the APKs (and manifest.json)")
    args = parser.parse_args()

    apks_dir = Path(args.apks_dir)
    renames: dict[str, str] = {}
    for apk in sorted(apks_dir.glob("*.apk")):
        safe = safe_filename(apk.name)
        if safe == apk.name:
            continue
        apk.replace(apk.with_name(safe))
        renames[apk.name] = safe
        print(f"Renamed {apk.name} -> {safe}")

    manifest = apks_dir / "manifest.json"
    if renames and manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for entry in data.get("entries", {}).values():
            if entry.get("apk", "") in renames:
                entry["apk"] = renames[entry["apk"]]
        manifest.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Patched manifest.json for {len(renames)} renamed file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
