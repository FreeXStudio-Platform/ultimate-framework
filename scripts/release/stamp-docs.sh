#!/usr/bin/env bash
# Stamp step for the governed documentation set — the executable form of the two-commit procedure
# GUIDE-100 §Source of truth and GUIDE-170 describe. Usage:
#   scripts/release/stamp-docs.sh A     # set verified_state: verified / status: approved, rebuild — then COMMIT (anchor A)
#   scripts/release/stamp-docs.sh B     # stamp every governed document against HEAD, rebuild, re-cut the
#                                       # archive generations, regenerate the allowlist, prove with the
#                                       # engine's identity/stamps guards — then COMMIT (B)
# Set STAMP_STATUS to the verifier's verdict (default: Approved).
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1
ROOT="$(git rev-parse --show-toplevel)"; P="$(ls -d "$ROOT"/absolute-canonical-framework-v*/ | head -1)"; P="${P%/}"; export STAMP_STATUS="${STAMP_STATUS:-Approved}"
export ENGINE_HOST_ROOT=$P ENGINE_AUTHORED_DOCS_ROOT=docs/ultimate-engine PYTHONPATH=$ROOT/engine
DOCS="GUIDE-100-project-guide SYS-110-architecture SYS-120-runtime-enforcement REF-130-extension-points GUIDE-140-operations-verification REF-150-evidence-limitations REF-160-agent-blueprint-guide GUIDE-170-repository-release"
PHASE="$1"; cd "$ROOT"
rebuild(){ for d in $DOCS; do python3 -m tools.docgen.cli --strict build "$P/docs/ultimate-engine/$d.md" --formats html,json >/dev/null 2>&1 || { echo "BUILD FAILED $d"; exit 2; }; python3 -m tools.docgen.cli check "$P/docs/ultimate-engine/$d.md" >/dev/null 2>&1 || { echo "CHECK FAILED $d"; exit 2; }; done; echo "rebuild+check x8 OK"; }
hygiene(){ find "$P" "$ROOT/engine" -name __pycache__ -prune -exec rm -rf {} + ; rm -rf "$P/.docgen" "$P/.health" "$P/graphify-out" "$P/.blueprint" "$P/.docgen_cache.json" "$ROOT/engine/.docgen" "$ROOT/engine/.health"; find "$P" -type d -name .claude -empty -delete 2>/dev/null; true; }
if [ "$PHASE" = "A" ]; then
  python3 - "$P" <<'PY'
import sys,re
from pathlib import Path
P=Path(sys.argv[1])/"docs/ultimate-engine"
for f in sorted(P.glob("*.md")):
    s=f.read_text()
    if not s.startswith("---\n"): continue
    head,rest=s[4:].split("\n---\n",1)
    if "\nid: " not in "\n"+head: continue
    assert "verified_state: unverified" in head and "status: review" in head, f.name
    head=head.replace("verified_state: unverified","verified_state: verified",1).replace("status: review","status: approved",1)
    f.write_text("---\n"+head+"\n---\n"+rest); print("header ->", f.name)
PY
  rebuild; hygiene; echo "PHASE A done (verified claim in headers; commit next)"
elif [ "$PHASE" = "B" ]; then
  A=$(git rev-parse --short=12 HEAD); echo "stamping against commit $A"
  python3 - "$P" "$A" <<'PY'
import sys
from pathlib import Path
P=Path(sys.argv[1])/"docs/ultimate-engine"; A=sys.argv[2]
import os,datetime
line=f"<!-- artifact-hardened: {os.environ.get('STAMP_STATUS','Approved')} @ {A} on {datetime.date.today().isoformat()} via three-pass-v1 -->"
for f in sorted(P.glob("*.md")):
    s=f.read_text()
    if not s.startswith("---\n"): continue
    head,rest=s[4:].split("\n---\n",1)
    if "\nid: " not in "\n"+head: continue
    from tools.docgen.identity import STAMP_RE
    assert not any(m.group(1)=="artifact-hardened" for m in STAMP_RE.finditer(s)), f.name
    f.write_text("---\n"+head+"\n---\n"+line+"\n"+rest); print("stamped", f.name)
PY
  rebuild
  rm -rf "$P"/docs/archive/*
  for d in $DOCS; do python3 -m tools.docgen.cli archive cut "$P/docs/ultimate-engine/$d.md" --date "$(date +%F)" >/dev/null 2>&1 || { echo "CUT FAILED $d"; exit 3; }; done; echo "archive cut x8 OK"
  H1=$(find "$P/docs/ultimate-engine" -name "*.html" -o -name "*.json" | sort | xargs shasum -a 256 | shasum -a 256 | cut -c1-16); rebuild; H2=$(find "$P/docs/ultimate-engine" -name "*.html" -o -name "*.json" | sort | xargs shasum -a 256 | shasum -a 256 | cut -c1-16); [ "$H1" = "$H2" ] && echo "builds stable after cut" || echo "WARNING builds changed after cut ($H1 -> $H2)"
  hygiene
  ( cd "$P" && python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2 | tail -1 && python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2 --check | tail -1 )
  ( cd "$P" && python3 tools/deep_verify.py --quiet; python3 04_enforcement/validators/absolute_validate.py . | python3 -c "import sys,json; d=json.load(sys.stdin); print('validator',d['status'],d['counts'])" )
  python3 -m tools.corpus_check --root "$P" --guard stamps --guard identity --json > "${TMPDIR:-/tmp}/stamps-guards.json" 2>&1; echo "corpus_check stamps+identity rc=$?"; python3 -c "
import json; d=json.load(open('${TMPDIR:-/tmp}/stamps-guards.json')); [print(' ',g.get('guard'),g.get('status'),str(g.get('summary',''))[:200]) for g in d.get('guards',d.get('results',[]))]" 2>/dev/null || tail -5 "${TMPDIR:-/tmp}/stamps-guards.json"
  python3 -m tools.blueprint build >/dev/null 2>&1; python3 -m tools.blueprint layout >/dev/null 2>&1; python3 -m tools.blueprint completeness >/dev/null 2>&1; grep -A12 "^| document " "$P/blueprint/COMPLETENESS.md" | head -14
  hygiene; echo "PHASE B done (commit next)"
fi
