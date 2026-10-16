#!/usr/bin/env python3
"""Reference pre-write gate: deny writes lacking explicit scope and authority references."""
import sys

# Importing a sibling module must never write __pycache__ into the governed
# tree. A release tree that mutates itself when a tool runs cannot satisfy
# ABS.CFG.RELEASE.SOURCE_TREE_MUTATION, and the resulting .pyc trips the very
# denylist this tooling enforces.
sys.dont_write_bytecode = True

import json, sys
request=json.load(sys.stdin)
missing=[k for k in ("scope_id","actor_id","authority_ref","rollback_ref") if not request.get(k)]
print(json.dumps({"decision":"DENY" if missing else "ALLOW","missing":missing}))
raise SystemExit(2 if missing else 0)
