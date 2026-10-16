#!/usr/bin/env python3
"""Compatibility entry point for the canonical gate-bound release builder."""
import sys

# Importing a sibling module must never write __pycache__ into the governed
# tree. A release tree that mutates itself when a tool runs cannot satisfy
# ABS.CFG.RELEASE.SOURCE_TREE_MUTATION, and the resulting .pyc trips the very
# denylist this tooling enforces.
sys.dont_write_bytecode = True

from pathlib import Path
import runpy
import sys
canonical = Path(__file__).resolve().parents[1] / "01_control_plane/manifests_releases/tools"
sys.path.insert(0, str(canonical))
runpy.run_path(str(canonical / "build_release.py"), run_name="__main__")
