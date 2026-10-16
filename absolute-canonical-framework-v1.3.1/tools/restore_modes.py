#!/usr/bin/env python3
"""Restore the declared UNIX modes on a release tree.

Copying a release tree across a filesystem, a network share, a container mount,
or a restrictive umask commonly rewrites file permissions. The release declares
exactly which files are executable (``release_integrity.EXECUTABLE_PATHS``); the
rest are 0644. When a copy loses that, ``verify_release`` reports a mode
mismatch and refuses the tree — correctly, because a release whose executable
surface is not what it declared is not the release.

This tool re-applies the declared modes. It changes nothing else, and it cannot
change the candidate identity, which is computed from paths, sizes, and content
only.

    python3 tools/restore_modes.py [tree] [--check]
"""
from __future__ import annotations

import argparse
import json
import stat
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_control_plane/manifests_releases/tools"))

import release_integrity as integrity  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tree", nargs="?", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="report mismatches without changing anything")
    args = parser.parse_args()
    root = args.tree.resolve()

    changed: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        expected = integrity.expected_mode(relative)
        observed = stat.S_IMODE(path.stat().st_mode)
        if observed == expected:
            continue
        changed.append({"path": relative, "observed": oct(observed), "expected": oct(expected)})
        if not args.check:
            path.chmod(expected)

    result = {
        "tree": str(root),
        "mode": "CHECK" if args.check else "APPLY",
        "mismatch_count": len(changed),
        "mismatches": changed,
        "status": "PASS" if not changed else ("FAIL" if args.check else "REPAIRED"),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"PASS", "REPAIRED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
